#!/bin/bash
# Azure Web App Deployment Script (Bash version)
# Run these commands in Azure CLI or Azure Cloud Shell

# Variables (update these as needed)
RESOURCE_GROUP="FastAPITrading"
WEB_APP_NAME="fastapi-energy-trading"
LOCATION="East US"  # or your preferred location
SKU="B1"  # Basic tier, can upgrade later

echo "Creating Azure Web App for FastAPI Energy Trading Platform..."

# 1. Create App Service Plan (Linux-based for Python)
echo "Creating App Service Plan..."
az appservice plan create \
  --name "${WEB_APP_NAME}-plan" \
  --resource-group $RESOURCE_GROUP \
  --location "$LOCATION" \
  --is-linux \
  --sku $SKU

# 2. Create Web App with Python 3.11 runtime
echo "Creating Web App..."
az webapp create \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --plan "${WEB_APP_NAME}-plan" \
  --runtime "PYTHON:3.11"

# 3. Enable System Assigned Managed Identity
echo "Enabling System Assigned Managed Identity..."
az webapp identity assign \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP

# 4. Get the Managed Identity Principal ID (save this for database permissions)
echo "Getting Managed Identity Principal ID..."
PRINCIPAL_ID=$(az webapp identity show \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --query principalId \
  --output tsv)

echo "Managed Identity Principal ID: $PRINCIPAL_ID"
echo "Save this Principal ID - you'll need it for database permissions!"

# 5. Configure App Settings for Production
echo "Configuring App Settings..."
az webapp config appsettings set \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings \
  AZURE_SQL_SERVER="fastapitrading.database.windows.net" \
  AZURE_SQL_DATABASE="fastapi" \
  USE_MANAGED_IDENTITY="True" \
  DEBUG="False" \
  LOG_LEVEL="INFO"

# 6. Configure startup command
echo "Setting startup command..."
az webapp config set \
  --name $WEB_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --startup-file "startup.sh"

echo "Azure Web App '$WEB_APP_NAME' created successfully!"
echo "URL: https://$WEB_APP_NAME.azurewebsites.net"
echo ""
echo "Next steps:"
echo "1. Configure database permissions for Principal ID: $PRINCIPAL_ID"
echo "2. Deploy your code using: az webapp up"
echo "3. Test the deployment"
