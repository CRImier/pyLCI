INSTALL_DIR="/opt/lcs"
SUDO=''
if (( $EUID != 0 )); then
    SUDO='sudo'
fi
git pull
$SUDO cp ./. $INSTALL_DIR -R
$SUDO systemctl restart lcs.service

