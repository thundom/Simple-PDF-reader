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
        self.assertEqual(state,{'page':1,'zoom':1.4})
        self.assertEqual(len(key),64)

    def test_google_and_onedrive_upload_protocol(self):
        from cloud import Cloud
        for provider in ['Google Drive','OneDrive']:
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
        cloud.provider = 'OneDrive'
        cloud.settings = PROVIDERS['OneDrive']
        cloud.client = {'client_id':'test-client'}
        cloud.tokens = {'refresh_token':'test-refresh','expires_at':0}
        from unittest.mock import Mock
        response = Mock(ok=True)
        response.json.return_value = {'access_token':'test-access','expires_in':3600}
        with patch('cloud.requests.post',return_value=response) as post, patch('cloud.requests.request',return_value=response) as request, patch('cloud.keyring.get_password',return_value=None),patch('cloud.keyring.set_password'):
            cloud._request('GET','https://graph.microsoft.com/v1.0/me/drive/special/approot/children')
            self.assertEqual(post.call_args.kwargs['data']['grant_type'],'refresh_token')
            self.assertEqual(request.call_args.kwargs['headers']['Authorization'],'Bearer test-access')
            self.assertEqual(cloud.tokens['refresh_token'],'test-refresh')


if __name__=='__main__': unittest.main()
