curl -fOL https://github.com/coder/code-server/releases/download/v4.105.1/code-server-4.105.1-linux-amd64.tar.gz
tar -xzf code-server-4.105.1-linux-amd64.tar.gz
mv code-server-4.105.1-linux-amd64.tar.gz /usr/lib/code-server
rm code-server-4.105.1-linux-amd64.tar.gz
mv code-server-4.105.1-linux-amd64 /usr/lib/code-server
rm -rf /usr/local/bin/code-server
ln -s /usr/lib/code-server/bin/code-server /usr/local/bin/code-server
