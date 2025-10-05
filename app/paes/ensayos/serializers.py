from rest_framework import serializers
from .models import Ensayo, Pregunta, Opcion, Resultado, Respuesta, Intento
from usuarios.serializers import UserSerializer

class OpcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opcion
        fields = ('id', 'texto', 'es_correcta')

class PreguntaSerializer(serializers.ModelSerializer):
    opciones = OpcionSerializer(many=True, read_only=True)
    class Meta:
        model = Pregunta
        fields = ('id', 'enunciado', 'tipo', 'opciones', 'explicacion_texto', 'explicacion_url')

class EnsayoSerializer(serializers.ModelSerializer):
    preguntas = PreguntaSerializer(many=True, read_only=True)
    class Meta:
        model = Ensayo
        fields = ('id', 'titulo', 'materia', 'curso', 'fecha', 'preguntas')

class RespuestaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Respuesta
        fields = ('id', 'pregunta', 'opcion', 'texto', 'correcta')

class ResultadoSerializer(serializers.ModelSerializer):
    respuestas = RespuestaSerializer(many=True, read_only=True)
    alumno = serializers.CharField(source='alumno.username', read_only=True)
    class Meta:
        model = Resultado
        fields = ('id', 'ensayo', 'alumno', 'puntaje_total', 'fecha', 'respuestas')