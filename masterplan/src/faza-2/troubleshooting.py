# Troubleshooting Common Issues

# Problem: "Memory usage growing"
from memory_profiler import profile
import gc

@profile
async def diagnose_memory():
    # Your code here
    pass

# Check for circular references
def check_circular_references():
    gc.collect()
    print(f"Uncollectable objects: {gc.garbage}")

# Problem: "Event not received"
class EventBus:
    @staticmethod
    def enable_tracing():
        # Enable event tracing
        pass
    
    @staticmethod
    def get_subscribers(event_name: str):
        # Check event subscriptions
        return []
    
    @staticmethod
    async def publish(event_name: str, data: dict):
        # Test event manually
        pass

async def debug_events():
    # Enable event tracing
    EventBus.enable_tracing()
    
    # Check event subscriptions
    subscribers = EventBus.get_subscribers("agent.task.completed")
    print(f"Subscribers: {subscribers}")
    
    # Test event manually
    await EventBus.publish("test.event", {"data": "test"})