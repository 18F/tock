#/bin/bash

set -e

if [ "$#" -lt 1 ]
then
  printf "Usage \n\n\$ bin/deploy.sh <Environment>\n"
fi

case $1 in
  stag*)
    cf_space_name='staging'
    manifest_name='manifest-staging.yml'
    ;;
  prod*)
    cf_space_name='prod'
    manifest_name='manifest-production.yml'
    ;;
  *)
    echo "Please pick from either staging or production environments"
    exit 99
    ;;
esac

# Update this version number for what's found on the Release page for Autopilot
# e.g. https://github.com/contraband/autopilot/releases/latest
autopilot_version="0.0.4"
local_os_type=$(
  echo "${OSTYPE}" | grep -o '[a-z]\+' | head -n 1
)
github_release_autopilot_url="https://github.com/contraband/autopilot/releases/download/${autopilot_version}/autopilot-${local_os_type}"

if ! cf plugins | grep autopilot > /dev/null
then
  echo "Installing Autopilot for ${OSTYPE}."
  cf install-plugin "${github_release_autopilot_url}" -f
fi

cf login -a https://api.fr.cloud.gov -u "${CF_DEPLOYER_USERNAME}" -p "${CF_DEPLOYER_PASSWORD}" -o "${cf_organization_name}" -s "${cf_space_name}"

cf target -o "${cf_organization_name}" -s "${cf_space_name}"

cf zero-downtime-push tock -f "${manifest_name}"
