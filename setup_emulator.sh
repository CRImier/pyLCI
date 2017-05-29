touch emulator
cat << EOF > config.json
{"input":[{"driver":"pygame_input"}],"output":[{"driver":"pygame_emulator"}]}
EOF
