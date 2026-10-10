"""Durable local reading state and portable, validated cloud book bundles."""
import hashlib
import json
import os
import re
from pathlib import Path
import tempfile
import zipfile

import sys
import time
APP_DIR = Path(sys.executable).parent if getattr(sys,'frozen',False) else Path(__file__).parent
PORTABLE=(APP_DIR/'portable.flag').exists() or (Path(getattr(sys,'_MEIPASS',APP_DIR))/'portable.flag').exists() or (getattr(sys,'frozen',False) and 'Portable' in Path(sys.executable).stem)
DATA_DIR = APP_DIR/'Data' if PORTABLE else Path(os.environ.get('LOCALAPPDATA', Path.home()/'.local/share'))/'Simple PDF reader'


def digest(data):
    return hashlib.sha256(data).hexdigest()


class Library:
    def __init__(self, directory=DATA_DIR):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory/'library.json'
        try:
            self.books = json.loads(self.path.read_text('utf-8'))
        except (FileNotFoundError, ValueError):
            self.books = {}

    def remember(self, path, page, zoom, view='单页', offset=0):
        path = Path(path)
        key = digest(path.read_bytes())
        self.books[key] = {'name': path.name, 'path': str(path.resolve()), 'page': page, 'zoom': zoom, 'view':view, 'offset':offset, 'updated':time.time()}
        fd, temporary = tempfile.mkstemp(dir=self.directory, suffix='.json')
        with os.fdopen(fd, 'w', encoding='utf-8') as out:
            json.dump(self.books, out, ensure_ascii=False, indent=2)
        os.replace(temporary, self.path)
        return key

    def state(self, path):
        return self.books.get(digest(Path(path).read_bytes()), {})


def make_bundle(path, page, zoom, view='单页', offset=0):
    from io import BytesIO
    path = Path(path)
    data = path.read_bytes()
    key = digest(data)
    manifest = {'version':1, 'name':path.name, 'sha256':key, 'page':page, 'zoom':zoom, 'view':view, 'offset':offset}
    output = BytesIO()
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('book.pdf', data)
        archive.writestr('progress.json', json.dumps(manifest, ensure_ascii=False))
    return key, output.getvalue()


def restore_bundle(data, directory):
    from io import BytesIO
    with zipfile.ZipFile(BytesIO(data)) as archive:
        if set(archive.namelist()) != {'book.pdf','progress.json'}:
            raise ValueError('云端文件不是有效的阅读备份')
        if archive.getinfo('book.pdf').file_size > 512*1024*1024:
            raise ValueError('PDF 超过 512 MB 限制')
        if archive.getinfo('progress.json').file_size > 16384:
            raise ValueError('进度信息异常')
        manifest = json.loads(archive.read('progress.json'))
        pdf = archive.read('book.pdf')
    if manifest.get('version') != 1 or digest(pdf) != manifest.get('sha256'):
        raise ValueError('备份校验失败')
    name = Path(str(manifest['name']).replace('\\','/')).name
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]','_',name).strip(' .')
    if name.split('.')[0].upper() in {'CON','PRN','AUX','NUL',*[f'COM{i}' for i in range(1,10)],*[f'LPT{i}' for i in range(1,10)]}:
        name = '_'+name
    if not name.lower().endswith('.pdf'): raise ValueError('无效的 PDF 文件名')
    page = int(manifest['page'])
    zoom = float(manifest['zoom'])
    if page < 0 or not .3 <= zoom <= 2.5: raise ValueError('进度数据无效')
    view = manifest.get('view','单页')
    offset = float(manifest.get('offset',0))
    if view not in {'单页','双页','连续滚动','双页连续'} or not 0<=offset<=1:
        raise ValueError('阅读布局数据无效')
    directory = Path(directory)/manifest['sha256']
    directory.mkdir(parents=True,exist_ok=True)
    target = directory/name
    target.write_bytes(pdf)
    return target, {'page':page,'zoom':zoom,'view':view,'offset':offset}
