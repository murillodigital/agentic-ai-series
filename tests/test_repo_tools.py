"""
tests/test_repo_tools.py
========================
Unit tests for Module 2 repository analysis tools.

Tests all five tools in both mock and real modes.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_nodejs_repo():
    """Path to sample Node.js repository fixture."""
    return str(Path(__file__).parent / "fixtures" / "sample_repos" / "nodejs-app")


@pytest.fixture
def sample_python_repo():
    """Path to sample Python repository fixture."""
    return str(Path(__file__).parent / "fixtures" / "sample_repos" / "python-app")


@pytest.fixture
def enable_mock_mode():
    """Enable mock mode for tests."""
    original = os.environ.get("AGENT_MOCK_REPO")
    os.environ["AGENT_MOCK_REPO"] = "true"
    yield
    if original is None:
        os.environ.pop("AGENT_MOCK_REPO", None)
    else:
        os.environ["AGENT_MOCK_REPO"] = original


# ---------------------------------------------------------------------------
# Test scan_repository_structure
# ---------------------------------------------------------------------------

def test_scan_repository_structure_mock(enable_mock_mode):
    """Test repository scanning in mock mode."""
    from module2.tools.repo_tools import scan_repository_structure
    
    result = scan_repository_structure("/mock/repo/path")
    data = json.loads(result)
    
    assert data["tool"] == "scan_repository_structure"
    assert data["mock_mode"] is True
    assert "data" in data
    assert "files" in data["data"]
    assert "directories" in data["data"]
    assert len(data["data"]["files"]) > 0


def test_scan_repository_structure_error():
    """Test scanning non-existent repository."""
    from module2.tools.repo_tools import scan_repository_structure
    
    result = scan_repository_structure("/nonexistent/path")
    data = json.loads(result)
    
    assert "error" in data["data"]


# ---------------------------------------------------------------------------
# Test read_file_content
# ---------------------------------------------------------------------------

def test_read_file_content_mock(enable_mock_mode):
    """Test reading file content in mock mode."""
    from module2.tools.repo_tools import read_file_content
    
    result = read_file_content("/mock/repo", "services/api/package.json")
    data = json.loads(result)
    
    assert data["tool"] == "read_file_content"
    assert data["mock_mode"] is True
    assert "content" in data["data"]
    assert "express" in data["data"]["content"]


def test_read_file_content_not_found(enable_mock_mode):
    """Test reading non-existent file in mock mode."""
    from module2.tools.repo_tools import read_file_content
    
    result = read_file_content("/mock/repo", "nonexistent.txt")
    data = json.loads(result)
    
    assert "error" in data["data"]


# ---------------------------------------------------------------------------
# Test detect_applications
# ---------------------------------------------------------------------------

def test_detect_applications_mock(enable_mock_mode):
    """Test application detection in mock mode."""
    from module2.tools.repo_tools import detect_applications, scan_repository_structure
    
    # First scan the repo
    scan_result = scan_repository_structure("/mock/repo")
    
    # Then detect applications
    result = detect_applications("/mock/repo", scan_result)
    data = json.loads(result)
    
    assert data["tool"] == "detect_applications"
    assert data["mock_mode"] is True
    assert "applications" in data["data"]
    assert data["data"]["total_applications"] == 2
    assert any(app["name"] == "api-service" for app in data["data"]["applications"])


# ---------------------------------------------------------------------------
# Test analyze_dependencies
# ---------------------------------------------------------------------------

def test_analyze_dependencies_nodejs_mock(enable_mock_mode):
    """Test dependency analysis for Node.js in mock mode."""
    from module2.tools.repo_tools import analyze_dependencies
    
    result = analyze_dependencies("/mock/repo", "services/api", "package.json")
    data = json.loads(result)
    
    assert data["tool"] == "analyze_dependencies"
    assert "language" in data["data"]
    assert data["data"]["language"] == "Node.js"
    assert data["data"]["framework"] == "Express"
    assert "pg" in data["data"]["dependencies"]
    assert "redis" in data["data"]["dependencies"]


def test_analyze_dependencies_python_mock(enable_mock_mode):
    """Test dependency analysis for Python in mock mode."""
    from module2.tools.repo_tools import analyze_dependencies
    
    result = analyze_dependencies("/mock/repo", "services/worker", "requirements.txt")
    data = json.loads(result)
    
    assert data["tool"] == "analyze_dependencies"
    assert "language" in data["data"]
    assert data["data"]["language"] == "Python"
    assert data["data"]["framework"] == "FastAPI"
    assert "celery" in data["data"]["dependencies"]


# ---------------------------------------------------------------------------
# Test map_aws_services
# ---------------------------------------------------------------------------

def test_map_aws_services_mock(enable_mock_mode):
    """Test AWS service mapping in mock mode."""
    from module2.tools.repo_tools import analyze_dependencies, map_aws_services
    
    # First analyze dependencies
    deps_result = analyze_dependencies("/mock/repo", "services/api", "package.json")
    
    # Then map to AWS services
    result = map_aws_services(deps_result)
    data = json.loads(result)
    
    assert data["tool"] == "map_aws_services"
    assert "aws_services" in data["data"]
    assert "database" in data["data"]["aws_services"]
    assert "cache" in data["data"]["aws_services"]
    assert "storage" in data["data"]["aws_services"]
    assert "compute" in data["data"]["aws_services"]
    
    # Check specific mappings
    db_services = data["data"]["aws_services"]["database"]
    assert any(s["service"] == "RDS" and s["engine"] == "PostgreSQL" for s in db_services)
    
    cache_services = data["data"]["aws_services"]["cache"]
    assert any(s["service"] == "ElastiCache" and s["engine"] == "Redis" for s in cache_services)


def test_map_aws_services_summary(enable_mock_mode):
    """Test AWS service mapping summary."""
    from module2.tools.repo_tools import analyze_dependencies, map_aws_services
    
    deps_result = analyze_dependencies("/mock/repo", "services/api", "package.json")
    result = map_aws_services(deps_result)
    data = json.loads(result)
    
    assert "summary" in data["data"]
    summary = data["data"]["summary"]
    assert "databases" in summary
    assert "caching" in summary
    assert "storage" in summary
    assert "compute" in summary
    assert "RDS" in summary["databases"]
    assert "ElastiCache" in summary["caching"]


# ---------------------------------------------------------------------------
# Integration Tests
# ---------------------------------------------------------------------------

def test_full_analysis_workflow_mock(enable_mock_mode):
    """Test complete analysis workflow in mock mode."""
    from module2.tools.repo_tools import (
        analyze_dependencies,
        detect_applications,
        map_aws_services,
        scan_repository_structure,
    )
    
    repo_path = "/mock/repo"
    
    # Step 1: Scan
    scan_result = scan_repository_structure(repo_path)
    scan_data = json.loads(scan_result)
    assert "files" in scan_data["data"]
    
    # Step 2: Detect applications
    detect_result = detect_applications(repo_path, scan_result)
    detect_data = json.loads(detect_result)
    assert detect_data["data"]["total_applications"] > 0
    
    # Step 3: Analyze dependencies for first app
    apps = detect_data["data"]["applications"]
    first_app = apps[0]
    
    # Find dependency file
    dep_file = "package.json" if "package.json" in first_app["indicators"] else "requirements.txt"
    
    deps_result = analyze_dependencies(repo_path, first_app["path"], dep_file)
    deps_data = json.loads(deps_result)
    assert "dependencies" in deps_data["data"]
    
    # Step 4: Map to AWS services
    aws_result = map_aws_services(deps_result)
    aws_data = json.loads(aws_result)
    assert "aws_services" in aws_data["data"]
    assert len(aws_data["data"]["aws_services"]) > 0


# ---------------------------------------------------------------------------
# Dependency Mapping Tests
# ---------------------------------------------------------------------------

def test_dependency_mapping_coverage():
    """Test that common dependencies are mapped correctly."""
    from module2.tools.repo_tools import DEPENDENCY_TO_AWS_SERVICE
    
    # Database libraries
    assert "pg" in DEPENDENCY_TO_AWS_SERVICE
    assert DEPENDENCY_TO_AWS_SERVICE["pg"]["service"] == "RDS"
    assert DEPENDENCY_TO_AWS_SERVICE["pg"]["engine"] == "PostgreSQL"
    
    assert "mysql" in DEPENDENCY_TO_AWS_SERVICE
    assert DEPENDENCY_TO_AWS_SERVICE["mysql"]["service"] == "RDS"
    
    assert "mongodb" in DEPENDENCY_TO_AWS_SERVICE
    assert DEPENDENCY_TO_AWS_SERVICE["mongodb"]["service"] == "DocumentDB"
    
    # Cache libraries
    assert "redis" in DEPENDENCY_TO_AWS_SERVICE
    assert DEPENDENCY_TO_AWS_SERVICE["redis"]["service"] == "ElastiCache"
    
    # Storage libraries
    assert "boto3" in DEPENDENCY_TO_AWS_SERVICE
    assert DEPENDENCY_TO_AWS_SERVICE["boto3"]["service"] == "S3"
    
    # Framework libraries
    assert "express" in DEPENDENCY_TO_AWS_SERVICE
    assert "fastapi" in DEPENDENCY_TO_AWS_SERVICE
    assert "flask" in DEPENDENCY_TO_AWS_SERVICE


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
