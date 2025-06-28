# Performance Optimization Guide

import asyncio
import aiohttp
from functools import lru_cache
from typing import List, Any
import weakref

# 1. Use connection pooling
async def connection_pooling_example():
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(limit=100)
    ) as session:
        # Reuse session for multiple requests
        pass

# 2. Batch operations
async def batch_process(items: List[Any], batch_size: int = 10):
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        await asyncio.gather(*[process_item(item) for item in batch])

async def process_item(item: Any):
    # Process individual item
    pass

# 3. Cache frequently used data
@lru_cache(maxsize=1000)
def get_tool_metadata(tool_name: str) -> dict:
    return expensive_metadata_lookup(tool_name)

def expensive_metadata_lookup(tool_name: str) -> dict:
    # Expensive operation
    return {"name": tool_name, "metadata": "..."}

# 4. Use weak references for large objects
agent_cache = weakref.WeakValueDictionary()