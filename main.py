#!/usr/bin/env python3

import json
import logging
import subprocess

# NOTE: If the key binds do not fire off, ensure you have a /etc/keyd/default.conf config file populated.
# NOTE: I'll probably add a check, cover it in a wrapper script.

# Set logger object, replace prints with it later
logging.basicConfig()
logger = logging.getLogger()


def is_browser_window(BROWSERS, window_item):
    return window_item['app_id'] in BROWSERS


def is_window_id_in_browser_id(browser_ids, window_id):
    return window_id in browser_ids


def apply_browser_keyd_config():
    subprocess.run(['keyd', 'bind', 'meta+alt.left = C-S-tab', 'meta+alt.right = C-tab'])


def reset_global_keyd_config():
    subprocess.run(['keyd', 'bind', 'meta+alt.left = left', 'meta+alt.right = right'])


# This function may not be required later on, once this script runs as a daemon on startup
# Only reason this is required now is cause we invoke the script manually once we have opened windows
# The event only fires once
def handle_windows_changed(windows, BROWSERS, browser_ids):
    for window_item in windows:
        if is_browser_window(BROWSERS, window_item=window_item):
            browser_ids.add(window_item['id'])
    print(browser_ids)



def handle_window_opened_or_changed(window, BROWSERS, browser_ids):
    if is_browser_window(BROWSERS, window_item=window):
        browser_ids.add(window['id'])
        apply_browser_keyd_config()
    print(f'added or changed id: {window["id"]} browser_ids: {browser_ids}')


def handle_window_focus_changed(window_id, browser_ids):
    if is_window_id_in_browser_id(browser_ids, window_id):
        print(f'id: {window_id} in browser_ids: {browser_ids}')
        apply_browser_keyd_config()
    else:
        print(f'id: {window_id} not in browser_ids: {browser_ids}')
        reset_global_keyd_config()


def handle_window_closed(window_id, browser_ids):
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
        key = next(iter(event))
        match key:
            case 'WindowsChanged':
                windows = event.get(key).get('windows')
                handle_windows_changed(windows, BROWSERS, browser_ids)
            case 'WindowOpenedOrChanged':
                window = event.get('WindowOpenedOrChanged').get('window')
                handle_window_opened_or_changed(window, BROWSERS, browser_ids)
            case 'WindowFocusChanged':
                window_id = event['WindowFocusChanged']['id']
                handle_window_focus_changed(window_id, browser_ids)
            case 'WindowClosed':
                window_id = event['WindowClosed']['id']
                handle_window_closed(window_id, browser_ids)
