import unittest
import requests
import json

# URL base de la API. Asegúrate de que tu servidor de desarrollo esté corriendo.
BASE_URL = "http://127.0.0.1:8000/api/ensayos/"

class TestEnsayoAPI(unittest.TestCase):
    """
    Clase de pruebas para el endpoint de Ensayos (/api/ensayos/).
    """

    @classmethod
    def setUpClass(cls):
        """
        Configura los datos iniciales para todas las pruebas de la clase.
        Este método se ejecuta una sola vez al inicio.
        [cite: 28]
        """
        print("Iniciando pruebas para el API de Ensayos.")
        # Podrías crear aquí datos de prueba necesarios, como preguntas,
        # para asegurar un estado consistente. Por ahora, lo dejamos como ejemplo.
        cls.datos_ensayo_valido = {
            "nombre": "Ensayo de Prueba Hito 3",
            "preguntas": [] # Asume que puedes crear un ensayo sin preguntas o ajusta según tu modelo
        }
        cls.datos_ensayo_invalido = {
            "preguntas": []
        }

    @classmethod
    def tearDownClass(cls):
        """
        Limpia los datos después de que todas las pruebas de la clase han terminado.
        Este método se ejecuta una sola vez al final.
        [cite: 28]
        """
        print("Finalizando pruebas para el API de Ensayos.")
        # Aquí podrías eliminar los datos de prueba creados en setUpClass.

    def test_1_crear_ensayo_exitoso(self):
        """
        Prueba 3: Verifica la creación exitosa de un ensayo con datos válidos.
        """
        print("Ejecutando: test_1_crear_ensayo_exitoso")
        response = requests.post(BASE_URL, json=self.datos_ensayo_valido)
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertIn("id", response_data)
        self.assertEqual(response_data["nombre"], self.datos_ensayo_valido["nombre"])
        # Guardamos el ID para usarlo en otra prueba si es necesario
        TestEnsayoAPI.id_ensayo_creado = response_data['id']

    def test_2_crear_ensayo_invalido(self):
        """
        Prueba 4: Verifica que la API rechace la creación de un ensayo con datos inválidos.
        """
        print("Ejecutando: test_2_crear_ensayo_invalido")
        response = requests.post(BASE_URL, json=self.datos_ensayo_invalido)
        # Se espera una excepción o error por parte del cliente 
        self.assertEqual(response.status_code, 400)

    def test_3_listar_ensayos_con_contenido(self):
        """
        Prueba 1: Verifica que se pueda obtener una lista de ensayos.
        """
        print("Ejecutando: test_3_listar_ensayos_con_contenido")
        # Aseguramos que haya al menos un ensayo creado (el de la prueba 1)
        response = requests.get(BASE_URL)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        self.assertGreater(len(response.json()), 0) # La lista no debe estar vacía

    def test_4_recuperar_ensayo_existente(self):
        """
        Prueba adicional: Verifica que se pueda recuperar un ensayo específico por su ID.
        """
        print("Ejecutando: test_4_recuperar_ensayo_existente")
        # Usamos el ID del ensayo creado en la primera prueba
        if hasattr(TestEnsayoAPI, 'id_ensayo_creado'):
            url = f"{BASE_URL}{TestEnsayoAPI.id_ensayo_creado}/"
            response = requests.get(url)
            self.assertEqual(response.status_code, 200)
            response_data = response.json()
            self.assertEqual(response_data['id'], TestEnsayoAPI.id_ensayo_creado)
        else:
            self.skipTest("No se pudo ejecutar porque no se creó un ensayo previamente.")


if __name__ == '__main__':
    # Esto permite ejecutar las pruebas directamente desde la línea de comandos
    unittest.main(verbosity=2)