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
        # Solucionada la advertencia de deprecación de Streamlit
        st.image(ruta_imagen, width="stretch")
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

# --- FUNCIONES MÚLTIPLES Y TRAMOS ---
st.sidebar.subheader("🧮 Matemáticas")
st.sidebar.markdown("Escribe **una función por línea**. Para tramos usa: `expresión1 if condición else expresión2`")
funcion = st.sidebar.text_area("Funciones principales f(x):", value="x**2 if x < 0 else x")

# --- ASÍNTOTAS EXPLICITAS ---
st.sidebar.subheader("⚠️ Asíntotas y Rupturas")
asintotas_v = st.sidebar.text_input("Verticales (x = ..., separadas por coma):", value="")
asintotas_ho = st.sidebar.text_area("Horizontales / Oblicuas (y = ..., una por línea):", value="")

st.sidebar.subheader("📐 Rango de Ejes")
col1, col2 = st.sidebar.columns(2)
with col1:
    x_min = st.number_input("X Mínimo", value=-10.0, step=1.0)
    y_min = st.number_input("Y Mínimo", value=-10.0, step=1.0)
with col2:
    x_max = st.number_input("X Máximo", value=10.0, step=1.0)
    y_max = st.number_input("Y Máximo", value=10.0, step=1.0)

st.sidebar.subheader("🎨 Estilo")
color_grafica = st.sidebar.color_picker("Color de la función principal", "#00FF00")
color_ejes = st.sidebar.color_picker("Color de los ejes", "#FFFFFF")
grosor = st.sidebar.slider("Grosor de la línea", 1, 10, 3)
duracion_animacion = st.sidebar.slider("Duración de la animación (segundos)", 1, 5, 2)


# --- PARSERS MATEMÁTICOS ---
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
            while inicio >= 0 and texto[inicio] not in "+-*/^()= ": inicio -= 1
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
            while fin < len(texto) and texto[fin] not in "+-*/^()= ": fin += 1
            fin -= 1
            
        denominador = texto[idx+1:fin+1].strip()
        num_limpio = limpiar_parentesis_extremos(numerador)
        den_limpio = limpiar_parentesis_extremos(denominador)
        
        reemplazo = f"\\frac{{{num_limpio}}}{{{den_limpio}}}"
        texto = texto[:inicio] + reemplazo + texto[fin+1:]
    return texto

def python_a_latex(texto):
    t = texto.replace("np.pi", r"\pi")
    t = reemplazar_funcion_anidada(t, "np.abs", r"\left| ", r" \right|")
    t = reemplazar_funcion_anidada(t, "np.floor", r"\left\lfloor ", r" \right\rfloor")
    t = reemplazar_funcion_anidada(t, "np.ceil", r"\left\lceil ", r" \right\rceil")
    t = reemplazar_funcion_anidada(t, "np.sqrt", r"\sqrt{", r"}")
    t = reemplazar_funcion_anidada(t, "np.exp", r"e^{", r"}")
    t = reemplazar_funcion_anidada(t, "np.square", r"\left(", r"\right)^2")
    t = re.sub(r"np\.power\(([^,]+),\s*([^)]+)\)", r"{\1}^{\2}", t)
    
    # Solucionado el Syntax Warning en la terminal (usando raw strings r"")
    t = t.replace("**", "^").replace("*", r" \cdot ")
    t = t.replace(" if ", r" \text{ si } ").replace(" else ", r" \text{ sino } ")
    t = t.replace("<=", r"\le ").replace(">=", r"\ge ")
    t = t.replace("==", "=").replace("!=", r"\neq ")
    t = t.replace("np.sin", r"\sin").replace("np.cos", r"\cos").replace("np.tan", r"\tan")
    t = t.replace("np.log", r"\ln") 
    t = formatear_fracciones(t)
    t = re.sub(r"np\.([a-zA-Z0-9_]+)", r"\\operatorname{\1}", t)
    return t

