#!/bin/bash

# Load localization
source "$(dirname "$0")/locale.sh"

# Install and configure launchd agents for Watcher
PROJECT_DIR="$(cd "$(dirname "$0")"; pwd)"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"

echo "$(get_message "configuring_agents")"

# Make sure package is installed
if [ ! -f "$PROJECT_DIR/.venv/bin/watcher-capture" ]; then
    echo "❌ Watcher package not installed. Run first: ./setup.sh"
    exit 1
fi

# Create log directories if they don't exist
mkdir -p "$PROJECT_DIR/logs"

# Install launchd agents
for plist in "$PROJECT_DIR/launchd/"*.plist; do
    if [ -f "$plist" ]; then
        TARGET="$LAUNCHD_DIR/$(basename "$plist")"
        echo "$(get_message "installing_agent") $(basename "$plist")..."
        
        # Substitute project path
        sed "s#__PROJECT_PATH__#$PROJECT_DIR#g" "$plist" > "$TARGET"
        
        # Unload old agent if exists
        launchctl unload "$TARGET" 2>/dev/null
        
        # Load new agent
        launchctl load "$TARGET"
        
        if [ $? -eq 0 ]; then
            echo "$(get_message "agent_activated") $(basename "$plist")"
        else
            echo "❌ Error activating $(basename "$plist")"
        fi
    fi
done

echo ""
echo "$(get_message "agents_setup_complete")"
echo ""
echo "$(get_message "agent_status_title")"
watcher-status

echo ""
echo "$(get_message "management"):"
echo "  watcher-tray     - $(get_message "start_tray")"
echo "  watcher-status   - $(get_message "check_agents")"
echo "  watcher-devices  - $(get_message "list_cameras")"
echo "  ./uninstall_launchd.sh - $(get_message "remove_agents")"
