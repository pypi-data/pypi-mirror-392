import asyncio
import time
from typing import Optional
from unittest.mock import patch

import pytest
from pydantic import BaseModel, Field

from dr_agent.mcp_backend.cache import DEFAULT_CACHE, ApiCache, cached


class ApiResponse(BaseModel):
    query: str
    results: list
    call_number: int


class TestApiCache:
    """Test the ApiCache class functionality"""

    @pytest.fixture
    def test_cache(self):
        """Create a test cache instance with a separate cache directory"""
        cache = ApiCache(cache_dir=".test_cache", cache_ttl=60)
        yield cache
        # Cleanup
        cache.clear_all()

    def test_cache_initialization(self, test_cache):
        """Test cache initialization with custom parameters"""
        assert test_cache.cache_ttl == 60
        assert ".test_cache" in str(test_cache.cache_dir)

    def test_cache_key_generation(self, test_cache):
        """Test cache key generation for different inputs"""

        def test_func(arg1, arg2, param):
            return f"{arg1}-{arg2}-{param}"

        key1 = test_cache._get_cache_key(
            test_func, ("arg1", "arg2"), {"param": "value"}
        )
        key2 = test_cache._get_cache_key(
            test_func, ("arg1", "arg2"), {"param": "value"}
        )
        key3 = test_cache._get_cache_key(
            test_func, ("arg1", "arg3"), {"param": "value"}
        )

        # Same inputs should generate same key
        assert key1 == key2

        # Different inputs should generate different keys
        assert key1 != key3

    def test_cache_set_and_get(self, test_cache):
        """Test basic cache set and get operations"""
        test_data = {"result": "test_value", "timestamp": time.time()}
        cache_key = "test_key"

        # Set data
        test_cache.set(cache_key, test_data)

        # Get data
        retrieved_data = test_cache.get(cache_key)
        assert retrieved_data == test_data

    def test_cache_miss(self, test_cache):
        """Test cache miss returns None"""
        result = test_cache.get("nonexistent_key")
        assert result is None

    def test_cache_clear_all(self, test_cache):
        """Test clearing all cache entries"""
        # Add some data
        test_cache.set("key1", {"data": "value1"})
        test_cache.set("key2", {"data": "value2"})

        # Clear cache
        cleared_count = test_cache.clear_all()
        assert cleared_count >= 0  # Should return count

        # Verify cache is empty
        assert test_cache.get("key1") is None
        assert test_cache.get("key2") is None


