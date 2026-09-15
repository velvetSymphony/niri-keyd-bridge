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


def init_add_browser_ids(browser_ids, BROWSERS, window_item):
    if window_item['app_id'] in BROWSERS:
        browser_ids.add(window_item['id'])


def check_window_id(browser_ids, window_id):
    return True if window_id in browser_ids else False


def apply_browser_keyd_config():
    subprocess.run(['keyd', 'bind', 'meta+alt.left = C-S-tab', 'meta+alt.right = C-tab'])


def reset_global_keyd_config():
    subprocess.run(['keyd', 'bind', 'meta+alt.left = left', 'meta+alt.right = right'])


def handle_windows_changed(event, BROWSERS):
    windows = extract_windows(event, key='WindowsChanged')
    for window_item in windows:
        init_add_browser_ids(browser_ids, BROWSERS, window_item)
    print(browser_ids)


def handle_window_opened_or_changed(event, BROWSERS, browser_ids):
    window = extract_windows(event, key='WindowOpenedOrChanged')
    if window['app_id'] in BROWSERS:
        browser_ids.add(window['id'])  # if it exists, it exists right?
        apply_browser_keyd_config()
    print(f'added or changed id: {window["id"]} browser_ids: {browser_ids}')


def handle_window_focus_changed(event, browser_ids):
    window_id = event['WindowFocusChanged'].get('id')
    does_it_belong = check_window_id(browser_ids, window_id)
    if does_it_belong:
        print(f'id: {window_id} in browser_ids: {browser_ids}')
        apply_browser_keyd_config()
    else:
        print(f'id: {window_id} not in browser_ids: {browser_ids}')
        reset_global_keyd_config()


def handle_window_closed(event, browser_ids):
    window_id = event['WindowClosed'].get('id')
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
            handle_windows_changed(event, BROWSERS)

        if event.get('WindowOpenedOrChanged'):
            handle_window_opened_or_changed(event, BROWSERS, browser_ids)

        if event.get('WindowFocusChanged'):
            handle_window_focus_changed(event, browser_ids)

        if event.get('WindowClosed'):
            handle_window_closed(event, browser_ids)
