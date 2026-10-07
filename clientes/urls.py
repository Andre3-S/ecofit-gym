from django.urls import path
from .views import eliminar_flyer_promocion, exportar_excel, exportar_pdf, notificaciones, listar_promociones, crear_promocion, editar_promocion, eliminar_promocion, registrar_cliente, listar_clientes, buscar_cliente, editar_cliente, eliminar_cliente, menu_principal, registrar_asistencia, registrar_asistencia_ajax, registrar_pago, listar_pagos, listar_membresias, editar_membresia, eliminar_membresia

urlpatterns = [
    path('notificaciones/', notificaciones, name='notificaciones'),

    path('promociones/', listar_promociones, name='listar_promociones'),
    path('promociones/crear/', crear_promocion, name='crear_promocion'),
    path('promociones/editar/<int:id>/', editar_promocion, name='editar_promocion'),
    path('promociones/eliminar/<int:id>/', eliminar_promocion, name='eliminar_promocion'),

    path('registrar/', registrar_cliente, name='registrar_cliente'),
    path('listar/', listar_clientes, name='listar_clientes'),
    path('buscar/', buscar_cliente, name='buscar_cliente'),
    path('editar/<int:id>/', editar_cliente, name='editar_cliente'),
    path('eliminar/<int:id>/', eliminar_cliente, name='eliminar_cliente'),
    path('asistencia/', registrar_asistencia, name='registrar_asistencia'),
    path('asistencia/ajax/', registrar_asistencia_ajax, name='registrar_asistencia_ajax'),
    path('pago/nuevo/', registrar_pago, name='registrar_pago'),
    path('pagos/', listar_pagos, name='listar_pagos'),
    path('membresias/', listar_membresias, name='listar_membresias'),
    path('membresias/editar/<int:id>/', editar_membresia, name='editar_membresia'),
    path('membresias/eliminar/<int:id>/', eliminar_membresia, name='eliminar_membresia'),
    path('exportar_excel/', exportar_excel, name='exportar_excel'),
    path('exportar_pdf/', exportar_pdf, name='exportar_pdf'),
    path('', menu_principal, name='menu_principal'),
    path('promociones/eliminar_flyer/<int:id>/', eliminar_flyer_promocion, name='eliminar_flyer_promocion'),
]