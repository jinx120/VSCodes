#!/bin/bash

# Script to install SoftEther and Shadowsocks VPN servers on Arch Linux
# Configured for stealth operation on port 443
# For kernel 6.14.7-arch2-1

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${GREEN}[*] $1${NC}"
}

# Function to print error messages
print_error() {
    echo -e "${RED}[!] $1${NC}"
    exit 1
}

# Function to print warning messages
print_warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root"
fi

# Check if running on Arch Linux
if [ ! -f /etc/arch-release ]; then
    print_error "This script is designed for Arch Linux"
fi

# Cleanup previous installations
print_status "Checking for previous installations to clean up..."

# Stop and disable services if they exist
if systemctl list-unit-files | grep -q vpnserver.service; then
    print_warning "Found previous SoftEther installation. Stopping and disabling service..."
    systemctl stop vpnserver.service
    systemctl disable vpnserver.service
    rm -f /etc/systemd/system/vpnserver.service
fi

if systemctl list-unit-files | grep -q shadowsocks-libev; then
    print_warning "Found previous Shadowsocks installation. Stopping and disabling service..."
    systemctl stop shadowsocks-libev-server@config.service
    systemctl disable shadowsocks-libev-server@config.service
    rm -f /etc/systemd/system/shadowsocks-libev-server@config.service
fi

# Remove previous SoftEther installation
if [ -d "/opt/vpnserver" ]; then
    print_warning "Removing previous SoftEther installation files..."
    rm -rf /opt/vpnserver
fi

# Remove previous Shadowsocks configuration
if [ -d "/etc/shadowsocks" ]; then
    print_warning "Backing up and removing previous Shadowsocks configuration..."
    mkdir -p /root/backup
    cp -r /etc/shadowsocks /root/backup/shadowsocks.bak.$(date +%Y%m%d%H%M%S)
    rm -rf /etc/shadowsocks
fi

# Remove previous DNS update script and cron job
if [ -f "/opt/update_shadowsocks_dns.sh" ]; then
    print_warning "Removing previous DNS update script..."
    rm -f /opt/update_shadowsocks_dns.sh
fi

if [ -f "/etc/cron.d/shadowsocks_dns_update" ]; then
    print_warning "Removing previous DNS update cron job..."
    rm -f /etc/cron.d/shadowsocks_dns_update
fi

# Clean up temporary files
print_status "Cleaning up temporary files..."
rm -rf /tmp/vpnserver /tmp/softether.tar.gz /tmp/vpn_init.txt

# Reload systemd to recognize removed services
systemctl daemon-reload

# Update system
print_status "Updating system packages..."
pacman -Syu --noconfirm || print_error "Failed to update system packages"

# Install dependencies
print_status "Installing dependencies..."
pacman -S --noconfirm base-devel git wget tar gzip unzip openssl dhcpcd iptables-nft net-tools \
    gcc make cmake automake autoconf libtool || print_error "Failed to install dependencies"

# Ask for dynamic hostnames
read -p "Enter the first dynamic hostname for SoftEther: " softether_hostname
read -p "Enter the second dynamic hostname for Shadowsocks: " shadowsocks_hostname

# Ask for Shadowsocks password
read -s -p "Enter password for Shadowsocks server: " shadowsocks_password
echo ""

# Install SoftEther VPN
print_status "Installing SoftEther VPN..."
cd /tmp
wget -O softether.tar.gz https://github.com/SoftEtherVPN/SoftEtherVPN_Stable/releases/download/v4.38-9760-rtm/softether-vpnserver-v4.38-9760-rtm-2021.08.17-linux-x64-64bit.tar.gz || print_error "Failed to download SoftEther"
tar xzf softether.tar.gz
cd vpnserver
make i_read_and_agree_the_license_agreement || print_error "Failed to build SoftEther"

# Install SoftEther to /opt
print_status "Installing SoftEther to /opt..."
mkdir -p /opt/vpnserver
cp -rf * /opt/vpnserver
cd /opt/vpnserver
chmod 600 *
chmod 700 vpnserver vpncmd

# Create systemd service for SoftEther
print_status "Creating systemd service for SoftEther..."
cat > /etc/systemd/system/vpnserver.service << EOF
[Unit]
Description=SoftEther VPN Server
After=network.target

[Service]
Type=forking
ExecStart=/opt/vpnserver/vpnserver start
ExecStop=/opt/vpnserver/vpnserver stop
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Enable and start SoftEther service
systemctl enable vpnserver.service
systemctl start vpnserver.service

# Configure SoftEther VPN server
print_status "Configuring SoftEther VPN server..."
# Generate a random admin password
ADMIN_PASSWORD=$(openssl rand -base64 12)
echo "SoftEther admin password: $ADMIN_PASSWORD"

# Create initial configuration script
cat > /tmp/vpn_init.txt << EOF
ServerPasswordSet ${ADMIN_PASSWORD}
HubCreate DEFAULT /PASSWORD:${ADMIN_PASSWORD}
Hub DEFAULT
SecureNatEnable
DhcpSet
UserCreate vpnuser /GROUP:none /REALNAME:none /NOTE:none
UserPasswordSet vpnuser /PASSWORD:${shadowsocks_password}
BridgeCreate DEFAULT /DEVICE:soft /TAP:yes
ListenerCreate 443
ListenerList
SstpEnable yes
OpenVpnEnable yes /PORTS:1194
IPsecEnable
DynamicDnsSetHostname ${softether_hostname}
VpnOverIcmpDnsEnable /ICMP:yes /DNS:yes
ServerCertRegenerate ${softether_hostname}
SyslogDisable
EOF

