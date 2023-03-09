#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

cd src/

poetry run python manage.py migrate
poetry run python manage.py runserver 0.0.0.0:9010

cd ..
