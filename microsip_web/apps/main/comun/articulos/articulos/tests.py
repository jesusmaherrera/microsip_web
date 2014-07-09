"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase


class ArticulosViewsTestCase(TestCase):
    def test_articulos(self):
        resp = self.client.get('/punto_de_venta/articulos/')
        self.assertEqual(resp.status_code, 200)
