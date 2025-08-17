#!/usr/bin/env python3
"""
Example configurations for different types of repositories
"""

from main import GitHubRepoManager, RepoConfig
import os

# Example configurations
EXAMPLES = {
    "simple_api": {
        "name": "simple-api",
        "owner": "vsbopi",
        "description": "A simple REST API service",
        "application": "SimpleAPI",
        "team": "Backend Team",
        "poc": "backend-team@company.com",
        "gitignore_template": "Python",
        "environments": ["dev", "staging", "prod"]
    },
    
    "frontend_app": {
        "name": "customer-portal",
        "owner": "vsbopi", 
        "description": "Customer facing web portal",
        "application": "CustomerPortal",
        "compliance_audit_to_review": "Yes",
        "deployed_to_prod": "Yes",
        "impact_on_prod_app": "High",
        "poc": "frontend-team@company.com",
        "repo_owner": "Frontend Team",
        "prod_deployment_method": "GitOps",
        "team": "Frontend Team",
        "gitignore_template": "Node",
        "enable_branch_protection": True,
        "required_reviews": 2,
        "environments": ["development", "staging", "production"],
        "variables": {
            "NODE_ENV": "production",
            "BUILD_ENV": "production"
        }
    },
    
    "microservice": {
        "name": "payment-service",
        "owner": "vsbopi",
        "description": "Payment processing microservice",
        "application": "PaymentService",
        "compliance_audit_to_review": "Yes",
        "deployed_to_prod": "Yes", 
        "impact_on_prod_app": "Critical",
        "poc": "payments-team@company.com",
        "repo_owner": "Payments Team",
        "prod_deployment_method": "Kubernetes",
        "team": "Payments Team",
        "gitignore_template": "Java",
        "enable_branch_protection": True,
        "required_reviews": 3,
        "environments": ["dev", "test", "staging", "prod"],
        "secrets": {
            "DATABASE_PASSWORD": "secure-db-password",
            "STRIPE_SECRET_KEY": "sk_live_..."
        },
        "variables": {
            "JAVA_VERSION": "17",
            "SPRING_PROFILE": "production"
        }
    },
    
    "data_pipeline": {
        "name": "customer-analytics",
        "owner": "vsbopi",
        "description": "Customer data analytics pipeline",
        "application": "CustomerAnalytics",
        "compliance_audit_to_review": "Yes",
        "deployed_to_prod": "Yes",
        "impact_on_prod_app": "Medium",
        "poc": "data-team@company.com",
        "repo_owner": "Data Engineering Team",
        "prod_deployment_method": "Airflow",
        "team": "Data Engineering",
        "gitignore_template": "Python",
        "enable_branch_protection": True,
        "environments": ["dev", "staging", "prod"],
        "secrets": {
            "SNOWFLAKE_PASSWORD": "secure-password",
            "AWS_SECRET_ACCESS_KEY": "secret-key"
        },
        "variables": {
            "PYTHON_VERSION": "3.11",
            "SPARK_VERSION": "3.4.0"
        }
    }
}

def create_example_repo(example_name: str, token: str):
    """Create a repository using one of the predefined examples"""
    
    if example_name not in EXAMPLES:
        print(f"❌ Example '{example_name}' not found")
        print(f"Available examples: {', '.join(EXAMPLES.keys())}")
        return False
    
    example_config = EXAMPLES[example_name]
    
    # Create RepoConfig from example
    config = RepoConfig(
        name=example_config["name"],
        owner=example_config["owner"],
        description=example_config["description"],
        visibility=example_config.get("visibility", "internal"),
        application=example_config.get("application", ""),
        compliance_audit_to_review=example_config.get("compliance_audit_to_review", ""),
        deployed_to_prod=example_config.get("deployed_to_prod", ""),
        impact_on_prod_app=example_config.get("impact_on_prod_app", ""),
        poc=example_config.get("poc", ""),
        repo_owner=example_config.get("repo_owner", ""),
        prod_deployment_method=example_config.get("prod_deployment_method", ""),
        team=example_config.get("team", ""),
        gitignore_template=example_config.get("gitignore_template", "Python"),
        enable_branch_protection=example_config.get("enable_branch_protection", False),
        required_reviews=example_config.get("required_reviews", 2),
        environments=example_config.get("environments", []),
        secrets=example_config.get("secrets", {}),
        variables=example_config.get("variables", {})
    )
    
    # Create repository
    manager = GitHubRepoManager(token)
    result = manager.create_repository(config)
    
    if result["success"]:
        print(f"\n✅ {result['message']}")
        print(f"🔗 Repository URL: {result['repository_url']}")
        return True
    else:
        print(f"\n❌ Error: {result['error']}")
        return False

def main():
    """Interactive example selector"""
    print("GitHub Repository Examples")
    print("=" * 40)
    
    # List available examples
    print("Available examples:")
    for i, (name, config) in enumerate(EXAMPLES.items(), 1):
        print(f"{i}. {name}: {config['description']}")
    
    # Get user selection
    try:
        choice = int(input(f"\nSelect example (1-{len(EXAMPLES)}): "))
        if choice < 1 or choice > len(EXAMPLES):
            raise ValueError()
        
        example_name = list(EXAMPLES.keys())[choice - 1]
    except (ValueError, IndexError):
        print("❌ Invalid selection")
        return
    
    # Get GitHub token
    token = input("Enter your GitHub token: ").strip()
    if not token:
        print("❌ GitHub token is required")
        return
    
    # Option to customize repository name
    current_name = EXAMPLES[example_name]["name"]
    new_name = input(f"Repository name (current: {current_name}): ").strip()
    if new_name:
        EXAMPLES[example_name]["name"] = new_name
    
    # Create the repository
    create_example_repo(example_name, token)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Command line usage: python examples.py simple_api
        example_name = sys.argv[1]
        token = os.getenv('GITHUB_TOKEN') or input("Enter your GitHub token: ").strip()
        if token:
            create_example_repo(example_name, token)
    else:
        # Interactive mode
        main()
