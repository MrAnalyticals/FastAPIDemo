-- SQL Script to Configure Managed Identity for Azure SQL Database
-- Run this script in SQL Server Management Studio, Azure Data Studio, or Azure Portal Query Editor
-- You must be connected as a user with admin privileges

-- Replace 'fastapi-energy-trading' with your actual Web App name
-- The Web App name becomes the user name in Azure SQL when using System Assigned Identity

-- 1. Create contained database user for the Web App's managed identity
CREATE USER [fastapi-energy-trading] FROM EXTERNAL PROVIDER;

-- 2. Grant necessary permissions for the FastAPI application
-- Option A: Grant broad permissions (easier setup)
ALTER ROLE db_datareader ADD MEMBER [fastapi-energy-trading];
ALTER ROLE db_datawriter ADD MEMBER [fastapi-energy-trading];
ALTER ROLE db_ddladmin ADD MEMBER [fastapi-energy-trading];  -- Allows creating/altering tables

-- Option B: Grant specific permissions (more secure, recommended for production)
-- Uncomment and use these instead of Option A for tighter security:
/*
GRANT SELECT, INSERT, UPDATE, DELETE ON dbo.trades TO [fastapi-energy-trading];
GRANT CREATE TABLE TO [fastapi-energy-trading];
GRANT ALTER ON SCHEMA::dbo TO [fastapi-energy-trading];
*/

-- 3. Verify the user was created successfully
SELECT 
    name,
    type_desc,
    authentication_type_desc
FROM sys.database_principals 
WHERE name = 'fastapi-energy-trading';

-- 4. Check permissions granted
SELECT 
    dp.class_desc,
    dp.permission_name,
    dp.state_desc,
    p.name AS principal_name
FROM sys.database_permissions dp
JOIN sys.database_principals p ON dp.grantee_principal_id = p.principal_id
WHERE p.name = 'fastapi-energy-trading';

-- 5. Test connection (optional) - this would be done from the application
-- The following is just for documentation - cannot be run in SQL directly
/*
-- From your FastAPI application with managed identity enabled,
-- the connection should now work without username/password
*/

PRINT 'Managed Identity setup completed for Web App: fastapi-energy-trading'
PRINT 'The Web App can now connect to this database using its managed identity'
