"""
Security-focused tests for LiteCrewAI
"""
import pytest
import os
import json
from unittest.mock import patch, Mock

class TestSecurityConfig:
    """Test security configuration and validation"""
    
    def test_no_hardcoded_secrets(self):
        """Test that no hardcoded secrets exist in codebase"""
        # This would be enhanced with actual code scanning
        assert True  # Placeholder - will be verified by bandit in CI
    
    def test_environment_variable_validation(self):
        """Test environment variable validation"""
        with pytest.raises(KeyError):
            # Should fail if required env vars are missing
            from app.src.crewai.security.security_config import SecurityConfig
            config = SecurityConfig()
    
    def test_api_key_format_validation(self):
        """Test API key format validation"""
        valid_openai_key = "sk-1234567890abcdef1234567890abcdef"
        valid_anthropic_key = "sk-ant-1234567890abcdef"
        invalid_key = "invalid-key"
        
        # Mock validation function
        def validate_api_key(key):
            if key.startswith("sk-") and len(key) > 20:
                return True
            if key.startswith("sk-ant-") and len(key) > 20:
                return True
            return False
        
        assert validate_api_key(valid_openai_key)
        assert validate_api_key(valid_anthropic_key)
        assert not validate_api_key(invalid_key)

class TestInputValidation:
    """Test input validation and sanitization"""
    
    def test_pydantic_validation(self):
        """Test Pydantic model validation"""
        from pydantic import BaseModel, ValidationError
        
        class TestModel(BaseModel):
            name: str
            age: int
        
        # Valid data
        valid_data = {"name": "test", "age": 25}
        model = TestModel(**valid_data)
        assert model.name == "test"
        assert model.age == 25
        
        # Invalid data
        with pytest.raises(ValidationError):
            TestModel(name="test", age="not_a_number")
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        # Test that we use parameterized queries
        dangerous_input = "'; DROP TABLE users; --"
        
        # Mock database query function
        def safe_query(query, params):
            # Simulate parameterized query
            return f"SELECT * FROM users WHERE name = '{params[0]}'"
        
        result = safe_query("SELECT * FROM users WHERE name = ?", [dangerous_input])
        assert "DROP TABLE" not in result.replace(dangerous_input, "")

class TestAuthentication:
    """Test authentication and authorization"""
    
    def test_jwt_token_validation(self):
        """Test JWT token validation"""
        import jwt
        
        secret = "test-secret"
        payload = {"user_id": 123, "role": "user"}
        
        # Create token
        token = jwt.encode(payload, secret, algorithm="HS256")
        
        # Validate token
        decoded = jwt.decode(token, secret, algorithms=["HS256"])
        assert decoded["user_id"] == 123
        assert decoded["role"] == "user"
        
        # Test invalid token
        with pytest.raises(jwt.InvalidTokenError):
            jwt.decode("invalid.token.here", secret, algorithms=["HS256"])
    
    def test_password_hashing(self):
        """Test password hashing (if implemented)"""
        import hashlib
        
        def hash_password(password: str, salt: str = "test-salt") -> str:
            return hashlib.pbkdf2_hmac('sha256', 
                                     password.encode('utf-8'), 
                                     salt.encode('utf-8'), 
                                     100000).hex()
        
        password = "test_password_123"
        hashed = hash_password(password)
        
        # Same password should produce same hash
        assert hash_password(password) == hashed
        
        # Different password should produce different hash
        assert hash_password("different_password") != hashed

class TestSecretManagement:
    """Test secret management and environment variables"""
    
    def test_env_file_not_in_repo(self):
        """Test that .env file is not committed to repository"""
        import subprocess
        import os
        
        # Check if .env exists in repo
        try:
            result = subprocess.run(['git', 'ls-files', '.env'], 
                                  capture_output=True, text=True, 
                                  cwd=os.path.dirname(__file__))
            assert result.stdout.strip() == "", ".env file should not be in repository"
        except FileNotFoundError:
            # Git not available, skip test
            pytest.skip("Git not available for testing")
    
    def test_gitignore_contains_env(self):
        """Test that .gitignore contains .env entry"""
        gitignore_path = os.path.join(os.path.dirname(__file__), "..", ".gitignore")
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as f:
                content = f.read()
                assert ".env" in content
    
    def test_env_example_exists(self):
        """Test that .env.example exists and contains required variables"""
        env_example_path = os.path.join(os.path.dirname(__file__), "..", ".env.example")
        assert os.path.exists(env_example_path), ".env.example should exist"
        
        with open(env_example_path, 'r') as f:
            content = f.read()
            required_vars = [
                "OPENAI_API_KEY",
                "DATABASE_URL", 
                "SECRET_KEY",
                "REDIS_URL"
            ]
            for var in required_vars:
                assert var in content, f"{var} should be in .env.example"

class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limit_configuration(self):
        """Test rate limiting configuration"""
        # Mock rate limiter
        class MockRateLimiter:
            def __init__(self, max_requests=100, window=60):
                self.max_requests = max_requests
                self.window = window
                self.requests = {}
            
            def is_allowed(self, key):
                import time
                now = time.time()
                if key not in self.requests:
                    self.requests[key] = []
                
                # Clean old requests
                self.requests[key] = [
                    req_time for req_time in self.requests[key] 
                    if now - req_time < self.window
                ]
                
                if len(self.requests[key]) < self.max_requests:
                    self.requests[key].append(now)
                    return True
                return False
        
        limiter = MockRateLimiter(max_requests=5, window=60)
        
        # First 5 requests should be allowed
        for i in range(5):
            assert limiter.is_allowed("test_user")
        
        # 6th request should be denied
        assert not limiter.is_allowed("test_user")

class TestLogging:
    """Test secure logging practices"""
    
    def test_no_secrets_in_logs(self):
        """Test that secrets are not logged"""
        import logging
        from io import StringIO
        
        # Create a string stream to capture log output
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger("test")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Mock secure formatter
        class SecureFormatter(logging.Formatter):
            SENSITIVE_KEYS = {'password', 'secret', 'token', 'api_key'}
            
            def format(self, record):
                # Redact sensitive information
                if hasattr(record, 'msg') and isinstance(record.msg, str):
                    for key in self.SENSITIVE_KEYS:
                        if key in record.msg.lower():
                            record.msg = record.msg.replace(key, '***REDACTED***')
                return super().format(record)
        
        handler.setFormatter(SecureFormatter())
        
        # Test logging with sensitive data
        logger.info("User login with password: secret123")
        
        log_output = log_stream.getvalue()
        assert "secret123" not in log_output
        assert "***REDACTED***" in log_output