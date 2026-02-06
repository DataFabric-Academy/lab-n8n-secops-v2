#!/bin/bash

# Default to wazuh-manager if not set
WAZUH_MANAGER="${WAZUH_MANAGER:-wazuh.manager}"

echo "Waiting for Wazuh Manager ($WAZUH_MANAGER) to be ready..."
# Simple wait loop (could be improved with netcat)
sleep 10

echo "Registering Wazuh Agent..."
/var/ossec/bin/agent-auth -m $WAZUH_MANAGER

echo "Starting Wazuh Agent..."
/var/ossec/bin/wazuh-control start

echo "Starting Main Application..."
exec "$@"
