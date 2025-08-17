import requests
import json
import base64
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import os
from nacl import encoding, public


@dataclass
class RepoConfig:
    """Configuration class for GitHub repository creation"""
    # Basic repository info
    name: str
    owner: str  # Organization or user
    description: str
    visibility: str = "internal"  # "public", "private", or "internal"
    
    # Backward compatibility
    @property
    def private(self) -> bool:
        """Backward compatibility property"""
        return self.visibility in ["private", "internal"]
    
    # Custom properties
    application: str = ""
    compliance_audit_to_review: str = ""
    deployed_to_prod: str = ""
    impact_on_prod_app: str = ""
    poc: str = ""
    repo_owner: str = ""  # Different from GitHub owner
    prod_deployment_method: str = ""
    team: str = ""
    
    # Files
    readme_content: str = ""
    gitignore_template: str = "Python"  # Can be language name or custom content
    
    # Branch protection (backward compatibility)
    enable_branch_protection: bool = False
    protected_branch: str = "main"
    require_reviews: bool = True
    required_reviews: int = 2
    dismiss_stale_reviews: bool = True
    require_code_owner_reviews: bool = True
    
    # Enhanced branch protection (new structure)
    branch_protection_rules: Dict[str, Dict] = None  # {"branch_name": {"enable": True, ...}}
    auto_create_branches: bool = True  # Whether to auto-create branches if they don't exist
    
    # Environments
    environments: List[str] = None
    
    # Secrets and variables
    secrets: Dict[str, str] = None
    variables: Dict[str, str] = None
    
    # Environment-specific secrets and variables
    environment_secrets: Dict[str, Dict[str, str]] = None  # {"env_name": {"secret_name": "value"}}
    environment_variables: Dict[str, Dict[str, str]] = None  # {"env_name": {"var_name": "value"}}
    
    # Environment protection rules
    environment_protection: Dict[str, Dict] = None  # {"env_name": {"wait_timer": 0, "reviewers": [...]}}
    
    # Repository access management
    team_access: Dict[str, str] = None  # {"team_name": "permission_level"}
    user_access: Dict[str, str] = None  # {"username": "permission_level"}


