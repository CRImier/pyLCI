#!/bin/bash

set -euo pipefail

TMP_DIR="/tmp/zpui_update"
INSTALL_DIR="/opt/zpui"

cd "$(dirname "$0")"  # Make sure we are in the script's directory when running
set -e  # Strict mode : script stops if any command fails

if test "$EUID" -ne 0
then
   echo "This script must be run as root, exiting..."
   exit 1
fi

mkdir -p "${INSTALL_DIR}"
rsync -av --delete ./ --exclude='*.pyc' "${INSTALL_DIR}"
systemctl restart zpui.service
#rm -rf ${TMP_DIR}
exit 0
