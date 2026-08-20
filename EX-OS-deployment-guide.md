# Ex-OS — Deployment Guide

---

## 1. Overview

Ex-OS can be deployed across multiple hardware targets:

| Target | Purpose | Difficulty |
| **VPS (Hetzner CX22)** | Always-on cloud brain | ⭐⭐ |
| **Local PC (Linux/Windows)** | Development environment | ⭐ |
| **UEFI USB** | Bare-metal boot, sovereignty | ⭐⭐⭐ |
| **ESP32-C3/C6** | Edge sensory nodes | ⭐⭐⭐ |
| **S24 Ultra (Termux)** | Mobile edge development | ⭐⭐ |

---

## 2. VPS Deployment (Hetzner CX22)

### 2.1 Prerequisites

| Requirement | Specification |
| **OS** | Ubuntu 24.04 LTS |
| **CPU** | 2 vCPUs |
| **RAM** | 4GB |
| **Storage** | 35GB |
| **Network** | Public IP, port 8080 open |
| **Domain** | (Optional) DNS A record |

### 2.2 Quick Install (One Command)

```bash
curl -sSL https://raw.githubusercontent.com/JamesTheGiblet/Ex-OS/main/install.sh | bash
```

### 2.3 Manual Install (Step by Step)

#### Step 1: Clone Repositories

```bash
cd /root

# Clone core
git clone https://github.com/JamesTheGiblet/UBVM-os
git clone https://github.com/JamesTheGiblet/mimir

# Clone optional components
git clone https://github.com/JamesTheGiblet/BuddAI
git clone https://github.com/JamesTheGiblet/replicant
git clone https://github.com/JamesTheGiblet/anchor
git clone https://github.com/JamesTheGiblet/axiom

# Set environment
export UBVM_HOME=/root/UBVM-os
export MIMIR_HOME=/root/mimir
```

#### Step 2: Install Python Dependencies

```bash
# Update package lists
apt update
apt install -y python3 python3-pip python3-venv git

# Install core requirements
cd $UBVM_HOME
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install Mimir requirements
cd $MIMIR_HOME
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Step 3: Install Ollama (LLM Server)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull gemma2:2b      # For BuddAI
ollama pull qwen2.5-coder:3b  # For Mimir (optional)
ollama pull phi3:mini       # For Mimir (optional)

# Set environment variables
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=gemma2:2b
```

#### Step 4: Initialize Leighton Weight Engine

```bash
cd $UBVM_HOME

# Initialize with default parameters
python leighton_weight.py init \
    --k-per-day 0.01 \
    --beta-plus 0.10 \
    --rho 2.0 \
    --sigma 3.0

# Verify initialization
python leighton_weight.py status
```

#### Step 5: Anchor ChronoSCRIBE Root Ledger

```bash
cd $UBVM_HOME

# Create root ledger
python ledger.py anchor-root

# Verify anchor
python ledger.py status

# Expected output:
# Root anchored: yes
# Anchor hash: <sha256>
# Consumer ledgers: 0
```

#### Step 6: Create Systemd Services

Create `/etc/systemd/system/exos-network.service`:

```ini
[Unit]
Description=Ex-OS Network Daemon
After=network.target ollama.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/UBVM-os
Environment="UBVM_HOME=/root/UBVM-os"
Environment="OLLAMA_HOST=http://localhost:11434"
Environment="OLLAMA_MODEL=gemma2:2b"
ExecStart=/root/UBVM-os/venv/bin/python /root/UBVM-os/network_daemon.py 8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/exos-scheduler.service`:

```ini
[Unit]
Description=Ex-OS Scheduler Daemon
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/UBVM-os
Environment="UBVM_HOME=/root/UBVM-os"
ExecStart=/root/UBVM-os/venv/bin/python /root/UBVM-os/scheduler_daemon.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/mimir-api.service`:

```ini
[Unit]
Description=Mimir API Service
After=network.target ollama.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/mimir
Environment="UBVM_HOME=/root/UBVM-os"
Environment="OLLAMA_HOST=http://localhost:11434"
Environment="MIMIR_MODEL=mimir-phi3"
ExecStart=/root/mimir/venv/bin/python /root/mimir/cli/mimir-web.py --host 0.0.0.0 --port 5001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Step 7: Start Services

```bash
# Reload systemd
systemctl daemon-reload

# Enable services
systemctl enable exos-network exos-scheduler mimir-api

# Start services
systemctl start exos-network exos-scheduler mimir-api

# Check status
systemctl status exos-network exos-scheduler mimir-api
```

#### Step 8: Configure Nginx (Optional)

```bash
# Install Nginx
apt install -y nginx

