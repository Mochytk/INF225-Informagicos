from rest_framework import serializers
from .models import Ensayo, Pregunta, Intento

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pregunta
        fields = '__all__'

class ExamSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    class Meta:
        model = Ensayo
        fields = '__all__'