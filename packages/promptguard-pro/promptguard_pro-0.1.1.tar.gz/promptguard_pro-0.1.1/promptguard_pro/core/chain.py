"""Main PromptChain orchestrator for PromptGuard."""
import asyncio
import time
from typing import Optional, List, Union, Dict, Any, AsyncIterator, Type, Callable, Literal
from pydantic import BaseModel

from promptguard.core.response import PromptResult, StreamChunk, ExecutionMetadata
from promptguard.core.executor import PromptExecutor
from promptguard.core.models import get_model_info
from promptguard.providers import get_provider
from promptguard.validation.semantic import Validator
from promptguard.validation.schema import SchemaValidator
from promptguard.caching.base import CacheBackend, generate_cache_key
from promptguard.retry.strategies import RetryStrategy, ExponentialBackoff
from promptguard.exceptions import PromptExecutionError, ValidationError, InvalidConfigurationError
from promptguard.core.response import LogLevel


class PromptChain:
    """Main orchestrator for LLM prompt execution with reliability features."""
    
    def __init__(
        self,
        models: List[str],
        strategy: Literal["cascade", "fastest", "cheapest", "parallel"] = "cascade",
        max_retries: int = 3,
        retry_delay: Union[float, Literal["exponential", "fibonacci"]] = "exponential",
        timeout: float = 30.0,
        response_schema: Optional[Type[BaseModel]] = None,
        validation_mode: Literal["strict", "lenient"] = "strict",
        validators: Optional[List[Validator]] = None,
        cache: Optional[CacheBackend] = None,
        cache_ttl: int = 3600,
        log_level: LogLevel = LogLevel.INFO,
        on_success: Optional[Callable] = None,
        on_retry: Optional[Callable] = None,
        on_failure: Optional[Callable] = None,
        **provider_kwargs
    ):
        """Initialize PromptChain.
        
        Args:
            models: List of model identifiers
            strategy: Execution strategy
            max_retries: Maximum retry attempts
            retry_delay: Delay between retries
            timeout: Request timeout
            response_schema: Pydantic model for validation
            validation_mode: Strict or lenient validation
            validators: List of semantic validators
            cache: Cache backend
            cache_ttl: Cache TTL in seconds
            log_level: Logging level
            on_success: Success callback
            on_retry: Retry callback
            on_failure: Failure callback
            **provider_kwargs: Provider-specific config
        """
        self.models = models
        self.strategy = strategy
        self.max_retries = max_retries
        self.timeout = timeout
        self.response_schema = response_schema
        self.validation_mode = validation_mode
        self.validators = validators or []
        self.cache = cache
        self.cache_ttl = cache_ttl
        self.log_level = log_level
        self.on_success = on_success
        self.on_retry = on_retry
        self.on_failure = on_failure
        self.provider_kwargs = provider_kwargs
        
        # Initialize providers
        self.providers = {}
        for model in models:
            provider_name = model.split("/")[0]
            if provider_name not in self.providers:
                self.providers[provider_name] = get_provider(model, **provider_kwargs)
        
        # Initialize retry strategy
        if isinstance(retry_delay, str):
            if retry_delay == "exponential":
                self.retry_strategy = ExponentialBackoff(max_retries=max_retries)
            else:
                self.retry_strategy = ExponentialBackoff(max_retries=max_retries)
        else:
            from promptguard.retry.strategies import ConstantDelay
            self.retry_strategy = ConstantDelay(delay=retry_delay, max_retries=max_retries)
        
        # Initialize schema validator
        self.schema_validator = SchemaValidator(response_schema) if response_schema else None
    
    async def execute(
        self,
        prompt: Union[str, List[dict]],
        context: Optional[dict] = None,
        temperature: float = 0.01,
        max_tokens: int = 4096,
        cache_key: Optional[str] = None,
        metadata: Optional[dict] = None,
        **kwargs
    ) -> PromptResult:
        """Execute prompt with automatic retry and fallback.
        
        Args:
            prompt: Prompt string or message list
            context: Additional context
            temperature: Model temperature
            max_tokens: Maximum output tokens
            cache_key: Cache key
            metadata: Custom metadata
            **kwargs: Additional arguments
            
        Returns:
            PromptResult
            
        Raises:
            PromptExecutionError: If all attempts fail
            ValidationError: If validation fails in strict mode
        """
        # Convert prompt to messages format
        messages = self._format_messages(prompt, context)
        
        # Generate cache key if not provided
        if not cache_key and self.cache:
            cache_key = generate_cache_key(
                self._messages_to_string(messages),
                self.models[0],
                prefix="promptguard"
            )
        
        try:
            # Execute based on strategy
            if self.strategy == "cascade":
                result = await self._execute_cascade(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    cache_key=cache_key,
                    **kwargs
                )
            else:
                result = await self._execute_cascade(messages, temperature, max_tokens, cache_key, **kwargs)
            
            # Validate response
            if self.response_schema:
                success, validated, error = self.schema_validator.validate(result.response)
                if not success and self.validation_mode == "strict":
                    raise ValidationError(error, {'schema': error})
                if success:
                    result.response = validated
            
            # Run semantic validators
            validation_results = {}
            for validator in self.validators:
                v_result = await validator.validate(
                    result.response if isinstance(result.response, str) else str(result.response),
                    context=context
                )
                validation_results[validator.__class__.__name__] = {
                    'passed': v_result.passed,
                    'confidence': v_result.confidence,
                    'message': v_result.message,
                }
                if not v_result.passed and self.validation_mode == "strict":
                    raise ValidationError(v_result.message, validation_results)
            
            result.validation_results = validation_results
            
            if self.on_success:
                self.on_success(result)
            
            return result
        
        except Exception as e:
            if self.on_failure:
                self.on_failure(e)
            raise
    
    async def stream(
        self,
        prompt: Union[str, List[dict]],
        context: Optional[dict] = None,
        temperature: float = 0.01,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """Stream response chunks.
        
        Args:
            prompt: Prompt string or message list
            context: Additional context
            temperature: Model temperature
            max_tokens: Maximum output tokens
            **kwargs: Additional arguments
            
        Yields:
            StreamChunk objects
        """
        messages = self._format_messages(prompt, context)
        
        accumulated_text = ""
        for model in self.models:
            provider_name = model.split("/")[0]
            provider = self.providers[provider_name]
            
            try:
                async for chunk in provider.stream(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                ):
                    accumulated_text += chunk
                    yield StreamChunk(
                        delta=chunk,
                        accumulated_text=accumulated_text,
                        finished=False
                    )
                
                # Successful stream
                yield StreamChunk(
                    delta="",
                    accumulated_text=accumulated_text,
                    finished=True
                )
                return
            
            except Exception as e:
                if model == self.models[-1]:
                    raise PromptExecutionError(f"Streaming failed for all models", [], e)
                continue
    
    async def batch_execute(
        self,
        prompts: List[Union[str, List[dict]]],
        max_concurrent: int = 5,
        show_progress: bool = False,
        fail_fast: bool = False,
        **kwargs
    ) -> List[PromptResult]:
        """Execute multiple prompts with concurrency control.
        
        Args:
            prompts: List of prompts
            max_concurrent: Max concurrent requests
            show_progress: Show progress bar
            fail_fast: Stop on first error
            **kwargs: Additional arguments
            
        Returns:
            List of PromptResult objects
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def bounded_execute(prompt):
            async with semaphore:
                try:
                    return await self.execute(prompt, **kwargs)
                except Exception as e:
                    if fail_fast:
                        raise
                    return PromptResult(
                        success=False,
                        error=e,
                        metadata=ExecutionMetadata(
                            model_used="",
                            provider="",
                            attempts=0,
                            execution_time_ms=0,
                            tokens_used={},
                            estimated_cost=0,
                            cached=False,
                        )
                    )
        
        tasks = [bounded_execute(prompt) for prompt in prompts]
        
        if show_progress:
            # Simple progress indicator
            results = []
            for i, task in enumerate(asyncio.as_completed(tasks)):
                result = await task
                results.append(result)
                print(f"Progress: {len(results)}/{len(prompts)}")
            return results
        else:
            return await asyncio.gather(*tasks)
    
    async def _execute_cascade(
        self,
        messages: List[dict],
        temperature: float,
        max_tokens: int,
        cache_key: Optional[str],
        **kwargs
    ) -> PromptResult:
        """Execute with cascade strategy."""
        executor = PromptExecutor(
            providers=list(self.providers.values()),
            retry_strategy=self.retry_strategy,
            cache=self.cache,
            timeout=self.timeout,
            on_retry=self.on_retry,
            on_failure=self.on_failure,
        )
        
        return await executor.execute_cascade(
            messages=messages,
            models=self.models,
            cache_key=cache_key,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def _format_messages(
        self,
        prompt: Union[str, List[dict]],
        context: Optional[dict] = None
    ) -> List[dict]:
        """Format prompt into messages list."""
        if isinstance(prompt, list):
            return prompt
        
        # String prompt
        if context:
            prompt = prompt.format(**context)
        
        return [{"role": "user", "content": prompt}]
    
    def _messages_to_string(self, messages: List[dict]) -> str:
        """Convert messages list to string for caching."""
        return " ".join(msg.get("content", "") for msg in messages)
