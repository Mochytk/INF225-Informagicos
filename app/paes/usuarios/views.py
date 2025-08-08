from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import UserSerializer, LoginSerializer

from rest_framework.permissions import AllowAny

from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .models import Usuario

class LoginAPIView(APIView):
    permission_classes = [AllowAny] 
    def post(self, request):
        email = request.data.get('email')
        contraseña = request.data.get('contraseña')

        print("🔹 Intento de login con email:", email)
        print("🔹 Contraseña recibida:", contraseña)

        try:
            usuario = Usuario.objects.get(email=email)
            print("✅ Usuario encontrado:", usuario.username)
        except Usuario.DoesNotExist:
            print("❌ Usuario no encontrado con email:", email)
            return Response({'error': 'email o contraseña inválidos'}, status=status.HTTP_401_UNAUTHORIZED)

        if usuario.check_password(contraseña):
            print("✅ Contraseña correcta")

            token, created = Token.objects.get_or_create(user=usuario)
            print("✅ Token:", token.key)

            return Response({
                'token': token.key,
                'rol': usuario.rol,
                'username': usuario.username,
            }, status=status.HTTP_200_OK)
        else:
            print("❌ Contraseña incorrecta")
            return Response({'error': 'email o contraseña inválidos'}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)