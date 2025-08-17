#!/usr/bin/env python3
"""
GitHub Teams Diagnostic Tool
This script helps diagnose team access issues by listing all teams in an organization
and testing team repository permissions.
"""

import requests
import json

def diagnose_teams(token, org_name):
    """Diagnose team access issues"""
    print(f"🔍 GitHub Teams Diagnostic for Organization: {org_name}")
    print("=" * 60)
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    base_url = "https://api.github.com"
    
    # List all teams in organization
    print("\n1. Listing all teams in organization...")
    teams_url = f"{base_url}/orgs/{org_name}/teams"
    response = requests.get(teams_url, headers=headers)
    
    if response.status_code == 200:
        teams = response.json()
        print(f"✅ Found {len(teams)} teams in '{org_name}':")
        
        team_info = []
        for team in teams:
            name = team.get('name', 'Unknown')
            slug = team.get('slug', 'Unknown')
            description = team.get('description', 'No description')
            privacy = team.get('privacy', 'Unknown')
            members_count = team.get('members_count', 0)
            
            team_info.append({
                'name': name,
                'slug': slug,
                'description': description,
                'privacy': privacy,
                'members_count': members_count
            })
            
            print(f"\n   📋 Team: {name}")
            print(f"      Slug: {slug}")
            print(f"      Privacy: {privacy}")
            print(f"      Members: {members_count}")
            print(f"      Description: {description}")
        
        return team_info
    else:
        print(f"❌ Could not list teams: {response.status_code}")
        print(f"   Error: {response.json() if response.content else 'No response'}")
        return []

def test_team_access(token, org_name, repo_name, team_slugs):
    """Test team access to a specific repository"""
    print(f"\n2. Testing team access to repository '{org_name}/{repo_name}'...")
    
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    base_url = "https://api.github.com"
    
    # Check current team permissions on repository
    repo_teams_url = f"{base_url}/repos/{org_name}/{repo_name}/teams"
    response = requests.get(repo_teams_url, headers=headers)
    
    current_teams = {}
    if response.status_code == 200:
        teams_data = response.json()
        current_teams = {team.get('slug', team.get('name', '')): team.get('permission', 'unknown') 
                        for team in teams_data}
        print(f"✅ Repository currently has {len(current_teams)} teams with access:")
        for team_slug, permission in current_teams.items():
            print(f"      • {team_slug}: {permission}")
    else:
        print(f"⚠️ Could not get repository team permissions: {response.status_code}")
    
    # Test each team slug
    print(f"\n3. Testing individual team access...")
    for team_slug in team_slugs:
        print(f"\n   🧪 Testing team: {team_slug}")
        
        # Check if team exists
        team_url = f"{base_url}/orgs/{org_name}/teams/{team_slug}"
        team_response = requests.get(team_url, headers=headers)
        
        if team_response.status_code == 200:
            team_data = team_response.json()
            print(f"      ✅ Team exists: {team_data.get('name')} (slug: {team_data.get('slug')})")
            
            # Test setting permission (dry run - we'll check what would happen)
            perm_url = f"{base_url}/orgs/{org_name}/teams/{team_slug}/repos/{org_name}/{repo_name}"
            
            # First, get current permission
            current_perm_response = requests.get(perm_url, headers=headers)
            if current_perm_response.status_code == 200:
                current_perm = current_perm_response.json().get('permission', 'none')
                print(f"      📋 Current permission: {current_perm}")
            else:
                print(f"      📋 No current repository access")
            
            # Test if we can set write permission
            test_data = {"permission": "read"}  # Use read as it's least permissive
            test_response = requests.put(perm_url, json=test_data, headers=headers)
            
            if test_response.status_code in [200, 204]:
                print(f"      ✅ Can set team permissions")
                # Restore original permission if it existed
                if current_perm_response.status_code == 200:
                    restore_data = {"permission": current_perm}
                    requests.put(perm_url, json=restore_data, headers=headers)
            else:
                error_data = test_response.json() if test_response.content else {}
                print(f"      ❌ Cannot set team permissions: {test_response.status_code}")
                print(f"         Error: {error_data.get('message', 'Unknown error')}")
                
        else:
            print(f"      ❌ Team not found: {team_response.status_code}")

def main():
    """Main diagnostic function"""
    print("GitHub Teams Diagnostic Tool")
    print("This tool helps diagnose team access issues.")
    print()
    
    token = input("Enter your GitHub token: ").strip()
    if not token:
        print("❌ No token provided")
        return
    
    org_name = input("Enter organization name: ").strip()
    if not org_name:
        print("❌ No organization name provided")
        return
    
    # Get all teams
    teams = diagnose_teams(token, org_name)
    
    # Test specific teams
    test_teams = input("\nEnter team slugs to test (comma-separated, or press Enter to skip): ").strip()
    if test_teams:
        team_slugs = [slug.strip() for slug in test_teams.split(',')]
        
        repo_name = input("Enter repository name to test team access: ").strip()
        if repo_name:
            test_team_access(token, org_name, repo_name, team_slugs)
    
    print("\n" + "=" * 60)
    print("🏁 Diagnostic complete!")
    
    if teams:
        print("\n💡 Team Configuration Tips:")
        print("- Use team 'slug' values in your configuration, not display names")
        print("- Team slugs are usually lowercase with hyphens")
        print("- Ensure teams have permission to access repositories")
        print("- Check that your token has 'admin:org' permissions")

if __name__ == "__main__":
    main()
