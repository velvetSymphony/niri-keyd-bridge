#!/usr/bin/env python3

import json
import subprocess

# NOTE: If the key binds do not fire off, ensure you have a /etc/keyd/default.conf config file populated.
# NOTE: I'll probably add a check, cover it in a wrapper script.


def extract_windows(event, key):
    match key:
        case 'WindowsChanged':
            return event.get('WindowsChanged').get('windows')
        case 'WindowOpenedOrChanged':
            return event.get('WindowOpenedOrChanged').get('window')


def init_add_browser_ids(BROWSER_IDS, window_item):
    if window_item['app_id'] in BROWSERS:
        BROWSER_IDS.add(window_item['id'])


def check_window_id(BROWSER_IDS, window_id):
    return True if window_id in BROWSER_IDS else False


def apply_browser_keyd_config():
    subprocess.run(['keyd', 'bind', 'meta+alt.left = C-S-tab', 'meta+alt.right = C-tab'])


def reset_global_keyd_config():
    subprocess.run(['keyd', 'bind', 'meta+alt.left = left', 'meta+alt.right = right'])


if __name__ == '__main__':
    BROWSERS = {'brave-browser', 'firefox', 'chromium-browser', 'google-chrome'}
    BROWSER_IDS = set()

    proc = subprocess.Popen(
        ['niri', 'msg', '--json', 'event-stream'],
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    for line in proc.stdout:
        event = json.loads(line)
        if event.get('WindowsChanged'):
            windows = extract_windows(event, key='WindowsChanged')
            for window_item in windows:
                init_add_browser_ids(BROWSER_IDS, window_item)
            print(BROWSER_IDS)
        if event.get('WindowOpenedOrChanged'):
            window = extract_windows(event, key='WindowOpenedOrChanged')
            window_id = window['id']
            if window.get('app_id') in BROWSERS:
                BROWSER_IDS.add(window_id)  # if it exists, it exists right?
                apply_browser_keyd_config()
            print(f'added or changed id: {window_id} BROWSER_IDS: {BROWSER_IDS}')
        if event.get('WindowFocusChanged'):
            window_id = event['WindowFocusChanged'].get('id')
            does_it_belong = check_window_id(BROWSER_IDS, window_id)
            if does_it_belong:
                print(f'id: {window_id} in BROWSER_IDS: {BROWSER_IDS}')
                apply_browser_keyd_config()
            else:
                print(f'id: {window_id} not in BROWSER_IDS: {BROWSER_IDS}')
                reset_global_keyd_config()

        if event.get('WindowClosed'):
            window_id = event['WindowClosed'].get('id')
            BROWSER_IDS.discard(window_id)
            print(f'removed id: {window_id} from BROWSER_IDS: {BROWSER_IDS}')
