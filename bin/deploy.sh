#/bin/bash

set -e

if [ "$#" -lt 1 ]
then
  printf "Usage \n\n\$ bin/deploy.sh <Environment>\n"
fi

case $1 in
  stag*)
    cf_user="${CF_DEPLOYER_USERNAME_STAGING}"
    cf_password="${CF_DEPLOYER_PASSWORD_STAGING}"
    manifest_name='manifest-staging.yml'
    ;;
  prod*)
    cf_user="${CF_DEPLOYER_USERNAME_PRODUCTION}"
    cf_password="${CF_DEPLOYER_PASSWORD_PRODUCTION}"
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
case $(uname) in
  Linux)
    local_os_type='linux'
    local_release_type='linux64-binary'
    ;;
  Darwin)
    local_os_type='darwin'
    local_release_type='macosx64-binary'
    ;;
  *)
    echo "Unsupported operating system"
    exit 99
    ;;
esac

github_release_autopilot_url="https://github.com/contraband/autopilot/releases/download/${autopilot_version}/autopilot-${local_os_type}"

if ! which cf > /dev/null
then
  echo "Installing Cloud Foundry CLI for ${OSTYPE}."
  curl -L "https://cli.run.pivotal.io/stable?release=${local_release_type}&source=github" | tar xzv -C /usr/local/bin cf
fi

if ! cf plugins | grep autopilot > /dev/null
then
  echo "Installing Autopilot for ${OSTYPE}."
  cf install-plugin "${github_release_autopilot_url}" -f
fi

# Disable interactive mode by removing stdin
cf login -a https://api.fr.cloud.gov -u "${cf_user}" -p "${cf_password}" <&-

if [ "$?" -gt 0 ]
then
  echo "There was an issue authenticating with cloud.gov."
  echo "Please verify the Service Account Deployer Credentials are correct."
else
  cf zero-downtime-push tock -f "${manifest_name}"
fi

