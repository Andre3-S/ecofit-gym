
from django.shortcuts import render, redirect, get_object_or_404
from .models import Clientes
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from datetime import timedelta

from django.shortcuts import render, redirect
from .models import Clientes

@login_required
def registrar_cliente(request):
    mensaje = None
    error = None

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        dni = request.POST.get("dni")
        correo = request.POST.get("correo")
        telefono = request.POST.get("telefono")
        
        # 🔴 VALIDACIÓN: DNI debe tener exactamente 8 dígitos
        if len(dni) != 8:
            error = "El DNI debe tener exactamente 8 dígitos."
            return render(request, "registrar_cliente.html", {
                "mensaje": mensaje,
                "error": error
            })

        try:
            Clientes.objects.create(
                nombre=nombre,
                dni=dni,
                correo=correo,
                telefono=telefono
            )

            messages.success(request, "Cliente registrado correctamente.")
            return redirect("menu_principal")

        except IntegrityError:
            error = "El DNI ingresado ya está registrado."

    return render(request, "registrar_cliente.html", {
        "mensaje": mensaje,
        "error": error
    })


@login_required
def listar_clientes(request):
    clientes = Clientes.objects.all()
    promociones_activas = Promocion.objects.filter(activa=True)
    mensaje = None
    return render(request, 'listar_clientes.html', {
        "clientes": clientes,
        "mensaje": mensaje
    })

@login_required
def buscar_cliente(request):
    cliente = None
    if request.method == 'POST':
        dni = request.POST.get('dni')
        try:
            cliente = Clientes.objects.get(dni=dni)
        except Clientes.DoesNotExist:
            cliente = "no_encontrado"
            
    mensaje = None
    return render(request, 'buscar_cliente.html', {"cliente": cliente,"mensaje": mensaje})

@login_required
def editar_cliente(request, id):
    cliente = Clientes.objects.get(id=id)

    if request.method == 'POST':
        cliente.nombre = request.POST['nombre']
        cliente.dni = request.POST['dni']
        cliente.correo = request.POST['correo']
        cliente.telefono = request.POST['telefono']
        cliente.save()
        messages.success(request, "Cliente editado correctamente.")
        return redirect("buscar_cliente")

    return render(request, 'editar_cliente.html', {"cliente": cliente})

@login_required
def eliminar_cliente(request, id):
    cliente = get_object_or_404(Clientes, id=id)  # buscamos el cliente
    cliente.delete()  # lo eliminamos
    messages.success(request, f"Cliente {cliente.nombre} eliminado correctamente.")
    return redirect("buscar_cliente")

@login_required
def registrar_asistencia(request):
    mensaje = None
    error = None
    hoy = timezone.now().date()
    
    if request.method == 'POST':
        dni = request.POST.get('dni')
        try:
            cliente = Clientes.objects.get(dni=dni)
            Asistencia.objects.create(cliente=cliente)
            mensaje = f"Asistencia registrada exitosamente para {cliente.nombre}."
        except Clientes.DoesNotExist:
            error = "No existe un cliente con ese DNI."
            
    asistencias_hoy = Asistencia.objects.filter(fecha_hora_ingreso__date=hoy).order_by('-fecha_hora_ingreso')
            
    return render(request, 'registrar_asistencia.html', {
        'mensaje': mensaje,
        'error': error,
        'asistencias_hoy': asistencias_hoy
    })

@login_required
def registrar_pago(request):
    clientes = Clientes.objects.all()
    promociones_activas = Promocion.objects.filter(activa=True)
    error = None
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente')
        tipo_membresia = request.POST.get('tipo_membresia')
        duracion_meses = int(request.POST.get('duracion_meses', 1))
        monto = request.POST.get('monto')
        monto_total = request.POST.get('monto_total', monto)
        metodo_pago = request.POST.get('metodo_pago')
        
        deuda = max(0, float(monto_total) - float(monto))
        promocion_id = request.POST.get('promocion')
        promocion_obj = Promocion.objects.get(id=promocion_id) if promocion_id else None
        
        try:
            cliente = Clientes.objects.get(id=cliente_id)
            
            # Crear o actualizar la membresia (Asignación automática tras el pago)
            fecha_hoy = timezone.now().date()
            fecha_venc = fecha_hoy + timedelta(days=30 * duracion_meses)
            
            # Buscar si el cliente ya tiene una membresía para actualizarla o crear una nueva
            membresia, created = Membresia.objects.get_or_create(
                cliente=cliente,
                defaults={
                    'tipo': tipo_membresia,
                    'fecha_inicio': fecha_hoy,
                    'fecha_vencimiento': fecha_venc,
                    'costo': monto_total,
                    'estado': 'Activa',
                    'promocion': promocion_obj
                }
            )
            
            if not created:
                membresia.tipo = tipo_membresia
                membresia.fecha_inicio = fecha_hoy
                membresia.fecha_vencimiento = fecha_venc
                membresia.costo = monto_total
                membresia.estado = 'Activa'
                membresia.promocion = promocion_obj
                membresia.save()
                
            # Registrar el pago asociado a la membresía
            Pago.objects.create(
                cliente=cliente,
                membresia=membresia,
                monto=monto,
                metodo_pago=metodo_pago,
                deuda=deuda
            )
            
            messages.success(request, f"Pago de S/{monto} registrado exitosamente para {cliente.nombre} y Membresía {tipo_membresia} por {duracion_meses} mes(es) activada.")
            return redirect('listar_pagos')
            
        except Exception as e:
            error = f"Error al procesar el pago: {str(e)}"
            
    return render(request, 'registrar_pago.html', {'clientes': clientes, 'error': error, 'promociones_activas': promociones_activas})

