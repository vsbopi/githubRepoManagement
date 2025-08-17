# Repository Access Management Feature

## 🎯 **Overview**

The GitHub Repository Management Tool now includes **comprehensive repository access management** that allows you to configure team and user permissions directly in your repository configuration.

## ✨ **New Access Management Features**

### 👥 **Team Access Management**
- **Add teams** to repositories with specific permission levels
- **Update existing team permissions** when they differ from configuration
- **Intelligent checking** - only updates what's changed
- **Organization-wide team support**

### 👤 **User Access Management** 
- **Add individual users** as collaborators with specific permissions
- **Update existing user permissions** when they differ from configuration
- **Smart permission checking** - preserves existing access when not specified
- **External collaborator support**

## 🔧 **Permission Levels**

GitHub supports the following permission levels:

| Permission | Description |
|------------|-------------|
| **read** | Can view and clone the repository |
| **triage** | Can manage issues and pull requests (read + issue management) |
| **write** | Can push to repository (read + write access) |
| **maintain** | Can manage repository settings (write + repository management) |
| **admin** | Full access including repository deletion and team management |

## 📋 **Configuration Format**

### **JSON Configuration File**

```json
{
  "repository": {
    "name": "my-project",
    "owner": "vsbopi",
    "description": "My awesome project",
    "visibility": "internal"
  },
  "team_access": {
    "backend-team": "write",
    "devops-team": "admin", 
    "qa-team": "read",
    "security-team": "maintain"
  },
  "user_access": {
    "john.doe": "write",
    "jane.smith": "admin",
    "external.contractor": "read"
  }
}
```

### **Interactive Mode**

```bash
python main.py
# Follow prompts...

Team Access (permissions: read, triage, write, maintain, admin)
Add team access? (y/n): y
Team name/slug (press Enter to finish): backend-team
Permission for team backend-team (read/write/admin): write

User Access (permissions: read, triage, write, maintain, admin)
Add user access? (y/n): y
Username (press Enter to finish): john.doe
Permission for user john.doe (read/write/admin): write
```

### **Command Line**

```bash
python create_repo.py \
  --name "my-project" \
  --owner "vsbopi" \
  --description "My project" \
  --team-access "backend-team:write,devops-team:admin,qa-team:read" \
  --user-access "john.doe:write,jane.smith:admin"
```

## 🚀 **How It Works**

### **1. Intelligent Checking**
The tool checks existing team and user permissions before making any changes:

```
👥 Checking repository access...
🏢 Checking team access...
📋 Found 3 existing team permissions
🔄 Will update team backend-team: 'read' → 'write'
➕ Will add team devops-team: 'admin'
✅ 1 team permissions already up to date
```

### **2. Team Permission Management**
- Checks existing teams assigned to the repository
- Compares current permissions with desired configuration
- Only updates teams that need permission changes
- Adds new teams that aren't currently assigned

### **3. User Permission Management**
- Checks existing collaborators on the repository
- Compares current user permissions with desired state
- Updates users with different permission levels
- Adds new users as collaborators

### **4. Error Handling**
- Validates team names exist in the organization
- Handles invalid usernames gracefully
- Provides clear error messages for permission issues
- Continues processing even if some access changes fail

## 📊 **Example Output**

```bash
👥 Checking repository access...
🏢 Checking team access...
📋 Found 2 existing team permissions
🔄 Will update team platform: 'read' → 'write'
➕ Will add team devops-india: 'admin'
✅ 1 team permissions already up to date
   ✅ Set team platform permission to: write
   ✅ Set team devops-india permission to: admin

👤 Checking user access...
📋 Found 1 existing collaborators  
➕ Will add user vs-vsbopi: 'admin'
➕ Will add user nishantvsbopi: 'write'
   ✅ Set user vs-vsbopi permission to: admin
   ✅ Set user nishantvsbopi permission to: write

✓ Repository access configured
```

## 🔧 **Configuration Examples**

### **Example 1: Development Team Setup**

```json
{
  "team_access": {
    "frontend-developers": "write",
    "backend-developers": "write", 
    "devops-engineers": "admin",
    "qa-engineers": "triage",
    "security-team": "maintain"
  },
  "user_access": {
    "tech.lead": "admin",
    "external.consultant": "read"
  }
}
```

### **Example 2: Multi-Team Project**

```json
{
  "team_access": {
    "product-team": "read",
    "engineering-team": "write",
    "platform-team": "admin",
    "compliance-team": "read"
  },
  "user_access": {
    "project.manager": "triage",
    "release.manager": "maintain"
  }
}
```

### **Example 3: Open Source Project**

```json
{
  "repository": {
    "visibility": "public"
  },
  "team_access": {
    "core-maintainers": "admin",
    "contributors": "write",
    "triagers": "triage"
  },
  "user_access": {
    "lead.maintainer": "admin",
    "trusted.contributor": "maintain"
  }
}
```

## 🛡️ **Security Considerations**

### **Best Practices**
1. **Principle of Least Privilege** - Give users minimum necessary permissions
2. **Use Teams** - Prefer team-based access over individual user access
3. **Regular Audits** - Review and update permissions regularly
4. **Admin Access** - Limit admin access to essential personnel only

### **Permission Guidelines**
- **read**: External stakeholders, documentation reviewers
- **triage**: Support team, issue managers, community moderators  
- **write**: Active developers, content creators
- **maintain**: Team leads, release managers
- **admin**: Repository owners, security administrators

## 🔄 **Integration with Existing Features**

The access management works seamlessly with all existing features:

- ✅ **Idempotent Operations** - Safe to run multiple times
- ✅ **Configuration Drift Detection** - Shows what will change
- ✅ **Intelligent Updates** - Only changes what's needed
- ✅ **Error Recovery** - Continues even if some permissions fail
- ✅ **Comprehensive Logging** - Clear feedback on all actions

## 🚀 **Use Cases**

### **1. New Repository Setup**
- Create repository with full team and user access configuration
- Ensure proper permissions from day one
- Avoid manual permission setup

### **2. Team Restructuring**
- Update team permissions when organizational structure changes
- Bulk update access across multiple repositories
- Maintain consistent access patterns

### **3. Security Compliance**
- Audit and standardize repository access
- Implement security policies via configuration
- Track permission changes over time

### **4. Onboarding/Offboarding**
- Add new team members with appropriate permissions
- Update access when roles change
- Automate permission management

The repository access management feature makes the tool enterprise-ready for managing complex organizational repository structures with proper security and access controls!
