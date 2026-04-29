import streamlit as st
import subprocess
import os
import re

st.set_page_config(page_title="Creador Manim", layout="wide")

st.title("🎬 Creador de Animaciones Matemáticas")
st.markdown("Ingresa tu función y personaliza los parámetros para generar la animación.")

# --- BARRA LATERAL PARA PARÁMETROS ---
st.sidebar.header("⚙️ Parámetros")

# Sección de Ayuda (Cheatsheet)
st.sidebar.subheader("📖 Ayuda")
with st.sidebar.expander("Ver Hoja de Trucos (Sintaxis)"):
    ruta_imagen = "cheatsheet.png"
    if os.path.exists(ruta_imagen):
        st.image(ruta_imagen, use_container_width=True)
        with open(ruta_imagen, "rb") as file:
            st.download_button(
                label="📥 Descargar Imagen",
                data=file,
                file_name="Guia_Numpy_Manim.jpg",
                mime="image/jpeg"
            )
    else:
        st.warning("Guarda la imagen como 'cheatsheet.jpg' en la misma carpeta para verla aquí.")

st.sidebar.markdown("---")

# Textos descriptivos y Posición
st.sidebar.subheader("📝 Textos")
texto_titulo = st.sidebar.text_input("Título de la animación:", value="Gráfica de mi función")
posicion_texto = st.sidebar.selectbox(
    "Ubicación del texto:",
    ["Arriba Centro", "Abajo Centro", "Esquina Superior Izquierda", "Esquina Superior Derecha"]
)

# Input de la función
st.sidebar.subheader("🧮 Matemáticas")
funcion = st.sidebar.text_input("Función f(x) (usa 'np.' para math):", value="np.exp(x)")

# Personalización
st.sidebar.subheader("🎨 Estilo")
color_grafica = st.sidebar.color_picker("Color de la función", "#00FF00")
color_ejes = st.sidebar.color_picker("Color de los ejes", "#FFFFFF")
grosor = st.sidebar.slider("Grosor de la línea", 1, 10, 3)
duracion_animacion = st.sidebar.slider("Duración de la animación (segundos)", 1, 5, 2)

# --- TRADUCTOR AUTOMÁTICO DE PYTHON A LATEX ---
def python_a_latex(texto):
    """Convierte la sintaxis de Numpy a un texto que Manim/LaTeX pueda dibujar"""
    t = texto.replace("np.pi", "\\pi")
    
    # Transformar potencias, raíces y exponenciales (e^x)
    t = re.sub(r"np\.power\(([^,]+),\s*([^)]+)\)", r"{\1}^{\2}", t)
    t = re.sub(r"np\.square\(([^)]+)\)", r"{\1}^2", t)
    t = re.sub(r"np\.sqrt\(([^)]+)\)", r"\\sqrt{\1}", t)
    t = re.sub(r"np\.exp\(([^)]+)\)", r"e^{\1}", t) # NUEVO: e elevado a la x
    
    # Transformar operadores estándar
    t = t.replace("**", "^").replace("*", " \cdot ")
    
    # Funciones trigonométricas y logaritmos
    t = t.replace("np.sin", "\\sin").replace("np.cos", "\\cos").replace("np.tan", "\\tan")
    t = t.replace("np.log", "\\log")
    
    # Todo lo que sobre de numpy (para evitar que LaTeX falle al dibujar)
    t = re.sub(r"np\.([a-zA-Z0-9_]+)", r"\\operatorname{\1}", t)
    
    return t

# --- GENERADOR DEL CÓDIGO MANIM ---
def generar_script_manim(func_str, color_graf, color_ej, grosor_linea, duracion, titulo, posicion):
    formula_visual = python_a_latex(func_str)
    
    # Protegemos las llaves para que no rompan el string de Python
    latex_seguro = formula_visual.replace("{", "{{").replace("}", "}}")
    titulo_seguro = titulo.replace("{", "{{").replace("}", "}}")
    
    # Configurar la posición en código Manim
    if posicion == "Arriba Centro":
        pos_code = "grupo_texto.to_edge(UP)"
        shift_ejes = "ejes.shift(DOWN * 0.5)"
    elif posicion == "Abajo Centro":
        pos_code = "grupo_texto.to_edge(DOWN)"
        shift_ejes = "ejes.shift(UP * 0.5)"
    elif posicion == "Esquina Superior Izquierda":
        pos_code = "grupo_texto.to_corner(UL)"
        shift_ejes = "ejes.shift(DR * 0.2)"
    else: # Esquina Superior Derecha
        pos_code = "grupo_texto.to_corner(UR)"
        shift_ejes = "ejes.shift(DL * 0.2)"
    
    codigo = f"""
from manim import *
import numpy as np

class FuncionAnimada(Scene):
    def construct(self):
        # 1. Crear los textos
        titulo_anim = Text(r"{titulo_seguro}", font_size=36)
        formula_anim = MathTex(r"f(x) = {latex_seguro}", font_size=40)
        
        # Agruparlos y posicionarlos donde eligió el usuario
        grupo_texto = VGroup(titulo_anim, formula_anim).arrange(DOWN)
        {pos_code}
        
        # 2. Configurar ejes
        ejes = Axes(
            x_range=[-5, 5, 1],
            y_range=[-3, 3, 1],
            axis_config={{"color": "{color_ej}"}}
        ).scale(0.8)
        
        # Movemos ligeramente los ejes para que no choquen con el texto
        {shift_ejes}
        
        # 3. Crear la gráfica
        grafica = ejes.plot(lambda x: {func_str}, color="{color_graf}", stroke_width={grosor_linea})
        etiquetas = ejes.get_axis_labels(x_label="x", y_label="y")
        
        # 4. Animación
        self.play(Write(grupo_texto))
        self.play(Create(ejes), Write(etiquetas))
        self.play(Create(grafica), run_time={duracion})
        self.wait(2)
"""
    return codigo

# --- BOTÓN DE EJECUCIÓN ---
if st.button("Generar Animación 🚀"):
    with st.spinner("Renderizando con Manim..."):
        script_path = "temp_scene.py"
        with open(script_path, "w") as f:
            f.write(generar_script_manim(funcion, color_grafica, color_ejes, grosor, duracion_animacion, texto_titulo, posicion_texto))
        
        comando = ["manim", "-ql", script_path, "FuncionAnimada", "--format=mp4"]
        resultado = subprocess.run(comando, capture_output=True, text=True)
        
        if resultado.returncode != 0:
            st.error("Manim falló al compilar. Aquí está el error exacto:")
            st.code(resultado.stderr if resultado.stderr else resultado.stdout)
        else:
            video_path = "media/videos/temp_scene/480p15/FuncionAnimada.mp4"
            if os.path.exists(video_path):
                st.success("¡Animación generada!")
                st.video(video_path)
            else:
                st.error("El comando terminó bien, pero no se encontró el archivo de video.")