@login_required
def listar_pagos(request):
    from django.db.models import Sum, Count
    from django.utils import timezone
    hoy = timezone.now().date()
    pagos = Pago.objects.all().order_by('-fecha')
    
    # Metricas
    ingresos_hoy = Pago.objects.filter(fecha__year=hoy.year, fecha__month=hoy.month, fecha__day=hoy.day).aggregate(total=Sum('monto'))['total'] or 0
    deuda_total = Pago.objects.aggregate(total=Sum('deuda'))['total'] or 0
    metodo_fav = Pago.objects.values('metodo_pago').annotate(total=Count('id')).order_by('-total').first()
    metodo_nombre = metodo_fav['metodo_pago'] if metodo_fav else 'Ninguno'
    
    context = {
        'pagos': pagos,
        'ingresos_hoy': ingresos_hoy,
        'deuda_total': deuda_total,
        'metodo_nombre': metodo_nombre
    }
    return render(request, 'listar_pagos.html', context)

@login_required
def listar_membresias(request):
    hoy = timezone.now().date()
    Membresia.objects.filter(fecha_vencimiento__lt=hoy, estado='Activa').update(estado='Vencida')
    
    from django.db.models import Sum, Count
    
    membresias = list(Membresia.objects.all().order_by('-fecha_inicio'))
    
    for m in membresias:
        dias = (m.fecha_vencimiento - m.fecha_inicio).days
        if dias >= 360:
            m.duracion_texto = '12 Meses'
        elif dias >= 170:
            m.duracion_texto = '6 Meses'
        elif dias >= 80:
            m.duracion_texto = '3 Meses'
        else:
            meses = max(1, round(dias / 30.0))
            m.duracion_texto = f'{meses} Mes' if meses == 1 else f'{meses} Meses'
            
    # Metricas
    ingresos_mes = Membresia.objects.filter(fecha_inicio__year=hoy.year, fecha_inicio__month=hoy.month).aggregate(total=Sum('costo'))['total'] or 0
    
    tipo_popular = Membresia.objects.filter(estado='Activa').values('tipo').annotate(total=Count('id')).order_by('-total').first()
    popular_name = tipo_popular['tipo'] if tipo_popular else 'Ninguna'
    popular_count = tipo_popular['total'] if tipo_popular else 0
    
    renovaciones_hoy = Membresia.objects.filter(fecha_inicio=hoy).count()
    
    context = {
        'membresias': membresias,
        'ingresos_mes': ingresos_mes,
        'popular_name': popular_name,
        'popular_count': popular_count,
        'renovaciones_hoy': renovaciones_hoy
    }
    return render(request, 'listar_membresias.html', context)

@login_required
def editar_membresia(request, id):
    membresia = get_object_or_404(Membresia, id=id)
    if request.method == 'POST':
        membresia.tipo = request.POST.get('tipo_membresia')
        # We manually parse the dates. Note: Depending on HTML date format. Usually YYYY-MM-DD
        membresia.fecha_inicio = request.POST.get('fecha_inicio')
        membresia.fecha_vencimiento = request.POST.get('fecha_vencimiento')
        membresia.estado = request.POST.get('estado')
        membresia.save()
        
        messages.success(request, "Membresía editada correctamente.")
        return redirect('listar_membresias')
        
    return render(request, 'editar_membresia.html', {'membresia': membresia})

from django.utils import timezone
from .models import Clientes, Membresia, Pago, Asistencia, Promocion, Inventario

from django.db.models import Sum

from django.db.models import Sum, Max, F
from datetime import timedelta
import csv
from django.http import HttpResponse


