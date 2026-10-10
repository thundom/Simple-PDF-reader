"""Local PDF operations. No network requests; passwords never persisted."""
from io import BytesIO
from pathlib import Path
import os
import shutil
import subprocess
import tempfile

from PIL import Image, ImageOps
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Highlight
from pypdf.generic import ArrayObject, FloatObject
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import pypdfium2 as pdfium

pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))


class PasswordRequired(ValueError):
    pass


def read_pdf(path, password=''):
    reader = PdfReader(BytesIO(Path(path).read_bytes()))
    if reader.is_encrypted and not reader.decrypt(password):
        raise PasswordRequired('密码错误或需要密码')
    if not reader.pages:
        raise ValueError('PDF 没有页面')
    return reader


class Document:
    def __init__(self, path, password=''):
        self.path = Path(path)
        reader = read_pdf(path, password)
        self.writer = PdfWriter()
        self.writer.clone_document_from_reader(reader)
        self.dirty = False
        self.history = []

    def __len__(self):
        return len(self.writer.pages)

    def data(self):
        out = BytesIO()
        self.writer.write(out)
        return out.getvalue()

    def checkpoint(self):
        self.history.append(self.data())
        self.history = self.history[-10:]
        self.dirty = True

    def undo(self):
        if not self.history:
            return
        self.writer = PdfWriter(clone_from=BytesIO(self.history.pop()))
        self.dirty = True

    def render(self, index, scale=1):
        with pdfium.PdfDocument(self.data()) as pdf:
            page = pdf[index]
            bitmap = page.render(scale=scale)
            try:
                return bitmap.to_pil().copy()
            finally:
                bitmap.close()
                page.close()

    def rotate(self, index):
        self.checkpoint()
        self.writer.pages[index].rotate(90)

    def delete(self, index):
        if len(self) <= 1:
            raise ValueError('至少保留一页')
        self.checkpoint()
        self.writer.remove_page(index)

    def append(self, path, password=''):
        reader = read_pdf(path, password)
        self.checkpoint()
        self.writer.append(reader)

    def add_text(self, index, text, x, y, size=14):
        page = self.writer.pages[index]
        self.checkpoint()
        page.transfer_rotation_to_content()
        w, h = float(page.mediabox.width), float(page.mediabox.height)
        stream = BytesIO()
        c = canvas.Canvas(stream, pagesize=(w, h))
        c.setFont('STSong-Light', size)
        c.drawString(x, y, text)
        c.save()
        page.merge_page(PdfReader(stream).pages[0])

    def highlight(self, index, rect):
        self.checkpoint()
        x1, y1, x2, y2 = rect
        points = ArrayObject([FloatObject(v) for v in (x1,y2,x2,y2,x1,y1,x2,y1)])
        self.writer.add_annotation(index, Highlight(rect=rect, quad_points=points))

    def save(self, path, password=None, indices=None):
        writer = PdfWriter(clone_from=BytesIO(self.data()))
        if indices is not None:
            writer = PdfWriter()
            for i in indices:
                writer.add_page(self.writer.pages[i])
        if password is not None:
            if not password:
                raise ValueError('加密密码不能为空')
            writer.encrypt(password, algorithm='AES-256')
        target = Path(path)
        fd, temporary = tempfile.mkstemp(suffix='.pdf', dir=target.parent)
        try:
            with os.fdopen(fd, 'wb') as out:
                writer.write(out)
            read_pdf(temporary, password or '')
            os.replace(temporary, target)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        if indices is None:
            self.dirty = False


def convert_to_pdf(source, target):
    source, target = Path(source), Path(target)
    suffix = source.suffix.lower()
    if suffix in {'.png','.jpg','.jpeg','.bmp','.tif','.tiff','.webp'}:
        frames = []
        with Image.open(source) as image:
            for i in range(getattr(image, 'n_frames', 1)):
                image.seek(i)
                frames.append(ImageOps.exif_transpose(image).convert('RGB'))
        frames[0].save(target, 'PDF', save_all=True, append_images=frames[1:])
    elif suffix in {'.txt', '.md'}:
        c = canvas.Canvas(str(target))
        c.setFont('STSong-Light', 11)
        y = 800
        for line in source.read_text(encoding='utf-8-sig').splitlines():
            # Wrap by measured width, preserving Unicode text.
            chunks, part = [], ''
            for char in line:
                if pdfmetrics.stringWidth(part + char, 'STSong-Light', 11) > 495:
                    chunks.append(part)
                    part = ''
                part += char
            chunks.append(part)
            for chunk in chunks:
                if y < 45:
                    c.showPage()
                    c.setFont('STSong-Light', 11)
                    y = 800
                c.drawString(50, y, chunk)
                y -= 16
        c.save()
    elif suffix in {'.doc','.docx','.xls','.xlsx','.ppt','.pptx','.odt','.ods','.odp','.rtf','.html','.htm'}:
        candidates = [shutil.which('soffice'), r'C:\Program Files\LibreOffice\program\soffice.exe']
        executable = next((p for p in candidates if p and Path(p).is_file()), None)
        if not executable:
            raise ValueError('Office / HTML 转换需要先安装免费 LibreOffice')
        with tempfile.TemporaryDirectory() as directory:
            profile = (Path(directory) / 'profile').as_uri()
            result = subprocess.run([executable, '-env:UserInstallation='+profile,
                '--headless','--convert-to','pdf','--outdir',directory,str(source.resolve())],
                capture_output=True, timeout=120, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            output = Path(directory) / (source.stem + '.pdf')
            if result.returncode or not output.exists():
                raise ValueError('LibreOffice 转换失败；检查文件是否损坏或受密码保护')
            shutil.copyfile(output, target)
    else:
        raise ValueError('不支持此格式')
