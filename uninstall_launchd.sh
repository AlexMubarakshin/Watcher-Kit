#!/bin/bash

# Load localization
source "$(dirname "$0")/locale.sh"

# Remove launchd agents for Watcher
PROJECT_DIR="$(cd "$(dirname "$0")"; pwd)"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"

echo "$(get_message "removing_agents")"

for plist in "$PROJECT_DIR/launchd/"*.plist; do
    if [ -f "$plist" ]; then
        TARGET="$LAUNCHD_DIR/$(basename "$plist")"
        if [ -f "$TARGET" ]; then
            echo "$(get_message "removing_agent") $(basename "$plist")..."
            launchctl unload "$TARGET" 2>/dev/null
            rm "$TARGET"
            echo "$(get_message "agent_removed") $(basename "$plist")"
        else
            echo "$(get_message "agent_not_found") $(basename "$plist")"
        fi
    fi
done

echo ""
echo "$(get_message "removal_complete")"
echo ""
echo "$(get_message "agent_status_title")"
watcher-status
