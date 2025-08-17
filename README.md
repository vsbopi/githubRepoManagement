# GitHub Repository Management Tool

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)

A comprehensive Python tool for creating and managing GitHub repositories with full automation, including custom properties, branch protection, environments, secrets, variables, and team access management.

## 🚀 Features

### 🏗️ **Repository Creation & Management**
- ✅ **Auto Repository Creation** - Create repositories in organizations or personal accounts
- ✅ **Intelligent Updates** - Idempotent operations (safe to run multiple times)
- ✅ **Visibility Control** - Public, private, or internal repositories
- ✅ **Organization Support** - Full organization and personal account support

### 🏷️ **Custom Properties & Metadata**
- ✅ **Application Tracking** - Map applications to repositories
- ✅ **Compliance Management** - Track compliance audit requirements
- ✅ **Production Status** - Monitor production deployment status
- ✅ **Team Assignment** - Associate repositories with teams
- ✅ **POC Management** - Point of contact tracking
- ✅ **Deployment Methods** - Track how applications are deployed

### 📁 **File Management**
- ✅ **Auto-Generated README** - README with all custom properties
- ✅ **Custom README Support** - Use your own README content
- ✅ **Smart .gitignore** - Template-based or custom .gitignore files
- ✅ **Language Templates** - Python, Node.js, Java, Go, C#, and more

### 🔒 **Branch Protection**
- ✅ **Multi-Branch Protection** - Protect multiple branches with different rules
- ✅ **Review Requirements** - Configurable reviewer count
- ✅ **Code Owner Reviews** - Require code owner approval
- ✅ **Stale Review Dismissal** - Auto-dismiss outdated reviews
- ✅ **Admin Enforcement** - Apply rules to administrators
- ✅ **Status Checks** - Require specific status checks

### 🌍 **Environment Management**
- ✅ **Multiple Environments** - Development, staging, production, and custom environments
- ✅ **Environment Protection** - Deployment approval workflows
- ✅ **Branch Policies** - Control which branches can deploy to each environment
- ✅ **Custom Reviewers** - Team and user reviewers per environment
- ✅ **Wait Timers** - Deployment delays for safety
- ✅ **Self-Review Prevention** - Block self-approvals

### 🔐 **Secrets & Variables**
- ✅ **Encrypted Secrets** - Secure secret storage using GitHub's encryption
- ✅ **Repository Variables** - Plain-text configuration variables
- ✅ **Environment-Specific** - Different secrets/variables per environment
- ✅ **GitHub Actions Ready** - Accessible in CI/CD workflows

### 👥 **Access Management**
- ✅ **Team Access** - Assign teams with specific permission levels
- ✅ **User Access** - Add individual collaborators
- ✅ **Permission Levels** - Read, triage, write, maintain, admin
- ✅ **Smart Updates** - Only changes what's different

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- GitHub account with appropriate permissions
- GitHub Personal Access Token

### Dependencies
```bash
pip install -r requirements.txt
```

**Required packages:**
- `requests>=2.31.0` - HTTP library for GitHub API calls
- `PyNaCl>=1.5.0` - Encryption library for secrets

### Quick Setup
```bash
# Clone the repository
git clone <repository-url>
cd githubRepoManagement

# Install dependencies
pip install -r requirements.txt

# Test setup
python test_setup.py

# Create configuration template
python main.py create-template
```

## 🎯 Quick Start

### Method 1: Interactive Mode (Beginner-Friendly)
```bash
python main.py
```
Follow the step-by-step prompts to configure your repository.

### Method 2: Configuration File (Recommended)
```bash
# 1. Generate template
python main.py create-template

# 2. Edit config_template.json with your values
# 3. Run with configuration
python main.py
# Choose "y" when asked about using a configuration file
```

### Method 3: Command Line (Quick Creation)
```bash
python create_repo.py \
  --name "my-awesome-api" \
  --owner "vsbopi" \
  --description "My awesome REST API" \
  --application "MyAPI" \
  --team "Backend Team" \
  --poc "backend-team@company.com" \
  --branch-protection \
  --environments "dev,staging,prod"
```

### Method 4: Pre-built Examples
```bash
python examples.py simple_api
# or interactively:
python examples.py
```

## ⚙️ Configuration

