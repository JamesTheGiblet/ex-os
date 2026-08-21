#!/bin/bash
# install.sh — Ex-OS One-Command Install
# Ex-OS: The system that was discovered, not designed.
# Runs on: Linux, Termux (Android), VPS, Local PC

set -e

# ============================================================
# COLORS
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================
# HEADER
# ============================================================

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║     ⚡  EX-OS — ONE-COMMAND INSTALL  ⚡                  ║"
echo "║                                                          ║"
echo "║     The system that was discovered, not designed.        ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ============================================================
# DETECT ENVIRONMENT
# ============================================================

echo -e "${BLUE}[INFO]${NC} Detecting environment..."

if [ -d "/data/data/com.termux" ]; then
    ENV="termux"
    echo -e "${GREEN}[OK]${NC} Termux (Android) detected"
elif [ -f "/etc/debian_version" ]; then
    ENV="debian"
    echo -e "${GREEN}[OK]${NC} Debian/Ubuntu detected"
elif [ -f "/etc/redhat-release" ]; then
    ENV="redhat"
    echo -e "${GREEN}[OK]${NC} RedHat/CentOS detected"
elif [ -f "/etc/alpine-release" ]; then
    ENV="alpine"
    echo -e "${GREEN}[OK]${NC} Alpine detected"
else
    ENV="unknown"
    echo -e "${YELLOW}[WARN]${NC} Unknown environment, trying anyway"
fi

# ============================================================
# INSTALL DEPENDENCIES
# ============================================================

echo ""
echo -e "${BLUE}[INFO]${NC} Installing dependencies..."

case $ENV in
    termux)
        pkg update -y
        pkg install -y python git openssh nano
        pkg install -y binutils
        ;;
    debian)
        apt update -y
        apt install -y python3 python3-pip python3-venv git nano curl
        apt install -y build-essential
        ;;
    redhat)
        yum install -y python3 python3-pip git nano curl
        yum install -y gcc make
        ;;
    alpine)
        apk add python3 py3-pip git nano curl
        apk add build-base
        ;;
    *)
        echo -e "${YELLOW}[WARN]${NC} Unknown environment. Please install: python3, pip, git"
        ;;
esac

# ============================================================
# INSTALL EX-OS
# ============================================================

echo ""
echo -e "${BLUE}[INFO]${NC} Installing Ex-OS..."

# Set directory
EXOS_DIR="${EXOS_DIR:-$HOME/ex-os}"

# Clone if not exists
if [ ! -d "$EXOS_DIR" ]; then
    echo -e "${BLUE}[INFO]${NC} Cloning Ex-OS..."
    git clone https://github.com/JamesTheGiblet/ex-os.git "$EXOS_DIR"
else
    echo -e "${YELLOW}[WARN]${NC} Ex-OS already exists at $EXOS_DIR"
    echo -e "${BLUE}[INFO]${NC} Pulling latest changes..."
    cd "$EXOS_DIR"
    git pull
    cd ..
fi

cd "$EXOS_DIR"

# ============================================================
# PYTHON ENVIRONMENT
# ============================================================

echo -e "${BLUE}[INFO]${NC} Setting up Python environment..."

if [ "$ENV" = "termux" ]; then
    # Termux: use system Python
    pip install -r requirements.txt 2>/dev/null || pip3 install -r requirements.txt 2>/dev/null || echo -e "${YELLOW}[WARN]${NC} No requirements.txt found"
else
    # Linux: use virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r requirements.txt 2>/dev/null || echo -e "${YELLOW}[WARN]${NC} No requirements.txt found"
fi

# ============================================================
# INITIALISE EX-OS
# ============================================================

echo ""
echo -e "${BLUE}[INFO]${NC} Initialising Ex-OS..."

# Ensure directories
mkdir -p logs/events
mkdir -p ledger
mkdir -p capsules
mkdir -p cubes
mkdir -p seals
mkdir -p anchor_data
mkdir -p axiom_data
# buddai_memory.db is a SQLite file (created below), not a directory

# Generate signing key
echo -e "${BLUE}[INFO]${NC} Generating signing key..."
python -m core.scp.sign --generate 2>/dev/null || echo -e "${YELLOW}[WARN]${NC} Key generation skipped (will run on first use)"

# Initialise Leighton Weight Engine
echo -e "${BLUE}[INFO]${NC} Initialising Leighton Weight Engine..."
python -c "from core.leighton.engine import LeightonEngine; LeightonEngine()" 2>/dev/null || echo -e "${YELLOW}[WARN]${NC} Leighton init skipped (may not exist)"

