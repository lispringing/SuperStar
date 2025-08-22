"""
Shared pytest fixtures and configuration for all tests.
"""
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, Generator
from unittest.mock import Mock, MagicMock

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """
    Create a temporary directory for test files.
    
    Yields:
        Path: Path to the temporary directory
    """
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup after test
    if temp_path.exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def temp_file(temp_dir: Path) -> Generator[Path, None, None]:
    """
    Create a temporary file for testing.
    
    Args:
        temp_dir: Temporary directory fixture
        
    Yields:
        Path: Path to the temporary file
    """
    temp_file_path = temp_dir / "test_file.txt"
    temp_file_path.write_text("test content")
    yield temp_file_path


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """
    Provide a mock configuration dictionary.
    
    Returns:
        Dict containing mock configuration values
    """
    return {
        "api": {
            "base_url": "https://api.example.com",
            "timeout": 30,
            "retry_count": 3
        },
        "database": {
            "host": "localhost",
            "port": 5432,
            "name": "test_db",
            "user": "test_user",
            "password": "test_password"
        },
        "logging": {
            "level": "DEBUG",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": "test.log"
        },
        "features": {
            "enable_cache": True,
            "cache_ttl": 3600,
            "max_connections": 100
        }
    }


@pytest.fixture
def mock_api_response() -> Dict[str, Any]:
    """
    Provide a mock API response.
    
    Returns:
        Dict containing mock API response data
    """
    return {
        "status": "success",
        "data": {
            "id": 123,
            "name": "Test Item",
            "description": "This is a test item",
            "metadata": {
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z",
                "version": "1.0.0"
            }
        },
        "message": "Request successful"
    }


@pytest.fixture
def mock_database_connection():
    """
    Provide a mock database connection.
    
    Returns:
        Mock object simulating a database connection
    """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    
    # Setup mock cursor behavior
    mock_cursor.fetchone.return_value = (1, "test_data")
    mock_cursor.fetchall.return_value = [(1, "data1"), (2, "data2")]
    mock_cursor.rowcount = 1
    
    # Setup mock connection behavior
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.commit.return_value = None
    mock_conn.rollback.return_value = None
    mock_conn.close.return_value = None
    
    return mock_conn


@pytest.fixture
def mock_http_client():
    """
    Provide a mock HTTP client for testing API calls.
    
    Returns:
        Mock object simulating an HTTP client
    """
    mock_client = MagicMock()
    
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ok", "data": []}
    mock_response.text = '{"status": "ok", "data": []}'
    mock_response.headers = {"Content-Type": "application/json"}
    
    # Setup mock client methods
    mock_client.get.return_value = mock_response
    mock_client.post.return_value = mock_response
    mock_client.put.return_value = mock_response
    mock_client.delete.return_value = mock_response
    mock_client.patch.return_value = mock_response
    
    return mock_client


@pytest.fixture
def sample_json_file(temp_dir: Path) -> Path:
    """
    Create a sample JSON file for testing.
    
    Args:
        temp_dir: Temporary directory fixture
        
    Returns:
        Path to the created JSON file
    """
    json_file = temp_dir / "sample.json"
    sample_data = {
        "users": [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"}
        ],
        "settings": {
            "theme": "dark",
            "notifications": True
        }
    }
    json_file.write_text(json.dumps(sample_data, indent=2))
    return json_file


@pytest.fixture
def mock_logger():
    """
    Provide a mock logger for testing logging functionality.
    
    Returns:
        Mock logger object
    """
    mock_log = MagicMock()
    mock_log.debug = MagicMock()
    mock_log.info = MagicMock()
    mock_log.warning = MagicMock()
    mock_log.error = MagicMock()
    mock_log.critical = MagicMock()
    mock_log.exception = MagicMock()
    return mock_log


@pytest.fixture
def environment_variables():
    """
    Set up and tear down environment variables for testing.
    
    Yields:
        Dict of test environment variables
    """
    original_env = os.environ.copy()
    
    test_env = {
        "TEST_ENV": "testing",
        "API_KEY": "test_api_key_123",
        "SECRET_TOKEN": "test_secret_token",
        "DEBUG": "true",
        "LOG_LEVEL": "DEBUG"
    }
    
    # Set test environment variables
    os.environ.update(test_env)
    
    yield test_env
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_celery_task():
    """
    Provide a mock Celery task for testing async operations.
    
    Returns:
        Mock Celery task object
    """
    mock_task = MagicMock()
    mock_task.delay.return_value = MagicMock(id="task-123", state="PENDING")
    mock_task.apply_async.return_value = MagicMock(id="task-456", state="PENDING")
    mock_task.apply.return_value = MagicMock(result="Task completed")
    return mock_task


@pytest.fixture
def mock_flask_app():
    """
    Provide a mock Flask application for testing.
    
    Returns:
        Mock Flask app object
    """
    mock_app = MagicMock()
    mock_app.config = {
        "TESTING": True,
        "DEBUG": True,
        "SECRET_KEY": "test_secret_key"
    }
    mock_app.test_client.return_value = MagicMock()
    return mock_app


@pytest.fixture(autouse=True)
def reset_singleton_instances():
    """
    Reset singleton instances between tests to ensure test isolation.
    This fixture runs automatically before each test.
    """
    # This would be implemented based on actual singleton patterns in the codebase
    yield
    # Cleanup code would go here if needed


@pytest.fixture
def capture_logs(caplog):
    """
    Fixture to capture log messages during tests.
    
    Args:
        caplog: pytest's built-in log capture fixture
        
    Returns:
        The caplog fixture configured for testing
    """
    caplog.set_level("DEBUG")
    return caplog


# Markers for test categorization
def pytest_configure(config):
    """
    Register custom markers for test categorization.
    """
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "network: mark test as requiring network access"
    )
    config.addinivalue_line(
        "markers", "database: mark test as requiring database access"
    )