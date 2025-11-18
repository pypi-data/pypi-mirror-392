#!/usr/bin/env python3
"""Comprehensive test runner for mcrentcast MCP server.

This script provides various testing scenarios and configurations to thoroughly
test the mcrentcast MCP server functionality.
"""

import asyncio
import os
import subprocess
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n🧪 {description}")
    print(f"   Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        print(f"   ✅ Success ({result.returncode})")
        if result.stdout:
            # Show just the summary line
            lines = result.stdout.strip().split('\n')
            for line in lines[-10:]:
                if 'passed' in line or 'failed' in line or 'error' in line:
                    print(f"   📊 {line}")
                    break
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Failed ({e.returncode})")
        if e.stdout:
            print(f"   📝 Output: {e.stdout[-200:]}...")  # Last 200 chars
        if e.stderr:
            print(f"   🚨 Error: {e.stderr[-200:]}...")   # Last 200 chars
        return False


def main():
    """Run comprehensive test suite."""
    print("🏠 MCRentCast MCP Server - Comprehensive Test Suite")
    print("=" * 60)
    
    # Set environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    
    base_cmd = ["uv", "run", "pytest"]
    test_file = "tests/test_mcp_server.py"
    
    test_scenarios = [
        # Smoke tests - basic functionality
        {
            "cmd": base_cmd + [f"{test_file}::TestSmokeTests", "-v", "--tb=short"],
            "description": "Running smoke tests (basic functionality)",
        },
        
        # API key management tests
        {
            "cmd": base_cmd + [f"{test_file}::TestApiKeyManagement", "-v", "--tb=short"],
            "description": "Testing API key management",
        },
        
        # Property search tests (mocked)
        {
            "cmd": base_cmd + [f"{test_file}::TestPropertySearch::test_search_properties_no_api_key", "-v"],
            "description": "Testing property search error handling",
        },
        
        # Cache management tests
        {
            "cmd": base_cmd + [f"{test_file}::TestCacheManagement", "-v", "--tb=short"],
            "description": "Testing cache management functionality",
        },
        
        # Usage and limits tests
        {
            "cmd": base_cmd + [f"{test_file}::TestUsageAndLimits", "-v", "--tb=short"],
            "description": "Testing API usage and limits management",
        },
        
        # Error handling tests
        {
            "cmd": base_cmd + [f"{test_file}::TestErrorHandling", "-v", "--tb=short"],
            "description": "Testing comprehensive error handling",
        },
        
        # Run all tests with coverage
        {
            "cmd": base_cmd + [test_file, "--cov=src", "--cov-report=html", "--tb=short", "-q"],
            "description": "Full test suite with coverage report",
        },
        
        # Generate final HTML report
        {
            "cmd": base_cmd + [test_file, "--html=reports/comprehensive_test_report.html", "--self-contained-html", "-q"],
            "description": "Generating comprehensive HTML test report",
        }
    ]
    
    # Track results
    passed = 0
    failed = 0
    
    print("\n📋 Test Execution Plan:")
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"   {i}. {scenario['description']}")
    
    print("\n🚀 Starting test execution...")
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*60}")
        print(f"Step {i}/{len(test_scenarios)}")
        
        # Update environment for this command
        scenario_env = env.copy()
        
        success = run_command(scenario["cmd"], scenario["description"])
        
        if success:
            passed += 1
        else:
            failed += 1
            # For critical tests, we might want to stop
            if "smoke" in scenario["description"].lower():
                print("   🛑 Smoke tests failed - stopping execution")
                break
    
    # Final summary
    print(f"\n{'='*60}")
    print("🏁 TEST EXECUTION SUMMARY")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📊 Total:  {passed + failed}")
    
    if failed == 0:
        print("   🎉 All test scenarios completed successfully!")
        print("   📁 Check reports/ directory for detailed results")
    else:
        print("   ⚠️  Some test scenarios failed - review output above")
    
    # Show useful commands
    print(f"\n📚 USEFUL COMMANDS:")
    print(f"   # Run specific test categories:")
    print(f"   PYTHONPATH=src uv run pytest {test_file} -m smoke -v")
    print(f"   PYTHONPATH=src uv run pytest {test_file} -m unit -v") 
    print(f"   PYTHONPATH=src uv run pytest {test_file} -m integration -v")
    print(f"   PYTHONPATH=src uv run pytest {test_file} -m performance -v")
    print(f"   ")
    print(f"   # Run with different output formats:")
    print(f"   PYTHONPATH=src uv run pytest {test_file} --tb=line")
    print(f"   PYTHONPATH=src uv run pytest {test_file} --tb=no -q")
    print(f"   PYTHONPATH=src uv run pytest {test_file} --collect-only")
    print(f"   ")
    print(f"   # Generate reports:")
    print(f"   PYTHONPATH=src uv run pytest {test_file} --html=reports/test_results.html --self-contained-html")
    print(f"   PYTHONPATH=src uv run pytest {test_file} --cov=src --cov-report=html --cov-report=term")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())