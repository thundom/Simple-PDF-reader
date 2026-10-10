import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from io import BytesIO
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from reportlab.pdfgen import canvas
from pypdf import PdfReader
from PIL import Image
from core import Document, PasswordRequired, convert_to_pdf
from library import Library, make_bundle, restore_bundle


class PDFTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root/'source.pdf'
        c = canvas.Canvas(str(self.source))
        for text in ['First page','Second page']:
            c.drawString(50,750,text)
            c.showPage()
        c.save()

    def tearDown(self): self.temp.cleanup()

    def test_password_edit_and_roundtrip(self):
        doc = Document(self.source)
        encrypted = self.root/'locked.pdf'
        doc.save(encrypted,password='correct-password')
        with self.assertRaises(PasswordRequired): Document(encrypted,'wrong')
        doc = Document(encrypted,'correct-password')
        doc.add_text(0,'Added text',70,700)
        doc.highlight(0,(50,730,200,760))
        doc.rotate(1)
        output = self.root/'unlocked.pdf'
        doc.save(output)
        reader = PdfReader(output)
        self.assertFalse(reader.is_encrypted)
        self.assertIn('Added text',reader.pages[0].extract_text())
        self.assertEqual(reader.pages[1].rotation,90)
        self.assertEqual(reader.pages[0]['/Annots'][0].get_object()['/Subtype'],'/Highlight')
        self.assertGreater(doc.render(0,.5).width,100)

    def test_page_management_and_undo(self):
        doc = Document(self.source)
        doc.delete(0)
        self.assertEqual(len(doc),1)
        with self.assertRaises(ValueError): doc.delete(0)
        doc.undo()
        self.assertEqual(len(doc),2)
        doc.append(self.source)
        self.assertEqual(len(doc),4)
        output = self.root/'extract.pdf'
        doc.save(output,indices=[3,0])
        self.assertIn('Second page',PdfReader(output).pages[0].extract_text())
        self.assertTrue(doc.dirty)

    def test_conversion(self):
        text = self.root/'text.txt'
        text.write_text('测试中文\n'+'Long line '*300,encoding='utf-8')
        output = self.root/'text.pdf'
        convert_to_pdf(text,output)
        self.assertGreater(len(PdfReader(output).pages),0)
        image = self.root/'image.png'
        Image.new('RGB',(200,100),'white').save(image)
        convert_to_pdf(image,self.root/'image.pdf')
        self.assertEqual(len(PdfReader(self.root/'image.pdf').pages),1)

    def test_progress_survives_reinstall_bundle(self):
        library = Library(self.root/'local')
        library.remember(self.source,1,1.4)
        self.assertEqual(Library(self.root/'local').state(self.source)['page'],1)
        key,data = make_bundle(self.source,1,1.4)
        path,state = restore_bundle(data,self.root/'fresh-system')
        self.assertEqual(path.read_bytes(),self.source.read_bytes())
        self.assertEqual(state,{'page':1,'zoom':1.4,'view':'单页','offset':0})
        self.assertEqual(len(key),64)

    def test_google_upload_protocol(self):
        from cloud import Cloud
        for provider in ['Google Drive']:
            cloud = Cloud.__new__(Cloud)
            cloud.provider = provider
            with patch.object(cloud,'_request') as request, patch.object(cloud,'books',return_value=[]):
                cloud.upload('a'*64,'book.pdf',b'bundle')
                args,kwargs = request.call_args
                self.assertIn(args[0],['POST','PUT'])
                self.assertIn(b'bundle',kwargs['data'])
                if provider=='Google Drive':
                    self.assertIn('multipart/related',kwargs['content_type'])
                    self.assertIn(b'appDataFolder',kwargs['data'])

    def test_bundle_rejects_corruption(self):
        archive = BytesIO()
        with zipfile.ZipFile(archive,'w') as z:
            z.writestr('book.pdf',b'corrupt')
            z.writestr('progress.json',json.dumps({'version':1,'name':'book.pdf','sha256':'bad','page':0,'zoom':1}))
        with self.assertRaises(ValueError): restore_bundle(archive.getvalue(),self.root/'restore')

    def test_refresh_token_and_authorization_header(self):
        from cloud import Cloud,PROVIDERS
        cloud = Cloud.__new__(Cloud)
        cloud.provider = 'Google Drive'
        cloud.settings = PROVIDERS['Google Drive']
        cloud.client = {'client_id':'test-client'}
        cloud.tokens = {'refresh_token':'test-refresh','expires_at':0}
        from unittest.mock import Mock
        response = Mock(ok=True)
        response.json.return_value = {'access_token':'test-access','expires_in':3600}
        with patch('cloud.requests.post',return_value=response) as post, patch('cloud.requests.request',return_value=response) as request, patch('cloud.keyring.get_password',return_value=None),patch('cloud.keyring.set_password'):
            cloud._request('GET','https://www.googleapis.com/drive/v3/files')
            self.assertEqual(post.call_args.kwargs['data']['grant_type'],'refresh_token')
            self.assertEqual(request.call_args.kwargs['headers']['Authorization'],'Bearer test-access')
            self.assertEqual(cloud.tokens['refresh_token'],'test-refresh')

    def test_split_preserves_pages_and_source(self):
        document = Document(self.source)
        original = self.source.read_bytes()
        results = document.split(self.root,[[0],[1]])
        self.assertEqual(len(results),2)
        self.assertIn('First page',PdfReader(results[0]).pages[0].extract_text())
        self.assertIn('Second page',PdfReader(results[1]).pages[0].extract_text())
        self.assertEqual(self.source.read_bytes(),original)
        with self.assertRaises(ValueError): document.split(self.root,[[0],[1]])

    def test_continuous_progress_bundle(self):
        key,data = make_bundle(self.source,1,.75,'双页连续',.42)
        path,state = restore_bundle(data,self.root/'restored')
        self.assertEqual(state['view'],'双页连续')
        self.assertEqual(state['offset'],.42)
        sizes = Document(self.source).page_sizes()
        self.assertEqual(len(sizes),2)
        self.assertGreater(sizes[0][1],sizes[0][0])


if __name__=='__main__': unittest.main()
