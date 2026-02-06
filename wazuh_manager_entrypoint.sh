#!/bin/bash
# s6-overlay script to inject configuration

echo "Executing custom n8n integration setup..."
CONFIG_FILE="/var/ossec/etc/ossec.conf"

if [ -f "$CONFIG_FILE" ]; then
    if ! grep -q "custom-n8n" "$CONFIG_FILE"; then
        echo "Injecting n8n integration block..."
        sed -i '/<\/ossec_config>/i \
  <integration> \
    <name>custom-n8n</name> \
    <hook_url>http://n8n:5678/webhook/wazuh</hook_url> \
    <alert_format>json</alert_format> \
  </integration>' "$CONFIG_FILE"
    else
        echo "n8n integration already present."
    fi
else
    echo "ERROR: $CONFIG_FILE not found. Integration injection failed."
fi