# Create configuration
cat > /etc/nginx/sites-available/exos << 'EOF'
server {
    listen 80;
    server_name 178.105.96.89;  # Replace with your IP/domain

    # Main dashboard
    location / {
        proxy_pass http://127.0.0.1:8080/dashboard;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:8080/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Mimir
    location /mimir/ {
        proxy_pass http://127.0.0.1:5001/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Ledger explorer
    location /ledger {
        proxy_pass http://127.0.0.1:8080/api/ledger;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/exos /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default

# Test and restart
nginx -t
systemctl restart nginx
```

### 2.4 Verification

```bash
# Check services
curl http://localhost:8080/api/status

# Expected response:
# {
#   "status": "ok",
#   "ubvm": "1.0",
#   "capsules": 88,
#   "extensions": 11,
#   "primitives": 73,
#   "memory": {"short": 0, "long": 83}
# }

# Check dashboard
# Open http://178.105.96.89 in browser
```

---

## 3. UEFI USB Boot (Bare-Metal)

### 3.1 Prerequisites

| Requirement | Specification |
| **Hardware** | x86_64 PC with UEFI |
| **USB** | FAT32 formatted, ≥ 2GB |
| **Build System** | Linux or MSYS2 (Windows) |

### 3.2 Build Bootloader

```bash
# Clone UBVM-OS
git clone https://github.com/JamesTheGiblet/UBVM-OS
cd UBVM-OS

# Build UEFI bootloader
make bootx64.efi

# Expected output:
# Compiling kernel.c...
# Linking bootx64.efi...
# Done.
```

### 3.3 Prepare USB

```bash
# Format USB as FAT32
sudo mkfs.vfat -F 32 /dev/sdX1  # Replace sdX with your USB device

# Create EFI directory structure
sudo mkdir -p /media/usb/EFI/BOOT

# Copy bootloader
sudo cp bootx64.efi /media/usb/EFI/BOOT/

# Copy capsules
sudo cp -r capsules /media/usb/

# Copy root SCP
sudo cp root.scp.json /media/usb/

# Unmount USB
sudo umount /media/usb
```

### 3.4 Boot

1. **Insert USB** into target PC
2. **Enter BIOS** (F2/DEL/ESC during boot)
3. **Disable Secure Boot** (if required)
4. **Set UEFI: USB Drive** as first boot device
5. **Save and reboot**

### 3.5 Expected Output

```txt
[UEFI] BOOTX64.EFI loaded
[UEFI] SCP root loaded: root.scp.json
[UEFI] Found 88 capsules
[UEFI] Running on_load capsules...
[UEFI] ChronoSCRIBE anchored
[UEFI] HAL seal ready
[UEFI] System ready
```

---

## 4. ESP32-C3/C6 Edge Node

### 4.1 Prerequisites

| Requirement | Specification |
| **Hardware** | ESP32-C3 or ESP32-C6 |
| **Toolchain** | esptool.py, Micropython v1.28.0+ |
| **Network** | WiFi access point |

### 4.2 Flash Micropython

```bash
# Download firmware
wget https://micropython.org/resources/firmware/ESP32_GENERIC_C3-20241025-v1.24.0.bin

# Flash firmware
esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x0 firmware.bin

# Wait for flash complete
```

### 4.3 Upload Edge Firmware

```bash
# Upload edge script
python ubvm_edge.py --upload /dev/ttyUSB0

# Or manually copy
ampy --port /dev/ttyUSB0 put ubvm_edge.py main.py
ampy --port /dev/ttyUSB0 put ubvm_edge.h
ampy --port /dev/ttyUSB0 put ubvm_edge.c
```

### 4.4 Configure WiFi

```bash
# Connect to ESP32 via serial
screen /dev/ttyUSB0 115200

# Configure WiFi
>>> import network
>>> wlan = network.WLAN(network.STA_IF)
>>> wlan.active(True)
>>> wlan.connect('SSID', 'PASSWORD')
>>> wlan.isconnected()
True

# Set server IP
>>> import ubvm_edge
>>> ubvm_edge.set_server('192.168.1.130', 8080)
```

### 4.5 Verification

```bash
# Check network daemon logs
tail -f /root/UBVM-os/logs/events/queue.jsonl

# Press button on ESP32
# Expected event:
# {"event": "sensor.button.press", "source": "esp32-001", ...}
```

---

## 5. S24 Ultra (Termux) Edge

### 5.1 Prerequisites

| Requirement | Specification |
| **Hardware** | Android device |
| **App** | Termux (F-Droid version) |
| **Permissions** | Storage, Network |

### 5.2 Install Termux

```bash
# Open Termux
pkg update
pkg upgrade

# Install dependencies
pkg install python git openssh
```

### 5.3 Clone and Configure

```bash
# Clone repos
git clone https://github.com/JamesTheGiblet/UBVM-os
cd UBVM-os

# Install Python packages
pip install -r requirements.txt

# Set environment
export UBVM_HOME=$HOME/UBVM-os
export OLLAMA_HOST=http://192.168.1.130:11434
```

### 5.4 Start Services

```bash
# Start edge node
python edge_node.py --ip 192.168.1.130 --port 8080

# Expected output:
# [EDGE] Connected to 192.168.1.130:8080
# [EDGE] Transmitting 96-byte packets
```

### 5.5 Session Scripts

```bash
# Create start script
cat > termux-start.sh << 'EOF'
#!/bin/bash
cd ~/UBVM-os
git pull
export UBVM_HOME=$HOME/UBVM-os
export OLLAMA_HOST=http://192.168.1.130:11434
python edge_node.py --ip 192.168.1.130 --port 8080 &
EOF

chmod +x termux-start.sh

# Create finish script
cat > termux-finish.sh << 'EOF'
#!/bin/bash
pkill -f edge_node.py
cd ~/UBVM-os
git add .
git commit -m "Session sync: $(date)"
git push
EOF

chmod +x termux-finish.sh
```

---

## 6. Troubleshooting

### 6.1 VPS Common Issues

| Issue | Solution |
| **Port 8080 already in use** | `sudo netstat -tulpn | grep 8080` → kill process |
| **Ollama not responding** | `systemctl status ollama` → `systemctl restart ollama` |
| **Permission denied** | `chmod +x $UBVM_HOME/venv/bin/python` |
| **Module not found** | `pip install -r requirements.txt` |

### 6.2 UEFI Boot Issues

| Issue | Solution |
| **Secure Boot blocks** | Disable Secure Boot in BIOS |
| **USB not recognized** | Use FAT32 format, MBR partition |
| **No output** | Check UEFI display settings |

### 6.3 ESP32 Issues

| Issue | Solution |
| **Flash failed** | Check USB cable, try lower baud rate |
| **WiFi not connecting** | Check SSID/PASSWORD |
| **No events** | Check server IP and port |

### 6.4 Fresh Clone Verification

> *"Verifies on a fresh clone is the real test."*

```bash
# Clone fresh
cd /tmp
git clone https://github.com/JamesTheGiblet/Ex-OS
cd Ex-OS

# Install fresh
pip install -r requirements.txt

# Run tests
python ubvm test
python -m pytest tests/
python cli.py qa
```

---

## 7. Quick Reference

### 7.1 Environment Variables

| Variable | Default | Description |
| `UBVM_HOME` | `~/UBVM-os` | UBVM root directory |
| `MIMIR_HOME` | `~/mimir` | Mimir root directory |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama endpoint |
| `OLLAMA_MODEL` | `gemma2:2b` | Default model |
| `UBC_ALLOW_EXEC` | `0` | Enable shell exec |
| `EXOS_NODE_ID` | Auto-detected | Node identity |

### 7.2 Ports

| Port | Service |
| **8080** | Ex-OS Network Daemon |
| **5001** | Mimir API |
| **11434** | Ollama |
| **80** | Nginx (optional) |

### 7.3 Key Files

| File | Location | Purpose |
| `interpreter.py` | `$UBVM_HOME/` | Core runtime |
| `network_daemon.py` | `$UBVM_HOME/` | API server |
| `scheduler_daemon.py` | `$UBVM_HOME/` | Cron + events |
| `queue.jsonl` | `$UBVM_HOME/logs/events/` | Event bus |
| `ledger.jsonl` | `$UBVM_HOME/ledger/` | ChronoSCRIBE |
| `capsules/` | `$UBVM_HOME/` | SCP capsules |
| `memory.db` | `$BUDDAI_HOME/` | SQLite memory |

---

## 8. Verification Checklist

### 8.1 VPS

- [ ] Services running (`systemctl status exos-*`)
- [ ] Dashboard accessible (`http://<ip>/`)
- [ ] API responding (`curl http://localhost:8080/api/status`)
- [ ] ChronoSCRIBE anchored (`python ledger.py status`)
- [ ] Leighton Weight initialized (`python leighton_weight.py status`)
- [ ] Ollama responding (`curl http://localhost:11434/api/tags`)
- [ ] 88 capsules loaded (`python ubvm test`)

### 8.2 USB

- [ ] Bootloader compiles (`make bootx64.efi`)
- [ ] USB formatted FAT32
- [ ] `BOOTX64.EFI` in `/EFI/BOOT/`
- [ ] Capsules copied to USB
- [ ] PC boots from USB
- [ ] Console output visible

### 8.3 ESP32

- [ ] Firmware flashed
- [ ] WiFi connected
- [ ] Server IP configured
- [ ] Button press emits event
- [ ] Event appears in queue.jsonl

---

*Ex-OS: Your thoughts, staying yours, everywhere, verified, audited, and trusted.*
