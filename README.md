# niri-keyd-bridge

This is WIP. Expect rough edges and breaking changes.

Per-app keybindings for [niri](https://github.com/YaLTeR/niri), using [keyd](https://github.com/rvaiya/keyd).

## What it does

The script listens to niri's window events and changes your keyd bindings depending on which window is focused.

Right now it handles one case:

| Focused window | `meta+alt+left` | `meta+alt+right` |
|---|---|---|
| A browser | previous tab (`Ctrl+Shift+Tab`) | next tab (`Ctrl+Tab`) |
| Anything else | `left` | `right` |

So the same shortcut moves between tabs in your browser and acts as a normal arrow key everywhere else.

## Requirements

- niri
- keyd, running, with a config at `/etc/keyd/default.conf`
- Python 3.10 or newer (the script uses `match`)

## Usage

I haven't packaged this yet. Run it manually:

```
./main.py
```

It logs each event it handles and each binding change to the terminal. Stop it with `Ctrl+C`.

## Configuration

There's no config file yet. Edit `main.py` directly:

- `BROWSERS` lists the `app_id`s treated as browsers. Run `niri msg windows` to find an app's `app_id`.
- `apply_browser_keyd_config` and `reset_global_keyd_config` hold the bindings.

## How it works

1. Reads events from `niri msg --json event-stream`.
2. Keeps track of which open windows are browsers.
3. When focus moves to a browser, applies the browser bindings with `keyd bind`.
4. When focus moves anywhere else, resets them to the defaults.

## Status

Improvements I've planned next:

- Reset bindings when the script exits
- Report errors from keyd
- Support per-app bindings for apps other than browsers
- Run as a daemon on login

## License

GPL-3.0. See [LICENSE](LICENSE).
