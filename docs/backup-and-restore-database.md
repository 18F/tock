# Backup And Restore the Tock Database

[:arrow_left: Back to Tock Documentation](../docs)

This process requires the [cf-service-
connect](https://github.com/18F/cf-service-connect) plugin that folks on the
cloud.gov team have developed for Cloud Foundry. Please make sure you have the
latest version installed before starting. If you need to update the plugin, you
need to uninstall it first before you can install the new version. To uninstall
a plugin, run this command:

```bash
cf uninstall-plugin <plugin name>
```

Then follow the installation instructions found in the plugin's documentation.

## Step 1: Exporting data

```bash
# Target the environment you're exporting from
cf target [-o <org name>] -s <space name>

# Check to see if a SERVICE_CONNECT service key already exists
cf service-keys <service name>

# If a key exists, remove it first before starting
cf delete-service-key <service name> SERVICE_CONNECT

# In a separate shell window, connect to the service to setup a direct SSH tunnel and leave it running
# note the credentials and connection info given in the output
cf connect-to-service -no-client <app name> <service name>

# Back in the original window, dump the database
pg_dump -F c --no-acl --no-owner -f <file name> postgres://<username>:<password>@<host>:<port>/<name>

# In the window with the SSH Tunnel, close the SSH tunnel
Ctrl+C

# Back in the original window, remove the SERVICE_CONNECT service key to keep things clean
cf delete-service-key <service name> SERVICE_CONNECT
```

Tock retains daily backups for 14 days; for details, see the [cloud.gov backup documentation](https://cloud.gov/docs/services/relational-database/#backups). (Please note that if you are planning contingency tests, the cloud.gov support team prefers at least 48 hours of advance notice.)

## Step 2: Importing data

```bash
# Target the environment you're restoring into
cf target [-o <org name>] -s <space name>

# Check to see if a SERVICE_CONNECT service key already exists
cf service-keys <service name>

# If a key exists, remove it first before starting
cf delete-service-key <service name> SERVICE_CONNECT

# Check the current running applications
cf apps

# Unbind the database service connected to the app you're working with
cf us <app name> <service name>

# Delete the database service
cf ds <service name>

# Recreate the database service
# To see all available service plans, run cf marketplace
# Note: Only production should have something other than shared-psql
cf cs aws-rds <service plan> <service name>

# rebind the service to the app
cf bs <app name> <service name>

# In a separate shell window, connect to the service to setup a direct SSH tunnel and leave it running
# note the credentials and connection info given in the output
cf connect-to-service -no-client <app name> <service>

# back in the original window, restore the database
pg_restore --dbname postgres://<username>:<password>@<host>:<port>/<name> --no-acl --no-owner <file name>

# In the window with the SSH Tunnel, close the SSH tunnel
Ctrl+C

# Back in the original window, remove the SERVICE_CONNECT service key to keep things clean
cf delete-service-key <service name> SERVICE_CONNECT

# Restage the app associated with the service
cf restage <app name>
```
