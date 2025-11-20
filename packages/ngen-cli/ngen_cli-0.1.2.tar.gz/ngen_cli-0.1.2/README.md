# ngen

Universal command wrapper package that dispatches to `/usr/local/bin/ngen-*` scripts.

## Installation

Install from PyPI:

```bash
pip install ngen-cli
```

Or install from source:

```bash
pip install .
```

**Note:** Installation to `/usr/local/bin` requires sudo/root permissions. The package will automatically install bundled scripts to `/usr/local/bin/ngen-*` during installation.

## Usage

The `ngen` command dispatches to scripts located at `/usr/local/bin/ngen-{command}`.

### Format

- Script location: `/usr/local/bin/ngen-{command}`
- Command usage: `ngen {command}`

### Examples

If you have a script at `/usr/local/bin/ngen-rancher`, you can use it as:

```bash
ngen-cli rancher --help
ngen-cli rancher version
```

If you have a script at `/usr/local/bin/ngen-git`, you can use it as:

```bash
ngen-cli git clone https://github.com/user/repo.git
ngen-cli git status
```

## How It Works

1. When you run `ngen-tools {command}`, the CLI dispatcher looks for a script at `/usr/local/bin/ngen-{command}`
2. If found, it executes the script with any additional arguments passed
3. The script can be any executable file (bash, sh, Python, or binary)

## Adding New Commands

To add a new command:

1. Place a script at `/usr/local/bin/ngen-{your-command}`
2. Make sure it's executable: `chmod +x /usr/local/bin/ngen-{your-command}`
3. Use it with: `ngen-cli {your-command}`

## Development

### Building the Package

```bash
python -m build
```

### Publishing to PyPI

Menggunakan script otomatis:

```bash
./publish.sh --test      # Publish ke Test PyPI
./publish.sh --publish   # Publish ke PyPI production
```

Atau manual:

```bash
python -m build
python -m twine check dist/*
python -m twine upload dist/*
```

Untuk panduan lengkap, lihat [PUBLISH.md](PUBLISH.md).

## License

MIT

