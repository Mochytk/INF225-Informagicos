from django.shortcuts import render
from rest_framework import viewsets
from .models import Ensayo
from .serializers import ExamSerializer

class ExamViewSet(viewsets.ModelViewSet):
    queryset = Ensayo.objects.all()
    serializer_class = ExamSerializer