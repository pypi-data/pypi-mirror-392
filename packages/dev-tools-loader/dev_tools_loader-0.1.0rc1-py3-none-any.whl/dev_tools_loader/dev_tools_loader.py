import os
import sys
import re
import shutil
import time
import json
import runpy
import urllib.request
from pathlib import Path
from typing import Tuple


#----------------------------------------------------------------------------------------------------------------------

class DebugLog:
    __colors = {
        'black':            '\033[30m',
        'red':              '\033[31m',
        'green':            '\033[32m',
        'yellow':           '\033[33m',
        'blue':             '\033[34m',
        'magenta':          '\033[35m',
        'cyan':             '\033[36m',
        'white':            '\033[37m',
        'orange':           '\033[38;5;214m',
        'bright_black':     '\033[90m',
        'bright_red':       '\033[91m',
        'bright_green':     '\033[92m',
        'bright_yellow':    '\033[93m',
        'bright_blue':      '\033[94m',
        'bright_magenta':   '\033[95m',
        'bright_cyan':      '\033[96m',
        'bright_white':     '\033[97m',
        'gray_yellow':      '\033[38;5;186m',
        'reset': '\033[0m',
    }


    def __supports_color() -> bool:
        if not sys.stdout.isatty():
            return False
        if not sys.platform.startswith('win'):
            return True
        term = os.environ.get('TERM', '')
        if 'xterm' in term or 'ansi' in term or 'cygwin' in term:
            return True
        if os.environ.get('ANSICON') or os.environ.get('WT_SESSION') or os.environ.get('TERM_PROGRAM', '') == 'vscode':
            return True
        return False


    __enable_colors = __supports_color()


    @staticmethod
    def log(msg: str, color=None, end='\n', flush=False) -> None:
        if color and DebugLog.__enable_colors:
            print(DebugLog.__colors[color], msg, DebugLog.__colors['reset'], sep='', end=end, flush=flush)
        else:
            print(msg, end=end, flush=flush)


    @staticmethod
    def new_line() -> None:
        print()


    @staticmethod
    def sep_by_sides(left_side: str, right_side: str = '', color=None, end='\n', flush=False) -> None:
        width = shutil.get_terminal_size().columns
        space = width - len(left_side) - len(right_side) - 1
        if space > 0:
            msg = f'\r{left_side:{len(left_side) + space}}{right_side}'
        else:
            short_left_side = left_side[:14] + '...' + left_side[14 + 3 + 2 - space:] + '  '
            msg = f'\r{short_left_side}{right_side}'
        DebugLog.log(msg, color=color, end=end, flush=flush)

#----------------------------------------------------------------------------------------------------------------------

