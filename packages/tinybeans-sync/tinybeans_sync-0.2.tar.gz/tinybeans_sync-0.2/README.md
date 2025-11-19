# tinybeans-sync

Downloads original quality images from Tinybeans photo journals.

### Quickstart

From [PyPI](https://pypi.org/project/tinybeans-sync/):

```bash
pip install tinybeans-sync
```

Or from source:

```bash
git clone https://github.com/brege/tinybeans-sync.git
cd tinybeans-sync
pip install .
```

Test it out:

```bash
tinybeans-sync --help
```

After copying [`config.yaml.example`](./config.yaml.example) to `~/.config/tinybeans-sync/config.yaml`, fill in your 
- **email**
- **password**
- **tinybeans_id** (you can get this from journal URLs)

You should also configure the download path for all of photos.
```yaml
download:
  output_dir: downloads  # relative to this project dir, or absolute path
```

## Automated syncing with systemd

To run tinybeans-sync automatically every 12 hours, use the provided systemd timer:

```bash
bash <(curl https://raw.githubusercontent.com/brege/tinybeans-sync/refs/heads/main/systemd/install.sh)
```

This will
- Download and install the systemd service and timer files
- Replace placeholders with your username and group
- Enable the timer to check every 12 hours, relative to boot time

This install script can be found in [GitHub](https://github.com/brege/tinybeans-sync/blob/main/systemd/install.sh).

Timer status:
```bash
systemctl status tinybeans-sync.timer
systemctl list-timers
journalctl -u tinybeans-sync.service
```

## Usage

Options:
```bash
tinybeans-sync --help
```

Download images from last successful run date onwards:
```bash
tinybeans-sync --from-last-date
```

Download a date range:
```bash
tinybeans-sync --after 2025-06-01 --before 2025-08-31
```

Catch up from a specific day through today:
```bash
tinybeans-sync --after 2025-10-27
```

Force re-download (ignores history file):
```bash
tinybeans-sync --after 2025-06-01 --force
```

## History

Downloaded files are tracked in `~/.config/tinybeans-sync/tinybeans_history.json` (or your `--data` directory) to avoid re-downloading deleted images.

Delete that history file to start fresh, or rerun with `--after <date>` to start from a specific date.  Use `--force` to restore image files from a date range or over a date range via `--before` and `--after`.

## Roadmap

- support video downloads

## License

[GPLv3](https://www.gnu.org/licenses/gpl-3.0.en.html)
