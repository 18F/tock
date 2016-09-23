#!/bin/sh

set -e

app_name="tock"

timestamp="$(date +"%s")"
current_apps="$(cf apps)"

deploy()
{
	current_deployment=$1
	next_deployment=$2


	echo "$current_deployment is currently deployed, pushing $next_deployment"
	cf push $next_deployment --no-start -n $app_name-$timestamp
	cf push $next_deployment -n $app_name-$timestamp
	echo "Mapping $next_deployment to the Main Domain"
	cf map-route $next_deployment 18f.gov -n $app_name
	cf map-route $next_deployment 18f.gov -n $app_name --path api
	echo "Removing $current_deployment From the Main Domain"
	cf unmap-route $current_deployment 18f.gov -n $app_name
	cf unmap-route $current_deployment 18f.gov -n $app_name --path api
	read -p "Check your app. Is it functioning properly? (y/n)" -n 1 -r
	echo    # (optional) move to a new line
	if [[ $REPLY =~ ^[Yy]$ ]]; then
		cf delete $current_deployment -f
	else
		deploy $next_deployment $current_deployment
	fi
}

if [[ $current_apps == *"green"* ]]; then
	echo "Green Exists, Deploying Blue"
	deploy green blue
elif [[ $current_apps == *"blue"* ]]; then
	echo "Blue Exists, Deploying Green"
	deploy blue green
else
	echo "No existing blue or green app, please create one first!"
fi
