from rest_framework import serializers
from django.contrib.auth import authenticate
from usuarios.models import Usuario

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ('id', 'username', 'email')

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Credenciales incorrectas")