from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.urls import reverse

User = get_user_model()

class ThrottlingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="guardia", password="x")
        self.token = Token.objects.create(user=self.user)
        self.headers = {"HTTP_AUTHORIZATION": f"Token {self.token.key}"}
        self.url_acc = reverse("seguridad:control-acceso-vehicular")
        self.url_sal = reverse("seguridad:control-salida-vehicular")

    def test_rate_limit_control_acceso(self):
        # 30 permitidas, la 31 debería dar 429
        for i in range(30):
            r = self.client.post(self.url_acc, {"placa": "ABC123"}, format="json", **self.headers)
        r = self.client.post(self.url_acc, {"placa": "ABC123"}, format="json", **self.headers)
        self.assertEqual(r.status_code, 429)

    def test_rate_limit_control_salida(self):
        for i in range(30):
            r = self.client.post(self.url_sal, {"placa": "ABC123"}, format="json", **self.headers)
        r = self.client.post(self.url_sal, {"placa": "ABC123"}, format="json", **self.headers)
        self.assertEqual(r.status_code, 429)
