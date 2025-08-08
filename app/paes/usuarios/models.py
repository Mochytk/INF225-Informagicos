from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    nombre = models.CharField(max_length=30, blank=True)
    apellidos = models.CharField(max_length=30, blank=True)
    email = models.EmailField(max_length=254, blank=True, unique=True)
    ROL = (
        ('alumno', 'Alumno'),
        ('docente', 'Docente'),
    )
    rol = models.CharField(max_length=10, choices=ROL, default='alumno')
    def __str__(self):
        return self.username