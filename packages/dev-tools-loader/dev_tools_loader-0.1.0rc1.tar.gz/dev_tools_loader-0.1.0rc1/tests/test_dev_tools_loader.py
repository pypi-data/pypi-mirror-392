import json
import pytest
from pathlib import Path
from unittest.mock import patch

from dev_tools_loader.dev_tools_loader import DevToolsLoader
from dev_tools_loader.cli import main


@pytest.fixture
def config_template():
    return {
        'version': '0.1.0',
        'targets': [
            {
                'type': 'python',
                'platform': 'none',
                'version': '3.12.0',
                'installer': "load",
                'packages': [
                    {
                        'name': 'compiledb',
                        'version': '0.10.6'
                    },
                    {
                        'name': 'pyserial',
                        'version': '3.2'
                    },
                    {
                        'name': 'requests',
                        'version': 'latest'
                    }
                ]
            },
            {
                'type': 'vscode',
                'platform': 'none',
                'version': '1.96.0',
                'installer': "load",
                'extensions': [
                    {
                        'uid': 'ms-vscode.cpptools',
                        'version': '1.28.0'
                    },
                    {
                        'uid': 'ms-python.python',
                        'version': 'latest'
                    },
                    {
                        'uid': 'ms-python.debugpy',
                        'version': 'latest'
                    },
                    {
                        'uid': 'marus25.cortex-debug',
                        'version': '1.12.0'
                    },
                    {
                        'uid': 'streetsidesoftware.code-spell-checker-russian',
                        'version': 'latest'
                    }
                ]
            }
        ]
    }


def save_json_config(json_path: Path, config: dict) -> None:
    json_path = Path(json_path)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)
        f.write('\n')


def test_cli_help():
    print()
    with patch('sys.argv', ['dev_tools_loader', '-h']):
        with pytest.raises(SystemExit):
            main()


def test_cli_version():
    print()
    with patch('sys.argv', ['dev_tools_loader', '--version']):
        with pytest.raises(SystemExit):
            main()


def test_config_example(tmp_path):
    print()
    config_path = Path(__file__).parent / Path('data/config_example.json')
    with patch('sys.argv', ['dev_tools_loader', '-j', str(config_path), '-o', str(tmp_path)]):
        main()


@pytest.mark.parametrize('platform', DevToolsLoader.PYTHON_PLATFORMS)
def test_python_load(config_template, platform, tmp_path):
    config = config_template
    config['targets'][0]['platform'] = platform
    config['targets'].pop(1)
    json_path = tmp_path / Path(f'config_python_{platform}.json')
    save_json_config(json_path, config)
    print()
    dtl = DevToolsLoader(json_path, tmp_path)
    dtl.run()


@pytest.mark.parametrize('platform', DevToolsLoader.VSCODE_PLATFORMS)
def test_vscode_load(config_template, platform, tmp_path):
    config = config_template
    config['targets'][1]['platform'] = platform
    config['targets'].pop(0)
    json_path = tmp_path / Path(f'config_vscode_{platform}.json')
    save_json_config(json_path, config)
    print()
    dtl = DevToolsLoader(json_path, tmp_path)
    dtl.run()
