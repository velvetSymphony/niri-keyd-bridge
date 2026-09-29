#!/usr/bin/env python3

import json
import logging
import subprocess

# NOTE: If the key binds do not fire off, ensure you have a /etc/keyd/default.conf config file populated.
# NOTE: I'll probably add a check, cover it in a wrapper script.

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)
logger = logging.getLogger(__name__)


def is_browser_window(window_item, BROWSERS):
    return window_item['app_id'] in BROWSERS


def is_window_id_in_browser_id(window_id, browser_ids):
    return window_id in browser_ids


def apply_browser_keyd_config():
    subprocess.run(['keyd', 'bind', 'meta+alt.left = C-S-tab', 'meta+alt.right = C-tab'])


def reset_global_keyd_config():
    subprocess.run(['keyd', 'bind', 'meta+alt.left = left', 'meta+alt.right = right'])


def handle_window_opened_or_changed(window, BROWSERS, browser_ids):
    if is_browser_window(window, BROWSERS):
        browser_ids.add(window['id'])
        if window['is_focused']:
            apply_browser_keyd_config()
    logger.info(f'added or changed id: {window["id"]} browser_ids: {browser_ids}')


def handle_window_focus_changed(window_id, browser_ids):
    if is_window_id_in_browser_id(window_id, browser_ids):
        logger.info(f'id: {window_id} in browser_ids: {browser_ids}')
        apply_browser_keyd_config()
    else:
        logger.info(f'id: {window_id} not in browser_ids: {browser_ids}')
        reset_global_keyd_config()


def handle_window_closed(window_id, browser_ids):
    browser_ids.discard(window_id)
    logger.info(f'removed id: {window_id} from browser_ids: {browser_ids}')


def process(event, BROWSERS, browser_ids):
    key = next(iter(event))
    logger.info(f' Processing key: {key}')
    match key:
        case 'WindowsChanged':
            windows = event[key]['windows']
            reset_global_keyd_config()
            for window in windows:
                handle_window_opened_or_changed(window, BROWSERS, browser_ids)
        case 'WindowOpenedOrChanged':
            window = event[key]['window']
            handle_window_opened_or_changed(window, BROWSERS, browser_ids)
        case 'WindowFocusChanged':
            window_id = event[key]['id']
            handle_window_focus_changed(window_id, browser_ids)
        case 'WindowClosed':
            window_id = event[key]['id']
            handle_window_closed(window_id, browser_ids)


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
        print(event)
        process(event, BROWSERS, browser_ids)
