# Usage Guide

## Quick Start Methods

### Method 1: Interactive Mode (Recommended for first-time users)

```bash
python main.py
```

Follow the prompts to configure your repository step by step.

### Method 2: Configuration File (Recommended for automation)

1. Generate template:
   ```bash
   python main.py create-template
   ```

2. Edit `config_template.json` with your values:
   ```json
   {
     "repository": {
       "name": "my-awesome-project",
       "owner": "vsbopi",
       "description": "My project description"
     },
     "custom_properties": {
       "application": "MyApp",
       "team": "My Team",
       "poc": "me@company.com"
     }
   }
   ```

3. Run with config:
   ```bash
   python main.py
   # Choose "y" for configuration file
   ```

### Method 3: Command Line (Quick creation)

```bash
python create_repo.py \
  --name "my-api" \
  --owner "vsbopi" \
  --description "My REST API" \
  --application "MyAPI" \
  --team "Backend Team" \
  --branch-protection \
  --environments "dev,staging,prod"
```

### Method 4: Pre-built Examples

```bash
python examples.py simple_api
# or interactively:
python examples.py
```

## Configuration Options

### Repository Settings

```json
{
  "repository": {
    "name": "required-repo-name",
    "owner": "required-owner-or-org", 
    "description": "Required description",
    "private": true
  }
}
```

### Custom Properties (Your Requirements)

```json
{
  "custom_properties": {
    "application": "Application name",
    "compliance_audit_to_review": "Yes/No",
    "deployed_to_prod": "Yes/No", 
    "impact_on_prod_app": "High/Medium/Low",
    "poc": "point.of.contact@company.com",
    "owner": "Team or person responsible",
    "prod_deployment_method": "GitOps/Kubernetes/Manual/etc",
    "team": "Team name"
  }
}
```

### Files

```json
{
  "files": {
    "readme_content": "Custom README content or empty for auto-generated",
    "gitignore_template": "Python/Node/Java/Go/etc or custom content"
  }
}
```

### Branch Protection

```json
{
  "branch_protection": {
    "enable": true,
    "protected_branch": "main",
    "require_reviews": true,
    "required_reviews": 2,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true
  }
}
```

### Environments

```json
{
  "environments": [
    "development",
    "staging", 
    "production"
  ]
}
```

### Secrets & Variables

```json
{
  "secrets": {
    "API_KEY": "secret-value-here",
    "DATABASE_PASSWORD": "another-secret"
  },
  "variables": {
    "NODE_ENV": "production",
    "VERSION": "1.0.0"
  }
}
```

## Command Line Options

### create_repo.py Options

```bash
# Required
--name REPO_NAME              Repository name
--owner OWNER                 Repository owner/organization  
--description DESC             Repository description

# Repository settings
--private                     Make private (default)
--public                      Make public

# Custom properties
--application APP_NAME        Application name
--compliance-audit STATUS     Compliance audit status
--deployed-to-prod STATUS     Production deployment status
--impact-on-prod LEVEL        Production impact level
--poc EMAIL                   Point of contact
--repo-owner OWNER            Repository owner/team
--deployment-method METHOD    Deployment method
--team TEAM_NAME              Team name

# Files
--gitignore TEMPLATE          Gitignore template (default: Python)
--readme FILE_PATH            Path to README content file

# Branch protection
--branch-protection           Enable branch protection
--reviews COUNT               Required reviews (default: 2)

# Environments
--environments ENV_LIST       Comma-separated environments

# Authentication
--token TOKEN                 GitHub token (or use GITHUB_TOKEN env var)
```

### Examples

#### Simple repository:
```bash
python create_repo.py \
  --name "simple-project" \
  --owner "vsbopi" \
  --description "A simple project"
```

#### Production application:
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
  --gitignore "Node"
```

## Environment Variables

Set these for automation:

```bash
export GITHUB_TOKEN="your_github_token_here"
python create_repo.py --name "my-repo" --owner "vsbopi" --description "My repo"
```

## GitIgnore Templates

Supported templates (from GitHub):
- Python
- Node
- Java
- Go
- C++
- CSharp
- Ruby
- PHP
- Swift
- Kotlin
- Rust
- And many more...

Or provide custom content:
```json
{
  "files": {
    "gitignore_template": "*.log\n*.tmp\n.env\nnode_modules/"
  }
}
```

## Common Workflows

### 1. Development Team Onboarding

Create a new service repository for a team:

```bash
python create_repo.py \
  --name "user-service" \
  --owner "vsbopi" \
  --description "User management microservice" \
  --application "UserService" \
  --team "Backend Team" \
  --poc "backend-team@company.com" \
  --deployment-method "Kubernetes" \
  --branch-protection \
  --environments "dev,test,staging,prod"
```

### 2. Data Science Project

```bash
python create_repo.py \
  --name "customer-churn-model" \
  --owner "vsbopi" \
  --description "ML model for customer churn prediction" \
  --application "ChurnModel" \
  --team "Data Science" \
  --poc "data-science@company.com" \
  --gitignore "Python" \
  --environments "dev,staging,prod"
```

### 3. Frontend Application

```bash
python create_repo.py \
  --name "admin-dashboard" \
  --owner "vsbopi" \
  --description "Administrative dashboard" \
  --application "AdminDashboard" \
  --team "Frontend Team" \
  --poc "frontend@company.com" \
  --gitignore "Node" \
  --branch-protection \
  --reviews 2 \
  --environments "dev,staging,prod"
```

## Batch Creation

Create multiple repositories using a script:

```bash
#!/bin/bash

# Set your token
export GITHUB_TOKEN="your_token_here"

# Array of repositories to create
repos=(
  "user-service:User management service:Backend Team"
  "payment-service:Payment processing:Payments Team"
  "notification-service:Notification system:Platform Team"
)

# Create each repository
for repo in "${repos[@]}"; do
  IFS=':' read -r name desc team <<< "$repo"
  
  python create_repo.py \
    --name "$name" \
    --owner "vsbopi" \
    --description "$desc" \
    --team "$team" \
    --branch-protection \
    --environments "dev,staging,prod"
done
```

## Troubleshooting

### Common Issues

1. **Token permissions**: Ensure your token has `repo` and `admin:org` scope
2. **Organization access**: Verify you're a member of the organization
3. **Rate limiting**: GitHub API has rate limits; add delays between bulk operations
4. **Branch protection timing**: Protection is applied after repository creation

### Debug Mode

Add error logging by modifying the script:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Validation

The tool validates:
- GitHub token permissions
- Organization membership
- Repository name availability
- Required fields presence

## Best Practices

1. **Use configuration files** for consistent repository setup
2. **Set environment variables** for automation
3. **Enable branch protection** for important repositories
4. **Use descriptive names** for custom properties
5. **Test with personal repositories** before organization use
6. **Keep tokens secure** - never commit them to code
