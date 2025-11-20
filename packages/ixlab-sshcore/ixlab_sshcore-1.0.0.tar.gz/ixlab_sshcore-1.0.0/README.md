# sshcore

`sshcore` is the shared engine behind the `sshcli` and `sshui` applications. It provides a pure-Python API for reading, manipulating, and writing SSH configuration files with tag metadata, color definitions, backup helpers, and key-management utilities.

## Features

- Parse SSH config files (including `Include` directives) into structured `HostBlock` objects.
- Attach metadata such as `@tags` and global tag color definitions.
- Modify or append host blocks while preserving metadata comments.
- Manage key files (generation, listing, inspection) without touching the CLI/UI layers.
- Track config sources and settings (`sshcli.json`) so other apps can share the same configuration state.
- Backup and restore SSH configs with timestamped copies.

## Installation

```bash
pip install ixlab-sshcore
```

This installs only the reusable library—no CLI or GUI dependencies.

## Usage

```python
from sshcore import config

blocks = config.load_host_blocks()
for block in blocks:
    print(block.patterns, block.tags)

# Update a host's tags and persist them back to disk
target = config.default_config_path()
backup = config.replace_host_block_with_metadata(
    target,
    block,
    block.patterns,
    list(block.options.items()),
)
print("Updated host, backup saved to:", backup)
```

## Development

1. Create a virtual environment and install dependencies:

   ```bash
   pip install -e .[dev]
   ```

2. Run tests:

   ```bash
   pytest
   ```

`sshcore` is MIT licensed. Issues and pull requests are welcome.
