# app/paes/ensayos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # rutas relativas a /api/ensayos/ (porque paes.urls hace include('ensayos.urls') en 'api/ensayos/')
    path('<int:ensayo_id>/submit/', views.submit_ensayo, name='submit_ensayo'),
    path('<int:ensayo_id>/results/summary/', views.results_summary, name='results_summary'),
    path('<int:ensayo_id>/questions/<int:pregunta_id>/breakdown/', views.question_breakdown, name='question_breakdown'),

    # nuevos endpoints
    path('completados/', views.ensayos_completados, name='ensayos_completados'),
    path('<int:ensayo_id>/results/<int:resultado_id>/review/', views.review_resultado, name='review_resultado'),
    path('preguntas/<int:pregunta_id>/explicacion/', views.editar_explicacion, name='editar_explicacion'),
]
