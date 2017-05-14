INSTALL_DIR="/opt/pylci"
SUDO=''
if (( $EUID != 0 )); then
    SUDO='sudo'
fi
[ -f config.json ] || cp config.json.example config.json
$SUDO apt-get install python python-pip
#$SUDO mkdir -p $INSTALL_DIR
#$SUDO cp ./. $INSTALL_DIR -R
#cd $INSTALL_DIR
#$SUDO cp pylci.service /etc/systemd/system/
#$SUDO systemctl daemon-reload
#$SUDO systemctl enable pylci.service
#Start it maybe?

