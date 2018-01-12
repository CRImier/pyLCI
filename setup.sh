#!/bin/bash

set -euo pipefail

INSTALL_DIR="/opt/zpui"

if test "$EUID" -ne 0
then
   echo "This script must be run as root, exiting..."
   exit 1
fi

[ -f config.json ] || cp default_config.json config.json
apt-get install python python-pip python-smbus python-dev python-pygame libjpeg-dev python-serial nmap
pip2 install -r requirements.txt
mkdir -p ${INSTALL_DIR}
cp ./. ${INSTALL_DIR} -R
cd ${INSTALL_DIR}
cp zpui.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable zpui.service
systemctl start zpui.service