class TestCachedDecorator:
    """Test the @cached decorator functionality"""

    def setup_method(self):
        """Clear cache and reset counters before each test"""
        DEFAULT_CACHE.clear_all()

    def test_sync_function_caching(self):
        """Test caching behavior with sync functions"""
        call_count = 0

        @cached()
        def mock_sync_function(query: str, num_results: int = 10) -> dict:
            nonlocal call_count
            call_count += 1
            time.sleep(0.01)  # Simulate work

            return {
                "query": query,
                "num_results": num_results,
                "call_number": call_count,
                "timestamp": time.time(),
            }

        # First call should execute function
        result1 = mock_sync_function("python tutorial", 5)
        assert result1["call_number"] == 1

        # Second call with same params should use cache
        result2 = mock_sync_function("python tutorial", 5)
        assert result2["call_number"] == 1  # Same call number means cached
        assert result1 == result2

        # Third call with different params should execute function
        result3 = mock_sync_function("python tutorial", 10)
        assert result3["call_number"] == 2  # New call

    def test_cache_with_different_parameter_types(self):
        """Test caching with various parameter types"""
        call_count = 0

        @cached()
        def mock_function(query: str, num_results: int = 10) -> dict:
            nonlocal call_count
            call_count += 1
            return {
                "query": query,
                "num_results": num_results,
                "call_number": call_count,
            }

        # Test with positional args
        result1 = mock_function("test", 5)
        # Test with keyword args - should be treated as same call
        result2 = mock_function(query="test", num_results=5)

        # Should be treated as same call and use cache
        assert result1["call_number"] == result2["call_number"] == 1

    @pytest.mark.asyncio
    async def test_async_function_caching(self):
        """Test caching behavior with async functions"""
        call_count = 0

        @cached()
        async def mock_async_function(query: str, num_results: int = 10) -> dict:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)  # Simulate async work
            return {
                "query": query,
                "num_results": num_results,
                "call_number": call_count,
            }

        # First call should execute function
        result1 = await mock_async_function("async test", 5)
        assert result1["call_number"] == 1

        # Second call with same params should use cache
        result2 = await mock_async_function("async test", 5)
        assert result2["call_number"] == 1  # Same call number means cached
        assert result1 == result2

    @pytest.mark.asyncio
    async def test_async_and_sync_caching_together(self):
        """Test that async and sync functions can both be cached"""
        async_count = 0
        sync_count = 0

        @cached()
        async def async_func(value: str) -> dict:
            nonlocal async_count
            async_count += 1
            return {"value": f"async_{value}", "count": async_count}

        @cached()
        def sync_func(value: str) -> dict:
            nonlocal sync_count
            sync_count += 1
            return {"value": f"sync_{value}", "count": sync_count}

        # Test both function types
        async_result1 = await async_func("test")
        sync_result1 = sync_func("test")
        async_result2 = await async_func("test")  # Should use cache
        sync_result2 = sync_func("test")  # Should use cache

        assert async_result1["count"] == async_result2["count"] == 1
        assert sync_result1["count"] == sync_result2["count"] == 1

    @pytest.mark.asyncio
    async def test_async_function_different_params(self):
        """Test async function caching with different parameters"""
        call_count = 0

        @cached()
        async def async_api_call(url: str, timeout: int = 30) -> dict:
            nonlocal call_count
            call_count += 1
            return {"url": url, "call_count": call_count}

        # Different URLs should not use cache
        result1 = await async_api_call("https://example.com")
        result2 = await async_api_call("https://different.com")
        result3 = await async_api_call("https://example.com")  # Should use cache

        assert result1["call_count"] == 1
        assert result2["call_count"] == 2
        assert result3["call_count"] == 1  # Cached from first call

    def test_custom_cache_instance(self):
        """Test using custom cache instance with decorator"""
        custom_cache = ApiCache(cache_dir=".custom_test_cache", cache_ttl=30)
        call_count = 0

        @cached(cache=custom_cache)
        def custom_cached_func(value: str) -> dict:
            nonlocal call_count
            call_count += 1
            return {"value": value, "call_count": call_count}

        try:
            # Test caching works with custom cache
            result1 = custom_cached_func("test")
            result2 = custom_cached_func("test")

            assert result1["call_count"] == result2["call_count"] == 1
        finally:
            # Cleanup
            custom_cache.clear_all()

    def test_cache_with_timeout_filtering(self):
        """Test that timeout parameter is excluded from cache key generation"""
        call_count = 0

        @cached()
        def mock_function(query: str, num_results: int = 10, **kwargs) -> dict:
            nonlocal call_count
            call_count += 1
            return {
                "query": query,
                "num_results": num_results,
                "call_number": call_count,
            }

        # These should be cached as same call (timeout should be excluded)
        result1 = mock_function("test query", num_results=10, timeout=30)
        result2 = mock_function("test query", num_results=10, timeout=60)

        assert result1["call_number"] == result2["call_number"] == 1


