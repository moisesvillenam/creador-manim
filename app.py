import streamlit as st
import subprocess
import os

st.set_page_config(page_title="Creador Manim", layout="wide")

st.title("🎬 Creador de Animaciones Matemáticas")
st.markdown("Ingresa tu función y personaliza los parámetros para generar la animación.")

# --- BARRA LATERAL PARA PARÁMETROS ---
st.sidebar.header("⚙️ Parámetros")

# --- NUEVO: SECCIÓN DE AYUDA (CHEATSHEET) ---
st.sidebar.subheader("📖 Ayuda")
with st.sidebar.expander("Ver Hoja de Trucos (Sintaxis)"):
    # Comprobamos si la imagen existe en la carpeta
    ruta_imagen = "cheatsheet.png"
    if os.path.exists(ruta_imagen):
        # Mostramos la imagen ajustada al ancho de la barra
        st.image(ruta_imagen, use_container_width=True)
        
        # Botón de descarga
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

# Textos descriptivos
st.sidebar.subheader("📝 Textos")
texto_titulo = st.sidebar.text_input("Título de la animación:", value="Gráfica de mi función")

# Input de la función
st.sidebar.subheader("🧮 Matemáticas")
funcion = st.sidebar.text_input("Función f(x) (usa 'np.' para math):", value="np.sin(x)")

# Personalización
st.sidebar.subheader("🎨 Estilo")
color_grafica = st.sidebar.color_picker("Color de la función", "#00FF00")
color_ejes = st.sidebar.color_picker("Color de los ejes", "#FFFFFF")
grosor = st.sidebar.slider("Grosor de la línea", 1, 10, 3)
duracion_animacion = st.sidebar.slider("Duración de la animación (segundos)", 1, 5, 2)

# --- TRADUCTOR AUTOMÁTICO DE PYTHON A LATEX ---
def python_a_latex(texto):
    """Convierte la sintaxis de Numpy a un texto que Manim/LaTeX pueda dibujar"""
    texto_limpio = texto.replace("np.pi", "\\pi") 
    texto_limpio = texto_limpio.replace("np.", "\\") 
    texto_limpio = texto_limpio.replace("**", "^")   
    texto_limpio = texto_limpio.replace("*", " \cdot ") 
    return texto_limpio

# --- GENERADOR DEL CÓDIGO MANIM ---
def generar_script_manim(func_str, color_graf, color_ej, grosor_linea, duracion, titulo):
    formula_visual = python_a_latex(func_str)
    latex_seguro = formula_visual.replace("{", "{{").replace("}", "}}")
    titulo_seguro = titulo.replace("{", "{{").replace("}", "}}")
    
    codigo = f"""
from manim import *
import numpy as np

class FuncionAnimada(Scene):
    def construct(self):
        titulo_anim = Text("{titulo_seguro}", font_size=36).to_edge(UP)
        formula_anim = MathTex(r"f(x) = {latex_seguro}", font_size=40).next_to(titulo_anim, DOWN)
        
        ejes = Axes(
            x_range=[-5, 5, 1],
            y_range=[-3, 3, 1],
            axis_config={{"color": "{color_ej}"}}
        ).scale(0.8).shift(DOWN * 0.5)
        
        grafica = ejes.plot(lambda x: {func_str}, color="{color_graf}", stroke_width={grosor_linea})
        etiquetas = ejes.get_axis_labels(x_label="x", y_label="y")
        
        self.play(Write(titulo_anim), FadeIn(formula_anim, shift=UP))
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
            f.write(generar_script_manim(funcion, color_grafica, color_ejes, grosor, duracion_animacion, texto_titulo))
        
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