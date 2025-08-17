#!/usr/bin/env python3
"""
Test script to validate GitHub Repository Management Tool setup
"""

import sys
import importlib
import json

def test_imports():
    """Test that all required imports work"""
    print("Testing imports...")
    
    try:
        import requests
        print("✓ requests")
    except ImportError:
        print("❌ requests - Run: pip install requests")
        return False
    
    try:
        from nacl import encoding, public
        print("✓ PyNaCl")
    except ImportError:
        print("❌ PyNaCl - Run: pip install PyNaCl")
        return False
    
    try:
        from main import GitHubRepoManager, RepoConfig
        print("✓ main module")
    except ImportError as e:
        print(f"❌ main module - {e}")
        return False
    
    return True

def test_config_template():
    """Test that config template is valid JSON"""
    print("\nTesting configuration template...")
    
    try:
        with open('config_template.json', 'r') as f:
            json.load(f)
        print("✓ config_template.json is valid JSON")
        return True
    except FileNotFoundError:
        print("❌ config_template.json not found - Run: python main.py create-template")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ config_template.json invalid JSON - {e}")
        return False

def test_config_loading():
    """Test configuration loading functionality"""
    print("\nTesting configuration loading...")
    
    try:
        from main import load_config_from_file
        config = load_config_from_file('config_template.json')
        print("✓ Configuration loading works")
        
        # Test that all required fields are present
        required_fields = ['name', 'owner', 'description']
        for field in required_fields:
            if hasattr(config, field):
                print(f"✓ Config has {field}")
            else:
                print(f"❌ Config missing {field}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Configuration loading failed - {e}")
        return False

def test_repo_config():
    """Test RepoConfig class"""
    print("\nTesting RepoConfig class...")
    
    try:
        from main import RepoConfig
        
        config = RepoConfig(
            name="test-repo",
            owner="test-owner",
            description="Test repository"
        )
        
        print("✓ RepoConfig can be instantiated")
        
        # Test that default values work
        if config.private == True:
            print("✓ Default private setting")
        else:
            print("❌ Default private setting incorrect")
            return False
        
        return True
    except Exception as e:
        print(f"❌ RepoConfig test failed - {e}")
        return False

def test_github_manager():
    """Test GitHubRepoManager class instantiation"""
    print("\nTesting GitHubRepoManager class...")
    
    try:
        from main import GitHubRepoManager
        
        # Test with dummy token (won't make actual API calls)
        manager = GitHubRepoManager("dummy-token")
        print("✓ GitHubRepoManager can be instantiated")
        
        # Test that required methods exist
        required_methods = [
            'create_repository',
            '_create_base_repository',
            '_add_custom_properties',
            '_create_readme',
            '_create_gitignore',
            '_setup_branch_protection'
        ]
        
        for method in required_methods:
            if hasattr(manager, method):
                print(f"✓ Method {method} exists")
            else:
                print(f"❌ Method {method} missing")
                return False
        
        return True
    except Exception as e:
        print(f"❌ GitHubRepoManager test failed - {e}")
        return False

def test_command_line_tools():
    """Test that command line tools can be imported"""
    print("\nTesting command line tools...")
    
    try:
        import create_repo
        print("✓ create_repo.py imports successfully")
    except ImportError as e:
        print(f"❌ create_repo.py import failed - {e}")
        return False
    
    try:
        import examples
        print("✓ examples.py imports successfully")
    except ImportError as e:
        print(f"❌ examples.py import failed - {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("GitHub Repository Management Tool - Setup Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config_template,
        test_config_loading,
        test_repo_config,
        test_github_manager,
        test_command_line_tools
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print()
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready to use.")
        print("\nNext steps:")
        print("1. Get a GitHub token with 'repo' and 'admin:org' permissions")
        print("2. Run: python main.py")
        print("3. Or customize config_template.json and run with configuration file")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
