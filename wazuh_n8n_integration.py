#!/usr/bin/env python3
import sys
import json
import urllib.request
import urllib.error

# Wazuh passes: script alertFILE api_key hook_url
try:
    alert_file = sys.argv[1]
    # Check args for URL. It's usually arg 3, but let's be flexible.
    # Arg 0 is script name.
    hook_url = "http://n8n:5678/webhook/wazuh" # Default
    if len(sys.argv) > 3:
        hook_url = sys.argv[3]
    elif len(sys.argv) > 2 and sys.argv[2].startswith("http"):
        hook_url = sys.argv[2]
        
    print(f"Sending alert to: {hook_url}")
    
except Exception as e:
    print(f"Error reading arguments: {e}")
    sys.exit(1)

# Read Alert
try:
    with open(alert_file) as f:
        alert_json = json.load(f)
except Exception as e:
    print(f"Error reading alert file: {e}")
    sys.exit(1)

# Send to n8n
try:
    req = urllib.request.Request(hook_url)
    req.add_header('Content-Type', 'application/json')
    # req.add_header('User-Agent', 'Wazuh-n8n-Integration')
    
    jsondata = json.dumps(alert_json).encode('utf-8')
    req.add_header('Content-Length', len(jsondata))
    
    response = urllib.request.urlopen(req, jsondata)
    print(f"Response: {response.getcode()}")
    
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.reason}")
    sys.exit(1)
except Exception as e:
    print(f"Error sending request: {e}")
    sys.exit(1)

sys.exit(0)
