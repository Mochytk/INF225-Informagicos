from rest_framework import viewsets
from .serializers import EnsayoSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
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



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_ensayo(request, ensayo_id):
    ensayo = get_object_or_404(Ensayo, pk=ensayo_id)
    alumno = request.user


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


    resultado = Resultado.objects.create(ensayo=ensayo, alumno=alumno, puntaje_total=0)

    total_preguntas = ensayo.preguntas.count()
    correctas = 0
    errores = []

    for idx, rp in enumerate(respuestas_payload):
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

    if total_preguntas > 0:
        puntaje = int((correctas / total_preguntas) * 1000)
    else:
        puntaje = 0

    resultado.puntaje_total = puntaje
    resultado.save()


    resp = {
        'resultado_id': resultado.id,
        'puntaje': resultado.puntaje_total,
        'fecha': resultado.fecha.isoformat()
    }
    if errores:
        resp['errores'] = errores

    return Response(resp, status=status.HTTP_201_CREATED)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def results_summary(request, ensayo_id):
    ensayo = get_object_or_404(Ensayo, pk=ensayo_id)

    user = request.user
    if not (getattr(user, 'rol', None) == 'docente' or user.is_staff):
        return Response({'detail': 'Permisos insuficientes'}, status=status.HTTP_403_FORBIDDEN)

    total_participantes = Resultado.objects.filter(ensayo=ensayo).values('alumno').distinct().count()


    tipos_agg = Respuesta.objects.filter(pregunta__ensayo=ensayo) \
        .values('pregunta__tipo') \
        .annotate(respondidas=Count('id'), correctas=Count('id', filter=Q(correcta=True)))

    by_type = []
    for row in tipos_agg:
        total_resp = row['respondidas'] or 0
        correct_count = row['correctas'] or 0
        pct_type = round((correct_count / total_resp * 100), 1) if total_resp > 0 else 0.0
        by_type.append({
            'tipo': row['pregunta__tipo'],
            'respondidas': total_resp,
            'correctas': correct_count,
            'porcentaje_correctas': pct_type
        })


    preguntas_agg = Respuesta.objects.filter(pregunta__ensayo=ensayo) \
        .values('pregunta__id', 'pregunta__enunciado', 'pregunta__tipo') \
        .annotate(respondidas=Count('id'), correctas=Count('id', filter=Q(correcta=True)))

    by_question = []
    for row in preguntas_agg:
        total_q = row['respondidas'] or 0
        correct_q = row['correctas'] or 0
        pct_q = round((correct_q / total_q * 100), 1) if total_q > 0 else 0.0
        by_question.append({
            'pregunta_id': row['pregunta__id'],
            'texto': row.get('pregunta__enunciado') or '',
            'tipo': row.get('pregunta__tipo') or '',
            'respondidas': total_q,
            'correctas': correct_q,
            'porcentaje_correctas': pct_q
        })


    etiquetas_agg = Respuesta.objects.filter(pregunta__ensayo=ensayo) \
        .values('pregunta__etiquetas__id', 'pregunta__etiquetas__nombre') \
        .annotate(respondidas=Count('id'), correctas=Count('id', filter=Q(correcta=True))) \
        .order_by('-respondidas')

    by_tag = []
    for row in etiquetas_agg:
        tag_id = row.get('pregunta__etiquetas__id')
        tag_name = row.get('pregunta__etiquetas__nombre') or 'Sin etiqueta'
        total_tag = row['respondidas'] or 0
        correct_tag = row['correctas'] or 0
        pct = round((correct_tag / total_tag * 100), 1) if total_tag > 0 else 0.0
        by_tag.append({
            'tag_id': tag_id,
            'tag': tag_name,
            'respondidas': total_tag,
            'correctas': correct_tag,
            'porcentaje_correctas': pct
        })

    return Response({
        'ensayo_id': ensayo.id,
        'titulo': ensayo.titulo,
        'total_participantes': total_participantes,
        'by_type': by_type,
        'by_question': by_question,
        'by_tag': by_tag
    })



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def question_breakdown(request, ensayo_id, pregunta_id):
    ensayo = get_object_or_404(Ensayo, pk=ensayo_id)
    pregunta = get_object_or_404(Pregunta, pk=pregunta_id, ensayo=ensayo)
    user = request.user
    if not (getattr(user, 'rol', None) == 'docente' or user.is_staff):
        return Response({'detail': 'Permisos insuficientes'}, status=status.HTTP_403_FORBIDDEN)

    respuestas_qs = Respuesta.objects.filter(pregunta=pregunta)
    total = respuestas_qs.count()
    correctas = respuestas_qs.filter(correcta=True).count()
    porcentaje_correctos = round((correctas / total * 100), 1) if total > 0 else 0.0

    opciones_data = []
    for opcion in pregunta.opciones.all():
        count_op = respuestas_qs.filter(opcion=opcion).count()
        porcentaje = round((count_op / total * 100), 1) if total > 0 else 0.0
        opciones_data.append({
            'id': opcion.id,
            'texto': getattr(opcion, 'texto', ''),
            'porcentaje': porcentaje
        })

    return Response({
        'pregunta_id': pregunta.id,
        'texto': getattr(pregunta, 'enunciado', ''),
        'tipo': pregunta.tipo,
        'total_respondieron': total,
        'porcentaje_correctos': porcentaje_correctos,
        'opciones': opciones_data
    })
