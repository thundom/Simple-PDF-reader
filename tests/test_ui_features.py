import unittest
from io import BytesIO
from pathlib import Path
import tempfile
from PIL import Image
from reportlab.pdfgen import canvas
from core import Document
from printing import placement,sheet_groups,cells
import i18n

class Features(unittest.TestCase):
    def test_print_geometry(self):
        self.assertEqual(sheet_groups([0,1,2,3,4],4),[[0,1,2,3],[4]])
        self.assertEqual(len(cells(1000,1500,6)),6)
        x,y,w,h=placement((600,800),(0,0,300,300),'fit',300)
        self.assertEqual((w,h),(225,300))
        self.assertEqual(x,37.5)
        self.assertEqual(placement((72,72),(0,0,600,600),'actual',300)[2:],(300,300))
        self.assertEqual(placement((72,72),(0,0,600,600),'shrink',300)[2:],(300,300))

    def test_forms_signatures_comments(self):
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder)/'input.pdf'; output=Path(folder)/'output.pdf'
            c=canvas.Canvas(str(source)); c.drawString(40,750,'Test')
            c.acroForm.textfield(name='Name',x=40,y=700,width=200,height=20)
            c.showPage(); c.save()
            doc=Document(source); doc.fill_form({'Name':'Reader'})
            doc.add_image(0,Image.new('RGBA',(100,25),(20,40,60,255)),30,200,100,25)
            doc.comment(0,'Review note',30,300); doc.highlight(0,(30,340,160,355))
            doc.save(output); restored=Document(output)
            self.assertEqual(restored.writer.get_fields()['Name']['/V'],'Reader')
            self.assertGreaterEqual(len(restored.writer.pages[0]['/Annots']),3)
            self.assertIn('Review note',str(restored.writer.pages[0]['/Annots'][-2].get_object()))
            self.assertGreater(len(restored.render(0,.5).tobytes()),100)

    def test_languages(self):
        previous=i18n.language
        try:
            for code in ['en','zh','ja']:
                i18n.language=code
                for label in ['填写和签名','区域高亮','页面显示','打印机','每张纸页数','双面','云端书库']:
                    self.assertTrue(i18n.tr(label))
                    if code!='zh': self.assertNotEqual(i18n.tr(label),label)
        finally: i18n.language=previous
