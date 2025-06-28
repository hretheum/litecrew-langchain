# validate_database_schema.py
import sqlite3
import json
import time
from datetime import datetime, timedelta
import uuid

def test_schema_creation():
    """Test database schema creation"""
    conn = sqlite3.connect(":memory:")
    
    # Load schema
    with open("/opt/litecrewai/schema/schema.sql", "r") as f:
        schema_sql = f.read()
    
    # Execute schema
    conn.executescript(schema_sql)
    
    # Check tables exist
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    
    required_tables = {
        'agents', 'tasks', 'executions', 'memories',
        'tools', 'conversations', 'costs', 'errors'
    }
    
    missing = required_tables - tables
    assert not missing, f"Missing tables: {missing}"
    
    print(f"✅ All {len(required_tables)} tables created")
    
    # Check indexes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indexes = [row[0] for row in cursor.fetchall()]
    
    assert len(indexes) >= 10, f"Too few indexes: {len(indexes)}"
    print(f"✅ {len(indexes)} indexes created")
    
    conn.close()

def test_data_integrity():
    """Test constraints and triggers"""
    conn = sqlite3.connect(":memory:")
    
    # Create schema
    with open("/opt/litecrewai/schema/schema.sql", "r") as f:
        conn.executescript(f.read())
    
    cursor = conn.cursor()
    
    # Test unique constraint
    cursor.execute(
        "INSERT INTO agents (name, role) VALUES (?, ?)",
        ("test_agent", "assistant")
    )
    
    try:
        cursor.execute(
            "INSERT INTO agents (name, role) VALUES (?, ?)",
            ("test_agent", "researcher")
        )
        assert False, "Unique constraint not working"
    except sqlite3.IntegrityError:
        print("✅ Unique constraints working")
    
    # Test JSON validation
    try:
        cursor.execute(
            "INSERT INTO agents (name, role, config) VALUES (?, ?, ?)",
            ("agent2", "assistant", "invalid json")
        )
        assert False, "JSON validation not working"
    except sqlite3.IntegrityError:
        print("✅ JSON validation working")
    
    # Test trigger
    cursor.execute("SELECT updated_at FROM agents WHERE name='test_agent'")
    original_time = cursor.fetchone()[0]
    
    time.sleep(0.1)
    cursor.execute(
        "UPDATE agents SET role='researcher' WHERE name='test_agent'"
    )
    
    cursor.execute("SELECT updated_at FROM agents WHERE name='test_agent'")
    new_time = cursor.fetchone()[0]
    
    assert new_time > original_time, "Update trigger not working"
    print("✅ Triggers working")
    
    conn.close()

def test_query_performance():
    """Test query performance with data"""
    conn = sqlite3.connect(":memory:")
    
    # Create schema
    with open("/opt/litecrewai/schema/schema.sql", "r") as f:
        conn.executescript(f.read())
    
    cursor = conn.cursor()
    
    # Insert test data
    print("Inserting test data...")
    
    # Insert agents
    for i in range(100):
        cursor.execute(
            "INSERT INTO agents (name, role, config) VALUES (?, ?, ?)",
            (f"agent_{i}", "assistant", json.dumps({"model": "gpt-3.5"}))
        )
    
    # Insert tasks
    for i in range(10000):
        cursor.execute(
            "INSERT INTO tasks (description, agent_id, status) VALUES (?, ?, ?)",
            (f"Task {i}", f"agent_{i % 100}", "completed" if i % 3 == 0 else "pending")
        )
    
    # Insert executions
    for i in range(5000):
        cursor.execute(
            """INSERT INTO executions 
               (task_id, started_at, completed_at, cost, tokens)
               VALUES (?, ?, ?, ?, ?)""",
            (i + 1, datetime.now(), datetime.now(), 0.001 * i, 100 * i)
        )
    
    conn.commit()
    
    # Test queries
    queries = [
        ("Simple select", "SELECT * FROM agents WHERE name = 'agent_50'"),
        ("Join query", """
            SELECT a.name, COUNT(t.id) as task_count
            FROM agents a
            LEFT JOIN tasks t ON a.id = t.agent_id
            GROUP BY a.id
            LIMIT 10
        """),
        ("Analytics query", """
            SELECT 
                DATE(started_at) as date,
                COUNT(*) as executions,
                SUM(cost) as total_cost,
                AVG(tokens) as avg_tokens
            FROM executions
            GROUP BY DATE(started_at)
        """),
        ("Complex filter", """
            SELECT t.*, a.name as agent_name
            FROM tasks t
            JOIN agents a ON t.agent_id = a.id
            WHERE t.status = 'completed'
            AND t.created_at > datetime('now', '-7 days')
            ORDER BY t.created_at DESC
            LIMIT 50
        """)
    ]
    
    for name, query in queries:
        start = time.time()
        cursor.execute(query)
        results = cursor.fetchall()
        elapsed = (time.time() - start) * 1000
        
        print(f"✅ {name}: {elapsed:.1f}ms ({len(results)} rows)")
        assert elapsed < 50, f"{name} too slow: {elapsed}ms"
    
    conn.close()