class TestCacheIntegration:
    """Integration tests for cache functionality"""

    def setup_method(self):
        """Clear default cache before each test"""
        DEFAULT_CACHE.clear_all()

    def test_default_cache_usage(self):
        """Test that functions use default cache when no cache specified"""
        call_count = 0

        @cached()
        def test_function(param: str) -> dict:
            nonlocal call_count
            call_count += 1
            return {"param": param, "count": call_count}

        # First call
        result1 = test_function("test")
        assert result1["count"] == 1

        # Second call should use cache
        result2 = test_function("test")
        assert result2["count"] == 1  # Should be cached

        # Clear default cache
        DEFAULT_CACHE.clear_all()

        # Call again should execute function
        result3 = test_function("test")
        assert result3["count"] == 2  # Should be new execution

    def test_cache_error_handling(self):
        """Test cache behavior when caching fails"""
        call_count = 0

        @cached()
        def test_function(param: str) -> dict:
            nonlocal call_count
            call_count += 1
            return {"param": param, "count": call_count}

        with patch.object(DEFAULT_CACHE, "set", side_effect=Exception("Cache error")):
            # Function should still work even if caching fails
            result = test_function("test")
            assert result["count"] == 1

        # Subsequent call should work normally (no cache was set due to error)
        result2 = test_function("test")
        assert result2["count"] == 2

    def test_real_api_usage_pattern(self):
        """Test caching with a realistic API usage pattern"""
        call_count = 0

        @cached()
        def mock_api_call(query: str, num_results: int = 10) -> dict:
            nonlocal call_count
            call_count += 1
            return {
                "query": query,
                "results": [f"Result {i}" for i in range(num_results)],
                "call_number": call_count,
            }

        # Simulate multiple API calls that might happen in real usage
        queries = [
            ("python programming", 10),
            ("javascript tutorial", 5),
            ("python programming", 10),  # Duplicate - should use cache
            ("react hooks", 8),
            ("javascript tutorial", 5),  # Duplicate - should use cache
        ]

        results = []
        for query, num_results in queries:
            result = mock_api_call(query, num_results)
            results.append(result)

        # Should have made 3 actual API calls (2 were cached)
        assert call_count == 3

        # Verify caching worked correctly
        assert (
            results[0]["call_number"] == results[2]["call_number"]
        )  # Same query cached
        assert (
            results[1]["call_number"] == results[4]["call_number"]
        )  # Same query cached
        assert (
            results[0]["call_number"] != results[1]["call_number"]
        )  # Different queries


class TestCacheWithPydanticModels:
    """Test cache functionality with Pydantic models (like in actual API usage)"""

    def setup_method(self):
        """Clear cache before each test"""
        DEFAULT_CACHE.clear_all()

    def test_cache_with_pydantic_return_types(self):
        """Test that caching works with functions that return Pydantic models"""

        call_count2 = 0

        @cached()
        def mock_api_with_pydantic(query: str) -> ApiResponse:
            nonlocal call_count2
            call_count2 += 1
            return ApiResponse(
                query=query,
                results=[f"result_{i}" for i in range(3)],
                call_number=call_count2,
            )

        # First call
        result1 = mock_api_with_pydantic("test query")
        assert result1.call_number == 1

        # Second call should use cache
        result2 = mock_api_with_pydantic("test query")
        assert result2.call_number == 1  # Should be cached
        assert result1.model_dump() == result2.model_dump()


class SearchResult(BaseModel):
    """Mock search result model similar to API response models"""

    query: str
    results: list
    total_results: int


class FetchResult(BaseModel):
    """Mock fetch result model similar to crawl4ai result"""

    url: str
    success: bool
    content: str
    error: Optional[str] = Field(None)


