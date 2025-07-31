# Azure Managed Identity Setup Guide

This guide explains how to configure Azure Managed Identity for secure database access without storing credentials.

## 🔐 Azure Managed Identity Overview

### System Assigned Managed Identity
- Automatically created and managed by Azure
- Tied to the lifecycle of the Azure resource (App Service)
- Automatically deleted when the resource is deleted
- Simpler to set up and manage

### User Assigned Managed Identity  
- Created as a standalone Azure resource
- Can be assigned to multiple Azure resources
- Persists independently of the resources it's assigned to
- More flexible for complex scenarios

## 🚀 Setup Instructions

### Step 1: Enable System Assigned Managed Identity on App Service

```bash
# Enable system assigned managed identity
az webapp identity assign --name <your-app-name> --resource-group <your-resource-group>

# Get the principal ID (you'll need this for database permissions)
az webapp identity show --name <your-app-name> --resource-group <your-resource-group> --query principalId --output tsv
```

### Step 2: Configure Azure SQL Database for Managed Identity

1. **Connect to your Azure SQL Database** using SQL Server Management Studio or Azure Data Studio with an admin account.

2. **Create a contained database user** for the managed identity:

```sql
-- Create user for system assigned managed identity
CREATE USER [<your-app-name>] FROM EXTERNAL PROVIDER;

-- Grant necessary permissions (adjust as needed)
ALTER ROLE db_datareader ADD MEMBER [<your-app-name>];
ALTER ROLE db_datawriter ADD MEMBER [<your-app-name>];
ALTER ROLE db_ddladmin ADD MEMBER [<your-app-name>];  -- If you need to create/alter tables

-- For minimal permissions, grant specific permissions:
-- GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.trades TO [<your-app-name>];
```

### Step 3: Configure App Service Settings

Set the following application settings in your Azure App Service:

```bash
az webapp config appsettings set \
  --name <your-app-name> \
  --resource-group <your-resource-group> \
  --settings \
  AZURE_SQL_SERVER=<your-server>.database.windows.net \
  AZURE_SQL_DATABASE=<your-database> \
  USE_MANAGED_IDENTITY=True
```

### Step 4: Alternative - User Assigned Managed Identity

If you prefer to use User Assigned Managed Identity:

1. **Create User Assigned Managed Identity:**
```bash
az identity create --name <identity-name> --resource-group <your-resource-group>
```

2. **Assign it to your App Service:**
```bash
az webapp identity assign --name <your-app-name> --resource-group <your-resource-group> --identities <identity-resource-id>
```

3. **Add the client ID to app settings:**
```bash
az webapp config appsettings set \
  --name <your-app-name> \
  --resource-group <your-resource-group> \
  --settings \
  AZURE_CLIENT_ID=<user-assigned-identity-client-id>
```

4. **Create database user with the identity name:**
```sql
CREATE USER [<identity-name>] FROM EXTERNAL PROVIDER;
ALTER ROLE db_datareader ADD MEMBER [<identity-name>];
ALTER ROLE db_datawriter ADD MEMBER [<identity-name>];
```

## 🔧 Local Development Setup

For local development, you have several options:

### Option 1: Use Azure CLI Authentication (Recommended)
```bash
# Login to Azure CLI
az login

# Set environment variable
USE_MANAGED_IDENTITY=False
```

The `DefaultAzureCredential` will automatically use your Azure CLI credentials.

### Option 2: Use SQL Authentication (Fallback)
Keep SQL authentication credentials in your local `.env` file:
```
USE_MANAGED_IDENTITY=False
AZURE_SQL_USERNAME=your-username
AZURE_SQL_PASSWORD=your-password
```

### Option 3: Use Service Principal (CI/CD)
For automated deployments, create a service principal:
```bash
az ad sp create-for-rbac --name "fastapi-energy-trading-sp"
```

Set these environment variables:
```
AZURE_CLIENT_ID=<service-principal-client-id>
AZURE_CLIENT_SECRET=<service-principal-secret>
AZURE_TENANT_ID=<tenant-id>
```

## 🛡️ Security Best Practices

1. **Principle of Least Privilege**: Grant only the minimum permissions needed
2. **Network Security**: Use Private Endpoints or VNet integration when possible
3. **Monitoring**: Enable Azure AD audit logs to monitor access
4. **Rotation**: Managed identities don't require credential rotation
5. **Environment Separation**: Use different identities for dev/staging/production

## 🧪 Testing Managed Identity

Test the connection locally (requires Azure CLI login):

```bash
python -c "
from app.database import test_connection
import os
os.environ['USE_MANAGED_IDENTITY'] = 'True'
os.environ['AZURE_SQL_SERVER'] = 'your-server.database.windows.net'
os.environ['AZURE_SQL_DATABASE'] = 'your-database'
test_connection()
"
```

## 📋 Troubleshooting

### Common Issues:

1. **"Login failed for user" error**
   - Verify the managed identity is enabled
   - Check that the database user was created correctly
   - Ensure proper permissions are granted

2. **"AADSTS700016" error (App not found)**
   - The App Service managed identity might not be properly configured
   - Verify the identity is enabled and note the principal ID

3. **Connection timeout**
   - Check Azure SQL firewall settings
   - Verify "Allow Azure services" is enabled if not using Private Endpoint

4. **Token acquisition failed**
   - For local development, ensure `az login` was successful
   - Check that the Azure Identity libraries are installed

### Debug Steps:

1. **Verify managed identity:**
```bash
az webapp identity show --name <your-app-name> --resource-group <your-resource-group>
```

2. **Test database connection:**
```bash
az sql db show-connection-string --server <server-name> --name <database-name> --client ado.net
```

3. **Check application logs:**
```bash
az webapp log tail --name <your-app-name> --resource-group <your-resource-group>
```

## 🔄 Migration from SQL Authentication

To migrate from SQL authentication to managed identity:

1. Enable managed identity (Step 1)
2. Create database user (Step 2)  
3. Test with both authentication methods
4. Update app settings to use managed identity
5. Remove SQL credentials from configuration
6. Monitor for any issues

This approach ensures zero downtime during the migration.
