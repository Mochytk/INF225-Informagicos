from django.db import models
from usuarios.models import Usuario

class Ensayo(models.Model):
    titulo = models.CharField(max_length=200, default="Título") # Nombre del ensayo
    materia = models.CharField(max_length=100, default="Materia") # Ej: 'Matemáticas', 'Lenguaje', 'Ciencias', 'Historia'.
    curso = models.CharField(max_length=50, default="Curso")
    fecha = models.DateTimeField(auto_now_add=True)
    creador = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True, default=None) # Docente que creó el ensayo

    def __str__(self):
        return self.titulo
class Pregunta(models.Model):
    ensayo = models.ForeignKey(Ensayo, on_delete=models.CASCADE, related_name='preguntas') # Clave foránea al ensayo correspondiente
    enunciado = models.TextField() # Enunciado de la pregunta
    enunciado_img = models.ImageField(upload_to='preguntas/', null=True, blank=True)  # imagen que acompaña al enunciado (opcional)
    #opciones = models.JSONField(default=list)  # Ej: ['Opción A', 'Opción B', ...]
    dificultad = models.CharField(max_length=50, default="Sin definir")  # Ej: 'Fácil', 'Medio', 'Difícil'
    correct_answer = models.CharField(max_length=1, default="A")  # Ej: 'A', 'B', etc.
    tipo = models.CharField(max_length=50, choices=[("alternativa_simple", "Alternativa Simple"), ("desarrollo", "Desarrollo")])
    
    def __str__(self):
        return f"{self.enunciado[:200]}..."
class Intento(models.Model):
    estudiante = models.ForeignKey(Usuario, on_delete=models.CASCADE) # Estudiante que realiza el intento
    ensayo = models.ForeignKey(Ensayo, on_delete=models.CASCADE) # Ensayo que se está intentando
    respuestas = models.JSONField(default=list)  # Respuestas del estudiante en formato lista
    puntaje = models.IntegerField(default="100") # Puntaje obtenido en el intento
    fecha = models.DateTimeField(auto_now_add=True) # Fecha y hora del intento
    duracion = models.DurationField(default="0") # Duración del intento (segundos)

class Opcion(models.Model):
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE, related_name="opciones")
    texto = models.CharField(max_length=200)
    es_correcta = models.BooleanField(default=False)

    def __str__(self):
        return self.texto
    
class Resultado(models.Model):
    ensayo = models.ForeignKey(Ensayo, on_delete=models.CASCADE, related_name="resultados")
    alumno = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    puntaje_total = models.IntegerField(default=0)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resultado de {self.alumno.username} en {self.ensayo.titulo}"

class Respuesta(models.Model):
    resultado = models.ForeignKey(Resultado, on_delete=models.CASCADE, related_name="respuestas")
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    opcion = models.ForeignKey(Opcion, null=True, blank=True, on_delete=models.SET_NULL)
    texto = models.TextField(blank=True, null=True)
    correcta = models.BooleanField(default=False)

    def __str__(self):
        return f"Resp. {self.pregunta.id} por {self.resultado.alumno.username}"