class TestCacheApiPatterns:
    """Test cache with patterns similar to actual API functions"""

    def setup_method(self):
        """Clear cache before each test"""
        DEFAULT_CACHE.clear_all()

    def test_search_api_caching_with_pydantic_models(self):
        """Test caching works with Pydantic model returns (like SearchResponse)"""
        search_call_count = 0

        @cached()
        def mock_search_api(
            query: str, num_results: int = 10, search_type: str = "search"
        ) -> SearchResult:
            """Mock search API similar to serper_apis.py patterns"""
            nonlocal search_call_count
            search_call_count += 1

            return SearchResult(
                query=query,
                results=[f"Result {i} for {query}" for i in range(min(num_results, 5))],
                total_results=search_call_count
                * 100,  # Use call count to verify caching
            )

        # First call
        result1 = mock_search_api("python programming", 10, "search")
        assert result1.total_results == 100  # First call

        # Same call should use cache
        result2 = mock_search_api("python programming", 10, "search")
        assert result2.total_results == 100  # Should be cached
        assert result1.model_dump() == result2.model_dump()

        # Different query should call API again
        result3 = mock_search_api("machine learning", 10, "search")
        assert result3.total_results == 200  # Second actual call

    def test_sync_api_with_optional_parameters(self):
        """Test caching behavior with optional parameters (like real API functions)"""
        call_count = 0

        @cached()
        def mock_fetch_api(
            url: str,
            query: Optional[str] = None,
            ignore_links: bool = True,
            use_pruning: bool = False,
        ) -> FetchResult:
            """Mock fetch API similar to sync patterns"""
            nonlocal call_count
            call_count += 1

            return FetchResult(
                url=url, success=True, content=f"Content for {url} (call #{call_count})"
            )

        # First call
        result1 = mock_fetch_api("https://example.com", ignore_links=True)
        assert "call #1" in result1.content

        # Same parameters should use cache
        result2 = mock_fetch_api("https://example.com", ignore_links=True)
        assert "call #1" in result2.content  # Should be cached
        assert result1.model_dump() == result2.model_dump()

        # Different URL should call API again
        result3 = mock_fetch_api("https://different.com", ignore_links=True)
        assert "call #2" in result3.content

    def test_cache_with_default_parameters(self):
        """Test caching behavior with default parameters"""
        call_count = 0

        @cached()
        def mock_api(
            query: str, num_results: int = 10, search_type: str = "search"
        ) -> dict:
            nonlocal call_count
            call_count += 1
            return {
                "query": query,
                "num_results": num_results,
                "call_count": call_count,
            }

        # Call with default parameters
        result1 = mock_api("test query")

        # Explicitly specify default parameters - should use cache
        result2 = mock_api("test query", num_results=10, search_type="search")
        assert result1["call_count"] == result2["call_count"] == 1

    def test_cache_with_kwargs_filtering(self):
        """Test that certain parameters (like timeout) are filtered from cache keys"""
        call_count = 0

        @cached()
        def mock_api_with_kwargs(url: str, **kwargs) -> dict:
            nonlocal call_count
            call_count += 1
            return {"url": url, "call_count": call_count}

        # These should be cached as same call despite different timeout
        result1 = mock_api_with_kwargs("https://example.com", timeout=30000)
        result2 = mock_api_with_kwargs("https://example.com", timeout=60000)

        # Should be same cached result (timeout filtered out)
        assert result1["call_count"] == result2["call_count"] == 1

    def test_cache_key_generation_with_pydantic_models(self):
        """Test that cache works correctly when functions receive Pydantic models as input"""
        call_count = 0

        @cached()
        def api_with_pydantic_input(search_params: SearchResult) -> dict:
            nonlocal call_count
            call_count += 1
            return {"processed": search_params.query, "call": call_count}

        # Create test models with same content
        params1 = SearchResult(query="test", results=[], total_results=5)
        params2 = SearchResult(query="test", results=[], total_results=5)

        result1 = api_with_pydantic_input(params1)
        result2 = api_with_pydantic_input(params2)

        # Should use cache since model contents are the same
        assert result1["call"] == result2["call"] == 1

    def test_real_world_api_usage_pattern(self):
        """Test caching with a realistic API usage pattern"""
        search_call_count = 0

        @cached()
        def mock_search_api(query: str, num_results: int = 10) -> SearchResult:
            nonlocal search_call_count
            search_call_count += 1

            return SearchResult(
                query=query,
                results=[f"Result {i} for {query}" for i in range(min(num_results, 3))],
                total_results=search_call_count * 100,
            )

        # Simulate multiple searches that might happen in real usage
        queries = [
            ("python programming", 10),
            ("javascript tutorial", 5),
            ("python programming", 10),  # Duplicate - should use cache
            ("react hooks", 8),
            ("javascript tutorial", 5),  # Duplicate - should use cache
        ]

        results = []
        for query, num_results in queries:
            result = mock_search_api(query, num_results)
            results.append(result)

        # Should have made 3 actual API calls (2 were cached)
        assert search_call_count == 3

        # Verify caching worked correctly
        assert results[0].total_results == results[2].total_results  # Same query cached
        assert results[1].total_results == results[4].total_results  # Same query cached
        assert results[0].total_results != results[1].total_results  # Different queries

    def test_cache_with_complex_return_types(self):
        """Test caching with complex nested data structures like real API responses"""
        call_count = 0

        @cached()
        def mock_complex_api(query: str) -> dict:
            nonlocal call_count
            call_count += 1

            return {
                "query": query,
                "metadata": {
                    "call_id": call_count,
                    "timestamp": "2023-01-01T00:00:00Z",
                    "credits_used": 1,
                },
                "results": [
                    {
                        "title": f"Result {i} for {query}",
                        "snippet": f"This is snippet {i}",
                        "url": f"https://example{i}.com",
                    }
                    for i in range(3)
                ],
            }

        # First call
        result1 = mock_complex_api("test search")
        assert result1["metadata"]["call_id"] == 1

        # Second call should use cache
        result2 = mock_complex_api("test search")
        assert result2["metadata"]["call_id"] == 1  # Should be cached
        assert result1 == result2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
