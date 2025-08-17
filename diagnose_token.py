#!/usr/bin/env python3
"""
GitHub Token and Organization Diagnostic Tool
This script helps diagnose token permissions and organization access issues.
"""

import requests
import json

def test_token_permissions(token):
    """Test GitHub token permissions and capabilities"""
    print("🔍 GitHub Token Diagnostic")
    print("=" * 50)
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    base_url = "https://api.github.com"
    
    # Test 1: Basic token validation
    print("\n1. Testing token validity...")
    response = requests.get(f"{base_url}/user", headers=headers)
    
    if response.status_code == 200:
        user_data = response.json()
        username = user_data.get('login', 'Unknown')
        print(f"✅ Token is valid for user: {username}")
        print(f"   Account type: {user_data.get('type', 'Unknown')}")
        print(f"   Public repos: {user_data.get('public_repos', 0)}")
        print(f"   Private repos: {user_data.get('total_private_repos', 0)}")
    else:
        print(f"❌ Token validation failed: {response.status_code}")
        print(f"   Error: {response.json() if response.content else 'No content'}")
        return False
    
    # Test 2: Check token scopes
    print("\n2. Checking token scopes...")
    scopes = response.headers.get('X-OAuth-Scopes', '').split(', ') if response.headers.get('X-OAuth-Scopes') else []
    if scopes and scopes != ['']:
        print(f"✅ Token scopes: {', '.join(scopes)}")
        
        required_scopes = ['repo', 'admin:org']
        missing_scopes = []
        for scope in required_scopes:
            if scope not in scopes:
                missing_scopes.append(scope)
        
        if missing_scopes:
            print(f"⚠️  Missing required scopes: {', '.join(missing_scopes)}")
        else:
            print("✅ All required scopes present")
    else:
        print("⚠️  No scopes information available")
    
    # Test 3: Organization access
    print("\n3. Testing organization access...")
    test_orgs = ['vsbopi']  # Add more orgs if needed
    
    for org in test_orgs:
        print(f"\n   Testing organization: {org}")
        
        # Check if org exists and is accessible
        org_response = requests.get(f"{base_url}/orgs/{org}", headers=headers)
        
        if org_response.status_code == 200:
            org_data = org_response.json()
            print(f"   ✅ Organization exists: {org_data.get('name', org)}")
            print(f"      Description: {org_data.get('description', 'No description')}")
            print(f"      Public repos: {org_data.get('public_repos', 0)}")
        elif org_response.status_code == 404:
            print(f"   ❌ Organization '{org}' not found or not accessible")
            continue
        else:
            print(f"   ⚠️  Error accessing organization: {org_response.status_code}")
            continue
        
        # Check membership
        membership_response = requests.get(f"{base_url}/orgs/{org}/memberships/{username}", headers=headers)
        
        if membership_response.status_code == 200:
            membership_data = membership_response.json()
            role = membership_data.get('role', 'Unknown')
            state = membership_data.get('state', 'Unknown')
            print(f"   ✅ Membership: {role} ({state})")
        elif membership_response.status_code == 404:
            print(f"   ❌ Not a member of organization '{org}'")
        else:
            print(f"   ⚠️  Error checking membership: {membership_response.status_code}")
        
        # Test custom properties support
        print(f"   🔧 Checking custom properties support...")
        properties_response = requests.get(f"{base_url}/orgs/{org}/properties/schema", headers=headers)
        
        if properties_response.status_code == 200:
            properties_data = properties_response.json()
            print(f"   ✅ Custom properties supported ({len(properties_data)} properties defined)")
        elif properties_response.status_code == 404:
            print(f"   ⚠️  Custom properties not configured for '{org}'")
        else:
            print(f"   ❓ Custom properties status unknown (HTTP {properties_response.status_code})")
        
        # Test repository creation permission
        print(f"   🧪 Testing repository creation in '{org}'...")
        test_repo_data = {
            "name": f"test-repo-{username}-123456",  # Unique name
            "description": "Test repository for permission validation",
            "private": True,
            "auto_init": False
        }
        
        create_response = requests.post(f"{base_url}/orgs/{org}/repos", 
                                      json=test_repo_data, headers=headers)
        
        if create_response.status_code == 201:
            repo_data = create_response.json()
            print(f"   ✅ Can create repositories in '{org}'")
            
            # Clean up test repository
            delete_response = requests.delete(f"{base_url}/repos/{org}/{test_repo_data['name']}", 
                                            headers=headers)
            if delete_response.status_code == 204:
                print(f"   🧹 Test repository cleaned up")
            else:
                print(f"   ⚠️  Could not delete test repository (status: {delete_response.status_code})")
                print(f"      Please manually delete: {repo_data.get('html_url', 'Unknown URL')}")
        else:
            error_data = create_response.json() if create_response.content else {}
            print(f"   ❌ Cannot create repositories in '{org}' (HTTP {create_response.status_code})")
            print(f"      Error: {error_data.get('message', 'Unknown error')}")
    
    print("\n" + "=" * 50)
    print("🏁 Diagnostic complete!")
    return True

def main():
    """Main diagnostic function"""
    print("GitHub Token Diagnostic Tool")
    print("This tool will test your GitHub token permissions and organization access.")
    print()
    
    token = input("Enter your GitHub token: ").strip()
    if not token:
        print("❌ No token provided")
        return
    
    try:
        test_token_permissions(token)
    except Exception as e:
        print(f"\n❌ Diagnostic failed with error: {e}")
    
    print("\n💡 Recommendations:")
    print("1. Ensure your token has 'repo' and 'admin:org' scopes")
    print("2. Verify you're a member of the 'vsbopi' organization")
    print("3. Check if the organization allows repository creation")
    print("4. If issues persist, contact your organization admin")

if __name__ == "__main__":
    main()
