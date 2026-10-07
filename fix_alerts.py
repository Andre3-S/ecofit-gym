import re
import os

clientes_path = r'C:\Users\DELL\Desktop\sistema_gym\sistema_gym\clientes\templates\listar_clientes.html'
promos_path = r'C:\Users\DELL\Desktop\sistema_gym\sistema_gym\clientes\templates\listar_promociones.html'

# 1. FIX LISTAR CLIENTES
with open(clientes_path, 'r', encoding='utf-8') as f:
    clientes_content = f.read()

# Remove the scripts from block title
clientes_content = re.sub(
    r'<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>\s*<script>.*?function verDetalles.*?\}\s*</script>\s*(?={% endblock %})',
    '', clientes_content, flags=re.DOTALL
)

# Replace the mangled verDetalles inside block content with the correct one
correct_ver_detalles = """    function verDetalles(nombre, dni, telefono, correo, plan, estado, exp) {
        let colorEstado = estado === 'Activo' ? '#00E676' : (estado === 'Vencida' ? '#ef4444' : '#6b7280');
        let badgeEstado = `<span style="background: ${colorEstado}15; color: ${colorEstado}; border: 1px solid ${colorEstado}40; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;">${estado}</span>`;
        let inicial = nombre.charAt(0).toUpperCase();

        Swal.fire({
            title: 'Perfil del Cliente',
            html: `
                <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px; text-align: left; background: rgba(255,255,255,0.03); padding: 15px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);">
                    <div style="width: 50px; height: 50px; background: #00E676; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: bold; color: #000;">
                        ${inicial}
                    </div>
                    <div>
                        <h3 style="margin: 0; color: #fff; font-size: 18px;">${nombre}</h3>
                        <p style="margin: 5px 0 0; color: rgba(255,255,255,0.5); font-size: 13px;">DNI: ${dni}</p>
                    </div>
                </div>
                
                <div style="text-align: left; display: grid; gap: 12px;">
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;">
                        <span style="color: rgba(255,255,255,0.5); font-size: 13px;"><i class="fa-solid fa-phone" style="width: 20px;"></i> Teléfono</span>
                        <span style="color: #fff; font-size: 14px;">+51 ${telefono}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;">
                        <span style="color: rgba(255,255,255,0.5); font-size: 13px;"><i class="fa-solid fa-envelope" style="width: 20px;"></i> Correo</span>
                        <span style="color: #fff; font-size: 14px;">${correo}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;">
                        <span style="color: rgba(255,255,255,0.5); font-size: 13px;"><i class="fa-solid fa-dumbbell" style="width: 20px;"></i> Plan Actual</span>
                        <span style="color: #fff; font-size: 14px; font-weight: 600;">${plan}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px;">
                        <span style="color: rgba(255,255,255,0.5); font-size: 13px;"><i class="fa-solid fa-circle-check" style="width: 20px;"></i> Estado</span>
                        ${badgeEstado}
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: rgba(255,255,255,0.5); font-size: 13px;"><i class="fa-regular fa-calendar-xmark" style="width: 20px;"></i> Vencimiento</span>
                        <span style="color: #fff; font-size: 14px;">${exp}</span>
                    </div>
                </div>
            `,
            background: 'rgba(28, 33, 40, 0.85)',
            color: '#fff',
            showConfirmButton: true,
            confirmButtonText: 'Cerrar',
            buttonsStyling: false,
            backdrop: `rgba(0,0,0,0.85)`,
            customClass: {
                popup: 'swal-glass-popup',
                title: 'swal-neon-title',
                confirmButton: 'swal-btn-glass-cancel'
            }
        });
    }"""

clientes_content = re.sub(
    r'function verDetalles.*?\}\s*\}\);\s*\}', 
    correct_ver_detalles, 
    clientes_content, 
    flags=re.DOTALL
)

with open(clientes_path, 'w', encoding='utf-8') as f:
    f.write(clientes_content)


# 2. FIX LISTAR PROMOCIONES
with open(promos_path, 'r', encoding='utf-8') as f:
    promos_content = f.read()

correct_handle_files = """        Swal.fire({
            title: 'Configurar Promoción',
            html: `
                <input id="swal-input-nombre" class="swal2-input" placeholder="Nombre (ej. CyberWeek)" style="background: rgba(0,0,0,0.2); color: #fff; border: 1px solid rgba(255,255,255,0.1); width: 85%;">
                <input id="swal-input-desc" type="number" class="swal2-input" placeholder="% Descuento (ej. 20)" style="background: rgba(0,0,0,0.2); color: #fff; border: 1px solid rgba(255,255,255,0.1); width: 85%;">
                <select id="swal-input-tipo" class="swal2-input" style="background: rgba(0,0,0,0.2); color: #fff; border: 1px solid rgba(255,255,255,0.1); width: 85%;">
                    <option value="Porcentaje" style="background: #1c2128;">Descuento %</option>
                    <option value="Monto Fijo" style="background: #1c2128;">Monto Fijo</option>
                    <option value="2x1" style="background: #1c2128;">Promo 2x1</option>
                    <option value="Especial" style="background: #1c2128;">Especial</option>
                </select>
                <p style="color: rgba(255,255,255,0.4); font-size: 12px; margin-top: 15px;">Archivo seleccionado: ${file.name}</p>
            `,
            background: 'rgba(28, 33, 40, 0.85)',
            color: '#fff',
            showCancelButton: true,
            confirmButtonText: 'Subir y Activar',
            cancelButtonText: 'Cancelar',
            backdrop: `rgba(0,0,0,0.85)`,
            customClass: {
                popup: 'swal-glass-popup',
                title: 'swal-neon-title',
                confirmButton: 'swal-btn-neon-green',
                cancelButton: 'swal-btn-glass-cancel'
            },
            preConfirm: () => {
                const nombre = document.getElementById('swal-input-nombre').value;
                const desc = document.getElementById('swal-input-desc').value;
                const tipo = document.getElementById('swal-input-tipo').value;
                if (!nombre || !desc) {
                    Swal.showValidationMessage('Por favor completa todos los campos');
                }
                return { nombre: nombre, desc: desc, tipo: tipo }
            }
        }).then((result) => {
            if (result.isConfirmed) {
                document.getElementById('promo-nombre').value = result.value.nombre;
                document.getElementById('promo-descuento').value = result.value.desc;
                document.getElementById('promo-tipo').value = result.value.tipo;
                document.getElementById('quick-promo-form').submit();
            } else {
                fileInput.value = ""; // Clear file if cancelled
            }
        });"""

promos_content = re.sub(
    r'Swal\.fire\(\{\s*title: \'Configurar Promoción\',.*?\}\);', 
    correct_handle_files, 
    promos_content, 
    flags=re.DOTALL
)

with open(promos_path, 'w', encoding='utf-8') as f:
    f.write(promos_content)

print("FIXED SUCCESSFULLY")