### Complete Configuration Example
```json
{
  "repository": {
    "name": "customer-service",
    "owner": "vsbopi",
    "description": "Customer management microservice",
    "visibility": "internal"
  },
  "custom_properties": {
    "application": "CustomerService",
    "compliance_audit_to_review": "Yes",
    "deployed_to_prod": "Yes",
    "impact_on_prod_app": "High",
    "poc": "backend-team@company.com",
    "owner": "Backend Team",
    "prod_deployment_method": "Kubernetes",
    "team": "Backend Team"
  },
  "files": {
    "readme_content": "",
    "gitignore_template": "Python"
  },
  "branch_protection": {
    "auto_create_branches": true,
    "branches": {
      "main": {
        "enable": true,
        "require_reviews": true,
        "required_reviews": 2,
        "dismiss_stale_reviews": true,
        "require_code_owner_reviews": true,
        "enforce_admins": true,
        "require_status_checks": false,
        "status_checks": []
      },
      "develop": {
        "enable": true,
        "require_reviews": true,
        "required_reviews": 1,
        "dismiss_stale_reviews": false,
        "require_code_owner_reviews": false,
        "enforce_admins": false
      }
    }
  },
  "environments": ["dev", "staging", "prod"],
  "environment_protection": {
    "dev": {
      "wait_timer": 0,
      "prevent_self_review": false,
      "deployment_branch_policy": {
        "protected_branches": false,
        "custom_branch_policies": false
      },
      "reviewers": []
    },
    "staging": {
      "wait_timer": 5,
      "prevent_self_review": true,
      "deployment_branch_policy": {
        "protected_branches": true,
        "custom_branch_policies": false
      },
      "reviewers": [
        {"type": "Team", "id": "vsbopi/qa-team"}
      ]
    },
    "prod": {
      "wait_timer": 10,
      "prevent_self_review": true,
      "deployment_branch_policy": {
        "protected_branches": false,
        "custom_branch_policies": true,
        "custom_branches": ["main", "prod"]
      },
      "reviewers": [
        {"type": "Team", "id": "vsbopi/prod-approvers"},
        {"type": "User", "id": "deployment-manager"}
      ]
    }
  },
  "secrets": {
    "DATABASE_URL": "postgresql://user:pass@host:5432/db",
    "API_KEY": "secret-api-key",
    "JWT_SECRET": "jwt-signing-secret"
  },
  "variables": {
    "NODE_ENV": "production",
    "LOG_LEVEL": "info",
    "REGION": "us-east-1"
  },
  "environment_secrets": {
    "dev": {
      "DATABASE_URL": "postgresql://dev-host:5432/dev_db"
    },
    "prod": {
      "DATABASE_URL": "postgresql://prod-host:5432/prod_db"
    }
  },
  "environment_variables": {
    "dev": {
      "ENVIRONMENT": "development",
      "DEBUG": "true"
    },
    "staging": {
      "ENVIRONMENT": "staging",
      "DEBUG": "false"
    },
    "prod": {
      "ENVIRONMENT": "production",
      "DEBUG": "false"
    }
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
```

### Environment-Specific Configuration

#### Development Environment
```json
"dev": {
  "wait_timer": 0,
  "prevent_self_review": false,
  "deployment_branch_policy": {
    "protected_branches": false,
    "custom_branch_policies": false
  },
  "reviewers": []
}
```

#### Production Environment
```json
"prod": {
  "wait_timer": 10,
  "prevent_self_review": true,
  "deployment_branch_policy": {
    "protected_branches": false,
    "custom_branch_policies": true,
    "custom_branches": ["main", "prod", "release/*"]
  },
  "reviewers": [
    {"type": "Team", "id": "vsbopi/prod-approvers"},
    {"type": "User", "id": "release-manager"}
  ]
}
```

## 🔧 Command Line Reference

### create_repo.py Options

#### Required Arguments
```bash
--name REPO_NAME              # Repository name
--owner OWNER                 # Repository owner/organization  
--description DESC             # Repository description
```

#### Repository Settings
```bash
--visibility public|internal|private  # Repository visibility
--private                     # Make private (legacy)
--public                      # Make public (legacy)
```

#### Custom Properties
```bash
--application APP_NAME        # Application name
--compliance-audit STATUS     # Compliance audit status (Yes/No)
--deployed-to-prod STATUS     # Production deployment status (Yes/No)
--impact-on-prod LEVEL        # Production impact level (High/Medium/Low)
--poc EMAIL                   # Point of contact email
--repo-owner OWNER            # Repository owner/team
--deployment-method METHOD    # Deployment method (Kubernetes/GitOps/etc)
--team TEAM_NAME              # Responsible team name
```

#### Files & Content
```bash
--gitignore TEMPLATE          # Gitignore template (Python/Node/Java/etc)
--readme FILE_PATH            # Path to README content file
```

#### Branch Protection
```bash
--branch-protection           # Enable branch protection
--reviews COUNT               # Required reviews (default: 2)
```

