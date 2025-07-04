#!/usr/bin/env python3
import subprocess
from .locale import _

def check(label):
    try:
        result = subprocess.run(['launchctl', 'list'], capture_output=True, text=True)
        lines = result.stdout.splitlines()
        found = any(label in line for line in lines)
        status = _('agent_running') if found else _('agent_not_running')
        print(f"🔎 {label}: {status}")
    except Exception as e:
        print(f"{_('error')}: {e}")

def main():
    print(_('agents_status'))
    print("=" * 40)
    check("com.watcher.capture")
    check("com.watcher.merge_send")

if __name__ == "__main__":
    main()