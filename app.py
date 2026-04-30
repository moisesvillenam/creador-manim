import streamlit as st
import subprocess
import os
import re

st.set_page_config(page_title="Creador Manim", layout="wide")

st.title("🎬 Creador de Animaciones Matemáticas")
st.markdown("Ingresa tu función y personaliza los parámetros para generar la animación.")

# --- BARRA LATERAL PARA PARÁMETROS ---
st.sidebar.header("⚙️ Parámetros")

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

st.sidebar.subheader("📝 Textos")
texto_titulo = st.sidebar.text_input("Título de la animación:", value="Gráfica de mi función")
posicion_texto = st.sidebar.selectbox(
    "Ubicación del texto:",
    ["Arriba Centro", "Abajo Centro", "Esquina Superior Izquierda", "Esquina Superior Derecha"]
)

st.sidebar.subheader("🧮 Matemáticas")
funcion = st.sidebar.text_input("Función f(x) (usa 'np.' para math):", value="np.sin(x) / (x + 1)")

st.sidebar.subheader("⚠️ Asíntotas / Saltos")
st.sidebar.markdown("Si la función divide por cero, pon el valor de X aquí.")
puntos_disc = st.sidebar.text_input("Puntos de ruptura (ej: -1, 0, 2):", value="-1")
lista_disc = "None" if puntos_disc.strip() == "" else f"[{puntos_disc}]"

st.sidebar.subheader("📐 Rango de Ejes")
col1, col2 = st.sidebar.columns(2)
with col1:
    x_min = st.number_input("X Mínimo", value=-5.0, step=1.0)
    y_min = st.number_input("Y Mínimo", value=-5.0, step=1.0)
with col2:
    x_max = st.number_input("X Máximo", value=5.0, step=1.0)
    y_max = st.number_input("Y Máximo", value=5.0, step=1.0)

st.sidebar.subheader("🎨 Estilo")
color_grafica = st.sidebar.color_picker("Color de la función", "#00FF00")
color_ejes = st.sidebar.color_picker("Color de los ejes", "#FFFFFF")
grosor = st.sidebar.slider("Grosor de la línea", 1, 10, 3)
duracion_animacion = st.sidebar.slider("Duración de la animación (segundos)", 1, 5, 2)

# --- PARSER DE PARÉNTESIS ANIDADOS ---
def reemplazar_funcion_anidada(texto, funcion_np, prefijo, sufijo):
    iteraciones = 0
    while funcion_np + "(" in texto and iteraciones < 100:
        iteraciones += 1
        inicio = texto.find(funcion_np + "(")
        idx_apertura = inicio + len(funcion_np)
        contador = 0
        idx_cierre = -1
        for i in range(idx_apertura, len(texto)):
            if texto[i] == '(': contador += 1
            elif texto[i] == ')':
                contador -= 1
                if contador == 0:
                    idx_cierre = i
                    break
        if idx_cierre != -1:
            contenido = texto[idx_apertura+1 : idx_cierre]
            texto = texto[:inicio] + prefijo + contenido + sufijo + texto[idx_cierre+1:]
        else:
            break
    return texto

# --- PARSER DE FRACCIONES ---
def limpiar_parentesis_extremos(s):
    s = s.strip()
    if s.startswith("(") and s.endswith(")"):
        pares = 0
        for i, char in enumerate(s):
            if char == '(': pares += 1
            elif char == ')': pares -= 1
            if pares == 0 and i < len(s) - 1:
                return s 
        return s[1:-1]
    return s

def formatear_fracciones(texto):
    iteraciones = 0
    while "/" in texto and iteraciones < 50:
        iteraciones += 1
        idx = texto.find("/")
        
        inicio = idx - 1
        while inicio >= 0 and texto[inicio] == " ": inicio -= 1
        
        if inicio >= 0 and texto[inicio] in ")}]":
            pares = 0
            for i in range(inicio, -1, -1):
                if texto[i] in ")}]": pares += 1
                elif texto[i] in "({[": pares -= 1
                if pares == 0:
                    inicio = i
                    break
            i = inicio - 1
            while i >= 0 and (texto[i].isalnum() or texto[i] in "_\\."):
                i -= 1
            inicio = i + 1
        else:
            while inicio >= 0 and texto[inicio] not in "+-*/^()= ":
                inicio -= 1
            inicio += 1
            
        numerador = texto[inicio:idx].strip()
        fin = idx + 1
        while fin < len(texto) and texto[fin] == " ": fin += 1
        
        if fin < len(texto) and texto[fin] in "({[":
            pares = 0
            for i in range(fin, len(texto)):
                if texto[i] in "({[": pares += 1
                elif texto[i] in ")}]": pares -= 1
                if pares == 0:
                    fin = i
                    break
        else:
            while fin < len(texto) and texto[fin] not in "+-*/^()= ":
                fin += 1
            fin -= 1
            
        denominador = texto[idx+1:fin+1].strip()
        num_limpio = limpiar_parentesis_extremos(numerador)
        den_limpio = limpiar_parentesis_extremos(denominador)
        
        reemplazo = f"\\frac{{{num_limpio}}}{{{den_limpio}}}"
        texto = texto[:inicio] + reemplazo + texto[fin+1:]
        
    return texto

