#!/usr/bin/env python3
"""
Quick repository creation script
Usage: python create_repo.py --name "my-repo" --owner "vsbopi" --description "My awesome repo"
"""

import argparse
import sys
from main import GitHubRepoManager, RepoConfig
import os

def main():
    parser = argparse.ArgumentParser(description='Create GitHub repository with custom properties')
    
    # Required arguments
    parser.add_argument('--name', required=True, help='Repository name')
    parser.add_argument('--owner', required=True, help='Repository owner (organization or username)')
    parser.add_argument('--description', required=True, help='Repository description')
    
    # Repository visibility settings
    parser.add_argument('--visibility', choices=['public', 'internal', 'private'], 
                       default='internal', help='Repository visibility (default: internal)')
    # Backward compatibility flags
    parser.add_argument('--private', action='store_true', help='Make repository private (sets visibility to private)')
    parser.add_argument('--public', action='store_true', help='Make repository public (sets visibility to public)')
    parser.add_argument('--internal', action='store_true', help='Make repository internal (sets visibility to internal)')
    
    # Custom properties
    parser.add_argument('--application', default='', help='Application name')
    parser.add_argument('--compliance-audit', default='', help='Compliance audit to review')
    parser.add_argument('--deployed-to-prod', default='', help='Deployed to production')
    parser.add_argument('--impact-on-prod', default='', help='Impact on production application')
    parser.add_argument('--poc', default='', help='Point of contact')
    parser.add_argument('--repo-owner', default='', help='Repository owner/team')
    parser.add_argument('--deployment-method', default='', help='Production deployment method')
    parser.add_argument('--team', default='', help='Responsible team')
    
    # File options
    parser.add_argument('--gitignore', default='Python', help='Gitignore template (default: Python)')
    parser.add_argument('--readme', help='Path to README content file')
    
    # Branch protection
    parser.add_argument('--branch-protection', action='store_true', help='Enable branch protection')
    parser.add_argument('--reviews', type=int, default=2, help='Required number of reviews (default: 2)')
    
    # Environments
    parser.add_argument('--environments', help='Comma-separated list of environments')
    
    # Repository access
    parser.add_argument('--team-access', help='Team access in format "team1:permission1,team2:permission2"')
    parser.add_argument('--user-access', help='User access in format "user1:permission1,user2:permission2"')
    
    # Token
    parser.add_argument('--token', help='GitHub token (if not provided, will prompt)')
    parser.add_argument('--force-org', action='store_true', help='Force organization mode (skip org detection)')
    
    args = parser.parse_args()
    
    # Handle visibility with backward compatibility
    visibility = args.visibility
    if args.private:
        visibility = "private"
    elif args.public:
        visibility = "public"
    elif args.internal:
        visibility = "internal"
    
    # Get token
    token = args.token
    if not token:
        token = os.getenv('GITHUB_TOKEN')
    if not token:
        token = input("Enter your GitHub token: ").strip()
    
    if not token:
        print("Error: GitHub token is required")
        sys.exit(1)
    
    # Read README content if provided
    readme_content = ""
    if args.readme:
        try:
            with open(args.readme, 'r') as f:
                readme_content = f.read()
        except FileNotFoundError:
            print(f"Warning: README file {args.readme} not found")
    
    # Parse environments
    environments = []
    if args.environments:
        environments = [env.strip() for env in args.environments.split(',')]
    
    # Parse team access
    team_access = {}
    if args.team_access:
        try:
            for team_perm in args.team_access.split(','):
                team, permission = team_perm.strip().split(':')
                team_access[team.strip()] = permission.strip()
        except ValueError:
            print("Warning: Invalid team-access format. Use 'team1:permission1,team2:permission2'")
    
    # Parse user access
    user_access = {}
    if args.user_access:
        try:
            for user_perm in args.user_access.split(','):
                user, permission = user_perm.strip().split(':')
                user_access[user.strip()] = permission.strip()
        except ValueError:
            print("Warning: Invalid user-access format. Use 'user1:permission1,user2:permission2'")
    
    # Create configuration
    config = RepoConfig(
        name=args.name,
        owner=args.owner,
        description=args.description,
        visibility=visibility,
        application=args.application,
        compliance_audit_to_review=args.compliance_audit,
        deployed_to_prod=args.deployed_to_prod,
        impact_on_prod_app=args.impact_on_prod,
        poc=args.poc,
        repo_owner=args.repo_owner,
        prod_deployment_method=args.deployment_method,
        team=args.team,
        readme_content=readme_content,
        gitignore_template=args.gitignore,
        enable_branch_protection=args.branch_protection,
        required_reviews=args.reviews,
        environments=environments,
        team_access=team_access,
        user_access=user_access
    )
    
    # Create repository
    print(f"Creating repository: {args.owner}/{args.name}")
    manager = GitHubRepoManager(token)
    
    # Force organization mode if requested
    if args.force_org:
        print(f"🔧 Forcing organization mode for '{args.owner}'")
        manager._is_organization = lambda owner: True
    
    result = manager.create_repository(config)
    
    if result["success"]:
        print(f"\n✅ {result['message']}")
        print(f"🔗 Repository URL: {result['repository_url']}")
    else:
        print(f"\n❌ Error: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
