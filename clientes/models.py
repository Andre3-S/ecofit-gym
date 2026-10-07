from django.db import models
from django.utils import timezone

class Clientes(models.Model):
    nombre = models.CharField(max_length=100)
    dni = models.CharField(max_length=8, unique=True)
    correo = models.EmailField()
    telefono = models.CharField(max_length=9)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Promocion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=50, default='Estacional')
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=2)
    fecha_limite = models.DateField(null=True, blank=True)
    activa = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='promociones/', null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} - {self.descuento_porcentaje}%"

class Membresia(models.Model):
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE, related_name='membresias')
    tipo = models.CharField(
        max_length=20,
        choices=[
            ('Básica', 'Básica'),
            ('Premium', 'Premium'),
            ('VIP', 'VIP')
        ],
        default='Básica'
    )
    fecha_inicio = models.DateField(default=timezone.now)
    fecha_vencimiento = models.DateField()
    costo = models.DecimalField(max_digits=8, decimal_places=2)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('Activa', 'Activa'),
            ('Vencida', 'Vencida')
        ],
        default='Activa'
    )
    promocion = models.ForeignKey(Promocion, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.tipo} - {self.cliente.nombre}"

class Pago(models.Model):
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE, related_name='pagos')
    membresia = models.ForeignKey(Membresia, on_delete=models.CASCADE, related_name='pagos')
    fecha = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    deuda = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    metodo_pago = models.CharField(
        max_length=20,
        choices=[
            ('Efectivo', 'Efectivo'),
            ('Yape', 'Yape'),
            ('Plin', 'Plin'),
            ('Tarjeta', 'Tarjeta')
        ],
        default='Efectivo'
    )

    def __str__(self):
        return f"Pago de {self.monto} - {self.cliente.nombre}"

class Asistencia(models.Model):
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE, related_name='asistencias')
    fecha_hora_ingreso = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cliente.nombre} - {self.fecha_hora_ingreso}"

class Inventario(models.Model):
    nombre_equipo = models.CharField(max_length=100)
    cantidad = models.IntegerField(default=1)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('Buen Estado', 'Buen Estado'),
            ('Mantenimiento', 'Mantenimiento'),
            ('Dado de Baja', 'Dado de Baja')
        ],
        default='Buen Estado'
    )
    fecha_adquisicion = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.nombre_equipo