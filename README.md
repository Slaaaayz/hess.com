# Installation Guide - Honeypot Infrastructure

## Table of Contents
- [VM Setup](#vm-setup)
- [Dependencies Installation](#dependencies-installation)
- [Cowrie Honeypot Setup](#cowrie-honeypot-setup)
- [API Integration](#api-integration)
- [Testing](#testing)

## VM Setup

### Requirements
- 2 CPU cores
- 4GB RAM
- 15GB storage
- Rocky Linux distribution

## Dependencies Installation

```bash
# Update system
sudo dnf update
sudo dnf upgrade

# Install required packages
sudo dnf install python3 python3-pip git

# Install virtualenv
python -m pip install --user virtualenv
```

## Cowrie Honeypot Setup

### User Setup
```bash
# Create dedicated user
sudo useradd -r -m -s /bin/bash cowrie
sudo su - cowrie
```

### Cowrie Installation
```bash
# Clone repository
git clone https://github.com/cowrie/cowrie.git
cd cowrie

# Create Python environment
python3 -m venv cowrie-env
source cowrie-env/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure Cowrie
cp etc/cowrie.cfg.dist etc/cowrie.cfg

# Start Cowrie
bin/cowrie start

# Exit cowrie user
exit
```

### Firewall Configuration
```bash
# Allow SSH port
sudo firewall-cmd --permanent --add-port=2222/tcp
sudo firewall-cmd --reload
```

## API Integration

### Server Setup
Create a file named `send_logs.py` with the following content:

```python
import json
import requests

API_URL = "http://<FLASK_SERVER_IP>:5000"  # Replace with your Flask server IP
LOG_FILE = "/home/cowrie/cowrie/var/log/cowrie/cowrie.json"

def send_logs():
    with open(LOG_FILE, "r") as f:
        for line in f:
            try:
                log = json.loads(line)
                requests.post(API_URL, json=log)
            except Exception as e:
                print("Error:", e)

if __name__ == "__main__":
    send_logs()
```

## Testing

### Generate Traffic
1. From your local machine:
```bash
ssh root@<VM_IP> -p 2222
```

2. On the VM:
```bash
sudo python3 send_logs.py
```

### View Logs
1. Run the Flask application (`app.py`)
2. Access the logs through your web browser at `/log` endpoint


