#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

cd src

poetry run python manage.py bot
