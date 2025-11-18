#!/bin/bash
set -e

VERSION=4.105.1
DOWNLOAD_DIR=/usr/downloads
INSTALL_DIR=/usr/lib/code-server

# Create directories
mkdir -p "$DOWNLOAD_DIR"
mkdir -p "$INSTALL_DIR"

# Download tar.gz
curl -fLo "$DOWNLOAD_DIR/code-server.tar.gz" \
  "https://github.com/coder/code-server/releases/download/v$VERSION/code-server-$VERSION-linux-amd64.tar.gz"

# Extract inside downloads
tar -xzf "$DOWNLOAD_DIR/code-server.tar.gz" -C "$DOWNLOAD_DIR"

# Move extracted folder to install location
mv "$DOWNLOAD_DIR/code-server-$VERSION-linux-amd64"/* "$INSTALL_DIR"

# Cleanup
rm "$DOWNLOAD_DIR/code-server.tar.gz"
rm -rf "$DOWNLOAD_DIR/code-server-$VERSION-linux-amd64"

# Remove old symlink if exists
rm -f /usr/local/bin/code-server

# Create new symlink
ln -s "$INSTALL_DIR/bin/code-server" /usr/local/bin/code-server

echo "Code-Server installed successfully!"
