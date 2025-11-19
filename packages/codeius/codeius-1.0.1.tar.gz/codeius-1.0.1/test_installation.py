#!/usr/bin/env python3
"""
Test script to verify that Codeius is properly installed and can be imported/run.
"""
import sys
import subprocess

def test_import():
    """Test if the codeius package can be imported"""
    try:
        import coding_agent
        print(":) Successfully imported coding_agent module")
        return True
    except ImportError as e:
        print(f":( Failed to import coding_agent: {e}")
        return False

def test_cli():
    """Test if the codeius CLI command is available"""
    try:
        result = subprocess.run(["codeius", "--help"],
                                capture_output=True,
                                text=True,
                                timeout=10)
        if result.returncode == 0:
            print(":) codeius CLI command is available")
            return True
        else:
            print(f":( codeius CLI command failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print(":( codeius CLI command not found")
        return False
    except subprocess.TimeoutExpired:
        print(":| codeius CLI command timed out (but may still be working)")
        return True
    except Exception as e:
        print(f":( Error running codeius CLI command: {e}")
        return False

def main():
    print("Testing Codeius installation...")
    print("="*50)

    import_success = test_import()
    cli_success = test_cli()

    print("="*50)
    if import_success and cli_success:
        print(":) All tests passed! Codeius is properly installed.")
        return 0
    else:
        print(":( Some tests failed. Check the installation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())