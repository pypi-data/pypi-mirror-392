"""Execution engine for PromptGuard."""
import asyncio
import time
from typing import Optional, List, Union, Dict, Any
from datetime import datetime

from promptguard.core.response import PromptResult, ExecutionMetadata
from promptguard.exceptions import PromptExecutionError, ValidationError, RateLimitError
from promptguard.providers.base import BaseProvider
from promptguard.retry.strategies import RetryStrategy, ExponentialBackoff
from promptguard.caching.base import CacheBackend


class PromptExecutor:
    """Executes prompts with retry logic and fallbacks."""
    
    def __init__(
        self,
        providers: List[BaseProvider],
        retry_strategy: Optional[RetryStrategy] = None,
        cache: Optional[CacheBackend] = None,
        timeout: float = 30.0,
        on_retry: Optional[callable] = None,
        on_failure: Optional[callable] = None,
    ):
        """Initialize executor.
        
        Args:
            providers: List of providers to try
            retry_strategy: Retry strategy (default: exponential backoff)
            cache: Cache backend
            timeout: Request timeout
            on_retry: Callback on retry
            on_failure: Callback on failure
        """
        self.providers = providers
        self.retry_strategy = retry_strategy or ExponentialBackoff()
        self.cache = cache
        self.timeout = timeout
        self.on_retry = on_retry
        self.on_failure = on_failure
    
    async def execute_cascade(
        self,
        messages: List[dict],
        models: List[str],
        cache_key: Optional[str] = None,
        **kwargs
    ) -> PromptResult:
        """Execute with cascade strategy - try models in order.
        
        Args:
            messages: Message list
            models: Model identifiers to try in order
            cache_key: Cache key
            **kwargs: Execution parameters
            
        Returns:
            PromptResult
        """
        attempts = []
        last_error = None
        
        # Try cache first
        if self.cache and cache_key:
            try:
                cached = await self.cache.get(cache_key)
                if cached:
                    return PromptResult(
                        success=True,
                        response=cached.get('response'),
                        metadata=ExecutionMetadata(
                            model_used=cached.get('model'),
                            provider=cached.get('provider'),
                            attempts=0,
                            execution_time_ms=0,
                            tokens_used=cached.get('tokens', {}),
                            estimated_cost=cached.get('cost', 0),
                            cached=True,
                            cache_key=cache_key,
                        )
                    )
            except Exception:
                pass  # Ignore cache errors
        
        start_time = time.time()
        
        for model in models:
            provider = self.providers[0]  # Get from registry by provider
            
            for attempt in range(3):  # Max retries
                try:
                    response = await asyncio.wait_for(
                        provider.execute(
                            messages=messages,
                            model=model,
                            **kwargs
                        ),
                        timeout=self.timeout
                    )
                    
                    execution_time = (time.time() - start_time) * 1000
                    
                    result = PromptResult(
                        success=True,
                        response=response.get('content'),
                        raw_response=response.get('raw'),
                        metadata=ExecutionMetadata(
                            model_used=model,
                            provider=model.split('/')[0],
                            attempts=len(attempts) + 1,
                            execution_time_ms=execution_time,
                            tokens_used=response.get('usage', {}),
                            estimated_cost=provider.estimate_cost(
                                response.get('usage', {}).get('input', 0),
                                response.get('usage', {}).get('output', 0),
                                model
                            ),
                            cached=False,
                            retry_history=attempts,
                        )
                    )
                    
                    # Cache successful response
                    if self.cache and cache_key:
                        try:
                            await self.cache.set(cache_key, {
                                'response': response.get('content'),
                                'model': model,
                                'provider': model.split('/')[0],
                                'tokens': response.get('usage', {}),
                                'cost': result.metadata.estimated_cost,
                            }, ttl=3600)
                        except Exception:
                            pass  # Ignore cache errors
                    
                    return result
                
                except asyncio.TimeoutError:
                    error = Exception(f"Timeout after {self.timeout}s")
                    attempts.append({
                        'attempt': len(attempts) + 1,
                        'model': model,
                        'error': str(error),
                        'delay': 0
                    })
                    last_error = error
                    
                except RateLimitError as e:
                    delay = e.retry_after or (2 ** attempt)
                    attempts.append({
                        'attempt': len(attempts) + 1,
                        'model': model,
                        'error': str(e),
                        'delay': delay
                    })
                    last_error = e
                    
                    if self.on_retry:
                        self.on_retry(len(attempts), e)
                    
                    await asyncio.sleep(delay)
                
                except Exception as e:
                    if attempt < 2:  # Retry
                        delay = self.retry_strategy.get_delay(attempt, e)
                        attempts.append({
                            'attempt': len(attempts) + 1,
                            'model': model,
                            'error': str(e),
                            'delay': delay
                        })
                        last_error = e
                        
                        if self.on_retry:
                            self.on_retry(len(attempts), e)
                        
                        await asyncio.sleep(delay)
                    else:
                        attempts.append({
                            'attempt': len(attempts) + 1,
                            'model': model,
                            'error': str(e),
                            'delay': 0
                        })
                        last_error = e
        
        # All models and retries failed
        if self.on_failure:
            self.on_failure(last_error)
        
        raise PromptExecutionError(
            f"All models failed after {len(attempts)} attempts",
            attempts,
            last_error
        )
