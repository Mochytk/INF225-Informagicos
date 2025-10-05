from django.contrib import admin
from .models import Ensayo, Pregunta, Opcion, Resultado, Respuesta, Etiqueta

class OpcionInline(admin.TabularInline):
    model = Opcion
    extra = 4
    min_num = 1

class PreguntaInline(admin.StackedInline):
    model = Pregunta
    extra = 1


@admin.register(Ensayo)
class EnsayoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'materia', 'curso', 'fecha')
    search_fields = ('titulo', 'materia', 'curso')
    inlines = [PreguntaInline]

@admin.register(Etiqueta)
class EtiquetaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Pregunta)
class PreguntaAdmin(admin.ModelAdmin):
    list_display = ('id', 'enunciado', 'tipo', 'ensayo', 'explicacion_texto', 'explicacion_url', 'resumen_enunciado')
    list_filter = ('tipo',)
    search_fields = ('enunciado',)
    filter_horizontal = ('etiquetas',)
    inlines = [OpcionInline]

    def resumen_enunciado(self, obj):
        return (obj.enunciado[:60] + '...') if len(obj.enunciado) > 60 else obj.enunciado
    resumen_enunciado.short_description = 'Enunciado'

@admin.register(Opcion)
class OpcionAdmin(admin.ModelAdmin):
    list_display = ('id', 'texto', 'pregunta', 'es_correcta')
    list_filter = ('es_correcta',)

@admin.register(Resultado)
class ResultadoAdmin(admin.ModelAdmin):
    list_display = ('ensayo','alumno','puntaje_total','fecha')
    readonly_fields = ('puntaje_total','fecha')

@admin.register(Respuesta)
class RespuestaAdmin(admin.ModelAdmin):
    list_display = ('resultado','pregunta','opcion','correcta')

