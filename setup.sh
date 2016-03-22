INSTALL_DIR="/opt/lcs"
SUDO=''
if (( $EUID != 0 )); then
    SUDO='sudo'
fi
$SUDO apt-get install python python-dev python-serial python-pip
$SUDO pip install evdev
$SUDO mkdir -p $INSTALL_DIR
$SUDO cp ./. $INSTALL_DIR -R
cd $INSTALL_DIR
$SUDO cp lcs.service /etc/systemd/system/
$SUDO systemctl daemon-reload
$SUDO systemctl enable lcs.service
#Start it maybe?

