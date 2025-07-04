"""
Verify Phase 4 Block 2 metrics according to IMPLEMENTATION_ROADMAP.md
"""

import time
import tempfile
from pathlib import Path
from litecrew.state import StateManager, CrewState
from litecrew import LiteAgent, LiteTask, LiteCrew


def test_block_4_2_metrics():
    """Test Block 4.2: State Management metrics."""
    print("\n=== Block 4.2: State Management ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = StateManager(storage_path=Path(temp_dir))
        
        # Metric 1: Snapshot time < 100ms
        print("\n1. Testing snapshot time...")
        
        # Create a realistic crew state
        state = CrewState(
            crew_id="test_crew",
            agents=[
                {"role": f"agent_{i}", "goal": f"goal_{i}", "backstory": f"story_{i}"}
                for i in range(5)
            ],
            tasks=[
                {"description": f"task_{i}", "expected_output": f"output_{i}"}
                for i in range(10)
            ],
            process="sequential",
            context={"data": "x" * 1000},  # Some context data
            metadata={"run_id": "test_run", "config": {"verbose": True}}
        )
        
        # Update some task states
        for i in range(10):
            state.update_task_status(i, "completed")
            state.update_task_output(i, f"Result for task {i} with some data")
        
        # Measure snapshot time
        snapshot_times = []
        for i in range(10):
            start = time.perf_counter()
            snapshot_id = manager.save_state(state)
            duration = (time.perf_counter() - start) * 1000
            snapshot_times.append(duration)
        
        avg_snapshot_time = sum(snapshot_times) / len(snapshot_times)
        print(f"   Average snapshot time: {avg_snapshot_time:.2f}ms")
        print(f"   ✅ PASS: {avg_snapshot_time:.2f}ms < 100ms" if avg_snapshot_time < 100 else f"   ❌ FAIL: {avg_snapshot_time:.2f}ms >= 100ms")
        
        # Metric 2: Restore time < 200ms
        print("\n2. Testing restore time...")
        
        restore_times = []
        for i in range(10):
            start = time.perf_counter()
            restored_state = manager.load_state("test_crew")
            duration = (time.perf_counter() - start) * 1000
            restore_times.append(duration)
        
        avg_restore_time = sum(restore_times) / len(restore_times)
        print(f"   Average restore time: {avg_restore_time:.2f}ms")
        print(f"   ✅ PASS: {avg_restore_time:.2f}ms < 200ms" if avg_restore_time < 200 else f"   ❌ FAIL: {avg_restore_time:.2f}ms >= 200ms")
        
        # Metric 3: State size < 1MB per crew
        print("\n3. Testing state size...")
        
        state_size = manager.get_state_size("test_crew")
        state_size_mb = state_size / (1024 * 1024)
        
        print(f"   State size: {state_size_mb:.2f}MB")
        print(f"   ✅ PASS: {state_size_mb:.2f}MB < 1MB" if state_size_mb < 1 else f"   ❌ FAIL: {state_size_mb:.2f}MB >= 1MB")
        
        # Test incremental updates
        print("\n4. Testing incremental updates...")
        
        # Make small change
        state.update_task_status(0, "in_progress")
        
        start = time.perf_counter()
        update_id = manager.save_incremental_update(state, changed_fields=["task_states"])
        incremental_time = (time.perf_counter() - start) * 1000
        
        print(f"   Incremental update time: {incremental_time:.2f}ms")
        print(f"   ✅ PASS: Incremental updates working" if incremental_time < 10 else f"   ⚠️  Incremental updates might be slow")
        
        # Test state migration
        print("\n5. Testing state migration...")
        
        # Create old format state
        old_state_data = {
            "crew_id": "migrate_crew",
            "agents": ["researcher", "writer"],  # Old format
            "tasks": ["research", "write"],      # Old format
            "process": "sequential"
        }
        
        # Apply migration
        start = time.perf_counter()
        migrated = manager.migrate_state(old_state_data, "1.0", "2.0")
        migration_time = (time.perf_counter() - start) * 1000
        
        print(f"   Migration time: {migration_time:.2f}ms")
        print(f"   Migrated agents: {migrated['agents']}")
        print(f"   ✅ PASS: Migration working" if isinstance(migrated["agents"][0], dict) else f"   ❌ FAIL: Migration failed")
        
        # Test state validation
        print("\n6. Testing state validation...")
        
        try:
            # Valid state
            valid_state = CrewState(
                crew_id="valid",
                agents=[{"role": "test"}],
                tasks=[{"description": "test"}],
                process="sequential"
            )
            valid_state.validate()
            print("   ✅ PASS: Valid state accepted")
            
            # Invalid state
            invalid_state = CrewState(
                crew_id="",
                agents=[],
                tasks=[],
                process="sequential"
            )
            try:
                invalid_state.validate()
                print("   ❌ FAIL: Invalid state not rejected")
            except:
                print("   ✅ PASS: Invalid state rejected")
                
        except Exception as e:
            print(f"   ❌ FAIL: Validation error: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 4 BLOCK 2 METRICS VERIFICATION")
    print("=" * 60)
    
    test_block_4_2_metrics()
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)