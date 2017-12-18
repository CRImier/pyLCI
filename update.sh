#!/bin/bash

TMP_DIR="/tmp/zpui_update"
INSTALL_DIR="/opt/zpui"
IGNORE_TEST=false

cd "$(dirname "$0")"  # Make sure we are in the script's directory when running
set -e  # Strict mode : script stops if any command fails

while :; do
    case "$1" in
        -i|--ignore-tests) IGNORE_TEST=true; shift 1 ;;
        --) shift; break ;;
        *) echo "Unknown parameter !"; exit 1
    esac
done


SUDO=''
if (( $EUID != 0 )); then
    SUDO='sudo'
fi

# cleanup update dir
if [ -d ${TMP_DIR} ]; then
    rm -rf ${TMP_DIR}
fi
mkdir -p ${TMP_DIR}

# update a copy of zpui in TMP_DIR
git clone . ${TMP_DIR}
cd ${TMP_DIR}
git pull origin master  # Always tell the branch we pull from

${SUDO} pip install -r requirements.txt  # Make sure we have the latest dependencies installed

# Run tests
if [ -n ${IGNORE_TEST} ]; then
    pytest2 --doctest-modules -v --doctest-ignore-import-errors --ignore=apps/example_apps/fire_detector/ --ignore=ui/tests/test_checkbox.py  #  todo : fixes checkbox testing not working at the moment
fi

${SUDO} mkdir -p ${INSTALL_DIR}
${SUDO} rsync -av --delete ./  ${INSTALL_DIR}
${SUDO} systemctl restart zpui.service
