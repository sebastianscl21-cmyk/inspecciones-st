import streamlit as st
from PIL import Image
from datetime import datetime
from fpdf import FPDF
import os
import tempfile
import uuid
import locale
llocale.setlocale(locale.LC_TIME, "es_CO.UTF-8")

# Configuración de la página
st.set_page_config(page_title="Inspecciones Técnicas", page_icon="🛠️", layout="centered")

# Inicializar hallazgos en sesión
if "findings" not in st.session_state:
    st.session_state.findings = []

# Título
st.title("📋 Registro de Inspección Técnica")

# Selección del tipo de inspección
inspection_type = st.selectbox("Tipo de inspección", ["Mecánica", "Eléctrica"])

# Nombre o código de la máquina
machine_id = st.text_input("Identificación de la máquina")

st.divider()

st.subheader("Registrar nuevo hallazgo")

# Selección de origen de imagen
option = st.radio("¿Cómo deseas agregar la foto?", ["📸 Cámara", "📁 Cargar archivo"])

if option == "📸 Cámara":
    image_file = st.camera_input("Tomar foto")
else:
    image_file = st.file_uploader("Seleccionar imagen", type=["jpg", "jpeg", "png"])

# Descripción del hallazgo
description = st.text_area("✍️ Descripción del hallazgo")

if st.button("✅ Guardar hallazgo"):
    if image_file and description.strip():
        try:
            image = Image.open(image_file)
            st.session_state.findings.append({
                "id": str(uuid.uuid4()),
                "image": image.copy(),
                "description": description,
                "timestamp": datetime.now()
            })
            st.success("Hallazgo guardado ✅")
            st.rerun()
        except Exception as e:
            st.error(f"Error al procesar la imagen: {e}")
    else:
        st.warning("⚠️ Debes tomar o subir una imagen y escribir una descripción.")

st.divider()

# 🔹 Mostrar hallazgos
if st.session_state.findings:
    st.subheader("📌 Hallazgos registrados")

    for f in st.session_state.findings:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(f["image"], width=200)
        with col2:
            st.write(f"**Descripción:** {f['description']}")
            st.caption(f"🕒 {f['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            if st.button(f"🗑️ Eliminar", key=f["id"]):
                st.session_state.findings = [x for x in st.session_state.findings if x["id"] != f["id"]]
                st.rerun()
else:
    st.info("Aún no hay hallazgos registrados.")

st.divider()

# 📄 Función para generar PDF
def generate_pdf():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()

    # --------- ENCABEZADO ----------
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, "INFORME DE INSPECCIÓN", ln=True, align="C")
    pdf.ln(4)

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, f"MAQUINA: {machine_id}", ln=True)
    pdf.cell(0, 8, f"FECHA: {datetime.now().strftime('%A %d de %B del %Y')}", ln=True)
    pdf.ln(6)

    # --------- GRID CONFIG ----------
    images_per_row = 3
    cell_width = 60       # ancho por hallazgo
    image_max_width = 55  # ancho máximo de la imagen
    spacing = 8

    x_start = 10
    y_start = pdf.get_y()
    x = x_start
    y = y_start

    pdf.set_font("Arial", "", 10)

    for idx, f in enumerate(st.session_state.findings):

        # --- Imprimir descripción arriba de la imagen ---
        pdf.set_xy(x, y)
        pdf.multi_cell(cell_width, 5, f["description"], align="L")

        # Preparar imagen temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            img_path = tmp.name
            f["image"].save(img_path)

        # — Calcular tamaño proporcional —
        width, height = f["image"].size
        ratio = image_max_width / float(width)
        new_height = int(height * ratio)

        # Posicionar imagen debajo del texto
        pdf.set_xy(x, pdf.get_y())
        pdf.image(img_path, w=image_max_width, h=new_height)

        os.remove(img_path)

        # Mover posición al siguiente bloque
        x += cell_width + spacing

        # Si ya imprimió 3 imágenes, saltar de fila
        if (idx + 1) % images_per_row == 0:
            x = x_start
            y = pdf.get_y() + new_height + 10
            pdf.set_y(y)

    file_unique = f"Reporte_Inspeccion_{uuid.uuid4().hex[:6]}.pdf"
    pdf.output(file_unique)
    return file_unique

# Botón para generar PDF
if st.session_state.findings and machine_id.strip():
    if st.button("📥 Generar y Descargar PDF"):
        file = generate_pdf()
        with open(file, "rb") as f:
            st.download_button(
                "⬇️ Descargar PDF",
                data=f,
                file_name=file,
                mime="application/pdf"
            )
else:
    st.info("Completa los datos y registra hallazgos para generar el PDF.")


