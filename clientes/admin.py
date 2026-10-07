from django.contrib import admin
from .models import Clientes, Promocion, Membresia, Pago, Asistencia, Inventario

@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'dni', 'correo', 'telefono', 'fecha_registro')
    search_fields = ('nombre', 'dni', 'correo')
    list_filter = ('fecha_registro',)
    ordering = ('-fecha_registro',)

admin.site.register(Promocion)
admin.site.register(Membresia)
admin.site.register(Pago)
admin.site.register(Asistencia)
admin.site.register(Inventario)
