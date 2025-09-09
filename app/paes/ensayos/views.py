from rest_framework import viewsets
from .serializers import EnsayoSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Ensayo, Pregunta, Opcion, Resultado, Respuesta

class ExamViewSet(viewsets.ModelViewSet):
    """
    ViewSet mínimo para exponer Ensayo vía /api/exams/
    """
    queryset = Ensayo.objects.all().order_by('-fecha')
    serializer_class = EnsayoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

# 1) Endpoint: POST /api/ensayos/<ensayo_id>/submit/
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_ensayo(request, ensayo_id):
    ensayo = get_object_or_404(Ensayo, pk=ensayo_id)
    # alumno = request.user (asumimos que el usuario es el alumno que responde)
    alumno = request.user

    payload = request.data
    respuestas_payload = payload.get('respuestas', [])
    if not isinstance(respuestas_payload, list):
        return Response({'error': 'Campo "respuestas" debe ser una lista.'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Crear Resultado
    resultado = Resultado.objects.create(ensayo=ensayo, alumno=alumno, puntaje_total=0)

    total_preguntas = ensayo.preguntas.count()
    correctas = 0

    for rp in respuestas_payload:
        pregunta_id = rp.get('pregunta_id')
        opcion_id = rp.get('opcion_id')
        texto = rp.get('texto', None)

        try:
            pregunta = Pregunta.objects.get(pk=pregunta_id, ensayo=ensayo)
        except Pregunta.DoesNotExist:
            # ignorar o recolectar errores: aquí se ignora
            continue

        opcion_obj = None
        correcta = False

        if opcion_id:
            try:
                opcion_obj = Opcion.objects.get(pk=opcion_id, pregunta=pregunta)
                correcta = opcion_obj.es_correcta
            except Opcion.DoesNotExist:
                opcion_obj = None
                correcta = False
        else:
            # Si no hay opción (pregunta abierta), marcar correcta=False por defecto;
            # si luego se evalúa manualmente, se podrá actualizar 'correcta' en admin.
            correcta = False

        if correcta:
            correctas += 1

        Respuesta.objects.create(
            resultado=resultado,
            pregunta=pregunta,
            opcion=opcion_obj,
            texto=texto if texto is not None else '',
            correcta=correcta
        )

    # Calcular puntaje (escala 0-1000)
    if total_preguntas > 0:
        puntaje = int((correctas / total_preguntas) * 1000)
    else:
        puntaje = 0

    resultado.puntaje_total = puntaje
    resultado.save()

    return Response({
        'resultado_id': resultado.id,
        'puntaje': resultado.puntaje_total,
        'fecha': resultado.fecha
    }, status=status.HTTP_201_CREATED)


# 2) Endpoint: GET /api/ensayos/<ensayo_id>/results/summary/
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def results_summary(request, ensayo_id):
    ensayo = get_object_or_404(Ensayo, pk=ensayo_id)

    # Permisos básicos: solo docentes (o staff) pueden ver resumen
    user = request.user
    if not (getattr(user, 'rol', None) == 'docente' or user.is_staff):
        return Response({'detail': 'Permisos insuficientes'}, status=status.HTTP_403_FORBIDDEN)

    total_participantes = Resultado.objects.filter(ensayo=ensayo).values('alumno').distinct().count()

    # Agregación por tipo de pregunta
    tipos = ensayo.preguntas.values_list('tipo', flat=True).distinct()
    by_type = []
    for t in tipos:
        preguntas_tipo = ensayo.preguntas.filter(tipo=t)
        preguntas_ids = list(preguntas_tipo.values_list('id', flat=True))
        # respuestas relativas a esas preguntas
        respuestas_qs = Respuesta.objects.filter(pregunta_id__in=preguntas_ids)
        respondidas = respuestas_qs.count()  # total de respuestas registradas
        correctas = respuestas_qs.filter(correcta=True).count()
        # número de preguntas (cantidad de items de ese tipo en el ensayo)
        cantidad_preguntas = preguntas_tipo.count()
        porcentaje_correctas = round((correctas / respondidas * 100), 1) if respondidas > 0 else 0.0

        by_type.append({
            'tipo': t,
            'preguntas': cantidad_preguntas,
            'correctas': correctas,
            'respondidas': respondidas,
            'porcentaje_correctas': porcentaje_correctas
        })

    return Response({
        'ensayo_id': ensayo.id,
        'titulo': ensayo.titulo,
        'total_participantes': total_participantes,
        'by_type': by_type
    })


# 3) Endpoint: GET /api/ensayos/<ensayo_id>/questions/<pregunta_id>/breakdown/
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def question_breakdown(request, ensayo_id, pregunta_id):
    ensayo = get_object_or_404(Ensayo, pk=ensayo_id)
    pregunta = get_object_or_404(Pregunta, pk=pregunta_id, ensayo=ensayo)

    # Permisos: solo docente o staff
    user = request.user
    if not (getattr(user, 'rol', None) == 'docente' or user.is_staff):
        return Response({'detail': 'Permisos insuficientes'}, status=status.HTTP_403_FORBIDDEN)

    respuestas_qs = Respuesta.objects.filter(pregunta=pregunta)
    total = respuestas_qs.count()
    correctas = respuestas_qs.filter(correcta=True).count()
    porcentaje_correctos = round((correctas / total * 100), 1) if total > 0 else 0.0

    opciones_data = []
    # Para preguntas con opciones
    for opcion in pregunta.opciones.all():
        count_op = respuestas_qs.filter(opcion=opcion).count()
        porcentaje = round((count_op / total * 100), 1) if total > 0 else 0.0
        opciones_data.append({
            'id': opcion.id,
            'texto': getattr(pregunta, 'enunciado', ''),
            'porcentaje': porcentaje
        })

    return Response({
        'pregunta_id': pregunta.id,
        'texto': pregunta.texto,
        'tipo': pregunta.tipo,
        'total_respondieron': total,
        'porcentaje_correctos': porcentaje_correctos,
        'opciones': opciones_data
    })