# --- TRADUCTOR AUTOMÁTICO ---
def python_a_latex(texto):
    t = texto.replace("np.pi", "\\pi")
    t = reemplazar_funcion_anidada(t, "np.abs", r"\left| ", r" \right|")
    t = reemplazar_funcion_anidada(t, "np.floor", r"\left\lfloor ", r" \right\rfloor")
    t = reemplazar_funcion_anidada(t, "np.ceil", r"\left\lceil ", r" \right\rceil")
    t = reemplazar_funcion_anidada(t, "np.sqrt", r"\sqrt{", r"}")
    t = reemplazar_funcion_anidada(t, "np.exp", r"e^{", r"}")
    t = reemplazar_funcion_anidada(t, "np.square", r"\left(", r"\right)^2")
    t = re.sub(r"np\.power\(([^,]+),\s*([^)]+)\)", r"{\1}^{\2}", t)
    t = t.replace("**", "^").replace("*", " \cdot ")
    t = t.replace("np.sin", "\\sin").replace("np.cos", "\\cos").replace("np.tan", "\\tan")
    t = t.replace("np.log", "\\ln") 
    t = formatear_fracciones(t)
    t = re.sub(r"np\.([a-zA-Z0-9_]+)", r"\\operatorname{\1}", t)
    return t

# --- GENERADOR DEL CÓDIGO MANIM CON ESCUDO MATEMÁTICO AVANZADO ---
def generar_script_manim(func_str, color_graf, color_ej, grosor_linea, duracion, titulo, posicion, x_min, x_max, y_min, y_max, discontinuidades):
    formula_visual = python_a_latex(func_str)
    latex_seguro = formula_visual.replace("{", "{{").replace("}", "}}")
    titulo_seguro = titulo.replace("{", "{{").replace("}", "}}")
    
    if posicion == "Arriba Centro":
        pos_code = "grupo_texto.to_edge(UP)"
        shift_ejes = "ejes.shift(DOWN * 0.5)"
    elif posicion == "Abajo Centro":
        pos_code = "grupo_texto.to_edge(DOWN)"
        shift_ejes = "ejes.shift(UP * 0.5)"
    elif posicion == "Esquina Superior Izquierda":
        pos_code = "grupo_texto.to_corner(UL)"
        shift_ejes = "ejes.shift(DR * 0.2)"
    else: 
        pos_code = "grupo_texto.to_corner(UR)"
        shift_ejes = "ejes.shift(DL * 0.2)"
    
    codigo = f"""
from manim import *
import numpy as np
import warnings

class FuncionAnimada(Scene):
    def construct(self):
        warnings.filterwarnings('ignore')
        
        titulo_anim = Text(r"{titulo_seguro}", font_size=36)
        formula_anim = MathTex(r"f(x) = {latex_seguro}", font_size=40)
        grupo_texto = VGroup(titulo_anim, formula_anim).arrange(DOWN)
        {pos_code}
        
        ejes = Axes(
            x_range=[{x_min}, {x_max}, 1],
            y_range=[{y_min}, {y_max}, 1],
            axis_config={{"color": "{color_ej}"}}
        ).scale(0.8)
        
        {shift_ejes}
        
        # ESCUDO PROTECTOR PARA CORTAR EL INFINITO
        def f_segura(x):
            try:
                y = {func_str}
                if np.isnan(y): return 0
                
                # Definimos los bordes de la pantalla (un poco más allá de los ejes visibles)
                limite_sup = {y_max} + 1.5
                limite_inf = {y_min} - 1.5
                
                if np.isinf(y): 
                    return limite_sup if y > 0 else limite_inf
                    
                y = float(y)
                
                # Si el valor se dispara, lo cortamos como con una tijera
                if y > limite_sup: return limite_sup
                if y < limite_inf: return limite_inf
                
                return y
            except:
                return 0 # Si ocurre división exacta por cero
        
        grafica = ejes.plot(f_segura, color="{color_graf}", stroke_width={grosor_linea}, use_smoothing=False, discontinuities={discontinuidades})
        etiquetas = ejes.get_axis_labels(x_label="x", y_label="y")
        
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
            f.write(generar_script_manim(funcion, color_grafica, color_ejes, grosor, duracion_animacion, texto_titulo, posicion_texto, x_min, x_max, y_min, y_max, lista_disc))
        
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