class DevToolsLoader:
    EXPECTED_JSON_VERSION = '0.1.0'
    LOAD_RETRY_QTY = 5

    PYTHON_PLATFORMS = [
        'win32',                    # Windows 32-bit
        'win_amd64',                # Windows 64-bit
        'win_arm64',                # Windows ARM64
        'manylinux1_x86_64',        # Linux 64-bit (old)
        'manylinux2010_x86_64',     # Linux 64-bit
        'manylinux2014_x86_64',     # Linux 64-bit
        'manylinux1_i686',          # Linux 32-bit
        'manylinux2010_i686',       # Linux 32-bit
        'manylinux2014_i686',       # Linux 32-bit
        'manylinux2014_aarch64',    # Linux ARM64
        'manylinux2014_armv7l',     # Linux ARM32
        'macosx_10_9_x86_64',       # macOS Intel
        'macosx_11_0_arm64',        # macOS Apple Silicon
    ]

    VSCODE_PLATFORMS = [
        'win32-x64',
        'win32-arm64',
        'linux-x64',
        'linux-arm64',
        'linux-armhf',
        'alpine-x64',
        'alpine-arm64',
        'darwin-x64',
        'darwin-arm64',
    ]


    def __init__(self, json_path: Path, output_path: Path = None, clean: bool = False):
        if json_path:
            json_path = Path(json_path)
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    raw_json = f.read()
                    raw_json = re.sub(r'.*//.*', '', raw_json)
                    raw_json = re.sub(r'/\*[\s\S]*?\*/', '', raw_json)
                    self.__config = json.loads(raw_json)
            else:
                raise ValueError(f'JSON file \'{json_path}\' doesn\'t exist')

            if self.__config['version'] != DevToolsLoader.EXPECTED_JSON_VERSION:
                raise ValueError(f'incompatible JSON version - \'{self.__config["version"]}\', expected - \'{DevToolsLoader.EXPECTED_JSON_VERSION}\'')
        else:
            raise ValueError(f'json path required parameter')

        if output_path:
            self.__output_path = Path(output_path)
        else:
            self.__output_path = Path(os.getcwd()) / Path('output')
        self.__clean = clean


    @staticmethod
    def __ver_2_tuple(ver_mmpb: str) -> Tuple[int]:
        ver_mmp = ver_mmpb.split('-')[0]
        return tuple(int(x) for x in ver_mmp.split('.'))


    @staticmethod
    def __load_file(url: str, dest_path: Path, deep: int = 0) -> None:
        dest_path = Path(dest_path)
        temp_path = Path(str(dest_path) + '.part')
        tree_str = ''
        if deep > 0:
            tree_str = '└' + (deep * '────')[1:-1] + ' '
        left_side = f'{tree_str}{dest_path}'

        if dest_path.exists():
            DebugLog.sep_by_sides(left_side, 'EXISTS', color='bright_black', end='', flush=True)
        else:
            DebugLog.sep_by_sides(left_side, color='gray_yellow', end='', flush=True)
            start_time = time.time()
            for attempt in range(DevToolsLoader.LOAD_RETRY_QTY):
                try:
                    with urllib.request.urlopen(url) as response, open(temp_path, 'wb') as out_file:
                        total_size = int(response.headers['Content-Length'], 0)
                        block_size = 128 * 1024
                        download_size = 0
                        while download_size < total_size:
                            chunk = response.read(block_size)
                            out_file.write(chunk)
                            download_size += len(chunk)
                            percent = download_size * 100 // total_size
                            minutes, seconds = divmod(int(time.time() - start_time), 60)
                            left_side = f'{tree_str}{dest_path}'
                            right_side = f'{percent}% {download_size // 1024:8}KB   {minutes:02d}:{seconds:02d}'
                            DebugLog.sep_by_sides(left_side, right_side, color='gray_yellow' if percent < 100 else 'bright_green', end='', flush=True)
                    temp_path.rename(dest_path)
                    break
                except (ConnectionResetError, urllib.error.URLError):
                    DebugLog.sep_by_sides(left_side, 'FAILED', color='red')
                    time.sleep(2)
            else:
                raise RuntimeError(f'failed to load \'{url}\'')

        DebugLog.new_line()


    def __load_python(self, cfg: dict):
        # make dir
        target_path = self.__output_path / Path(f'python-{cfg["platform"]}-{cfg["version"]}')
        if self.__clean:
            DebugLog.log(f'>>> Cleaning output \'{target_path}\'', color='bright_cyan')
            shutil.rmtree(target_path, ignore_errors=True)
        if not target_path.exists():
            target_path.mkdir(parents=True, exist_ok=True)
            DebugLog.log(f'>>> Create dir \'{target_path}\'', color='bright_cyan')

        # load installer
        if cfg['installer'] == 'load':
            try:
                plat, arch = cfg['platform'].split('_')
                arch = '-' + arch
            except ValueError:
                plat = cfg['platform']
                arch = ''
            if plat.startswith('win'):
                ver = cfg['version']
                file_name = f'python-{ver}{arch}.exe'
                dest = target_path / Path(file_name)
                url = f'https://www.python.org/ftp/python/{ver}/{file_name}'
                DebugLog.log(f'>>> Loading python {ver} for platform {cfg["platform"]}', color='bright_cyan')
                DevToolsLoader.__load_file(url, dest)
            else:
                DebugLog.log(f'>>> Load python for Linux is not supported yet', color='red')
                # ver_major = ver.split('.')[0] + '.' + ver.split('.')[1]
                # file_name = f'python{ver_major}_{ver}_{arch}.deb'
                # dest = VSCODE_PATH / Path(file_name)
                # url = f'https://deb.debian.org/debian/pool/main/p/python{ver_major}/{file_name}'

        # load packages
        if cfg.get('packages'):
            for pkg in cfg['packages']:
                pkg_name = pkg['name']
                if pkg['version'] != 'latest':
                    pkg_name +=  f'=={pkg["version"]}'

                pip_args = [
                    'pip', 'download', pkg_name,
                    '--only-binary=:all:', '-q',
                    '--python-version', cfg['version'],
                    '--platform', cfg['platform'],
                    '-d', str(target_path)
                ]

                DebugLog.log(f'>>> Loading python package \'{pkg_name}\'', color='bright_cyan')
                old_argv = sys.argv
                sys.argv = pip_args

                try:
                    runpy.run_module('pip', run_name='__main__')
                    sys.argv
                except SystemExit as e:
                    if e.code != 0:
                        raise RuntimeWarning(f'failed to install {pkg_name} for platform {cfg["platform"]}')
                finally:
                    sys.argv = old_argv

        #save setup script
        setup = ''
        setup_path = target_path / Path('setup' + ('.bat' if cfg["platform"].startswith('win') else '.sh'))
        for root, dirs, files in os.walk(target_path):
            for file in files:
                if Path(file).suffix == '.whl':
                    setup += f'pip install --no-index --find-links=./ {file}\n'
        DebugLog.log(f'>>> Save Python setup script to \'{setup_path}\'', color='bright_cyan')
        with open(setup_path, 'w', encoding='utf-8') as f:
            f.write(setup)


    @staticmethod
    def __get_extension_info(uid: str, version: str, engine: str, platform: str) -> dict:
        api_url = 'https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery'

        query = {
            'filters': [{ 'criteria': [{'filterType': 7, 'value': f'{uid}'}] }],
            'flags': 0x1 | 0x2 | 0x10 | 0x80
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json;api-version=3.0-preview.1',
            'User-Agent': 'Offline VSIX/1.0'
        }

        data = json.dumps(query).encode('utf-8')
        req = urllib.request.Request(api_url, data, headers)

        for attempt in range(DevToolsLoader.LOAD_RETRY_QTY):
            try:
                with urllib.request.urlopen(req) as resp:
                    info_list: list[dict] = json.load(resp)['results'][0]['extensions'][0]['versions']
                    # response_path = DevToolsLoader.TEMP_PATH / Path('response')
                    # if not response_path.exists():
                    #     response_path.mkdir(parents=True, exist_ok=True)
                    # with open(response_path / Path(f'{uid}.json'), 'w', encoding='utf-8') as f:
                    #     json.dump(info_list, f, indent=4)
                    #     f.write('\n')

                    for info in info_list:
                        if info.get('targetPlatform') and platform is None:
                            raise RuntimeError(f'platform must be specified for {uid} platform')

                        if info.get('targetPlatform') is None or info['targetPlatform'] == platform:
                            for prop in info['properties']:
                                if prop['key'] == 'Microsoft.VisualStudio.Code.Engine':
                                    ext_engine = prop['value'].replace('^', '')
                                    break
                            else:
                                raise RuntimeError('failed to find Microsoft.VisualStudio.Code.Engine')

                            if engine == 'latest' or DevToolsLoader.__ver_2_tuple(ext_engine) <= DevToolsLoader.__ver_2_tuple(engine):
                                if version == 'latest' or version == info['version']:
                                    return info
                    else:
                        raise RuntimeError(f'failed to find \'{uid}\' info')
            except (ConnectionResetError, urllib.error.URLError):
                time.sleep(2)
        else:
            raise RuntimeError(f'failed to connect \'{api_url}\'')


    @staticmethod
    def __load_vscode_extension_recursive(target_path: Path, uid: str, version: str, engine: str, platform: str, deep: int = 0, seen = None) -> None:
        if seen is None:
            seen = set()

        if uid in seen:
            return

        seen.add(uid)

        info = DevToolsLoader.__get_extension_info(uid, version, engine, platform)
        for prop in info['files']:
            if prop['assetType'] == 'Microsoft.VisualStudio.Services.VSIXPackage':
                url = prop['source']
                break
        else:
            raise RuntimeError(f'failed to find url')

        #url = f'https://{uid.split('.')[0]}.gallery.vsassets.io/_apis/public/gallery/publisher/{uid.split('.')[0]}/extension/{uid.split('.')[1]}/{ver}/assetbyname/Microsoft.VisualStudio.Services.VSIXPackage'
        #url = f'https://marketplace.visualstudio.com/_apis/public/gallery/publishers/{publisher}/vsextensions/{name}/{ver}/vspackage'

        ver = info['version']
        plat = info.get('targetPlatform')
        plat = f'-{plat}' if plat else ''
        file_name = f'{uid}-{ver}{plat}.vsix'
        dest = target_path / Path(file_name)

        DevToolsLoader.__load_file(url, dest, deep)

        for prop in info['properties']:
            if prop['key'] == 'Microsoft.VisualStudio.Code.ExtensionDependencies' or prop['key'] == 'Microsoft.VisualStudio.Code.ExtensionPack':
                for dep_uid in prop['value'].split(','):
                    if dep_uid != '':
                        DevToolsLoader.__load_vscode_extension_recursive(target_path, dep_uid, 'latest', engine, platform, deep + 1, seen)


    def __load_vscode(self, cfg: dict) -> None:
        # make dir
        target_path = self.__output_path / Path(f'vscode-{cfg["platform"]}-{cfg["version"]}')
        if self.__clean:
            DebugLog.log(f'>>> Cleaning output \'{target_path}\'', color='bright_cyan')
            shutil.rmtree(target_path, ignore_errors=True)
        if not target_path.exists():
            target_path.mkdir(parents=True, exist_ok=True)
            DebugLog.log(f'>>> Create dir \'{target_path}\'', color='bright_cyan')

        # load installer
        if cfg['installer'] == 'load':
            plat = cfg['platform']
            engine = cfg['version']
            if plat.startswith('win'):
                suffix = '.exe'
            elif plat.startswith('darwin'):
                suffix = '.zip'
            elif plat.startswith('linux'):
                suffix = '.tar.gz'
            else:
                suffix = None
                DebugLog.log(f'>>> Load vscode for {plat} is not supported yet', color='red')
            if suffix:
                url_plat = plat if plat != 'darwin-x64' else 'darwin'
                url = f'https://update.code.visualstudio.com/{engine}/{url_plat}/stable'
                dest = target_path / Path(f'vscode-{engine}-{plat}{suffix}')
                DebugLog.log(f'>>> Loading vscode {engine} for platform {plat}', color='bright_cyan')
                DevToolsLoader.__load_file(url, dest)

        # load extensions
        if cfg.get('extensions'):
            for ext in cfg['extensions']:
                DevToolsLoader.__load_vscode_extension_recursive(target_path, ext['uid'], ext['version'], cfg['version'], cfg['platform'])

        setup = ''
        setup_path = target_path / Path('setup' + ('.bat' if cfg["platform"].startswith('win') else '.sh'))
        for root, dirs, files in os.walk(target_path):
            for file in files:
                if Path(file).suffix == '.vsix':
                    setup += f'code --force --install-extension {file}\n'
        DebugLog.log(f'>>> Save VSCode setup script to \'{setup_path}\'', color='bright_cyan')
        with open(setup_path, 'w', encoding='utf-8') as f:
            f.write(setup)


    def run(self) -> None:
        for cfg in self.__config['targets']:
            if cfg['type'] == 'python':
                self.__load_python(cfg)
            elif cfg['type'] == 'vscode':
                self.__load_vscode(cfg)
            else:
                raise ValueError(f'invalid target type \'{cfg['type']}\'')
