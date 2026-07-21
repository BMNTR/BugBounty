#!/bin/bash

# setup-linux.sh - Install Bug Bounty tools in WSL
# Run this inside WSL or via: wsl bash scripts/setup-linux.sh

echo "[+] Starting WSL Bug Bounty Tools Installation..."

# Update and install basic dependencies
sudo apt-get update
sudo apt-get install -y wget curl git unzip jq make gcc libpcap-dev python3 python3-pip

# Install Go if not present
if ! command -v go &> /dev/null
then
    echo "[+] Installing Go..."
    GO_VERSION="1.22.4"
    wget https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz
    sudo rm -rf /usr/local/go
    sudo tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz
    rm go${GO_VERSION}.linux-amd64.tar.gz
    echo 'export PATH=$PATH:/usr/local/go/bin:~/go/bin' >> ~/.bashrc
    export PATH=$PATH:/usr/local/go/bin:~/go/bin
else
    echo "[+] Go is already installed."
fi

# Create tool directory
mkdir -p ~/go/bin

echo "[+] Installing ProjectDiscovery tools..."
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
go install -v github.com/projectdiscovery/katana/cmd/katana@latest

echo "[+] Installing ffuf..."
go install -v github.com/ffuf/ffuf/v2@latest

echo "[+] Tools installed successfully in ~/go/bin."
echo "[+] Ensure ~/go/bin is in your PATH."