#### Environments & Access
```bash
--environments ENV_LIST       # Comma-separated environments (dev,staging,prod)
--team-access TEAMS           # team1:permission1,team2:permission2
--user-access USERS           # user1:permission1,user2:permission2
```

#### Authentication
```bash
--token TOKEN                 # GitHub token (or use GITHUB_TOKEN env var)
--force-org                   # Force organization mode
```

### Examples

#### Simple Project
```bash
python create_repo.py \
  --name "simple-project" \
  --owner "vsbopi" \
  --description "A simple project"
```

#### Production Application
```bash
python create_repo.py \
  --name "customer-portal" \
  --owner "vsbopi" \
  --description "Customer web portal" \
  --application "CustomerPortal" \
  --team "Frontend Team" \
  --poc "frontend@company.com" \
  --deployed-to-prod "Yes" \
  --impact-on-prod "High" \
  --branch-protection \
  --reviews 3 \
  --environments "dev,staging,prod" \
  --gitignore "Node" \
  --team-access "frontend-team:write,devops:admin" \
  --user-access "tech-lead:admin"
```

#### Microservice with Full Configuration
```bash
python create_repo.py \
  --name "payment-service" \
  --owner "vsbopi" \
  --description "Payment processing microservice" \
  --application "PaymentService" \
  --team "Backend Team" \
  --poc "backend@company.com" \
  --compliance-audit "Yes" \
  --deployed-to-prod "Yes" \
  --impact-on-prod "Critical" \
  --deployment-method "Kubernetes" \
  --branch-protection \
  --reviews 2 \
  --environments "dev,test,staging,prod" \
  --gitignore "Java" \
  --team-access "backend-team:write,security-team:read"
```

## 🔐 Authentication & Permissions

### GitHub Token Setup

1. **Generate Personal Access Token**:
   - Go to GitHub Settings > Developer settings > Personal access tokens
   - Click "Generate new token (classic)"
   - Select required scopes (see below)

2. **Required Token Scopes**:
   - `repo` - Full control of repositories
   - `admin:org` - Organization administration (for org repositories)

3. **Set Environment Variable** (recommended):
   ```bash
   export GITHUB_TOKEN="ghp_your_token_here"
   ```

### Token Diagnostic Tool
```bash
python diagnose_token.py
```
This tool will test your token permissions and organization access.

### Organization Permissions
- Must be a member of the target organization
- Organization must allow repository creation by members
- Token must have appropriate organization permissions

## 🧪 Testing & Validation

### Setup Validation
```bash
python test_setup.py
```
This validates:
- ✅ All dependencies are installed
- ✅ Configuration files are valid JSON
- ✅ All classes and methods are importable
- ✅ Core functionality works

### Team Diagnostic
```bash
python diagnose_teams.py
```
This tests team access and validation.

### Manual Testing
```bash
# Test with a simple repository
python create_repo.py \
  --name "test-repo-$(date +%s)" \
  --owner "your-org" \
  --description "Test repository" \
  --team "Test Team"
```

## 📁 Project Structure

```
gitRepoManagement/
├── main.py                                    # Main application with GitHubRepoManager class
├── create_repo.py                             # Command-line interface for quick repo creation
├── examples.py                                # Pre-built repository templates
├── test_setup.py                              # Setup validation and testing script
├── diagnose_token.py                          # GitHub token diagnostic tool
├── diagnose_teams.py                          # Team access diagnostic tool
├── requirements.txt                           # Python dependencies
├── README.md                                  # This comprehensive documentation
├── config_template.json                       # JSON configuration template
├── config_template_structure.json             # Example configuration
└── __pycache__/                               # Python cache directory
```

## 🎨 Pre-built Templates

### Available Templates

#### Simple API
```bash
python examples.py simple_api
```
Basic REST API service with standard configuration.

#### Frontend Application
```bash
python examples.py frontend_app
```
Customer-facing web portal with Node.js setup.

#### Microservice
```bash
python examples.py microservice
```
Production-ready microservice with Java/Spring Boot.

#### Data Pipeline
```bash
python examples.py data_pipeline
```
Data analytics pipeline with Python/Spark configuration.

### Custom Templates
You can extend `examples.py` to add your own templates:

```python
EXAMPLES["my_template"] = {
    "name": "my-service",
    "owner": "vsbopi",
    "description": "My custom service",
    "application": "MyService",
    "team": "My Team",
    # ... additional configuration
}
```

## 🔄 Intelligent Features

### Repository Existence Check
- Automatically detects if repository already exists
- Skips creation and proceeds to configuration updates
- Safe to run multiple times (idempotent)

### Smart Configuration Updates
- Compares existing vs desired configuration
- Only updates changed items
- Preserves existing settings not specified in configuration

