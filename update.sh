#!/bin/bash

TMP_DIR="/tmp/zpui_update"
INSTALL_DIR="/opt/zpui"
IGNORE_TEST=false

cd "$(dirname "$0")"  # Make sure we are in the script's directory when running
set -e  # Strict mode : script stops if any command fails

case "$1" in
    -i|--ignore-tests) IGNORE_TEST=true; shift 1 ;;
    --) shift; break ;;
esac


SUDO=''
if (( $EUID != 0 )); then
    SUDO='sudo'
fi

# cleanup update dir
#if [ -d ${TMP_DIR} ]; then
#    rm -rf ${TMP_DIR}
#fi
#mkdir -p ${TMP_DIR}

# update a copy of zpui in TMP_DIR
#git clone . ${TMP_DIR}
#cd ${TMP_DIR}

UPSTREAM=${1:-'@{u}'}
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse "$UPSTREAM")
BASE=$(git merge-base @ "$UPSTREAM")


# from https://stackoverflow.com/questions/3258243/check-if-pull-needed-in-git#3278427
#if [ ${LOCAL} = ${REMOTE} ]; then
#    echo "Already Up-to-date"
#    exit 126  # 1, 127 and 128 error codes are used by git, 126 is free
#fi

# --ff-only Refuse to merge and exit with a non-zero status unless the current HEAD is already up to date or the merge can be resolved as a fast-forward.
#git pull origin master
#WORKAROUND only pulling the current branch
git pull

${SUDO} pip install -r requirements.txt  # Make sure we have the latest dependencies installed

# Run tests
if [ -n ${IGNORE_TEST} ]; then
    python -m pytest --doctest-modules -v --doctest-ignore-import-errors --ignore=output/drivers --ignore=input/drivers --ignore=apps/hardware_apps/status/ --ignore=apps/example_apps/fire_detector
fi

${SUDO} mkdir -p ${INSTALL_DIR}
${SUDO} rsync -av --delete ./  ${INSTALL_DIR}
${SUDO} systemctl restart zpui.service
#rm -rf ${TMP_DIR}
exit 0
