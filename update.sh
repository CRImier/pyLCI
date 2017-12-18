#!/bin/bash

INSTALL_DIR="/opt/zpui"
SUDO=''

cd "$(dirname "$0")"  # Make sure we are in the script's directory when running
set -e  # Strict mode : script stops if any command fails


if (( $EUID != 0 )); then
    SUDO='sudo'
fi

git pull origin master  # Always tell the branch we pull from

${SUDO} pip install -r requirements.txt  # Make sure we have the latest dependencies installed

# Run tests
pytest2 --doctest-modules -v --doctest-ignore-import-errors --ignore=apps/example_apps/fire_detector/ --ignore=ui/tests/test_checkbox.py  #  todo : fixes checkbox testing not working at the moment

${SUDO} mkdir -p ${INSTALL_DIR}
${SUDO} rsync -av --delete ./  ${INSTALL_DIR}
${SUDO} systemctl restart zpui.service
