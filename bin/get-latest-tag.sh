#/bin/bash

latest_tag=$( git tag | sort | tail -n 1 )

git checkout ${latest_tag}

git status
