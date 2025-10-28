# app/paes/paes/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from ensayos.views import ExamViewSet
from usuarios.views import LoginAPIView, current_user
from ensayos import views as ensayos_views

router = routers.DefaultRouter()
router.register(r'exams', ExamViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('api/login/', LoginAPIView.as_view(), name='login'),
    path('current_user/', current_user, name='current_user'),
    path('api/ensayos/', include('ensayos.urls')),
    path('api/preguntas/<int:pregunta_id>/explicacion/', ensayos_views.editar_explicacion, name='editar_explicacion'),
    
]