import io
import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse

@login_required
def exportar_excel(request):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Historial_Pagos_EcoFit.xlsx"'
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Pagos'
    
    ws.merge_cells('A1:F2')
    title_cell = ws.cell(row=1, column=1, value='REPORTE DE PAGOS - ECOFIT GYM')
    title_cell.font = Font(size=16, bold=True, color='FFFFFF')
    title_cell.fill = PatternFill(start_color='2C3E50', end_color='2C3E50', fill_type='solid')
    title_cell.alignment = Alignment(horizontal='center', vertical='center')
    
    headers = ['Fecha', 'Cliente', 'Membresía', 'Método', 'Monto Pagado', 'Deuda Pendiente']
    header_fill = PatternFill(start_color='27AE60', end_color='27AE60', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF')
    border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col_num, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center')
        cell.border = border
        ws.column_dimensions[openpyxl.utils.get_column_letter(col_num)].width = 22
        
    pagos = Pago.objects.all().order_by('-fecha')
    row_num = 5
    
    for pago in pagos:
        ws.cell(row=row_num, column=1, value=pago.fecha.strftime('%d/%m/%Y %H:%M')).alignment = Alignment(horizontal='center')
        ws.cell(row=row_num, column=2, value=pago.cliente.nombre)
        ws.cell(row=row_num, column=3, value=pago.membresia.tipo)
        ws.cell(row=row_num, column=4, value=pago.metodo_pago).alignment = Alignment(horizontal='center')
        
        monto_cell = ws.cell(row=row_num, column=5, value=float(pago.monto))
        monto_cell.number_format = '"S/" #,##0.00'
        
        if pago.deuda and pago.deuda > 0:
            deuda_cell = ws.cell(row=row_num, column=6, value=float(pago.deuda))
            deuda_cell.number_format = '"S/" #,##0.00'
            deuda_cell.font = Font(color='E74C3C', bold=True)
        else:
            ws.cell(row=row_num, column=6, value='Cancelado').alignment = Alignment(horizontal='center')
            
        row_num += 1
        
    wb.save(response)
    return response

@login_required
def exportar_pdf(request):
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Historial_Pagos_EcoFit.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=30)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#2C3E50'),
        alignment=1,
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    
    elements.append(Paragraph('REPORTE OFICIAL DE PAGOS - ECOFIT GYM', title_style))
    elements.append(Spacer(1, 15))
    
    pagos = Pago.objects.all().order_by('-fecha')
    
    data = [['FECHA', 'CLIENTE', 'MEMBRESÍA', 'MÉTODO', 'PAGADO', 'DEUDA']]
    
    for pago in pagos:
        deuda_texto = f'S/ {pago.deuda}' if pago.deuda and pago.deuda > 0 else 'Cancelado'
        data.append([
            pago.fecha.strftime('%d/%m/%Y'),
            pago.cliente.nombre[:22],
            pago.membresia.tipo,
            pago.metodo_pago,
            f'S/ {pago.monto}',
            deuda_texto
        ])
        
    t = Table(data, colWidths=[70, 140, 80, 70, 75, 75])
    
    t_style = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#27AE60')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (1,1), (1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('TOPPADDING', (0,0), (-1,0), 10),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor('#333333')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('BOTTOMPADDING', (0,1), (-1,-1), 8),
        ('TOPPADDING', (0,1), (-1,-1), 8),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8F9F9')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7E9')),
    ]
    
    for row_idx, row_data in enumerate(data):
        if row_idx == 0: continue
        if row_data[5] != 'Cancelado':
            t_style.append(('TEXTCOLOR', (5, row_idx), (5, row_idx), colors.HexColor('#E74C3C')))
            t_style.append(('FONTNAME', (5, row_idx), (5, row_idx), 'Helvetica-Bold'))
        else:
            t_style.append(('TEXTCOLOR', (5, row_idx), (5, row_idx), colors.HexColor('#7F8C8D')))
            
    t.setStyle(TableStyle(t_style))
    
    elements.append(t)
    doc.build(elements)
    return response

