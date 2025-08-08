from django.db import models
from usuarios.models import Usuario

class Ensayo(models.Model):
    nombre = models.CharField(max_length=200, default="Nombre") # Nombre del ensayo
    materia = models.CharField(max_length=100, default="General") # Ej: 'Matemáticas', 'Lenguaje', 'Ciencias', 'Historia'.
    creador = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True, default=None) # Docente que creó el ensayo

class Pregunta(models.Model):
    ensayo = models.ForeignKey(Ensayo, on_delete=models.CASCADE, related_name='preguntas') # Clave foránea al ensayo correspondiente
    enunciado = models.TextField(default="Enunciado por defecto") # Enunciado de la pregunta
    enunciado_img = models.ImageField(upload_to='preguntas/', null=True, blank=True)  # imagen que acompaña al enunciado (opcional)
    opciones = models.JSONField(default=list)  # Ej: ['Opción A', 'Opción B', ...]
    dificultad = models.CharField(max_length=50, default="Sin definir")  # Ej: 'Fácil', 'Medio', 'Difícil'
    correct_answer = models.CharField(max_length=1, default="A")  # Ej: 'A', 'B', etc.

class Intento(models.Model):
    estudiante = models.ForeignKey(Usuario, on_delete=models.CASCADE) # Estudiante que realiza el intento
    ensayo = models.ForeignKey(Ensayo, on_delete=models.CASCADE) # Ensayo que se está intentando
    respuestas = models.JSONField(default=list)  # Respuestas del estudiante en formato lista
    puntaje = models.IntegerField(default="100") # Puntaje obtenido en el intento
    fecha = models.DateTimeField(auto_now_add=True) # Fecha y hora del intento
    duracion = models.DurationField(default="0") # Duración del intento (segundos)