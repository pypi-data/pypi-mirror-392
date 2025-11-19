# Development Tools Loader

A CLI tool for automated downloading of development tools:

- VS Code installers and extensions (`.vsix` files).
- Python installers and pip packages;

The tool ensures version compatibility, handles dependencies, and supports repeatable configurations via JSON.


## Key Features

- **Version control**: Ensures VS Code extension versions match the target VS Code engine version.
- **Package bundles**: Supports downloading multiple packages/extensions in a single config.
- **Dependency handling**: Automatically resolves and downloads dependencies for VS Code extensions.
- **Resilient downloads**: Automatically retries on connection loss.
- **Repeatable setups**: JSON-based configuration enables reproducible environment setups.
- **Flexible versioning**: Supports `"latest"` for extensions and packages.


## Installation

```bash
pip install dev-tools-loader
```


## Running

Once installed, you can run the tool from the command line using the JSON configuration file.

```bash
dev_tools_loader -j path/to/config.json
```


## Command‑Line Options

- **`-j`, `--json-path` *`<json_config_path>`*** **(required)** Specifies the path to the JSON configuration file that defines download targets.
- **`-o`, `--output-path` *`<output_dir>`*** Sets the output directory where downloaded files will be saved.
- **`-c`, `--clean`** If specified, deletes files in the target output directory before starting the download process.
- **`-h`, `--help`** Displays the help message with a summary of all available options and exits.
- **`--version`** Prints the current version of the `dev-tools-loader` package and exits.


## Example Config

```json
{
    "version": "0.1.0",
    "targets": [
        {
            "type": "python",
            "platform": "win_amd64",
            "version": "3.12.0",
            "installer": "load",
            "packages": [
                {
                    "name": "compiledb",
                    "version": "0.10.6"
                },
                {
                    "name": "requests",
                    "version": "latest"
                }
            ]
        },
        {
            "type": "vscode",
            "platform": "win32-x64",
            "version": "1.96.0",
            "installer": "load",
            "extensions": [
                {
                    "uid": "ms-vscode.cpptools",
                    "version": "1.28.0"
                },
                {
                    "uid": "ms-python.python",
                    "version": "latest"
                }
            ]
        }
    ]
}
```


## Configuration Fields

- `version` (str): Schema version.
- `targets` (list): List of download targets. Each target has:
  - `type` (str): `"python"` or `"vscode"`.
  - `platform` (str): Target platform (see supported platforms below).
  - `version` (str): Version of the tool.
  - `installer` (str): `"load"` to download installer or `"skip"`.
  - `packages` (list, Python-only): List of pip packages to download.
    - `name` (str): Package name.
    - `version` (str): Package version (`"latest"` supported).
  - `extensions` (list, VS Code-only): List of VS Code extensions to download.
    - `uid` (str): Extension ID (e.g., `"ms-vscode.cpptools"`).
    - `version` (str): Extension version (`"latest"` supported).


## Supported Platforms Python

- `win32`
- `win_amd64`
- `win_arm64`
- `manylinux1_x86_64`
- `manylinux2010_x86_64`
- `manylinux2014_x86_64`
- `manylinux1_i686`
- `manylinux2010_i686`
- `manylinux2014_i686`
- `manylinux2014_aarch64`
- `manylinux2014_armv7l`
- `macosx_10_9_x86_64`
- `macosx_11_0_arm64`

## Supported Platforms VS Code

- `win32-x64`
- `win32-arm64`
- `linux-x64`
- `linux-arm64`
- `linux-armhf`
- `alpine-x64`
- `alpine-arm64`
- `darwin-x64`
- `darwin-arm64`
