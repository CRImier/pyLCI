touch emulator
cat << EOF > config.json
{"input":[{"driver":"pygame_input"}],"output":[{"driver":"pygame_emulator"}]}
EOF
touch apps/phone/do_not_load #Phone app will try to connect to modem, emulator environment is unlikely to have one
#In future, modem could be emulated - until that, the app will likely have to be disabled on emulators
