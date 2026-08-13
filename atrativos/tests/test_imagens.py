import io
import json
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from atrativos.models import Atrativo, AtrativoImagem

class ImagensAPITestCase(TestCase):
    def setUp(self):
        self.atrativo = Atrativo.objects.create(
            nome="Mercado Municipal",
            descricao="Tradicional mercado de Paranaguá",
            endereco="Centro Histórico",
            latitude="-25.520",
            longitude="-48.508",
        )

        # Create a dummy image file (GIF)
        image_content = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\xff\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        self.image_file = SimpleUploadedFile(
            name='test_image.gif',
            content=image_content,
            content_type='image/gif'
        )
        
        self.image_file_2 = SimpleUploadedFile(
            name='test_image_2.gif',
            content=image_content,
            content_type='image/gif'
        )

    def test_upload_imagem(self):
        response = self.client.post(
            f"/v1/atrativos/{self.atrativo.id}/imagens",
            data={"file": self.image_file}
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data["imagem_capa"]) # First image uploaded should be capa automatically
        self.assertIn("test_image", data["imagem_url"])

    def test_set_imagem_capa(self):
        # Create 2 images
        img1 = AtrativoImagem.objects.create(
            atrativo=self.atrativo, 
            imagem=self.image_file, 
            imagem_capa=True
        )
        img2 = AtrativoImagem.objects.create(
            atrativo=self.atrativo, 
            imagem=self.image_file_2, 
            imagem_capa=False
        )

        response = self.client.patch(f"/v1/atrativos/imagens/{img2.id}/capa")
        self.assertEqual(response.status_code, 200)
        
        img1.refresh_from_db()
        img2.refresh_from_db()

        self.assertFalse(img1.imagem_capa)
        self.assertTrue(img2.imagem_capa)

    def test_deletar_imagem(self):
        img = AtrativoImagem.objects.create(atrativo=self.atrativo, imagem=self.image_file)
        response = self.client.delete(f"/v1/atrativos/imagens/{img.id}")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(AtrativoImagem.objects.count(), 0)