@login_required
def menu_principal(request):
    mensaje = None
    
    # Dashboard Stats
    total_clientes = Clientes.objects.count()
    membresias_activas = Membresia.objects.filter(estado='Activa').count()
    
    today = timezone.now().date()
    asistencias_hoy = Asistencia.objects.filter(fecha_hora_ingreso__date=today).count()
    
    pagos_recientes = Pago.objects.order_by('-fecha')[:4]
    
    # Smart Alerts Logic
    limite_vencimiento = today + timedelta(days=7)
    alertas_vencimiento = Membresia.objects.filter(estado='Activa', fecha_vencimiento__lte=limite_vencimiento).count()
    
    hace_15_dias = timezone.now() - timedelta(days=15)
    # Clientes activos que no han venido en 15 dias
    clientes_en_riesgo = Clientes.objects.filter(
        membresias__estado='Activa'
    ).annotate(
        ultima_asistencia=Max('asistencias__fecha_hora_ingreso')
    ).filter(
        ultima_asistencia__lt=hace_15_dias
    ).count()
    
    membresias_vencidas = Membresia.objects.filter(estado='Vencida', fecha_vencimiento__gte=today - timedelta(days=30)).count()

    # Determine alert state
    alerta_tipo = "success"
    alerta_titulo = "¡Todo al día!"
    alerta_mensaje = "No hay tareas urgentes hoy. Excelente trabajo."
    alerta_icono = "fa-check-circle"
    alerta_color = "#00E676"
    
    if membresias_vencidas > 0:
        alerta_tipo = "danger"
        alerta_titulo = "Pagos Atrasados"
        alerta_mensaje = f"Hay {membresias_vencidas} membresías vencidas recientemente. Urgente contactar."
        alerta_icono = "fa-circle-xmark"
        alerta_color = "#ff4444"
    elif alertas_vencimiento > 0:
        alerta_tipo = "warning"
        alerta_titulo = "Próximos Vencimientos"
        alerta_mensaje = f"{alertas_vencimiento} membresías vencen en los próximos 7 días."
        alerta_icono = "fa-triangle-exclamation"
        alerta_color = "#ffc107"
    elif clientes_en_riesgo > 0:
        alerta_tipo = "risk"
        alerta_titulo = "Riesgo de Fuga"
        alerta_mensaje = f"{clientes_en_riesgo} clientes activos no han asistido en más de 15 días."
        alerta_icono = "fa-user-clock"
        alerta_color = "#f59e0b"

    # Calcular ingresos del mes
    primer_dia_mes = today.replace(day=1)
    ingresos_mes_dict = Pago.objects.filter(fecha__gte=primer_dia_mes).aggregate(Sum('monto'))
    ingresos_mes = ingresos_mes_dict['monto__sum'] or 0
    meta_mensual = 50000  
    porcentaje_meta = min(int((ingresos_mes / meta_mensual) * 100), 100) if meta_mensual > 0 else 0

    context = {
        "mensaje": mensaje,
        "total_clientes": total_clientes,
        "membresias_activas": membresias_activas,
        "asistencias_hoy": asistencias_hoy,
        "pagos_recientes": pagos_recientes,
        "ingresos_mes": ingresos_mes,
        "meta_mensual": meta_mensual,
        "porcentaje_meta": porcentaje_meta,
        "alerta_tipo": alerta_tipo,
        "alerta_titulo": alerta_titulo,
        "alerta_mensaje": alerta_mensaje,
        "alerta_icono": alerta_icono,
        "alerta_color": alerta_color,
    }
    return render(request, "menu_principal.html", context)
