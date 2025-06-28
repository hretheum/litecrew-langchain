# validate_core_tools.py
import os
import time
import tempfile
from litecrewai.tools.builtin import (
    web_search, calculator, file_system,
    database_query, http_request, datetime_tool
)

def test_web_search():
    """Test web search functionality"""
    # Mock search for testing
    results = web_search("Python programming", max_results=3)
    
    assert isinstance(results, list)
    assert len(results) <= 3
    
    if results:  # If not mocked
        result = results[0]
        assert "title" in result
        assert "url" in result
        assert "snippet" in result
    
    # Test rate limiting
    start = time.time()
    web_search("test1")
    web_search("test2")  # Should be delayed
    elapsed = time.time() - start
    assert elapsed >= 1.0, "Rate limiting not working"
    
    print("✅ Web search validated")

def test_calculator():
    """Test calculator functionality"""
    # Basic operations
    assert calculator("2 + 2") == 4
    assert calculator("10 * 5") == 50
    assert calculator("100 / 4") == 25
    assert calculator("2 ** 8") == 256
    
    # Scientific functions
    assert abs(calculator("sin(pi/2)") - 1.0) < 0.0001
    assert calculator("sqrt(16)") == 4
    assert calculator("log(e)") == 1
    
    # Safety test
    try:
        calculator("__import__('os').system('ls')")
        assert False, "Security breach!"
    except (ValueError, NameError):
        print("✅ Calculator security working")
    
    print("✅ Calculator validated")

def test_file_system():
    """Test file system operations"""
    # Create temp directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test write
        test_file = os.path.join(tmpdir, "test.txt")
        file_system.write(test_file, "Hello, World!")
        
        # Test read
        content = file_system.read(test_file)
        assert content == "Hello, World!"
        
        # Test list
        file_system.write(os.path.join(tmpdir, "test2.txt"), "Another file")
        files = file_system.list(tmpdir)
        assert len(files) == 2
        
        # Test search
        results = file_system.search(tmpdir, "*.txt")
        assert len(results) == 2
        
        # Test sandboxing
        try:
            file_system.read("/etc/passwd")
            assert False, "Sandbox breach!"
        except PermissionError:
            print("✅ File system sandboxing working")
    
    print("✅ File system validated")

def test_database():
    """Test database operations"""
    # Create test database
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        db_path = tmp.name
        
        # Create table
        database_query(
            "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)",
            db_path=db_path,
            read_only=False
        )
        
        # Insert data
        database_query(
            "INSERT INTO users (name) VALUES ('Alice'), ('Bob')",
            db_path=db_path,
            read_only=False
        )
        
        # Test query
        results = database_query(
            "SELECT * FROM users",
            db_path=db_path
        )
        assert len(results) == 2
        assert results[0]["name"] == "Alice"
        
        # Test read-only
        try:
            database_query(
                "DROP TABLE users",
                db_path=db_path,
                read_only=True
            )
            assert False, "Should be read-only"
        except PermissionError:
            print("✅ Database read-only working")
    
    print("✅ Database operations validated")

def test_http_request():
    """Test HTTP request functionality"""
    # Test GET (using httpbin for testing)
    response = http_request(
        "https://httpbin.org/get",
        method="GET",
        params={"test": "value"}
    )
    
    assert response["status_code"] == 200
    assert "args" in response["data"]
    assert response["data"]["args"]["test"] == "value"
    
    # Test POST
    response = http_request(
        "https://httpbin.org/post",
        method="POST",
        json={"key": "value"}
    )
    
    assert response["status_code"] == 200
    assert response["data"]["json"]["key"] == "value"
    
    # Test timeout
    try:
        http_request(
            "https://httpbin.org/delay/10",
            timeout=1
        )
        assert False, "Should timeout"
    except TimeoutError:
        print("✅ HTTP timeout working")
    
    print("✅ HTTP requests validated")

def test_datetime_tool():
    """Test datetime functionality"""
    # Current time
    now = datetime_tool("now")
    assert "datetime" in now
    assert "timezone" in now
    
    # Timezone conversion
    converted = datetime_tool(
        "convert",
        datetime="2024-01-01 12:00:00",
        from_tz="UTC",
        to_tz="America/New_York"
    )
    assert "07:00:00" in converted
    
    # Date arithmetic
    future = datetime_tool(
        "add",
        datetime="2024-01-01",
        days=30
    )
    assert "2024-01-31" in future
    
    # Parsing
    parsed = datetime_tool(
        "parse",
        date_string="January 1st, 2024"
    )
    assert "2024-01-01" in parsed
    
    print("✅ DateTime tool validated")

if __name__ == "__main__":
    print("🔍 Validating core tools...\n")
    
    test_web_search()
    test_calculator()
    test_file_system()
    test_database()
    test_http_request()
    test_datetime_tool()
    
    print("\n✅ All core tools validated!")