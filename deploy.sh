#!/bin/bash

timestamp="$(date +"%s")"
app_name="tock"
current_apps="$(cf apps)"
current_vars="$(cf env $app_name)"

deploy()
{
	current_deployment=$1
	next_deployment=$2

	database_url=$(echo $current_vars | sed -n "s/DATABASE_URL: \([a-zA-Z0-9:/@.-]*\)/\1/p")
	django_secret_key=$(echo $current_vars | sed -n "s/DJANGO_SECRET_KEY: \([a-zA-Z0-9:/@.-]*\)/\1/p")

	echo "$current_deployment is currently deployed, pushing $next_deployment"
	cf push $next_deployment --no-start -n $app_name-$timestamp
	cf set-env $app_name DATABASE_URL $database_url
	cf set-env $app_name DJANGO_SECRET_KEY $django_secret_key
	cf push $next_deployment -n $app_name-$timestamp
	echo "Mapping $next_deployment to the Main Domain"
	cf map-route $next_deployment 18f.gov -n $app_name
	echo "Removing Green From the Main Domain"
	cf unmap-route $current_deployment 18f.gov -n $app_name
	echo "Unmapping the temporary $next_deployment Domain"
	cf unmap-route $next_deployment 18f.gov -n $app_name-$timestamp
	echo "Deleting $current_deployment"
	cf delete $current_deployment
}

if [ "${current_apps/green}" = "$current_apps" ]; then
	deploy green blue
elif [ "${current_apps/blue}" = "$current_apps" ]; then
	deploy blue green
else
	echo "No Current Blue/Green Deployment Found!"
fi


