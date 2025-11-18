mkdir -p /usr/downloads
curl -fOL /usr/downloads https://github.com/coder/code-server/releases/download/v4.105.1/code-server-4.105.1-linux-amd64.tar.gz
tar -xzf /usr/downloads/code-server-4.105.1-linux-amd64.tar.gz
mv /usr/downloads/code-server-4.105.1-linux-amd64.tar.gz /usr/lib/code-server
rm /usr/downloads/code-server-4.105.1-linux-amd64.tar.gz
mv /usr/downloads/code-server-4.105.1-linux-amd64 /usr/lib/code-server
rm -rf /usr/local/bin/code-server
ln -s /usr/lib/code-server/bin/code-server /usr/local/bin/code-server