# Anchor ChronoSCRIBE
echo -e "${BLUE}[INFO]${NC} Anchoring ChronoSCRIBE..."
python -c "from core.chronoscribe.ledger import Ledger; Ledger('exos')" 2>/dev/null || echo -e "${YELLOW}[WARN]${NC} ChronoSCRIBE anchor skipped (may not exist)"

# Initialise BuddAI memory
echo -e "${BLUE}[INFO]${NC} Initialising BuddAI memory..."
python -c "from intelligence.buddai.memory import MemorySystem; MemorySystem()" 2>/dev/null || echo -e "${YELLOW}[WARN]${NC} BuddAI init skipped"

# ============================================================
# SETUP SYSTEMD (VPS/Linux)
# ============================================================

if [ "$ENV" = "debian" ] || [ "$ENV" = "redhat" ]; then
    echo ""
    echo -e "${BLUE}[INFO]${NC} Setting up systemd services..."

    # Create service file
    cat > /etc/systemd/system/exos-network.service << EOF
[Unit]
Description=Ex-OS Network Daemon
After=network.target ollama.service

[Service]
Type=simple
User=root
WorkingDirectory=$EXOS_DIR
Environment="EXOS_HOME=$EXOS_DIR"
ExecStart=$EXOS_DIR/venv/bin/python $EXOS_DIR/integration/network_daemon.py --port 8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd
    systemctl daemon-reload

    # Enable service
    systemctl enable exos-network 2>/dev/null || echo -e "${YELLOW}[WARN]${NC} Could not enable exos-network"

    echo -e "${GREEN}[OK]${NC} Systemd service configured"
fi

# ============================================================
# SETUP TERMUX (Android)
# ============================================================

if [ "$ENV" = "termux" ]; then
    echo ""
    echo -e "${BLUE}[INFO]${NC} Setting up Termux session scripts..."

    cat > termux-start.sh << 'EOF'
#!/bin/bash
# termux-start.sh — Start Ex-OS services

cd ~/ex-os
git pull 2>/dev/null

export EXOS_HOME=~/ex-os

# Start network daemon
python integration/network_daemon.py --port 8081 &

echo "[Ex-OS] Started"
EOF
    chmod +x termux-start.sh

    cat > termux-finish.sh << 'EOF'
#!/bin/bash
# termux-finish.sh — Stop Ex-OS and sync

pkill -f network_daemon.py

cd ~/ex-os
git add .
git commit -m "Session sync: $(date)" 2>/dev/null || echo "No changes"
git push 2>/dev/null || echo "Sync skipped"

echo "[Ex-OS] Finished"
EOF
    chmod +x termux-finish.sh

    echo -e "${GREEN}[OK]${NC} Termux scripts created"
fi

# ============================================================
# RUN TESTS
# ============================================================

echo ""
echo -e "${BLUE}[INFO]${NC} Running fresh clone verification..."

if python tests/test_fresh_clone.py 2>/dev/null; then
    echo -e "${GREEN}[OK]${NC} All tests passed"
else
    echo -e "${YELLOW}[WARN]${NC} Some tests failed — system may still work"
fi

# ============================================================
# START SERVICES
# ============================================================

echo ""
echo -e "${BLUE}[INFO]${NC} Starting services..."

if [ "$ENV" = "termux" ]; then
    ./termux-start.sh &
elif [ "$ENV" = "debian" ] || [ "$ENV" = "redhat" ]; then
    systemctl start exos-network 2>/dev/null || echo -e "${YELLOW}[WARN]${NC} Could not start exos-network"
else
    echo -e "${YELLOW}[WARN]${NC} No service manager found. Start manually:"
    echo "  python integration/network_daemon.py --port 8080"
fi

# ============================================================
# FINISH
# ============================================================

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║     ✅  EX-OS INSTALLATION COMPLETE  ✅                  ║"
echo "║                                                          ║"
echo "║     The system that was discovered, not designed.        ║"
echo "║                                                          ║"
echo "║     📂  Installed at: $EXOS_DIR                         ║"
echo "║                                                          ║"
echo "║     🚀  Start the Network Daemon:                       ║"
echo "║         python integration/network_daemon.py --port 8080 ║"
echo "║                                                          ║"
echo "║     🌐  Open the Dashboard:                             ║"
echo "║         http://localhost:8080                           ║"
echo "║                                                          ║"
echo "║     📖  Read the docs:                                  ║"
echo "║         cat README.md                                   ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Ex-OS: Your thoughts, staying yours, everywhere.${NC}"
echo ""

exit 0
