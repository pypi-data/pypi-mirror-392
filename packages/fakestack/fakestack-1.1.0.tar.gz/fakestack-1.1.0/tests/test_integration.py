"""Integration tests for fakestack Go wrapper."""

import os
import tempfile
from pathlib import Path

import pytest


def test_import_fakestack():
    """Test that fakestack can be imported."""
    import fakestack
    
    assert hasattr(fakestack, '__version__')
    assert hasattr(fakestack, 'main')
    assert hasattr(fakestack, 'run_fakestack')
    # Check version exists and is not empty
    assert fakestack.__version__
    assert isinstance(fakestack.__version__, str)


def test_run_fakestack_help():
    """Test running fakestack with no arguments shows help."""
    from fakestack import run_fakestack
    
    # Should show error and usage
    exit_code = run_fakestack([])
    assert exit_code != 0


def test_download_schema():
    """Test downloading example schema."""
    from fakestack import run_fakestack
    
    import json
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        schema_path = tmpdir_path / 'schema.json'
        
        # Run in subprocess-like manner to avoid file locking issues
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            exit_code = run_fakestack(['-d', '.'])
            
            assert exit_code == 0
            assert schema_path.exists()
            
            # Verify schema is valid JSON
            with open(schema_path) as f:
                schema = json.load(f)
            
            assert 'database' in schema
            assert 'tables' in schema
            assert 'populate' in schema
        finally:
            os.chdir(original_dir)


def test_create_and_populate():
    """Test creating tables and populating data."""
    from fakestack import run_fakestack
    import time
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        db_path = tmpdir_path / 'test.db'
        
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            
            # Download schema
            exit_code = run_fakestack(['-d', '.'])
            assert exit_code == 0
            
            # Create tables and populate
            exit_code = run_fakestack(['-c', '-p', '-f', 'schema.json'])
            assert exit_code == 0
            
            # Small delay to ensure file writes are complete on Windows
            time.sleep(0.1)
            
            # Verify database exists
            assert db_path.exists()
            assert db_path.stat().st_size > 0
        finally:
            os.chdir(original_dir)
            # Give Windows time to release file handles
            time.sleep(0.2)


def test_binary_detection():
    """Test that binary path detection works."""
    from fakestack.runner import get_binary_path
    
    binary_path = get_binary_path()
    
    assert binary_path.exists()
    assert binary_path.is_file()
    assert 'fakestack-' in binary_path.name


def test_version_consistency():
    """Test that version is consistent across package."""
    import fakestack
    
    # Check version exists and is valid semantic version
    assert fakestack.__version__
    parts = fakestack.__version__.split('.')
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)
    
    # Verify it matches package metadata
    import importlib.metadata
    try:
        pkg_version = importlib.metadata.version('fakestack')
        assert fakestack.__version__ == pkg_version, f"Version mismatch: __version__={fakestack.__version__}, metadata={pkg_version}"
    except importlib.metadata.PackageNotFoundError:
        # Package not installed yet (e.g., during development)
        pass


def test_cli_via_python_module():
    """Test running fakestack via python -m in same process."""
    from fakestack import run_fakestack
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            
            # Run via the imported function (simulates -m usage)
            exit_code = run_fakestack(['-d', '.'])
            
            assert exit_code == 0
            assert (tmpdir_path / 'schema.json').exists()
        finally:
            os.chdir(original_dir)


def test_multiple_runs():
    """Test that multiple runs work correctly."""
    from fakestack import run_fakestack
    
    with tempfile.TemporaryDirectory() as tmpdir:
        original_dir = os.getcwd()
        try:
            os.chdir(tmpdir)
            
            # First run
            exit_code = run_fakestack(['-d', '.'])
            assert exit_code == 0
            
            # Second run (should succeed or show already exists)
            exit_code = run_fakestack(['-d', '.'])
            # Either succeeds or file exists
            assert exit_code in [0, 1]
        finally:
            os.chdir(original_dir)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