class GitHubRepoManager:
    """Comprehensive GitHub repository management tool"""
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        self.base_url = "https://api.github.com"
    
    def _check_repository_exists(self, config: RepoConfig) -> Optional[Dict]:
        """Check if repository already exists"""
        url = f"{self.base_url}/repos/{config.owner}/{config.name}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            print(f"⚠️ Error checking repository existence: {response.status_code}")
            return None
    
    def create_repository(self, config: RepoConfig) -> Dict[str, Any]:
        """Create or update a GitHub repository with all configurations"""
        try:
            print(f"🔍 Checking repository: {config.owner}/{config.name}")
            
            # Step 1: Check if repository exists
            repo_data = self._check_repository_exists(config)
            repo_url = ""
            
            if repo_data:
                repo_url = repo_data["html_url"]
                print(f"✅ Repository already exists: {repo_url}")
                print("🔧 Proceeding to verify and update configurations...")
            else:
                print(f"📝 Repository doesn't exist, creating: {config.owner}/{config.name}")
                # Create the repository
                repo_data = self._create_base_repository(config)
                if not repo_data:
                    return {"success": False, "error": "Failed to create repository"}
                
                repo_url = repo_data["html_url"]
                print(f"✅ Repository created: {repo_url}")
                
                # Small delay to ensure repository is fully initialized
                print("⏳ Waiting for repository initialization...")
                time.sleep(2)
            
            # Step 2: Add custom properties
            print("🔧 Setting up custom properties...")
            # Check if custom properties are supported
            if self._check_custom_properties_support(config):
                self._add_custom_properties(config)
            else:
                print("🔄 Custom properties not available, using topics as fallback...")
                self._add_as_topics(config)
            print("✓ Custom properties configured")
            
            # Step 3: Check and update README file
            print("📖 Checking README file...")
            self._check_and_update_readme(config)
            print("✓ README configured")
            
            # Step 4: Check and update .gitignore file
            print("📄 Checking .gitignore file...")
            self._check_and_update_gitignore(config)
            print("✓ .gitignore configured")
            
            # Step 5: Check and set up branch protection
            print("🔒 Checking branch protection...")
            self._check_and_setup_branch_protection(config)
            print("✓ Branch protection configured")
            
            # Step 6: Check and create environments
            print("🌍 Checking environments...")
            self._check_and_create_environments(config)
            print("✓ Environments configured")
            
            # Step 7: Add secrets and variables
            if config.secrets or config.variables:
                self._setup_secrets_and_variables(config)
                print("✓ Secrets and variables configured")
            
            # Step 8: Set up team and user access
            print("👥 Checking repository access...")
            self._setup_repository_access(config)
            print("✓ Repository access configured")
            
            return {
                "success": True,
                "repository_url": repo_url,
                "message": "Repository created successfully with all configurations"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _create_base_repository(self, config: RepoConfig) -> Optional[Dict]:
        """Create the basic repository"""
        # Check if it's an organization or user repository
        is_org = self._is_organization(config.owner)
        
        if is_org:
            url = f"{self.base_url}/orgs/{config.owner}/repos"
            print(f"🏢 Creating repository in organization: {config.owner}")
        else:
            url = f"{self.base_url}/user/repos"
            print(f"👤 Creating repository in user account: {config.owner}")
        
        # Prepare repository data with visibility
        data = {
            "name": config.name,
            "description": config.description,
            "auto_init": True,  # Initialize with initial commit
            "gitignore_template": None,  # We'll create custom gitignore
        }
        
        # Set visibility based on configuration
        if config.visibility == "public":
            data["private"] = False
        elif config.visibility == "private":
            data["private"] = True
        elif config.visibility == "internal":
            data["visibility"] = "internal"
        else:
            # Default to internal for organizations, private for users
            if self._is_organization(config.owner):
                data["visibility"] = "internal"
            else:
                data["private"] = True
        
        print(f"🔒 Repository visibility: {config.visibility}")
        
        print(f"📡 Making API request to: {url}")
        response = requests.post(url, json=data, headers=self.headers)
        
        if response.status_code == 201:
            repo_data = response.json()
            actual_url = repo_data.get('html_url', 'Unknown')
            print(f"✅ Repository created successfully at: {actual_url}")
            return repo_data
        else:
            print(f"❌ Error creating repository: HTTP {response.status_code}")
            error_data = response.json() if response.content else {}
            print(f"Error details: {error_data}")
            
            # Provide specific guidance based on error
            if response.status_code == 404 and is_org:
                print(f"\n💡 Troubleshooting suggestions:")
                print(f"1. Verify you're a member of the '{config.owner}' organization")
                print(f"2. Check if your token has 'admin:org' permissions")
                print(f"3. Ensure the organization name is spelled correctly")
                print(f"4. Try creating the repository manually to test permissions")
            elif response.status_code == 403:
                print(f"\n💡 Permission issue:")
                print(f"Your token doesn't have permission to create repositories in '{config.owner}'")
            elif response.status_code == 422:
                error_msg = error_data.get('message', 'Unknown validation error')
                print(f"\n💡 Validation error: {error_msg}")
                if 'already exists' in error_msg.lower():
                    print(f"Repository '{config.owner}/{config.name}' already exists")
            
            return None
    
    def _is_organization(self, owner: str) -> bool:
        """Check if the owner is an organization"""
        url = f"{self.base_url}/orgs/{owner}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            print(f"✓ Detected '{owner}' as an organization")
            return True
        elif response.status_code == 404:
            print(f"ℹ️ '{owner}' not found as organization, treating as user account")
            return False
        else:
            print(f"⚠️ Error checking organization '{owner}': {response.status_code}")
            print(f"Response: {response.json() if response.content else 'No content'}")
            # If we can't determine, try organization first
            print(f"ℹ️ Defaulting to organization mode for '{owner}'")
            return True
    
    def _check_custom_properties_support(self, config: RepoConfig) -> bool:
        """Check if custom properties are supported for this repository/organization"""
        # First check if the organization has custom properties enabled
        if self._is_organization(config.owner):
            url = f"{self.base_url}/orgs/{config.owner}/properties/schema"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                properties_schema = response.json()
                print(f"✅ Organization '{config.owner}' supports custom properties")
                print(f"   Available properties: {len(properties_schema)} defined")
                return True
            elif response.status_code == 404:
                print(f"ℹ️ Organization '{config.owner}' doesn't have custom properties configured")
                return False
            else:
                print(f"⚠️ Could not check custom properties support: {response.status_code}")
                return False
        else:
            # User repositories might not support custom properties the same way
            print("ℹ️ Custom properties are primarily an organization feature")
            return False
    
    def _get_existing_custom_properties(self, config: RepoConfig) -> Dict[str, str]:
        """Get existing custom properties from repository"""
        url = f"{self.base_url}/repos/{config.owner}/{config.name}/properties/values"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            existing_props = {}
            for prop in data:
                existing_props[prop['property_name']] = prop['value']
            return existing_props
        else:
            return {}
    
    def _add_custom_properties(self, config: RepoConfig):
        """Add or update custom properties using GitHub's custom properties API"""
        # Get existing properties
        existing_properties = self._get_existing_custom_properties(config)
        
        # Map config fields to custom properties
        property_mapping = {
            "Application": config.application,
            "ComplianceAuditToReview": config.compliance_audit_to_review,
            "DeployedToProd": config.deployed_to_prod,
            "ImpactOnProdApp": config.impact_on_prod_app,
            "poc": config.poc,
            "owner": config.repo_owner,
            "ProdDeploymentMethod": config.prod_deployment_method,
            "Team": config.team
        }
        
        # Find properties that need to be added or updated
        properties_to_update = []
        unchanged_count = 0
        
        for property_name, value in property_mapping.items():
            if value:  # Only process non-empty values
                current_value = existing_properties.get(property_name)
                if current_value != str(value):
                    properties_to_update.append({
                        "property_name": property_name,
                        "value": value
                    })
                    if current_value:
                        print(f"🔄 Will update {property_name}: '{current_value}' → '{value}'")
                    else:
                        print(f"➕ Will add {property_name}: '{value}'")
                else:
                    unchanged_count += 1
        
        if unchanged_count > 0:
            print(f"✅ {unchanged_count} properties already up to date")
        
        if properties_to_update:
            url = f"{self.base_url}/repos/{config.owner}/{config.name}/properties/values"
            data = {"properties": properties_to_update}
            print(data)
            print(f"📝 Updating {len(properties_to_update)} custom properties...")
            
            response = requests.patch(url, json=data, headers=self.headers)
            
            if response.status_code in [200, 204]:
                print(f"✅ Custom properties updated successfully")
                # Log which properties were updated
                for prop in properties_to_update:
                    print(f"   • {prop['property_name']}: {prop['value']}")
            else:
                print(f"⚠️ Warning: Could not update custom properties (HTTP {response.status_code})")
                error_data = response.json() if response.content else {}
                print(f"   Error: {error_data.get('message', 'Unknown error')}")
                
                # Provide helpful guidance
                if response.status_code == 404:
                    print("   💡 This might be because:")
                    print("      - Custom properties feature is not enabled for this repository/organization")
                    print("      - You don't have permission to manage custom properties")
                    print("      - The repository was just created and properties aren't available yet")
                elif response.status_code == 403:
                    print("   💡 Permission issue: Your token needs 'repo' scope with admin access")
                
                # Fallback: Add as topics for visibility
                print("   🔄 Falling back to repository topics...")
                self._add_as_topics(config)
        else:
            print("✅ All custom properties are already up to date")
    
    def _add_as_topics(self, config: RepoConfig):
        """Fallback method: Add custom properties as repository topics"""
        topics = []
        
        # Convert custom properties to topics
        if config.application:
            topics.append(f"app-{config.application.lower().replace(' ', '-').replace('.', '-')}")
        if config.team:
            topics.append(f"team-{config.team.lower().replace(' ', '-').replace('.', '-')}")
        if config.poc:
            # Extract just the username part if it's an email
            poc_name = config.poc.split('@')[0] if '@' in config.poc else config.poc
            topics.append(f"poc-{poc_name.lower().replace(' ', '-').replace('.', '-')}")
        if config.deployed_to_prod and config.deployed_to_prod.lower() == 'yes':
            topics.append("production-deployed")
        if config.compliance_audit_to_review and config.compliance_audit_to_review.lower() == 'yes':
            topics.append("compliance-required")
        
        if topics:
            url = f"{self.base_url}/repos/{config.owner}/{config.name}/topics"
            data = {"names": topics}
            
            response = requests.put(url, json=data, headers=self.headers)
            if response.status_code == 200:
                print(f"✅ Added {len(topics)} topics as fallback")
                for topic in topics:
                    print(f"   • {topic}")
            else:
                print(f"⚠️ Warning: Could not add topics either: {response.json() if response.content else 'No response'}")
    
    def _check_and_update_readme(self, config: RepoConfig):
        """Check if README exists and update if needed"""
        # Check if README already exists
        url = f"{self.base_url}/repos/{config.owner}/{config.name}/contents/README.md"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            # README exists, check if we need to update it
            existing_readme = response.json()
            print("📖 README.md already exists")
            
            if config.readme_content:
                # User provided custom README content
                import base64
                current_content = base64.b64decode(existing_readme['content']).decode('utf-8')
                
                if current_content.strip() != config.readme_content.strip():
                    print("🔄 README content differs, updating...")
                    self._update_file(config, "README.md", config.readme_content, existing_readme['sha'])
                else:
                    print("✅ README content is already up to date")
            else:
                print("✅ README exists and no custom content specified, keeping current version")
        else:
            # README doesn't exist, create it
            print("📝 Creating README.md...")
            if not config.readme_content:
                # Generate basic README if none provided
                config.readme_content = f"""# {config.name}

## Description
{config.description}

## Application
{config.application}

## Team
{config.team}

## Point of Contact
{config.poc}

## Owner
{config.repo_owner}

## Production Deployment Method
{config.prod_deployment_method}

## Compliance & Audit
- Compliance Audit to Review: {config.compliance_audit_to_review}
- Deployed to Production: {config.deployed_to_prod}
- Impact on Production Application: {config.impact_on_prod_app}
"""
            
            self._create_file(config, "README.md", config.readme_content)
    
    def _check_and_update_gitignore(self, config: RepoConfig):
        """Check if .gitignore exists and update if needed"""
        # Check if .gitignore already exists
        url = f"{self.base_url}/repos/{config.owner}/{config.name}/contents/.gitignore"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            print("📄 .gitignore already exists")
            
            # Get desired gitignore content
            desired_content = self._get_gitignore_content(config)
            
            if desired_content:
                existing_gitignore = response.json()
                import base64
                current_content = base64.b64decode(existing_gitignore['content']).decode('utf-8')
                
                if current_content.strip() != desired_content.strip():
                    print("🔄 .gitignore content differs, updating...")
                    self._update_file(config, ".gitignore", desired_content, existing_gitignore['sha'])
                else:
                    print("✅ .gitignore content is already up to date")
            else:
                print("✅ .gitignore exists and no template specified, keeping current version")
        else:
            # .gitignore doesn't exist, create it
            print("📝 Creating .gitignore...")
            gitignore_content = self._get_gitignore_content(config)
            if gitignore_content:
                self._create_file(config, ".gitignore", gitignore_content)
    
    def _get_gitignore_content(self, config: RepoConfig) -> str:
        """Get the desired .gitignore content"""
        if not config.gitignore_template:
            return ""
            
        # If it's a template name, fetch from GitHub
        if len(config.gitignore_template.split('\n')) == 1:
            template_url = f"https://api.github.com/gitignore/templates/{config.gitignore_template}"
            response = requests.get(template_url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()["source"]
            else:
                # Fallback to basic Python .gitignore
                return """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
"""
        else:
            # Use provided content directly
            return config.gitignore_template
    
    def _create_file(self, config: RepoConfig, filename: str, content: str):
        """Create a file in the repository"""
        url = f"{self.base_url}/repos/{config.owner}/{config.name}/contents/{filename}"
        
        encoded_content = base64.b64encode(content.encode()).decode()
        
        data = {
            "message": f"Add {filename}",
            "content": encoded_content
        }
        
        response = requests.put(url, json=data, headers=self.headers)
        if response.status_code not in [200, 201]:
            print(f"Warning: Could not create {filename}: {response.json()}")
    
    def _update_file(self, config: RepoConfig, filename: str, content: str, sha: str):
        """Update an existing file in the repository"""
        url = f"{self.base_url}/repos/{config.owner}/{config.name}/contents/{filename}"
        
        encoded_content = base64.b64encode(content.encode()).decode()
        
        data = {
            "message": f"Update {filename}",
            "content": encoded_content,
            "sha": sha
        }
        
        response = requests.put(url, json=data, headers=self.headers)
        if response.status_code not in [200, 201]:
            print(f"Warning: Could not update {filename}: {response.json()}")
        else:
            print(f"✅ {filename} updated successfully")
    
    def _check_and_setup_branch_protection(self, config: RepoConfig):
        """Check and set up branch protection rules for multiple branches"""
        # Handle new multi-branch protection structure
        if config.branch_protection_rules:
            print(f"🔒 Setting up protection for {len(config.branch_protection_rules)} branches...")
            for branch_name, branch_config in config.branch_protection_rules.items():
                if branch_config.get('enable', False):
                    self._setup_single_branch_protection(config, branch_name, branch_config)
            return
        
        # Backward compatibility with old single-branch structure
        if config.enable_branch_protection:
            print(f"🔒 Setting up protection for single branch: {config.protected_branch}")
            legacy_config = {
                'enable': True,
                'require_reviews': config.require_reviews,
                'required_reviews': config.required_reviews,
                'dismiss_stale_reviews': config.dismiss_stale_reviews,
                'require_code_owner_reviews': config.require_code_owner_reviews,
                'enforce_admins': True,
                'require_status_checks': False,
                'status_checks': []
            }
            self._setup_single_branch_protection(config, config.protected_branch, legacy_config)
        else:
            print("ℹ️ Branch protection not enabled in configuration")
    
    def _setup_single_branch_protection(self, config: RepoConfig, branch_name: str, branch_config: Dict):
        """Set up protection for a single branch"""
        # First, ensure the branch exists
        if not self._branch_exists(config, branch_name):
            if config.auto_create_branches:
                print(f"   📝 Branch '{branch_name}' not found, creating it...")
                if self._create_branch(config, branch_name):
                    print(f"   ✅ Created branch '{branch_name}'")
                else:
                    print(f"   ❌ Failed to create branch '{branch_name}', skipping protection")
                    return
            else:
                print(f"   ⚠️ Branch '{branch_name}' not found and auto-create is disabled, skipping protection")
                return
        
        url = f"{self.base_url}/repos/{config.owner}/{config.name}/branches/{branch_name}/protection"
        
        # Check existing protection
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            # Branch protection exists, check if it matches our config
            existing_protection = response.json()
            print(f"🔒 Branch protection already exists for '{branch_name}'")
            
            # Compare with desired configuration
            needs_update = self._compare_branch_protection(existing_protection, branch_config)
            
            if not needs_update:
                print(f"   ✅ Branch protection for '{branch_name}' is already up to date")
                return
            
            print(f"   📝 Updating branch protection for '{branch_name}'...")
        else:
            print(f"🔒 Setting up branch protection for '{branch_name}'...")
        
        # Build protection data
        protection_data = self._build_protection_data(branch_config)
        
        response = requests.put(url, json=protection_data, headers=self.headers)
        if response.status_code == 200:
            print(f"   ✅ Branch protection configured successfully for '{branch_name}'")
        else:
            error_data = response.json() if response.content else {}
            print(f"   ⚠️ Could not set branch protection for '{branch_name}': {error_data.get('message', 'Unknown error')}")
    
    def _compare_branch_protection(self, existing: Dict, desired: Dict) -> bool:
        """Compare existing and desired branch protection settings"""
        needs_update = False
        current_reviews = existing.get('required_pull_request_reviews', {})
        
        # Check review requirements
        if current_reviews.get('required_approving_review_count') != desired.get('required_reviews', 2):
            print(f"     🔄 Review count differs: {current_reviews.get('required_approving_review_count')} → {desired.get('required_reviews', 2)}")
            needs_update = True
        
        if current_reviews.get('dismiss_stale_reviews') != desired.get('dismiss_stale_reviews', True):
            print(f"     🔄 Dismiss stale reviews setting differs")
            needs_update = True
            
        if current_reviews.get('require_code_owner_reviews') != desired.get('require_code_owner_reviews', True):
            print(f"     🔄 Code owner reviews setting differs")
            needs_update = True
        
        # Check admin enforcement
        if existing.get('enforce_admins', {}).get('enabled') != desired.get('enforce_admins', True):
            print(f"     🔄 Admin enforcement setting differs")
            needs_update = True
        
        # Check status checks
        existing_checks = existing.get('required_status_checks', {})
        desired_checks = desired.get('status_checks', [])
        current_checks = existing_checks.get('contexts', []) if existing_checks else []
        
        if set(current_checks) != set(desired_checks):
            print(f"     🔄 Status checks differ: {current_checks} → {desired_checks}")
            needs_update = True
        
        return needs_update
    
    def _build_protection_data(self, branch_config: Dict) -> Dict:
        """Build branch protection data for API call"""
        protection_data = {
            "required_pull_request_reviews": {
                "required_approving_review_count": branch_config.get('required_reviews', 2),
                "dismiss_stale_reviews": branch_config.get('dismiss_stale_reviews', True),
                "require_code_owner_reviews": branch_config.get('require_code_owner_reviews', True)
            },
            "enforce_admins": branch_config.get('enforce_admins', True),
            "restrictions": None
        }
        
        # Add status checks if required
        if branch_config.get('require_status_checks', False):
            status_checks = branch_config.get('status_checks', [])
            protection_data["required_status_checks"] = {
                "strict": True,
                "contexts": status_checks
            }
        else:
            protection_data["required_status_checks"] = None
        
        return protection_data
    
    def _branch_exists(self, config: RepoConfig, branch_name: str) -> bool:
        """Check if a branch exists in the repository"""
        url = f"{self.base_url}/repos/{config.owner}/{config.name}/branches/{branch_name}"
        response = requests.get(url, headers=self.headers)
        return response.status_code == 200
    
    def _create_branch(self, config: RepoConfig, branch_name: str) -> bool:
        """Create a new branch from the default branch"""
        try:
            # First, get the default branch (usually main or master)
            repo_url = f"{self.base_url}/repos/{config.owner}/{config.name}"
            repo_response = requests.get(repo_url, headers=self.headers)
            
            if repo_response.status_code != 200:
                print(f"   ⚠️ Could not get repository info")
                return False
            
            repo_data = repo_response.json()
            default_branch = repo_data.get('default_branch', 'main')
            
            # Get the SHA of the default branch
            default_branch_url = f"{self.base_url}/repos/{config.owner}/{config.name}/branches/{default_branch}"
            default_response = requests.get(default_branch_url, headers=self.headers)
            
            if default_response.status_code != 200:
                print(f"   ⚠️ Could not get default branch '{default_branch}' info")
                return False
            
            default_branch_data = default_response.json()
            sha = default_branch_data['commit']['sha']
            
            # Create the new branch
            create_url = f"{self.base_url}/repos/{config.owner}/{config.name}/git/refs"
            create_data = {
                "ref": f"refs/heads/{branch_name}",
                "sha": sha
            }
            
            create_response = requests.post(create_url, json=create_data, headers=self.headers)
            
            if create_response.status_code == 201:
                return True
            else:
                error_data = create_response.json() if create_response.content else {}
                print(f"   ⚠️ Could not create branch: {error_data.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"   ⚠️ Error creating branch: {str(e)}")
            return False
    
    def _check_and_create_environments(self, config: RepoConfig):
        """Check and create repository environments"""
        if not config.environments:
            print("ℹ️ No environments specified in configuration")
            return
            
        # Get existing environments
        url = f"{self.base_url}/repos/{config.owner}/{config.name}/environments"
        response = requests.get(url, headers=self.headers)
        
        existing_environments = set()
        if response.status_code == 200:
            environments_data = response.json()
            existing_environments = {env['name'] for env in environments_data.get('environments', [])}
            if existing_environments:
                print(f"📋 Found {len(existing_environments)} existing environments: {', '.join(existing_environments)}")
        
        environments_to_create = set(config.environments) - existing_environments
        unchanged_environments = set(config.environments) & existing_environments
        
        if unchanged_environments:
            print(f"✅ {len(unchanged_environments)} environments already exist: {', '.join(unchanged_environments)}")
        
        if environments_to_create:
            print(f"📝 Creating {len(environments_to_create)} new environments...")
            for env_name in environments_to_create:
                self._create_single_environment(config, env_name)
        else:
            print("✅ All environments are already up to date")
        
        # Update protection rules for all environments (both new and existing)
        self._setup_environment_protection_rules(config)
        
        # Now handle environment-specific secrets and variables
        self._setup_environment_secrets_and_variables(config)
    
    def _create_single_environment(self, config: RepoConfig, env_name: str):
        """Create a single environment with basic configuration"""
        env_url = f"{self.base_url}/repos/{config.owner}/{config.name}/environments/{env_name}"
        
        # Get protection rules for this environment if available
        protection_config = {}
        if config.environment_protection and env_name in config.environment_protection:
            protection_config = config.environment_protection[env_name]
        
        # Get deployment branch policy configuration
        branch_policy = protection_config.get("deployment_branch_policy", {})
        protected_branches = branch_policy.get("protected_branches", False)
        custom_branch_policies = branch_policy.get("custom_branch_policies", False)
        
        # Fix GitHub API validation issue: avoid both being false
        # If both are false, omit the deployment_branch_policy entirely
        env_data = {
            "wait_timer": protection_config.get("wait_timer", 0),
            "reviewers": [],  # Will be set up separately in protection rules
        }
        
        # Only add deployment_branch_policy if it's not the default "both false" state
        if protected_branches or custom_branch_policies:
            env_data["deployment_branch_policy"] = {
                "protected_branches": protected_branches,
                "custom_branch_policies": custom_branch_policies
            }
        
        response = requests.put(env_url, json=env_data, headers=self.headers)
        if response.status_code in [200, 201]:
            print(f"   ✅ Created environment: {env_name}")
        else:
            error_data = response.json() if response.content else {}
            print(f"   ⚠️ Could not create environment {env_name}: {error_data.get('message', 'No response')}")
    
    def _setup_environment_protection_rules(self, config: RepoConfig):
        """Set up protection rules for all environments"""
        if not config.environment_protection:
            print("ℹ️ No environment protection rules specified")
            return
        
        print("🛡️ Setting up environment protection rules...")
        
        for env_name, protection_config in config.environment_protection.items():
            if env_name in config.environments:
                print(f"   🔒 Configuring protection for '{env_name}'...")
                self._apply_environment_protection(config, env_name, protection_config)
            else:
                print(f"   ⚠️ Skipping protection for '{env_name}' - environment not in config")
    
    def _apply_environment_protection(self, config: RepoConfig, env_name: str, protection_config: Dict):
        """Apply protection rules to a specific environment"""
        env_url = f"{self.base_url}/repos/{config.owner}/{config.name}/environments/{env_name}"
        
        # Prepare reviewers list
        reviewers = []
        if "reviewers" in protection_config:
            for reviewer in protection_config["reviewers"]:
                reviewer_type = reviewer.get("type", "").lower()
                reviewer_id = reviewer.get("id", "")
                
                if reviewer_type == "team":
                    # Handle team IDs that may include org prefix (e.g., "vsbopi/team-name")
                    if "/" in reviewer_id:
                        # Format: "org/team-name" - extract just the team name
                        team_name = reviewer_id.split("/", 1)[1]
                    else:
                        team_name = reviewer_id
                    
                    # Validate team exists and get proper slug
                    team_slug = self._validate_and_get_team_slug(config, team_name)
                    if team_slug:
                        team_id = self._get_team_database_id(config.owner, team_slug)
                        if team_id:
                            reviewers.append({
                                "type": "Team",
                                "id": team_id
                            })
                            print(f"     ✅ Added team reviewer: {reviewer_id}")
                        else:
                            print(f"     ❌ Could not get database ID for team: {reviewer_id}")
                    else:
                        print(f"     ❌ Could not find team: {reviewer_id}")
                elif reviewer_type == "user":
                    # Validate user exists
                    user_id = self._get_user_database_id(reviewer_id)
                    if user_id:
                        reviewers.append({
                            "type": "User", 
                            "id": user_id
                        })
                        print(f"     ✅ Added user reviewer: {reviewer_id}")
                    else:
                        print(f"     ⚠️ Could not find user: {reviewer_id}")
        
        # Build deployment branch policy
        branch_policy = protection_config.get("deployment_branch_policy", {})
        protected_branches = branch_policy.get("protected_branches", False)
        custom_branch_policies = branch_policy.get("custom_branch_policies", False)
        
        # Build environment protection data
        env_data = {
            "wait_timer": protection_config.get("wait_timer", 0),
            "prevent_self_review": protection_config.get("prevent_self_review", False),
            "reviewers": reviewers,
        }
        
        # Only add deployment_branch_policy if it's not the default "both false" state
        # This fixes the GitHub API validation error
        if protected_branches or custom_branch_policies:
            deployment_branch_policy = {
                "protected_branches": protected_branches,
                "custom_branch_policies": custom_branch_policies
            }
            env_data["deployment_branch_policy"] = deployment_branch_policy
        
        response = requests.put(env_url, json=env_data, headers=self.headers)
        
        if response.status_code in [200, 201]:
            wait_timer = protection_config.get("wait_timer", 0)
            prevent_self = protection_config.get("prevent_self_review", False)
            reviewer_count = len(reviewers)
            
            # Handle custom branches if specified
            if branch_policy.get("custom_branches") and custom_branch_policies:
                self._set_environment_deployment_branches(config, env_name, branch_policy["custom_branches"])
            
            # Show deployment branch policy
            if protected_branches:
                branch_info = "protected branches only"
            elif custom_branch_policies and branch_policy.get("custom_branches"):
                branch_info = f"custom branches: {', '.join(branch_policy['custom_branches'])}"
            else:
                branch_info = "no restrictions"
            
            print(f"     ✅ Protection configured: {reviewer_count} reviewers, {wait_timer}min wait, self-review: {'blocked' if prevent_self else 'allowed'}, branches: {branch_info}")
        else:
            error_data = response.json() if response.content else {}
            print(f"     ⚠️ Could not set protection for '{env_name}': {error_data.get('message', 'Unknown error')}")
    
    def _set_environment_deployment_branches(self, config: RepoConfig, env_name: str, custom_branches: list):
        """Set custom deployment branches for an environment"""
        try:
            # First, get existing deployment branch policies
            url = f"{self.base_url}/repos/{config.owner}/{config.name}/environments/{env_name}/deployment-branch-policies"
            
            # Delete existing policies first
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                existing_policies = response.json().get('branch_policies', [])
                for policy in existing_policies:
                    delete_url = f"{url}/{policy['id']}"
                    requests.delete(delete_url, headers=self.headers)
            
            # Add new branch policies
            for branch in custom_branches:
                branch_data = {
                    "name": branch
                }
                response = requests.post(url, json=branch_data, headers=self.headers)
                if response.status_code == 200:
                    print(f"       🌿 Added deployment branch: {branch}")
                else:
                    print(f"       ⚠️ Could not add deployment branch {branch}: {response.status_code}")
                    
        except Exception as e:
            print(f"       ⚠️ Error setting deployment branches: {str(e)}")
    
    def _get_team_database_id(self, org: str, team_slug: str) -> int:
        """Get the GitHub database ID for a team (required for environment reviewers)"""
        try:
            url = f"{self.base_url}/orgs/{org}/teams/{team_slug}"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json().get("id", 0)
            return 0
        except Exception:
            return 0
    
    def _get_user_database_id(self, username: str) -> int:
        """Get the GitHub database ID for a user (required for environment reviewers)"""
        try:
            url = f"{self.base_url}/users/{username}"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json().get("id", 0)
            return 0
        except Exception:
            return 0
    
    def _get_team_node_id(self, org: str, team_slug: str) -> str:
        """Get the GitHub node ID for a team"""
        try:
            url = f"{self.base_url}/orgs/{org}/teams/{team_slug}"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json().get("node_id", "")
            return ""
        except Exception:
            return ""
    
    def _get_user_node_id(self, username: str) -> str:
        """Get the GitHub node ID for a user"""
        try:
            url = f"{self.base_url}/users/{username}"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json().get("node_id", "")
            return ""
        except Exception:
            return ""
    
    def _setup_environment_secrets_and_variables(self, config: RepoConfig):
        """Set up environment-specific secrets and variables"""
        
        # Handle environment-specific variables
        if config.environment_variables:
            print("🔧 Setting up environment-specific variables...")
            for env_name, variables in config.environment_variables.items():
                if env_name in config.environments:
                    print(f"   📝 Setting variables for environment '{env_name}'...")
                    self._check_and_create_environment_variables(config, env_name, variables)
                else:
                    print(f"   ⚠️ Skipping variables for '{env_name}' - environment not in config")
        
        # Handle environment-specific secrets
        if config.environment_secrets:
            print("🔐 Setting up environment-specific secrets...")
            for env_name, secrets in config.environment_secrets.items():
                if env_name in config.environments:
                    print(f"   🔒 Setting secrets for environment '{env_name}'...")
                    try:
                        self._check_and_create_environment_secrets(config, env_name, secrets)
                    except Exception as e:
                        print(f"   ⚠️ Could not set secrets for '{env_name}': {e}")
                else:
                    print(f"   ⚠️ Skipping secrets for '{env_name}' - environment not in config")
    
    def _setup_secrets_and_variables(self, config: RepoConfig):
        """Set up repository secrets and variables"""
        
        # Set up variables first (they don't need encryption)
        if config.variables:
            print("🔧 Checking variables...")
            self._check_and_create_variables(config)
        
        # Set up secrets (require encryption)
        if config.secrets:
            print("🔐 Checking secrets...")
            try:
                self._check_and_create_secrets(config)
            except Exception as e:
                print(f"\n📝 Could not automatically create secrets: {e}")
                print("Manual step required for secrets:")
                print("Go to Settings > Secrets and variables > Actions in your repository")
                print("Add the following secrets:")
                for key in config.secrets.keys():
                    print(f"  - {key}")
    
    def _check_and_create_environment_variables(self, config: RepoConfig, env_name: str, variables: Dict[str, str]):
        """Check and create variables for a specific environment"""
        if not variables:
            return
        
        # Get existing environment variables
        url = f"{self.base_url}/repos/{config.owner}/{config.name}/environments/{env_name}/variables"
        response = requests.get(url, headers=self.headers)
        
        existing_variables = {}
        if response.status_code == 200:
            variables_data = response.json()
            existing_variables = {var['name']: var['value'] for var in variables_data.get('variables', [])}
            print(f"     📋 Found {len(existing_variables)} existing variables in '{env_name}'")
        elif response.status_code == 404:
            print(f"     📋 No existing variables in '{env_name}'")
        else:
            print(f"     ⚠️ Could not fetch variables for '{env_name}': {response.status_code}")
        
        # Create/update variables
        variables_created = 0
        variables_updated = 0
        variables_unchanged = 0
        
        for var_name, var_value in variables.items():
            if var_name in existing_variables:
                if existing_variables[var_name] != var_value:
                    # Update variable
                    var_url = f"{self.base_url}/repos/{config.owner}/{config.name}/environments/{env_name}/variables/{var_name}"
                    var_data = {"name": var_name, "value": var_value}
                    response = requests.patch(var_url, json=var_data, headers=self.headers)
                    
                    if response.status_code == 204:
                        print(f"     🔄 Updated variable '{var_name}' in '{env_name}'")
                        variables_updated += 1
                    else:
                        print(f"     ⚠️ Could not update variable '{var_name}' in '{env_name}': {response.status_code}")
                else:
                    variables_unchanged += 1
            else:
                # Create new variable
                var_url = f"{self.base_url}/repos/{config.owner}/{config.name}/environments/{env_name}/variables"
                var_data = {"name": var_name, "value": var_value}
                response = requests.post(var_url, json=var_data, headers=self.headers)
                
                if response.status_code == 201:
                    print(f"     ➕ Created variable '{var_name}' in '{env_name}'")
                    variables_created += 1
                else:
                    print(f"     ⚠️ Could not create variable '{var_name}' in '{env_name}': {response.status_code}")
        
        if variables_unchanged > 0:
            print(f"     ✅ {variables_unchanged} variables in '{env_name}' already up to date")
    
    def _check_and_create_environment_secrets(self, config: RepoConfig, env_name: str, secrets: Dict[str, str]):
        """Check and create secrets for a specific environment"""
        if not secrets:
            return
        
        # Get environment public key for encryption
        key_url = f"{self.base_url}/repos/{config.owner}/{config.name}/environments/{env_name}/secrets/public-key"
        key_response = requests.get(key_url, headers=self.headers)
        
        if key_response.status_code != 200:
            print(f"     ⚠️ Could not get public key for environment '{env_name}': {key_response.status_code}")
            return
        
        key_data = key_response.json()
        public_key = key_data['key']
        key_id = key_data['key_id']
        
        # Get existing environment secrets (names only)
        secrets_url = f"{self.base_url}/repos/{config.owner}/{config.name}/environments/{env_name}/secrets"
        response = requests.get(secrets_url, headers=self.headers)
        
        existing_secrets = set()
        if response.status_code == 200:
            secrets_data = response.json()
            existing_secrets = {secret['name'] for secret in secrets_data.get('secrets', [])}
            print(f"     📋 Found {len(existing_secrets)} existing secrets in '{env_name}'")
        elif response.status_code == 404:
            print(f"     📋 No existing secrets in '{env_name}'")
        else:
            print(f"     ⚠️ Could not fetch secrets for '{env_name}': {response.status_code}")
        
        # Create/update secrets
        secrets_created = 0
        secrets_updated = 0
        
        for secret_name, secret_value in secrets.items():
            # Encrypt the secret value
            encrypted_value = self._encrypt_secret(public_key, secret_value)
            
            secret_url = f"{self.base_url}/repos/{config.owner}/{config.name}/environments/{env_name}/secrets/{secret_name}"
            secret_data = {
                "encrypted_value": encrypted_value,
                "key_id": key_id
            }
            
            response = requests.put(secret_url, json=secret_data, headers=self.headers)
            
            if response.status_code in [201, 204]:
                if secret_name in existing_secrets:
                    print(f"     🔄 Updated secret '{secret_name}' in '{env_name}'")
                    secrets_updated += 1
                else:
                    print(f"     ➕ Created secret '{secret_name}' in '{env_name}'")
                    secrets_created += 1
            else:
                print(f"     ⚠️ Could not set secret '{secret_name}' in '{env_name}': {response.status_code}")
    
    def _check_and_create_variables(self, config: RepoConfig):
        """Check existing variables and create/update as needed"""
        if not config.variables:
            return
            
        # Get existing variables
        url = f"{self.base_url}/repos/{config.owner}/{config.name}/actions/variables"
        response = requests.get(url, headers=self.headers)
        
        existing_variables = {}
        if response.status_code == 200:
            variables_data = response.json()
            existing_variables = {var['name']: var['value'] for var in variables_data.get('variables', [])}
            if existing_variables:
                print(f"📋 Found {len(existing_variables)} existing variables")
        
        variables_to_update = []
        variables_to_create = []
        unchanged_count = 0
        
        for key, value in config.variables.items():
            if key in existing_variables:
                if existing_variables[key] != str(value):
                    variables_to_update.append((key, value))
                    print(f"🔄 Will update variable {key}: '{existing_variables[key]}' → '{value}'")
                else:
                    unchanged_count += 1
            else:
                variables_to_create.append((key, value))
                print(f"➕ Will add variable {key}: '{value}'")
        
        if unchanged_count > 0:
            print(f"✅ {unchanged_count} variables already up to date")
        
        # Create new variables
        for key, value in variables_to_create:
            create_url = f"{self.base_url}/repos/{config.owner}/{config.name}/actions/variables"
            data = {"name": key, "value": str(value)}
            
            response = requests.post(create_url, json=data, headers=self.headers)
            if response.status_code in [200, 201]:
                print(f"   ✅ Created variable: {key}")
            else:
                print(f"   ⚠️ Could not create variable {key}: {response.json() if response.content else 'No response'}")
        
        # Update existing variables
        for key, value in variables_to_update:
            update_url = f"{self.base_url}/repos/{config.owner}/{config.name}/actions/variables/{key}"
            data = {"name": key, "value": str(value)}
            
            response = requests.patch(update_url, json=data, headers=self.headers)
            if response.status_code in [200, 204]:
                print(f"   ✅ Updated variable: {key}")
            else:
                print(f"   ⚠️ Could not update variable {key}: {response.json() if response.content else 'No response'}")
    
    def _get_public_key(self, config: RepoConfig) -> Optional[Dict]:
        """Get repository public key for secret encryption"""
        url = f"{self.base_url}/repos/{config.owner}/{config.name}/actions/secrets/public-key"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def _encrypt_secret(self, public_key: str, secret_value: str) -> str:
        """Encrypt a secret using the repository's public key"""
        public_key_obj = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
        box = public.SealedBox(public_key_obj)
        encrypted = box.encrypt(secret_value.encode("utf-8"))
        return base64.b64encode(encrypted).decode("utf-8")
    
    def _check_and_create_secrets(self, config: RepoConfig):
        """Check existing secrets and create/update as needed"""
        if not config.secrets:
            return
            
        # Get existing secrets (GitHub API doesn't return secret values, only names)
        url = f"{self.base_url}/repos/{config.owner}/{config.name}/actions/secrets"
        response = requests.get(url, headers=self.headers)
        
        existing_secrets = set()
        if response.status_code == 200:
            secrets_data = response.json()
            existing_secrets = {secret['name'] for secret in secrets_data.get('secrets', [])}
            if existing_secrets:
                print(f"📋 Found {len(existing_secrets)} existing secrets")
        
        secrets_to_create = set(config.secrets.keys()) - existing_secrets
        secrets_to_update = set(config.secrets.keys()) & existing_secrets
        
        if secrets_to_update:
            print(f"🔄 Will update {len(secrets_to_update)} existing secrets: {', '.join(secrets_to_update)}")
        
        if secrets_to_create:
            print(f"➕ Will create {len(secrets_to_create)} new secrets: {', '.join(secrets_to_create)}")
        
        if not secrets_to_create and not secrets_to_update:
            print("✅ All secrets are already up to date")
            return
        
        # Get the public key for encryption
        public_key_data = self._get_public_key(config)
        if not public_key_data:
            raise Exception("Could not retrieve repository public key")
        
        public_key = public_key_data["key"]
        key_id = public_key_data["key_id"]
        
        # Create/update secrets
        all_secrets = secrets_to_create | secrets_to_update
        for key in all_secrets:
            value = config.secrets[key]
            
            # Encrypt the secret
            encrypted_value = self._encrypt_secret(public_key, value)
            
            secret_url = f"{self.base_url}/repos/{config.owner}/{config.name}/actions/secrets/{key}"
            data = {
                "encrypted_value": encrypted_value,
                "key_id": key_id
            }
            
            response = requests.put(secret_url, json=data, headers=self.headers)
            if response.status_code in [200, 201, 204]:
                action = "Updated" if key in secrets_to_update else "Created"
                print(f"   ✅ {action} secret: {key}")
            else:
                print(f"   ⚠️ Could not create/update secret {key}: {response.json() if response.content else 'No response'}")
    
    def _create_secrets(self, config: RepoConfig):
        """Legacy method - redirects to intelligent checking"""
        self._check_and_create_secrets(config)
    
    def _setup_repository_access(self, config: RepoConfig):
        """Set up team and user access to the repository"""
        
        # Set up team access
        if config.team_access:
            print("🏢 Checking team access...")
            self._manage_team_access(config)
        
        # Set up user access
        if config.user_access:
            print("👤 Checking user access...")
            self._manage_user_access(config)
            
        if not config.team_access and not config.user_access:
            print("ℹ️ No team or user access configurations specified")
    
    def _manage_team_access(self, config: RepoConfig):
        """Manage team access to the repository"""
        # First, let's list available teams for debugging
        self._list_available_teams(config)
        
        # Get existing team permissions
        existing_teams = self._get_existing_team_permissions(config)
        
        teams_to_update = []
        teams_to_add = []
        unchanged_count = 0
        
        for team_slug, permission in config.team_access.items():
            current_permission = existing_teams.get(team_slug)
            
            if current_permission != permission:
                if current_permission:
                    teams_to_update.append((team_slug, permission, current_permission))
                    print(f"🔄 Will update team {team_slug}: '{current_permission}' → '{permission}'")
                else:
                    teams_to_add.append((team_slug, permission))
                    print(f"➕ Will add team {team_slug}: '{permission}'")
            else:
                unchanged_count += 1
        
        if unchanged_count > 0:
            print(f"✅ {unchanged_count} team permissions already up to date")
        
        # Apply team permissions
        # Create new teams
        for team_slug, permission in teams_to_add:
            self._set_team_permission(config, team_slug, permission)
        
        # Update existing teams
        for team_slug, permission, _ in teams_to_update:
            self._set_team_permission(config, team_slug, permission)
    
    def _manage_user_access(self, config: RepoConfig):
        """Manage user access to the repository"""
        # Get existing collaborators
        existing_collaborators = self._get_existing_collaborators(config)
        
        users_to_update = []
        users_to_add = []
        unchanged_count = 0
        
        for username, permission in config.user_access.items():
            current_permission = existing_collaborators.get(username)
            
            if current_permission != permission:
                if current_permission:
                    users_to_update.append((username, permission, current_permission))
                    print(f"🔄 Will update user {username}: '{current_permission}' → '{permission}'")
                else:
                    users_to_add.append((username, permission))
                    print(f"➕ Will add user {username}: '{permission}'")
            else:
                unchanged_count += 1
        
        if unchanged_count > 0:
            print(f"✅ {unchanged_count} user permissions already up to date")
        
        # Apply user permissions
        # Create new users
        for username, permission in users_to_add:
            self._set_user_permission(config, username, permission)
        
        # Update existing users
        for username, permission, _ in users_to_update:
            self._set_user_permission(config, username, permission)
    
    def _get_existing_team_permissions(self, config: RepoConfig) -> Dict[str, str]:
        """Get existing team permissions for the repository"""
        url = f"{self.base_url}/repos/{config.owner}/{config.name}/teams"
        response = requests.get(url, headers=self.headers)
        
        existing_teams = {}
        if response.status_code == 200:
            teams_data = response.json()
            for team in teams_data:
                team_slug = team.get('slug', team.get('name', ''))
                permission = team.get('permission', 'read')
                existing_teams[team_slug] = permission
            
            if existing_teams:
                print(f"📋 Found {len(existing_teams)} existing team permissions")
        
        return existing_teams
    
    def _get_existing_collaborators(self, config: RepoConfig) -> Dict[str, str]:
        """Get existing collaborators for the repository"""
        url = f"{self.base_url}/repos/{config.owner}/{config.name}/collaborators"
        response = requests.get(url, headers=self.headers)
        
        existing_collaborators = {}
        if response.status_code == 200:
            collaborators_data = response.json()
            for collaborator in collaborators_data:
                username = collaborator.get('login', '')
                # Note: GitHub API doesn't always return permission level in collaborators list
                # We'll need to check individual permission
                if username:
                    perm_response = requests.get(
                        f"{self.base_url}/repos/{config.owner}/{config.name}/collaborators/{username}/permission",
                        headers=self.headers
                    )
                    if perm_response.status_code == 200:
                        perm_data = perm_response.json()
                        permission = perm_data.get('permission', 'read')
                        existing_collaborators[username] = permission
            
            if existing_collaborators:
                print(f"📋 Found {len(existing_collaborators)} existing collaborators")
        
        return existing_collaborators
    
    def _set_team_permission(self, config: RepoConfig, team_slug: str, permission: str):
        """Set team permission for the repository"""
        # First, validate that the team exists and get its correct slug
        validated_slug = self._validate_and_get_team_slug(config, team_slug)
        if not validated_slug:
            print(f"   ⚠️ Team '{team_slug}' not found in organization '{config.owner}'")
            return
        
        url = f"{self.base_url}/orgs/{config.owner}/teams/{validated_slug}/repos/{config.owner}/{config.name}"
        
        data = {"permission": permission}
        
        response = requests.put(url, json=data, headers=self.headers)
        if response.status_code in [200, 204]:
            print(f"   ✅ Set team {validated_slug} permission to: {permission}")
        else:
            error_data = response.json() if response.content else {}
            error_msg = error_data.get('message', 'Unknown error')
            print(f"   ⚠️ Could not set team {validated_slug} permission: {error_msg}")
            
            # Provide helpful debugging info
            if response.status_code == 422:
                print(f"      💡 Possible issues:")
                print(f"      - Team '{validated_slug}' might not have access to create repositories")
                print(f"      - Invalid permission level '{permission}' (valid: read, triage, write, maintain, admin)")
                print(f"      - Repository might not be accessible to the team")
            elif response.status_code == 404:
                print(f"      💡 Team '{validated_slug}' or repository not found")
            elif response.status_code == 403:
                print(f"      💡 Insufficient permissions to manage team repository access")
    
    def _validate_and_get_team_slug(self, config: RepoConfig, team_identifier: str) -> Optional[str]:
        """Validate team exists and return correct slug"""
        # Try to get team by slug first
        url = f"{self.base_url}/orgs/{config.owner}/teams/{team_identifier}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            team_data = response.json()
            return team_data.get('slug', team_identifier)
        
        # If slug doesn't work, search teams by name
        teams_url = f"{self.base_url}/orgs/{config.owner}/teams"
        teams_response = requests.get(teams_url, headers=self.headers)
        
        if teams_response.status_code == 200:
            teams = teams_response.json()
            for team in teams:
                # Check if team name or slug matches
                if (team.get('name', '').lower() == team_identifier.lower() or 
                    team.get('slug', '') == team_identifier):
                    return team.get('slug')
        
        return None
    
    def _list_available_teams(self, config: RepoConfig):
        """List available teams in the organization for debugging"""
        teams_url = f"{self.base_url}/orgs/{config.owner}/teams"
        response = requests.get(teams_url, headers=self.headers)
        
        if response.status_code == 200:
            teams = response.json()
            print(f"🔍 Found {len(teams)} teams in organization '{config.owner}':")
            for team in teams[:10]:  # Show first 10 teams
                name = team.get('name', 'Unknown')
                slug = team.get('slug', 'Unknown')
                print(f"     • {name} (slug: {slug})")
            
            if len(teams) > 10:
                print(f"     ... and {len(teams) - 10} more teams")
        else:
            print(f"⚠️ Could not list teams: {response.status_code}")
    
    def _set_user_permission(self, config: RepoConfig, username: str, permission: str):
        """Set user permission for the repository"""
        url = f"{self.base_url}/repos/{config.owner}/{config.name}/collaborators/{username}"
        
        data = {"permission": permission}
        
        response = requests.put(url, json=data, headers=self.headers)
        if response.status_code in [200, 201, 204]:
            print(f"   ✅ Set user {username} permission to: {permission}")
        else:
            print(f"   ⚠️ Could not set user {username} permission: {response.json() if response.content else 'No response'}")


def load_config_from_file(config_file: str) -> RepoConfig:
    """Load repository configuration from a JSON file"""
    with open(config_file, 'r') as f:
        data = json.load(f)
    
    repo_data = data.get("repository", {})
    custom_props = data.get("custom_properties", {})
    files_data = data.get("files", {})
    branch_protection = data.get("branch_protection", {})
    
    # Handle visibility with backward compatibility
    visibility = repo_data.get("visibility", "internal")
    if "private" in repo_data and "visibility" not in repo_data:
        # Backward compatibility: convert private boolean to visibility
        visibility = "private" if repo_data.get("private", True) else "public"
    
    # Handle new branch protection structure vs legacy
    branch_protection_rules = None
    enable_branch_protection = False
    protected_branch = "main"
    
    if "branches" in branch_protection:
        # New multi-branch structure
        branch_protection_rules = branch_protection["branches"]
        auto_create_branches = branch_protection.get("auto_create_branches", True)
    else:
        # Legacy single-branch structure
        enable_branch_protection = branch_protection.get("enable", False)
        protected_branch = branch_protection.get("protected_branch", "main")
        auto_create_branches = True  # Default to True for backward compatibility
    
    return RepoConfig(
        name=repo_data.get("name", ""),
        owner=repo_data.get("owner", ""),
        description=repo_data.get("description", ""),
        visibility=visibility,
        
        application=custom_props.get("application", ""),
        compliance_audit_to_review=custom_props.get("compliance_audit_to_review", ""),
        deployed_to_prod=custom_props.get("deployed_to_prod", ""),
        impact_on_prod_app=custom_props.get("impact_on_prod_app", ""),
        poc=custom_props.get("poc", ""),
        repo_owner=custom_props.get("owner", ""),
        prod_deployment_method=custom_props.get("prod_deployment_method", ""),
        team=custom_props.get("team", ""),
        
        readme_content=files_data.get("readme_content", ""),
        gitignore_template=files_data.get("gitignore_template", "Python"),
        
        # Legacy branch protection (backward compatibility)
        enable_branch_protection=enable_branch_protection,
        protected_branch=protected_branch,
        require_reviews=branch_protection.get("require_reviews", True),
        required_reviews=branch_protection.get("required_reviews", 2),
        dismiss_stale_reviews=branch_protection.get("dismiss_stale_reviews", True),
        require_code_owner_reviews=branch_protection.get("require_code_owner_reviews", True),
        
        # New multi-branch protection
        branch_protection_rules=branch_protection_rules,
        auto_create_branches=auto_create_branches,
        
        environments=data.get("environments", []),
        secrets=data.get("secrets", {}),
        variables=data.get("variables", {}),
        environment_secrets=data.get("environment_secrets", {}),
        environment_variables=data.get("environment_variables", {}),
        environment_protection=data.get("environment_protection", {}),
        team_access=data.get("team_access", {}),
        user_access=data.get("user_access", {})
    )


def create_repository_from_config():
    """Main function to create repository with interactive input"""
    print("GitHub Repository Creator")
    print("=" * 40)
    
    # Check if user wants to use config file
    use_config_file = input("Do you want to use a configuration file? (y/n): ").strip().lower() == 'y'
    
    if use_config_file:
        config_file = input("Enter path to configuration file (default: config_template.json): ").strip()
        if not config_file:
            config_file = "config_template.json"
        
        try:
            config = load_config_from_file(config_file)
            print(f"✓ Configuration loaded from {config_file}")
        except FileNotFoundError:
            print(f"❌ Configuration file {config_file} not found")
            return
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in configuration file: {e}")
            return
    else:
        # Interactive input
        config = get_interactive_config()
    
    # Get GitHub token
    token = input("Enter your GitHub token: ").strip()
    if not token:
        print("Error: GitHub token is required")
        return
    
    # Option to force organization mode
    if config.owner and config.owner != "":
        force_org = input(f"Force organization mode for '{config.owner}'? (y/n, default: auto-detect): ").strip().lower()
        if force_org == 'y':
            print(f"🔧 Forcing organization mode for '{config.owner}'")
            # Override the organization detection
            original_is_org = GitHubRepoManager._is_organization
            GitHubRepoManager._is_organization = lambda self, owner: True
    
    # Create repository
    manager = GitHubRepoManager(token)
    result = manager.create_repository(config)
    
    if result["success"]:
        print(f"\n✅ {result['message']}")
        print(f"🔗 Repository URL: {result['repository_url']}")
    else:
        print(f"\n❌ Error: {result['error']}")


def get_interactive_config() -> RepoConfig:
    """Get repository configuration through interactive input"""
    # Basic repository info
    name = input("Repository name: ").strip()
    owner = input("Owner (organization/username): ").strip()
    description = input("Description: ").strip()
    
    # Repository visibility
    print("\nRepository visibility options:")
    print("1. public    - Visible to everyone")
    print("2. internal  - Visible to organization members (default)")
    print("3. private   - Visible only to collaborators")
    visibility_choice = input("Choose visibility (1-3, default: 2): ").strip()
    
    visibility_map = {"1": "public", "2": "internal", "3": "private"}
    visibility = visibility_map.get(visibility_choice, "internal")
    
    # Custom properties
    print("\nCustom Properties:")
    application = input("Application: ").strip()
    compliance_audit = input("Compliance Audit to Review: ").strip()
    deployed_to_prod = input("Deployed to Prod: ").strip()
    impact_on_prod = input("Impact on Prod App: ").strip()
    poc = input("POC: ").strip()
    repo_owner = input("Owner: ").strip()
    deployment_method = input("Prod Deployment Method: ").strip()
    team = input("Team: ").strip()
    
    # README content
    readme_content = input("README content (press Enter for auto-generated): ").strip()
    
    # .gitignore template
    gitignore = input("Gitignore template (default: Python): ").strip() or "Python"
    
    # Branch protection
    enable_protection = input("Enable branch protection? (y/n): ").strip().lower() == 'y'
    
    # Environments
    environments_input = input("Environments (comma-separated, optional): ").strip()
    environments = [env.strip() for env in environments_input.split(',')] if environments_input else []
    
    # Secrets and variables
    secrets = {}
    variables = {}
    
    add_secrets = input("Add secrets? (y/n): ").strip().lower() == 'y'
    if add_secrets:
        while True:
            secret_name = input("Secret name (press Enter to finish): ").strip()
            if not secret_name:
                break
            secret_value = input(f"Secret value for {secret_name}: ").strip()
            secrets[secret_name] = secret_value
    
    add_variables = input("Add variables? (y/n): ").strip().lower() == 'y'
    if add_variables:
        while True:
            var_name = input("Variable name (press Enter to finish): ").strip()
            if not var_name:
                break
            var_value = input(f"Variable value for {var_name}: ").strip()
            variables[var_name] = var_value
    
    # Team and user access
    team_access = {}
    user_access = {}
    
    print("\nTeam Access (permissions: read, triage, write, maintain, admin)")
    add_teams = input("Add team access? (y/n): ").strip().lower() == 'y'
    if add_teams:
        while True:
            team_name = input("Team name/slug (press Enter to finish): ").strip()
            if not team_name:
                break
            permission = input(f"Permission for team {team_name} (read/write/admin): ").strip().lower()
            if permission in ['read', 'triage', 'write', 'maintain', 'admin']:
                team_access[team_name] = permission
            else:
                print("Invalid permission. Using 'read' as default.")
                team_access[team_name] = 'read'
    
    print("\nUser Access (permissions: read, triage, write, maintain, admin)")
    add_users = input("Add user access? (y/n): ").strip().lower() == 'y'
    if add_users:
        while True:
            username = input("Username (press Enter to finish): ").strip()
            if not username:
                break
            permission = input(f"Permission for user {username} (read/write/admin): ").strip().lower()
            if permission in ['read', 'triage', 'write', 'maintain', 'admin']:
                user_access[username] = permission
            else:
                print("Invalid permission. Using 'read' as default.")
                user_access[username] = 'read'
    
    return RepoConfig(
        name=name,
        owner=owner,
        description=description,
        visibility=visibility,
        application=application,
        compliance_audit_to_review=compliance_audit,
        deployed_to_prod=deployed_to_prod,
        impact_on_prod_app=impact_on_prod,
        poc=poc,
        repo_owner=repo_owner,
        prod_deployment_method=deployment_method,
        team=team,
        readme_content=readme_content,
        gitignore_template=gitignore,
        enable_branch_protection=enable_protection,
        environments=environments,
        secrets=secrets,
        variables=variables,
        team_access=team_access,
        user_access=user_access
    )


def create_config_template():
    """Create a configuration template file"""
    template = {
        "repository": {
            "name": "my-project",
            "owner": "vsbopi",
            "description": "Description of my project",
            "visibility": "internal"
        },
        "custom_properties": {
            "application": "MyApplication",
            "compliance_audit_to_review": "Yes",
            "deployed_to_prod": "Yes",
            "impact_on_prod_app": "High",
            "poc": "john.doe@company.com",
            "owner": "Development Team",
            "prod_deployment_method": "GitOps",
            "team": "Platform Engineering"
        },
        "files": {
            "readme_content": "",
            "gitignore_template": "Python"
        },
        "branch_protection": {
            "enable": True,
            "protected_branch": "main",
            "require_reviews": True,
            "required_reviews": 2,
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": True
        },
        "environments": [
            "development",
            "staging",
            "production"
        ],
        "secrets": {
            "API_KEY": "your-secret-api-key",
            "DATABASE_PASSWORD": "your-database-password"
        },
        "variables": {
            "NODE_ENV": "production",
            "APP_VERSION": "1.0.0",
            "DEPLOYMENT_REGION": "us-east-1"
        },
        "team_access": {
            "backend-team": "write",
            "devops-team": "admin",
            "qa-team": "read"
        },
        "user_access": {
            "john.doe": "write",
            "jane.smith": "admin"
        }
    }
    
    with open("config_template.json", "w") as f:
        json.dump(template, f, indent=2)
    
    print("✓ Configuration template created: config_template.json")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "create-template":
        create_config_template()
    else:
        create_repository_from_config()
