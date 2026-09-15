#!/usr/bin/env python3

import json
import subprocess
import logging

# NOTE: If the key binds do not fire off, ensure you have a /etc/keyd/default.conf config file populated.
# NOTE: I'll probably add a check, cover it in a wrapper script.

# Set logging stuff, replace prints with it later
logging.basicConfig()
logger = logging.getLogger()


def init_add_browser_ids(browser_ids, BROWSERS, window_item):
    if window_item['app_id'] in BROWSERS:
        browser_ids.add(window_item['id'])


def apply_browser_keyd_config():
    subprocess.run(['keyd', 'bind', 'meta+alt.left = C-S-tab', 'meta+alt.right = C-tab'])


def reset_global_keyd_config():
    subprocess.run(['keyd', 'bind', 'meta+alt.left = left', 'meta+alt.right = right'])

# This function may not be required later on, once this script runs as a daemon on startup
# Only reason this is required now is cause we invoke the script manually once we have opened windows
def handle_windows_changed(event, BROWSERS, browser_ids):
    windows = event.get('WindowsChanged').get('windows')
    for window_item in windows:
        init_add_browser_ids(browser_ids, BROWSERS, window_item)
    print(browser_ids)


def handle_window_opened_or_changed(event, BROWSERS, browser_ids):
    window = event.get('WindowOpenedOrChanged').get('window')
    init_add_browser_ids(browser_ids, BROWSERS, event)
    apply_browser_keyd_config()
    print(f'added or changed id: {window["id"]} browser_ids: {browser_ids}')


def handle_window_focus_changed(event, browser_ids):
    window_id = event['WindowFocusChanged']['id']
    if window_id in browser_ids:
        print(f'id: {window_id} in browser_ids: {browser_ids}')
        apply_browser_keyd_config()
    else:
        print(f'id: {window_id} not in browser_ids: {browser_ids}')
        reset_global_keyd_config()


def handle_window_closed(event, browser_ids):
    window_id = event['WindowClosed']['id']
    browser_ids.discard(window_id)
    print(f'removed id: {window_id} from browser_ids: {browser_ids}')


if __name__ == '__main__':
    BROWSERS = {'brave-browser', 'firefox', 'chromium-browser', 'google-chrome'}
    browser_ids = set()

    proc = subprocess.Popen(
        ['niri', 'msg', '--json', 'event-stream'],
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    for line in proc.stdout:
        event = json.loads(line)

        if event.get('WindowsChanged'):
            handle_windows_changed(event, BROWSERS, browser_ids)

        if event.get('WindowOpenedOrChanged'):
            handle_window_opened_or_changed(event, BROWSERS, browser_ids)

        if event.get('WindowFocusChanged'):
            handle_window_focus_changed(event, browser_ids)

        if event.get('WindowClosed'):
            handle_window_closed(event, browser_ids)
