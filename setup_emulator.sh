touch emulator
sudo pip install luma.emulator || exit 2
cat << EOF > config.json
{"input":[{"driver":"pygame_input"}],"output":[{"driver":"pygame_emulator"}]}
EOF