### Custom Properties Management
- Supports GitHub's new custom properties API
- Falls back to repository topics if custom properties unavailable
- Intelligent property comparison and updates

### Branch Protection Intelligence
- Compares existing protection rules with desired configuration
- Only updates rules that have changed
- Supports multiple branch protection patterns

### Environment Protection
- Smart environment creation and updates
- Deployment branch policy management
- Team and user reviewer validation

## 🚨 Troubleshooting

### Common Issues

#### Token Permissions
```
Error: 403 Forbidden
```
**Solution**: Ensure token has `repo` and `admin:org` scopes.

#### Organization Access
```
Error: 404 Not Found (Organization)
```
**Solutions**:
- Verify you're a member of the organization
- Check organization name spelling
- Ensure organization allows repository creation

#### Team Not Found
```
Could not find team: team-name
```
**Solutions**:
- Verify team exists in the organization
- Check team name/slug spelling
- Ensure you have permission to view the team

#### Branch Protection Conflicts
```
"custom_branch_policies" and "protected_branches" cannot have the same value
```
**Solution**: This is fixed in the latest version. Update your code or ensure not both are `false`.

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Rate Limiting
GitHub API has rate limits:
- 5000 requests/hour for authenticated requests
- Add delays between bulk operations if needed

## 🔒 Security Best Practices

### Token Security
- ✅ Never commit tokens to code repositories
- ✅ Use environment variables for tokens
- ✅ Rotate tokens regularly
- ✅ Use minimum required scopes

### Secret Management
- ✅ Secrets are encrypted using GitHub's public key system
- ✅ Environment-specific secrets supported
- ✅ No plaintext secrets in configuration files

### Access Control
- ✅ Principle of least privilege for team/user access
- ✅ Regular access reviews recommended
- ✅ Environment-specific reviewer requirements

## 📈 Best Practices

### Configuration Management
1. **Use configuration files** for consistency across repositories
2. **Version control configurations** (without secrets)
3. **Template-based approach** for different project types
4. **Environment-specific configurations** for different deployment stages

### Repository Organization
1. **Consistent naming conventions** across repositories
2. **Meaningful descriptions** for all repositories
3. **Proper team assignments** for ownership clarity
4. **Regular compliance audits** using repository metadata

### Branch Protection Strategy
1. **Main branch protection** for all production repositories
2. **Progressive protection** (less restrictive for dev branches)
3. **Code owner requirements** for critical components
4. **Status check requirements** for automated testing

### Environment Strategy
1. **Clear environment progression** (dev → staging → prod)
2. **Environment-specific variables** for configuration
3. **Approval workflows** for production deployments
4. **Branch policies** matching environment criticality

## 🤝 Contributing

### Development Setup
```bash
git clone <repository-url>
cd gitRepoManagement
pip install -r requirements.txt
python test_setup.py
```

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints where appropriate
- Include docstrings for all public methods
- Write tests for new functionality

### Testing
```bash
# Run all tests
python test_setup.py

# Test specific functionality
python diagnose_token.py
python diagnose_teams.py
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Documentation
- **README.md** - This comprehensive guide
- **USAGE.md** - Detailed usage examples
- **PROJECT_SUMMARY.md** - Project overview
- **Feature Documentation** - Specific feature guides in respective `.md` files

### Diagnostic Tools
- `diagnose_token.py` - Token permission validation
- `diagnose_teams.py` - Team access validation
- `test_setup.py` - Complete setup validation

### Getting Help
1. **Check error messages** - They include specific guidance
2. **Run diagnostic tools** - Identify permission or configuration issues
3. **Review configuration examples** - Use working examples as templates
4. **Test with simple repositories** - Start small and build complexity

## 🎯 Use Cases

### Development Team Onboarding
Quickly create standardized repositories for new team members with consistent structure, permissions, and configurations.

### Microservices Architecture
Create multiple related services with consistent patterns, environment configurations, and deployment pipelines.

### Compliance & Audit
Track repository metadata for compliance requirements, including application ownership, deployment methods, and production impact.

### CI/CD Pipeline Setup
Automatically configure repositories with environments, secrets, and variables ready for GitHub Actions workflows.

### Organization Standardization
Enforce organization-wide repository standards including branch protection, access controls, and metadata requirements.

---

## 🚀 Getting Started Checklist

- [ ] Install Python 3.7+
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Generate GitHub token with `repo` and `admin:org` scopes
- [ ] Test setup: `python test_setup.py`
- [ ] Test token: `python diagnose_token.py`
- [ ] Create first repository: `python main.py`
- [ ] Explore examples: `python examples.py`
- [ ] Customize for your organization

**Ready to automate your GitHub repository management!** 🎉
