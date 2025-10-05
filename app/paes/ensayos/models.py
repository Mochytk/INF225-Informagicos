from django.db import models
from usuarios.models import Usuario
class Etiqueta(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.TextField(blank=True)
    
    def __str__(self):
        return self.nombre
class Ensayo(models.Model):
    titulo = models.CharField(max_length=200, default="Título")
    materia = models.CharField(max_length=100, default="Materia")
    curso = models.CharField(max_length=50, default="Curso")
    fecha = models.DateTimeField(auto_now_add=True)
    creador = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True, default=None)
    def __str__(self):
        return self.titulo
class Pregunta(models.Model):
    ensayo = models.ForeignKey(Ensayo, on_delete=models.CASCADE, related_name='preguntas')
    enunciado = models.TextField()
    #enunciado_img = models.ImageField(upload_to='preguntas/', null=True, blank=True)
    #opciones = models.JSONField(default=list)  
    dificultad = models.CharField(max_length=50, default="Sin definir")  
    correct_answer = models.CharField(max_length=1, default="A")  
    tipo = models.CharField(max_length=50, choices=[("alternativa_simple", "Alternativa Simple")])
    etiquetas = models.ManyToManyField(Etiqueta, blank=True, related_name='preguntas')
    explicacion_texto = models.TextField(blank=True, default='')
    explicacion_url = models.URLField(blank=True, default='')

    def __str__(self):
        return (self.enunciado[:80] + '...') if len(self.enunciado) > 80 else self.enunciado
class Intento(models.Model):
    estudiante = models.ForeignKey(Usuario, on_delete=models.CASCADE) 
    ensayo = models.ForeignKey(Ensayo, on_delete=models.CASCADE) 
    respuestas = models.JSONField(default=list)  
    puntaje = models.IntegerField(default="100") 
    fecha = models.DateTimeField(auto_now_add=True) 
    duracion = models.DurationField(default="0") 

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

