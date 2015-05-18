#!/bin/sh

set -e

app_name="tock"

timestamp="$(date +"%s")"
current_apps="$(cf apps)"

deploy()
{
	current_deployment=$1
	next_deployment=$2

	current_vars="$(cf env $current_deployment)"

	database_url="$(echo ${current_vars#*DATABASE_URL: } | awk '{print $1}')"
	django_secret_key="$(echo ${current_vars#*DJANGO_SECRET_KEY: } | awk '{print $1}')"


	echo "$current_deployment is currently deployed, pushing $next_deployment"
	cf push $next_deployment --no-start -n $app_name-$timestamp
	cf set-env $next_deployment DATABASE_URL $database_url
	cf set-env $next_deployment DJANGO_SECRET_KEY $django_secret_key
	cf push $next_deployment -n $app_name-$timestamp
	echo "Mapping $next_deployment to the Main Domain"
	cf map-route $next_deployment 18f.gov -n $app_name
	cf map-route $next_deployment cf.18f.us -n $app_name
	echo "Removing $current_deployment From the Main Domain"
	cf unmap-route $current_deployment 18f.gov -n $app_name
	cf unmap-route $current_deployment cf.18f.us -n $app_name
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