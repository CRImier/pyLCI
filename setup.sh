#!/bin/bash

INSTALL_DIR="/opt/zpui"
SUDO=''
if (( $EUID != 0 )); then
    SUDO='sudo'
fi
[ -f config.json ] || cp default_config.json config.json
${SUDO} apt-get install python python-pip python-smbus python-dev python-pygame libjpeg-dev python-serial nmap
${SUDO} pip2 install -r requirements.txt
${SUDO} mkdir -p ${INSTALL_DIR}
${SUDO} cp ./. ${INSTALL_DIR} -R
cd ${INSTALL_DIR}
${SUDO} cp zpui.service /etc/systemd/system/
${SUDO} systemctl daemon-reload
${SUDO} systemctl enable zpui.service
${SUDO} systemctl start zpui.service
