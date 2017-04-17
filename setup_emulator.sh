touch emulator
sudo apt-get install python-pip
sudo pip install luma.emulator
cat << EOF > config.json
{"input":[{"driver":"pygame_input"}],"output":[{"driver":"pygame_emulator"}]}
EOF
