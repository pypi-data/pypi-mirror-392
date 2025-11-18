wget -q -O ngrok.zip https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-stable-linux-amd64.zip
unzip -o ngrok.zip
rm ngrok.zip
chmod +x ngrok
mv ngrok /usr/local/bin/ngrok
