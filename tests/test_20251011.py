# app/paes/ensayos/tests.py

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from usuarios.models import Usuario
from .models import Ensayo, Pregunta, Opcion, Resultado

class SubmitEnsayoAPITest(TestCase):
    """
    Pruebas para el endpoint de envío de ensayos (/api/ensayos/<id>/submit/).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print("\n--- Iniciando Pruebas: Envío de Ensayos ---")
        cls.alumno = Usuario.objects.create_user(username='alumno_test', password='password', rol='alumno')
        cls.ensayo = Ensayo.objects.create(titulo='Ensayo de Prueba Hito 3')
        cls.pregunta = Pregunta.objects.create(ensayo=cls.ensayo, enunciado='Pregunta de prueba', tipo='alternativa_simple')
        cls.opcion_correcta = Opcion.objects.create(pregunta=cls.pregunta, texto='Opción Correcta', es_correcta=True)
        cls.opcion_incorrecta = Opcion.objects.create(pregunta=cls.pregunta, texto='Opción Incorrecta', es_correcta=False)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        print("--- Finalizando Pruebas: Envío de Ensayos ---")

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.alumno)
        self.submit_url = reverse('submit_ensayo', kwargs={'ensayo_id': self.ensayo.id})

    def test_submit_ensayo_exitoso(self):
        """Prueba 1: Envío exitoso de un ensayo con datos válidos."""
        print("▶️ Ejecutando: test_submit_ensayo_exitoso")
        data = [{'pregunta_id': self.pregunta.id, 'opcion_id': self.opcion_correcta.id}]
        response = self.client.post(self.submit_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('resultado_id', response.data)
        self.assertEqual(response.data['puntaje'], 1000)
        print("✅ Resultado: ¡Correcto!")


    def test_submit_ensayo_payload_invalido(self):
        """Prueba 2: La API rechaza un payload inválido."""
        print("▶️ Ejecutando: test_submit_ensayo_payload_invalido")
        data = {'respuestas': 'esto-no-es-una-lista'}
        response = self.client.post(self.submit_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        print("✅ Resultado: ¡Correcto!")


class EnsayosCompletadosAPITest(TestCase):
    """
    Pruebas para el endpoint de ensayos completados (/api/ensayos/completados/).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print("\n--- Iniciando Pruebas: Historial de Ensayos Completados ---")
        cls.alumno = Usuario.objects.create_user(username='alumno_historial', password='password', rol='alumno')
        cls.ensayo = Ensayo.objects.create(titulo='Ensayo para Historial')
        cls.resultado = Resultado.objects.create(ensayo=cls.ensayo, alumno=cls.alumno, puntaje_total=850)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        print("--- Finalizando Pruebas: Historial de Ensayos Completados ---")

    def setUp(self):
        self.client = APIClient()
        self.completados_url = reverse('ensayos_completados')

    def test_ensayos_completados_usuario_autenticado(self):
        """Prueba 3: Un usuario autenticado puede ver sus ensayos completados."""
        print("▶️ Ejecutando: test_ensayos_completados_usuario_autenticado")
        self.client.force_authenticate(user=self.alumno)
        response = self.client.get(self.completados_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        print("✅ Resultado: ¡Correcto!")

    def test_ensayos_completados_usuario_no_autenticado(self):
        """Prueba 4: Un usuario no autenticado no puede acceder."""
        print("▶️ Ejecutando: test_ensayos_completados_usuario_no_autenticado")
        response = self.client.get(self.completados_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        print("✅ Resultado: ¡Correcto!")