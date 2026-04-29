import streamlit as st
import subprocess
import os

st.set_page_config(page_title="Creador Manim", layout="wide")

st.title("🎬 Creador de Animaciones Matemáticas")
st.markdown("Ingresa tu función y personaliza los parámetros para generar la animación.")

# --- BARRA LATERAL PARA PARÁMETROS ---
st.sidebar.header("⚙️ Parámetros")

# Input de la función (usamos sintaxis de numpy)
funcion = st.sidebar.text_input("Función f(x) (usa 'np.' para math):", value="np.sin(x)")

# Personalización
color_grafica = st.sidebar.color_picker("Color de la función", "#00FF00")
color_ejes = st.sidebar.color_picker("Color de los ejes", "#FFFFFF")
grosor = st.sidebar.slider("Grosor de la línea", 1, 10, 3)
duracion_animacion = st.sidebar.slider("Duración de la animación (segundos)", 1, 5, 2)

# --- GENERADOR DEL CÓDIGO MANIM ---
def generar_script_manim(func_str, color_graf, color_ej, grosor_linea, duracion):
    # Por defecto Manim usa fondo oscuro, lo cual cumple con tu requerimiento
    codigo = f"""
from manim import *
import numpy as np

class FuncionAnimada(Scene):
    def construct(self):
        # Configurar ejes
        ejes = Axes(
            x_range=[-5, 5, 1],
            y_range=[-3, 3, 1],
            axis_config={{"color": "{color_ej}"}}
        )
        
        # Crear la gráfica
        grafica = ejes.plot(lambda x: {func_str}, color="{color_graf}", stroke_width={grosor_linea})
        
        # Etiquetas
        etiquetas = ejes.get_axis_labels(x_label="x", y_label="f(x)")
        
        # Animación
        self.play(Create(ejes), Write(etiquetas))
        self.play(Create(grafica), run_time={duracion})
        self.wait(1)
"""
    return codigo

# --- BOTÓN DE EJECUCIÓN ---
if st.button("Generar Animación 🚀"):
    with st.spinner("Renderizando con Manim..."):
        script_path = "temp_scene.py"
        with open(script_path, "w") as f:
            f.write(generar_script_manim(funcion, color_grafica, color_ejes, grosor, duracion_animacion))
        
        comando = ["manim", "-ql", script_path, "FuncionAnimada", "--format=mp4"]
        
        # Ejecutamos capturando la salida para poder ver los errores
        resultado = subprocess.run(comando, capture_output=True, text=True)
        
        if resultado.returncode != 0:
            st.error("Manim falló al compilar. Aquí está el error exacto:")
            # Mostramos el error de la terminal directamente en Streamlit
            st.code(resultado.stderr if resultado.stderr else resultado.stdout)
        else:
            video_path = "media/videos/temp_scene/480p15/FuncionAnimada.mp4"
            if os.path.exists(video_path):
                st.success("¡Animación generada!")
                st.video(video_path)
            else:
                st.error("El comando terminó bien, pero no se encontró el archivo de video.")