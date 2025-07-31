# Azure Web App Deployment Script
# Run these commands in Azure CLI or Azure Cloud Shell

# Variables (update these as needed)
$resourceGroup = "FastAPITrading"
$webAppName = "fastapi-energy-trading"
$location = "East US"  # or your preferred location
$sku = "B1"  # Basic tier, can upgrade later

# 1. Create App Service Plan (Linux-based for Python)
Write-Host "Creating App Service Plan..."
az appservice plan create `
  --name "$webAppName-plan" `
  --resource-group $resourceGroup `
  --location $location `
  --is-linux `
  --sku $sku

# 2. Create Web App with Python 3.11 runtime
Write-Host "Creating Web App..."
az webapp create `
  --name $webAppName `
  --resource-group $resourceGroup `
  --plan "$webAppName-plan" `
  --runtime "PYTHON:3.11"

# 3. Enable System Assigned Managed Identity
Write-Host "Enabling System Assigned Managed Identity..."
az webapp identity assign `
  --name $webAppName `
  --resource-group $resourceGroup

# 4. Get the Managed Identity Principal ID (save this for database permissions)
Write-Host "Getting Managed Identity Principal ID..."
$principalId = az webapp identity show `
  --name $webAppName `
  --resource-group $resourceGroup `
  --query principalId `
  --output tsv

Write-Host "Managed Identity Principal ID: $principalId"
Write-Host "Save this Principal ID - you'll need it for database permissions!"

# 5. Configure App Settings for Production
Write-Host "Configuring App Settings..."
az webapp config appsettings set `
  --name $webAppName `
  --resource-group $resourceGroup `
  --settings `
  AZURE_SQL_SERVER="fastapitrading.database.windows.net" `
  AZURE_SQL_DATABASE="fastapi" `
  USE_MANAGED_IDENTITY="True" `
  DEBUG="False" `
  LOG_LEVEL="INFO"

# 6. Configure startup command
Write-Host "Setting startup command..."
az webapp config set `
  --name $webAppName `
  --resource-group $resourceGroup `
  --startup-file "startup.sh"

Write-Host "Azure Web App '$webAppName' created successfully!"
Write-Host "URL: https://$webAppName.azurewebsites.net"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Configure database permissions for Principal ID: $principalId"
Write-Host "2. Deploy your code using: az webapp up"
Write-Host "3. Test the deployment"
