import streamlit as st
from PIL import Image
from datetime import datetime
from fpdf import FPDF
import os
import tempfile
import uuid

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

    # 🏷️ Portada
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, "INFORME DE INSPECCIÓN", ln=True, align="C")
    pdf.ln(6)

    pdf.set_font("Arial", size=12)

    # Información de la inspección
    data = [
        ("Tipo de inspección:", inspection_type),
        ("Máquina:", machine_id),
        ("Fecha:", datetime.now().strftime('%Y-%m-%d %H:%M')),
        ("Total de hallazgos:", str(len(st.session_state.findings)))
    ]

    for label, value in data:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(50, 8, label, border=0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, value, ln=True, border=0)

    # Línea divisoria
    pdf.ln(6)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    # 📌 Sección de Hallazgos
    for idx, f in enumerate(st.session_state.findings, start=1):
        pdf.set_font("Arial", "B", 14)
        pdf.ln(6)
        pdf.cell(0, 10, f"Hallazgo {idx}", ln=True)

        # Imagen con tamaño máximo calculado
        max_width = 180
        width, height = f["image"].size
        ratio = max_width / float(width)
        new_height = int(height * ratio)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            img_path = tmp.name
            f["image"].save(img_path)

        pdf.image(img_path, w=max_width, h=new_height)
        os.remove(img_path)

        pdf.ln(5)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 6, f["description"])

        # Línea separadora entre hallazgos
        pdf.ln(2)
        pdf.set_draw_color(150, 150, 150)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)

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

