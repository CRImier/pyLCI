#!/bin/bash
INSTALL_DIR="/opt/pylci"
SUDO=''
if (( $EUID != 0 )); then
    SUDO='sudo'
fi
git pull
$SUDO rsync -av ./  $INSTALL_DIR
$SUDO systemctl restart pylci.service

