#/bin/bash

set -o errexit
set -o pipefail

cd tock

# Only run migrations on the zeroth index when in a cloud.gov environment
if [[ -v CF_INSTANCE_INDEX && $CF_INSTANCE_INDEX == 0 ]]
then
  python manage.py migrate --settings=tock.settings.production --noinput
else
  echo "Migrations did not run."
  if [[ -v CF_INSTANCE_INDEX ]]
  then
    echo "CF Instance Index is ${CF_INSTANCE_INDEX}."
  fi
fi


if [[ -f VERSION ]]
then
  VERSION=$(cat VERSION)
else
  VERSION="Manual Deployment"
fi

NEW_RELIC_API_KEY=$(
  echo "${VCAP_SERVICES}" | \
  jq '.[] | map(select(.name == "tock-credentials")) | .[].credentials.NEW_RELIC_API_KEY' -r
)

# Append New Relic API key to New Relic INI file for `newrelic-admin` tool
cat <<EOF >> "${NEW_RELIC_CONFIG_FILE}"

# Adding license key from script $(basename "${0}")
api_key=${NEW_RELIC_API_KEY}
EOF

DEPLOYMENT_DESCRIPTION="Recording deployment of ${VERSION}."

echo "${DEPLOYMENT_DESCRIPTION}"

# Record deployment using the New Relic Python Admin CLI
newrelic-admin record-deploy "${NEW_RELIC_CONFIG_FILE}" "${DEPLOYMENT_DESCRIPTION}"

python manage.py collectstatic --settings=tock.settings.production --noinput
gunicorn -t 120 -k gevent -w 2 tock.wsgi:application
