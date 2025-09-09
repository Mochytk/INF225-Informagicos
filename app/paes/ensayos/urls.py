from django.urls import path
from . import views

urlpatterns = [
    path('<int:ensayo_id>/submit/', views.submit_ensayo, name='submit_ensayo'),
    path('<int:ensayo_id>/results/summary/', views.results_summary, name='results_summary'),
    path('<int:ensayo_id>/questions/<int:pregunta_id>/breakdown/', views.question_breakdown, name='question_breakdown'),
]
