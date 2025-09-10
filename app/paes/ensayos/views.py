from rest_framework import viewsets
from .serializers import EnsayoSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Ensayo, Pregunta, Opcion, Resultado, Respuesta
import logging
import json
logger = logging.getLogger(__name__)
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
    alumno = request.user

    # Normalizar payload: permitir body = list o body = {"respuestas": [...]}
    data = request.data
    if isinstance(data, list):
        respuestas_payload = data
    elif isinstance(data, dict) and 'respuestas' in data:
        respuestas_payload = data.get('respuestas') or []
    else:
        return Response({'error': 'Payload inválido. Esperado {"respuestas": [...]} o un array.'},
                        status=status.HTTP_400_BAD_REQUEST)

    if not isinstance(respuestas_payload, list):
        return Response({'error': 'Campo "respuestas" debe ser una lista.'},
                        status=status.HTTP_400_BAD_REQUEST)

    # Crear Resultado
    resultado = Resultado.objects.create(ensayo=ensayo, alumno=alumno, puntaje_total=0)

    total_preguntas = ensayo.preguntas.count()
    correctas = 0
    errores = []

    for idx, rp in enumerate(respuestas_payload):
        # Si rp es string, intentar parsear como JSON
        if isinstance(rp, str):
            try:
                rp = json.loads(rp)
            except Exception as e:
                errores.append({'index': idx, 'error': 'Elemento no parseable como JSON', 'raw': str(rp)})
                continue

        if not isinstance(rp, dict):
            errores.append({'index': idx, 'error': 'Elemento debe ser un objeto con keys pregunta_id/opcion_id/texto', 'raw': str(rp)})
            continue

        pregunta_id = rp.get('pregunta_id')
        opcion_id = rp.get('opcion_id')
        texto = rp.get('texto', None)

        # Validaciones básicas
        if pregunta_id is None:
            errores.append({'index': idx, 'error': 'Falta pregunta_id', 'data': rp})
            continue

        try:
            pregunta = Pregunta.objects.get(pk=int(pregunta_id), ensayo=ensayo)
        except (Pregunta.DoesNotExist, ValueError):
            errores.append({'index': idx, 'error': f'Pregunta {pregunta_id} no encontrada en el ensayo {ensayo_id}.'})
            continue

        opcion_obj = None
        correcta = False

        if opcion_id is not None:
            try:
                opcion_id_int = int(opcion_id)
            except Exception:
                errores.append({'index': idx, 'error': f'opcion_id inválido: {opcion_id}'})
                continue

            try:
                opcion_obj = Opcion.objects.get(pk=opcion_id_int)
                # verificar relación pregunta<->opcion
                if opcion_obj.pregunta_id != pregunta.id:
                    errores.append({'index': idx, 'error': f'Opción {opcion_id_int} no pertenece a la pregunta {pregunta_id}.'})
                    opcion_obj = None
                    correcta = False
                else:
                    correcta = bool(opcion_obj.es_correcta)
            except Opcion.DoesNotExist:
                errores.append({'index': idx, 'error': f'Opción {opcion_id_int} no encontrada.'})
                opcion_obj = None
                correcta = False
        else:
            # pregunta abierta: texto puede estar presente
            correcta = False

        if correcta:
            correctas += 1

        # Crear la respuesta (aunque tenga opcion_obj None, se guarda texto)
        Respuesta.objects.create(
            resultado=resultado,
            pregunta=pregunta,
            opcion=opcion_obj,
            texto=texto if texto is not None else '',
            correcta=correcta
        )

    # Calcular punto total (escala 0-1000)
    if total_preguntas > 0:
        puntaje = int((correctas / total_preguntas) * 1000)
    else:
        puntaje = 0

    resultado.puntaje_total = puntaje
    resultado.save()

    # Respuesta: incluir errores si los hubo (no abortamos) para que frontend los muestre
    resp = {
        'resultado_id': resultado.id,
        'puntaje': resultado.puntaje_total,
        'fecha': resultado.fecha.isoformat()
    }
    if errores:
        resp['errores'] = errores

    return Response(resp, status=status.HTTP_201_CREATED)


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
            'texto': getattr(opcion, 'texto', ''),   # 👈 aquí debe ir el texto de la opción
            'porcentaje': porcentaje
        })

    return Response({
        'pregunta_id': pregunta.id,
        'texto': getattr(pregunta, 'enunciado', ''),  # 👈 aquí debe ir el enunciado de la pregunta
        'tipo': pregunta.tipo,
        'total_respondieron': total,
        'porcentaje_correctos': porcentaje_correctos,
        'opciones': opciones_data
    })