# Apply the configuration
/opt/vpnserver/vpncmd /SERVER localhost /ADMINHUB:DEFAULT /IN:/tmp/vpn_init.txt > /dev/null

# Install Shadowsocks
print_status "Installing Shadowsocks..."
pacman -S --noconfirm shadowsocks-libev || print_error "Failed to install Shadowsocks"

# Configure Shadowsocks
print_status "Configuring Shadowsocks..."
cat > /etc/shadowsocks/config.json << EOF
{
    "server":"0.0.0.0",
    "server_port":443,
    "password":"${shadowsocks_password}",
    "timeout":300,
    "method":"chacha20-ietf-poly1305",
    "fast_open":true,
    "nameserver":"8.8.8.8",
    "mode":"tcp_and_udp"
}
EOF

# Create systemd service for Shadowsocks
print_status "Creating systemd service for Shadowsocks..."
cat > /etc/systemd/system/shadowsocks-libev-server@config.service << EOF
[Unit]
Description=Shadowsocks-Libev Server Service
After=network.target

[Service]
Type=simple
User=nobody
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
ExecStart=/usr/bin/ss-server -c /etc/shadowsocks/config.json
Restart=on-failure
LimitNOFILE=32768

[Install]
WantedBy=multi-user.target
EOF

# Enable and start Shadowsocks service
systemctl enable shadowsocks-libev-server@config.service
systemctl start shadowsocks-libev-server@config.service

# Configure firewall (using iptables-nft)
print_status "Configuring firewall..."
# Allow SSH
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
# Allow VPN traffic
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -p udp --dport 443 -j ACCEPT
iptables -A INPUT -p tcp --dport 1194 -j ACCEPT
iptables -A INPUT -p udp --dport 1194 -j ACCEPT
# Allow ICMP for VPN over ICMP
iptables -A INPUT -p icmp -j ACCEPT
# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
# Allow loopback
iptables -A INPUT -i lo -j ACCEPT
# Drop all other incoming traffic
iptables -A INPUT -j DROP
# Allow all outgoing traffic
iptables -A OUTPUT -j ACCEPT

# Save iptables rules
mkdir -p /etc/iptables
iptables-save > /etc/iptables/rules.v4

# Create service to load iptables rules on boot
cat > /etc/systemd/system/iptables-restore.service << EOF
[Unit]
Description=Restore iptables rules
Before=network-pre.target
Wants=network-pre.target

[Service]
Type=oneshot
ExecStart=/usr/sbin/iptables-restore /etc/iptables/rules.v4
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

systemctl enable iptables-restore.service

# Enable IP forwarding
print_status "Enabling IP forwarding..."
echo "net.ipv4.ip_forward = 1" > /etc/sysctl.d/30-ipforward.conf
sysctl -p /etc/sysctl.d/30-ipforward.conf

# Create a script to update dynamic DNS for Shadowsocks
print_status "Creating dynamic DNS update script for Shadowsocks..."
cat > /opt/update_shadowsocks_dns.sh << EOF
#!/bin/bash
# This script updates the Shadowsocks configuration with the current IP address
# for the dynamic hostname

HOSTNAME="${shadowsocks_hostname}"
IP=\$(dig +short \${HOSTNAME})

if [ -n "\${IP}" ]; then
    # Update Shadowsocks config
    sed -i "s/\"server\":\"[^\"]*\"/\"server\":\"\${IP}\"/" /etc/shadowsocks/config.json
    systemctl restart shadowsocks-libev-server@config.service
    echo "Updated Shadowsocks IP to \${IP} at \$(date)" >> /var/log/shadowsocks_dns_update.log
else
    echo "Failed to resolve \${HOSTNAME} at \$(date)" >> /var/log/shadowsocks_dns_update.log
fi
EOF

chmod +x /opt/update_shadowsocks_dns.sh

# Create a cron job to update the DNS every hour
print_status "Creating cron job for DNS updates..."
echo "0 * * * * root /opt/update_shadowsocks_dns.sh" > /etc/cron.d/shadowsocks_dns_update

# Final cleanup of any leftover files
print_status "Performing final cleanup..."
rm -f /tmp/vpn_init.txt
rm -f /tmp/softether.tar.gz

# Final status
print_status "Installation completed!"
print_status "SoftEther VPN is running on port 443 with hostname: ${softether_hostname}"
print_status "Shadowsocks is running on port 443 with hostname: ${shadowsocks_hostname}"
print_status "SoftEther admin password: ${ADMIN_PASSWORD}"
print_status "VPN and Shadowsocks user password: ${shadowsocks_password}"
print_status "Please save these credentials in a secure location."

# Save credentials to a file
print_status "Saving credentials to /root/vpn_credentials.txt..."
cat > /root/vpn_credentials.txt << EOF
# VPN Credentials - KEEP THIS FILE SECURE
# Generated on $(date)

SoftEther Hostname: ${softether_hostname}
Shadowsocks Hostname: ${shadowsocks_hostname}
SoftEther Admin Password: ${ADMIN_PASSWORD}
VPN/Shadowsocks User Password: ${shadowsocks_password}

# Connection Information
SoftEther VPN Server: ${softether_hostname}:443
Shadowsocks Server: ${shadowsocks_hostname}:443
Shadowsocks Encryption Method: chacha20-ietf-poly1305
EOF

chmod 600 /root/vpn_credentials.txt

# Reboot recommendation
print_warning "It is recommended to reboot your system to ensure all changes take effect."
read -p "Would you like to reboot now? (y/n): " choice
if [[ "$choice" =~ ^[Yy]$ ]]; then
    reboot
fi