def test_json_operations():
    """Test JSON column operations"""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Create schema
    with open("/opt/litecrewai/schema/schema.sql", "r") as f:
        conn.executescript(f.read())
    
    cursor = conn.cursor()
    
    # Insert with JSON
    config = {
        "model": "gpt-4",
        "temperature": 0.7,
        "tools": ["web_search", "calculator"],
        "memory": {"type": "long_term", "size": 1000}
    }
    
    cursor.execute(
        "INSERT INTO agents (name, role, config) VALUES (?, ?, ?)",
        ("json_agent", "researcher", json.dumps(config))
    )
    
    # Query JSON fields
    cursor.execute("""
        SELECT json_extract(config, '$.model') as model,
               json_extract(config, '$.temperature') as temp,
               json_extract(config, '$.tools[0]') as first_tool
        FROM agents 
        WHERE name = 'json_agent'
    """)
    
    row = cursor.fetchone()
    assert row[0] == "gpt-4"
    assert row[1] == 0.7
    assert row[2] == "web_search"
    
    print("✅ JSON operations working")
    
    # Update JSON field
    cursor.execute("""
        UPDATE agents 
        SET config = json_set(config, '$.temperature', 0.9)
        WHERE name = 'json_agent'
    """)
    
    cursor.execute("""
        SELECT json_extract(config, '$.temperature') 
        FROM agents 
        WHERE name = 'json_agent'
    """)
    
    assert cursor.fetchone()[0] == 0.9
    print("✅ JSON updates working")
    
    conn.close()

def test_full_text_search():
    """Test full-text search capabilities"""
    conn = sqlite3.connect(":memory:")
    
    # Create schema with FTS
    with open("/opt/litecrewai/schema/schema.sql", "r") as f:
        conn.executescript(f.read())
    
    # Create FTS table for task search
    conn.execute("""
        CREATE VIRTUAL TABLE tasks_fts USING fts5(
            task_id, description, content=tasks
        );
    """)
    
    cursor = conn.cursor()
    
    # Insert test data
    tasks = [
        "Research quantum computing applications",
        "Write article about machine learning",
        "Analyze quantum physics research papers",
        "Create presentation on AI ethics",
        "Study quantum mechanics fundamentals"
    ]
    
    for i, task in enumerate(tasks):
        cursor.execute(
            "INSERT INTO tasks (id, description, agent_id) VALUES (?, ?, ?)",
            (i + 1, task, "agent_1")
        )
        cursor.execute(
            "INSERT INTO tasks_fts (task_id, description) VALUES (?, ?)",
            (i + 1, task)
        )
    
    # Test FTS queries
    cursor.execute("""
        SELECT task_id, description, rank
        FROM tasks_fts
        WHERE tasks_fts MATCH 'quantum'
        ORDER BY rank
    """)
    
    results = cursor.fetchall()
    assert len(results) == 3
    assert all("quantum" in r[1].lower() for r in results)
    
    print(f"✅ Full-text search working ({len(results)} results)")
    
    conn.close()

def test_migration_system():
    """Test database migration system"""
    import os
    
    migrations_dir = "/opt/litecrewai/schema/migrations"
    
    # Check migration files exist
    assert os.path.exists(migrations_dir)
    
    migrations = sorted([
        f for f in os.listdir(migrations_dir) 
        if f.endswith('.sql')
    ])
    
    assert len(migrations) > 0
    print(f"✅ Found {len(migrations)} migration files")
    
    # Test migration application
    conn = sqlite3.connect(":memory:")
    
    # Create migrations table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Apply migrations
    for migration in migrations:
        with open(os.path.join(migrations_dir, migration), 'r') as f:
            sql = f.read()
        
        try:
            conn.executescript(sql)
            conn.execute(
                "INSERT INTO schema_migrations (version) VALUES (?)",
                (migration,)
            )
            print(f"✅ Applied migration: {migration}")
        except Exception as e:
            print(f"❌ Failed migration {migration}: {e}")
    
    conn.close()

def test_archival_system():
    """Test data archival functionality"""
    conn = sqlite3.connect(":memory:")
    
    # Create schema
    with open("/opt/litecrewai/schema/schema.sql", "r") as f:
        conn.executescript(f.read())
    
    cursor = conn.cursor()
    
    # Insert old data
    old_date = datetime.now() - timedelta(days=100)
    
    for i in range(100):
        cursor.execute(
            """INSERT INTO tasks 
               (description, agent_id, status, created_at)
               VALUES (?, ?, ?, ?)""",
            (f"Old task {i}", "agent_1", "completed", old_date)
        )
    
    # Insert recent data
    for i in range(50):
        cursor.execute(
            """INSERT INTO tasks 
               (description, agent_id, status)
               VALUES (?, ?, ?)""",
            (f"Recent task {i}", "agent_1", "pending")
        )
    
    # Test archival query
    cursor.execute("""
        SELECT COUNT(*) 
        FROM tasks 
        WHERE created_at < datetime('now', '-90 days')
    """)
    
    old_count = cursor.fetchone()[0]
    assert old_count == 100
    
    print(f"✅ Found {old_count} tasks ready for archival")
    
    conn.close()

if __name__ == "__main__":
    print("🔍 Validating database schema...\n")
    
    test_schema_creation()
    test_data_integrity()
    test_query_performance()
    test_json_operations()
    test_full_text_search()
    test_migration_system()
    test_archival_system()
    
    print("\n✅ Database schema validation complete!")