def login_usuario(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('menu_principal')  # va al menú principal
        else:
            return render(request, 'login.html', {"error": "Usuario o contraseña incorrectos"})

    return render(request, 'login.html')
@login_required
def listar_promociones(request):
    promociones = Promocion.objects.all().order_by('-activa', 'nombre')
    return render(request, 'listar_promociones.html', {'promociones': promociones})

@login_required
def crear_promocion(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        descuento = request.POST.get('descuento_porcentaje')
        tipo = request.POST.get('tipo', 'Especial')
        fecha_limite = request.POST.get('fecha_limite')
        if not fecha_limite:
            fecha_limite = None
        activa = request.POST.get('activa') == 'on' or request.POST.get('activa') == 'true' or request.POST.get('activa') == '1'
        imagen = request.FILES.get('imagen')
        
        Promocion.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            tipo=tipo,
            descuento_porcentaje=descuento,
            fecha_limite=fecha_limite,
            activa=True,
            imagen=imagen
        )
        messages.success(request, 'Promoción creada exitosamente.')
        return redirect('listar_promociones')
    return render(request, 'crear_promocion.html')

@login_required
def editar_promocion(request, id):
    promocion = get_object_or_404(Promocion, id=id)
    if request.method == 'POST':
        promocion.nombre = request.POST.get('nombre')
        promocion.descripcion = request.POST.get('descripcion')
        promocion.descuento_porcentaje = request.POST.get('descuento_porcentaje')
        promocion.activa = request.POST.get('activa') == 'on'
        promocion.save()
        messages.success(request, 'Promoción actualizada exitosamente.')
        return redirect('listar_promociones')
    return render(request, 'editar_promocion.html', {'promocion': promocion})

@login_required
def eliminar_promocion(request, id):
    promocion = get_object_or_404(Promocion, id=id)
    if request.method == 'POST':
        nombre = promocion.nombre
        promocion.delete()
        messages.success(request, f'Promoción {nombre} eliminada.')
    return redirect('listar_promociones')

@login_required
def notificaciones(request):
    from django.db.models import Sum
    from datetime import timedelta
    from django.utils import timezone
    hoy = timezone.now().date()
    limite_vencimiento = hoy + timedelta(days=7)
    
    # 1. Próximos a Vencer (7 días o menos)
    proximos_a_vencer = Membresia.objects.filter(
        estado='Activa',
        fecha_vencimiento__gte=hoy,
        fecha_vencimiento__lte=limite_vencimiento
    ).order_by('fecha_vencimiento')
    
    for m in proximos_a_vencer:
        dias = (m.fecha_vencimiento - hoy).days
        m.dias_restantes = dias
    
    # 2. Inactivos (Vencidos)
    inactivos = Membresia.objects.filter(estado='Vencida').order_by('-fecha_vencimiento')
    
    for m in inactivos:
        dias = (hoy - m.fecha_vencimiento).days
        m.dias_vencido = dias
    
    # 3. Con Deuda (Cobranzas)
    activas = Membresia.objects.filter(estado='Activa')
    con_deuda = []
    for m in activas:
        total_pagado = Pago.objects.filter(membresia=m).aggregate(total=Sum('monto'))['total'] or 0
        if total_pagado < m.costo:
            m.deuda_real = float(m.costo) - float(total_pagado)
            ultimo_pago = Pago.objects.filter(membresia=m).order_by('-fecha').first()
            m.fecha_ultimo_pago = ultimo_pago.fecha if ultimo_pago else m.fecha_inicio
            con_deuda.append(m)
            
    con_deuda.sort(key=lambda x: x.deuda_real, reverse=True)

    return render(request, 'notificaciones.html', {
        'proximos_a_vencer': proximos_a_vencer,
        'inactivos': inactivos,
        'con_deuda': con_deuda
    })


@login_required
def eliminar_flyer_promocion(request, id):
    promocion = get_object_or_404(Promocion, id=id)
    if promocion.imagen:
        promocion.imagen.delete()
        promocion.save()
    messages.success(request, 'Flyer eliminado del carrusel.')
    return redirect('listar_promociones')


@login_required
def eliminar_membresia(request, id):
    membresia = get_object_or_404(Membresia, id=id)
    if request.method == 'POST':
        membresia.delete()
        messages.success(request, 'Membresía eliminada correctamente.')
    return redirect('listar_membresias')

from django.http import JsonResponse

def registrar_asistencia_ajax(request):
    if request.method == 'POST':
        dni = request.POST.get('dni')
        try:
            cliente = Clientes.objects.get(dni=dni)
        except Clientes.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Cliente no encontrado con ese DNI.'})
            
        # Registrar asistencia
        Asistencia.objects.create(cliente=cliente)
        
        hoy = timezone.now().date()
        membresia = Membresia.objects.filter(cliente=cliente).order_by('-fecha_vencimiento').first()
        
        status_code = 'success'
        status_msg = f'¡Bienvenido, {cliente.nombre.split()[0]}!'
        deuda_msg = ''
        
        if not membresia:
            status_code = 'error'
            status_msg = 'Sin membresía registrada.'
        elif membresia.estado == 'Vencida' or membresia.fecha_vencimiento < hoy:
            status_code = 'error'
            status_msg = 'Membresía Vencida. Renovar.'
        else:
            from django.db.models import Sum
            total_pagado = Pago.objects.filter(membresia=membresia).aggregate(total=Sum('monto'))['total'] or 0
            if total_pagado < membresia.costo:
                deuda = float(membresia.costo) - float(total_pagado)
                status_code = 'warning'
                deuda_msg = f'Saldo pendiente: S/ {deuda:.2f}'
            else:
                dias_restantes = (membresia.fecha_vencimiento - hoy).days
                if dias_restantes <= 3:
                    status_code = 'warning'
                    deuda_msg = f'Vence en {dias_restantes} días'
                    
        return JsonResponse({
            'status': status_code,
            'message': status_msg,
            'deuda_msg': deuda_msg,
            'client_name': cliente.nombre,
            'plan': membresia.tipo if membresia else 'N/A',
            'client_id': cliente.id,
            'time': timezone.now().strftime('%H:%M:%S')
        })
    return JsonResponse({'status': 'error', 'message': 'Invalid'})