# --- GENERADOR DEL CÓDIGO MANIM ---
def generar_script_manim(funcs_list, asint_ho_list, asint_v_str, color_graf, color_ej, grosor_linea, duracion, titulo, posicion, x_min, x_max, y_min, y_max):
    lista_disc = f"[{asint_v_str}]" if asint_v_str.strip() else "None"
    titulo_seguro = titulo.replace("{", "{{").replace("}", "}}")
    
    formulas_tex = []
    for i, f_str in enumerate(funcs_list):
        if f_str == "0" and len(funcs_list) == 1: continue
        latex_str = python_a_latex(f_str).replace("{", "{{").replace("}", "}}")
        etiqueta = f"f_{{{i+1}}}(x)" if len(funcs_list) > 1 else "f(x)"
        formulas_tex.append(f"MathTex(r'{etiqueta} = {latex_str}', font_size={40 if len(funcs_list) == 1 else 30})")
    
    if formulas_tex:
        formulas_code = "formulas = VGroup(" + ", ".join(formulas_tex) + ").arrange(DOWN)"
        grupo_texto_code = "grupo_texto = VGroup(titulo_anim, formulas).arrange(DOWN)"
    else:
        formulas_code = ""
        grupo_texto_code = "grupo_texto = VGroup(titulo_anim)"

    if posicion == "Arriba Centro": pos_code, shift_ejes = "grupo_texto.to_edge(UP)", "ejes.shift(DOWN * 0.4)"
    elif posicion == "Abajo Centro": pos_code, shift_ejes = "grupo_texto.to_edge(DOWN)", "ejes.shift(UP * 0.4)"
    elif posicion == "Esquina Superior Izquierda": pos_code, shift_ejes = "grupo_texto.to_corner(UL)", "ejes.shift(DR * 0.2)"
    else: pos_code, shift_ejes = "grupo_texto.to_corner(UR)", "ejes.shift(DL * 0.2)"
    
    plots_code = ""
    for i, f_str in enumerate(funcs_list):
        if f_str == "0" and len(funcs_list) == 1: continue
        plots_code += f"""
        def func_{i}(x):
            try:
                y = {f_str}
                if np.isnan(y) or np.isinf(y): return {y_max} + 10
                y = float(y)
                
                # Dejamos que suba un poquito para asegurar el trazo continuo, 
                # los rectángulos negros ocultarán el resto.
                if y > {y_max} + 5: return {y_max} + 5
                if y < {y_min} - 5: return {y_min} - 5
                
                return y
            except: 
                return {y_max} + 10
        
        color_actual = colores[{i} % len(colores)]
        grafica_{i} = ejes.plot(func_{i}, color=color_actual, stroke_width={grosor_linea}, use_smoothing=False, discontinuities={lista_disc})
        graficas.add(grafica_{i})
"""

    asint_ho_code = ""
    for i, f_str in enumerate(asint_ho_list):
        asint_ho_code += f"""
        def asint_ho_{i}(x):
            try: return float({f_str})
            except: return 0
        graf_asint_{i} = ejes.plot(asint_ho_{i}, color=GRAY)
        dash_{i} = DashedVMobject(graf_asint_{i}, num_dashes=50)
        graficas.add(dash_{i})
"""

    asint_v_code = ""
    if asint_v_str.strip():
        asint_v_code = f"""
        for v in [{asint_v_str}]:
            try:
                linea = DashedLine(start=ejes.c2p(v, {y_min}), end=ejes.c2p(v, {y_max}), color=GRAY)
                graficas.add(linea)
            except: pass
"""

    dx = x_max - x_min
    dy = y_max - y_min

    codigo = f"""
from manim import *
import numpy as np
import warnings

class FuncionAnimada(Scene):
    def construct(self):
        warnings.filterwarnings('ignore')
        
        titulo_anim = Text(r"{titulo_seguro}", font_size=36)
        {formulas_code}
        {grupo_texto_code}
        {pos_code}
        
        ejes = Axes(
            x_range=[{x_min}, {x_max}, 1],
            y_range=[{y_min}, {y_max}, 1],
            x_length={dx}, 
            y_length={dy},
            axis_config={{"color": "{color_ej}"}}
        )
        
        if {dx} / {dy} > 12 / 6.5:
            ejes.scale_to_fit_width(12)
        else:
            ejes.scale_to_fit_height(6.5)
            
        {shift_ejes}
        
        graficas = VGroup()
        colores = ["{color_graf}", "#FFFF00", "#00FFFF", "#FF00FF", "#FFA500", "#FF0000"]
        
        {asint_ho_code}
        {asint_v_code}
        {plots_code}
        
        # --- EL TRUCO DEL MARCO NEGRO ---
        # Coordenadas exactas en pantalla
        p_top = ejes.c2p(({x_min}+{x_max})/2, {y_max})
        p_bottom = ejes.c2p(({x_min}+{x_max})/2, {y_min})
        p_left = ejes.c2p({x_min}, ({y_min}+{y_max})/2)
        p_right = ejes.c2p({x_max}, ({y_min}+{y_max})/2)

        # 4 Rectángulos gigantes que tapan lo que se sale del límite
        mask_top = Rectangle(width=100, height=50, color=BLACK, fill_opacity=1, stroke_width=0).move_to(p_top, aligned_edge=DOWN)
        mask_bottom = Rectangle(width=100, height=50, color=BLACK, fill_opacity=1, stroke_width=0).move_to(p_bottom, aligned_edge=UP)
        mask_left = Rectangle(width=50, height=100, color=BLACK, fill_opacity=1, stroke_width=0).move_to(p_left, aligned_edge=RIGHT)
        mask_right = Rectangle(width=50, height=100, color=BLACK, fill_opacity=1, stroke_width=0).move_to(p_right, aligned_edge=LEFT)
        mascaras = VGroup(mask_top, mask_bottom, mask_left, mask_right)
        
        # --- ASIGNACIÓN DE CAPAS (Z-INDEX) ---
        graficas.set_z_index(1)   # La curva se dibuja abajo
        mascaras.set_z_index(2)   # El marco negro tapa la curva sobrante
        ejes.set_z_index(3)       # El eje se dibuja sobre el marco negro
        etiquetas = ejes.get_axis_labels(x_label="x", y_label="y").set_z_index(4)
        grupo_texto.set_z_index(5) # El título va en la capa superior
        
        self.play(Write(grupo_texto))
        self.add(mascaras) # Añadimos las máscaras invisibles
        self.play(Create(ejes), Write(etiquetas))
        self.play(Create(graficas), run_time={duracion})
        self.wait(2)
"""
    return codigo

# --- BOTÓN DE EJECUCIÓN ---
if st.button("Generar Animación 🚀"):
    funcs_list = [f.strip() for f in funcion.split('\n') if f.strip()]
    if not funcs_list: funcs_list = ["0"]
    asint_ho_list = [f.strip() for f in asintotas_ho.split('\n') if f.strip()]
    
    with st.spinner("Renderizando con Manim..."):
        script_path = "temp_scene.py"
        with open(script_path, "w") as f:
            f.write(generar_script_manim(funcs_list, asint_ho_list, asintotas_v, color_grafica, color_ejes, grosor, duracion_animacion, texto_titulo, posicion_texto, x_min, x_max, y_min, y_max))
        
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