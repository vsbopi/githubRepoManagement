# Deployment Branch Policies for GitHub Environments

This document explains how to configure deployment branch policies for GitHub environments to control which branches can deploy to specific environments.

## Configuration Options

### 1. No Restrictions (Allow Any Branch)
```json
{
  "environment_protection": {
    "dev": {
      "deployment_branch_policy": {
        "protected_branches": false,
        "custom_branch_policies": false
      }
    }
  }
}
```
- **Effect**: Any branch can deploy to this environment
- **Use Case**: Development environments where you want maximum flexibility

### 2. Protected Branches Only
```json
{
  "environment_protection": {
    "qa": {
      "deployment_branch_policy": {
        "protected_branches": true,
        "custom_branch_policies": false
      }
    }
  }
}
```
- **Effect**: Only branches with protection rules can deploy
- **Use Case**: Environments where you want only stable, reviewed branches

### 3. Custom Branch List
```json
{
  "environment_protection": {
    "prod": {
      "deployment_branch_policy": {
        "protected_branches": false,
        "custom_branch_policies": true,
        "custom_branches": ["main", "prod", "release/*"]
      }
    }
  }
}
```
- **Effect**: Only specified branches can deploy
- **Use Case**: Production environments with strict deployment controls
- **Supports**: Exact branch names and wildcard patterns (e.g., `release/*`)

## Complete Example Configuration

```json
{
  "environments": ["dev", "qa", "uat", "prod"],
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
    "qa": {
      "wait_timer": 0,
      "prevent_self_review": true,
      "deployment_branch_policy": {
        "protected_branches": true,
        "custom_branch_policies": false
      },
      "reviewers": [
        {"type": "Team", "id": "qa-team"}
      ]
    },
    "uat": {
      "wait_timer": 5,
      "prevent_self_review": true,
      "deployment_branch_policy": {
        "protected_branches": false,
        "custom_branch_policies": true,
        "custom_branches": ["main", "uat"]
      },
      "reviewers": [
        {"type": "Team", "id": "uat-approvers"}
      ]
    },
    "prod": {
      "wait_timer": 10,
      "prevent_self_review": true,
      "deployment_branch_policy": {
        "protected_branches": false,
        "custom_branch_policies": true,
        "custom_branches": ["main", "prod", "release/*"]
      },
      "reviewers": [
        {"type": "Team", "id": "prod-approvers"},
        {"type": "User", "id": "deployment-manager"}
      ]
    }
  }
}
```

## Branch Policy Settings

| Setting | Type | Description |
|---------|------|-------------|
| `protected_branches` | boolean | Allow only branches with protection rules |
| `custom_branch_policies` | boolean | Use custom branch list |
| `custom_branches` | array | List of allowed branches (when custom_branch_policies is true) |

## Wildcard Patterns

You can use wildcard patterns in custom branches:
- `main` - Exact branch name
- `release/*` - Any branch starting with "release/"
- `feature/*` - Any branch starting with "feature/"
- `v*.*.*` - Version tags like v1.2.3

## Best Practices

### Development Environment
- **Policy**: No restrictions
- **Reasoning**: Developers need flexibility to test from any branch

### QA Environment  
- **Policy**: Protected branches only
- **Reasoning**: Only reviewed code should reach QA

### UAT Environment
- **Policy**: Custom branches (main, uat)
- **Reasoning**: Only stable branches ready for user testing

### Production Environment
- **Policy**: Custom branches (main, prod, release/*)
- **Reasoning**: Strict control over what can reach production

## GitHub Actions Workflow Integration

Your deployment workflows should respect these policies:

```yaml
name: Deploy to Environment
on:
  workflow_dispatch:
    inputs:
      environment:
        required: true
        type: choice
        options:
          - dev
          - qa  
          - uat
          - prod

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - name: Deploy
        run: echo "Deploying ${{ github.ref_name }} to ${{ inputs.environment }}"
```

The deployment will be blocked if the current branch doesn't match the environment's branch policy.

## Troubleshooting

### Common Issues

1. **"Branch not allowed"**: Check if your branch matches the deployment policy
2. **"Protected branch required"**: Ensure your branch has protection rules enabled
3. **"Custom branch policy failed"**: Verify branch name is in the custom_branches list

### API Limitations

- Branch policies are set per environment
- Wildcard patterns must be supported by GitHub
- Changes may take a few minutes to propagate

