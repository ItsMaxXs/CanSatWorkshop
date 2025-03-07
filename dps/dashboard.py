from vpython import *
import random
import numpy as np  # Necesario para manejar los ángulos

# Layout container that the 3D model is placed inside of
cansat_canvas = canvas(align="left",background=vec(0.15, 0.15, 0.15), width = 750)

cansat_canvas.forward = vec(0, 1, 0)  # Mira el CanSat desde el eje Y negativo

#cansat_canvas.camera.pos = vec(0, -8, 2)  # Coloca la cámara más lejos
#cansat_canvas.camera.axis = vec(0, 8, -2)  # Ajusta la dirección en que mira

cansat_body = cylinder(
    canvas=cansat_canvas,
    pos=vec(0, 0, 0),
    axis=vec(0, 0, 3),
    radius=0.8,
    color=vec(1, 0.84, 0),  # Amarillo dorado
    shininess=0.8,          # Efecto metálico
    opacity=0.9             # Un poco de transparencia
)

# Partes que deben girar con el cuerpo
rotating_parts = [cansat_body]

# Ángulos iniciales de rotación (en radianes)
angle_x = 0
angle_y = 0
angle_z = 0

# Flag de datos desactualizados
out_of_date = False  # Cambia esto a True para ver la advertencia

warning_label = label(
    pos=vec(0, 2, 0),
    text="",
    color=color.red,
    height=18,
    box=True,
    background=color.white * 0.1,  # Fondo gris claro
    opacity=0.6
)

# Función para actualizar la orientación del cuerpo en función de los ángulos
def update_rotation():
    global angle_x, angle_y, angle_z

    # Matrices de rotación
    Rz = np.array([[np.cos(angle_z), -np.sin(angle_z), 0],
                   [np.sin(angle_z),  np.cos(angle_z), 0],
                   [0, 0, 1]])

    Ry = np.array([[np.cos(angle_y), 0, np.sin(angle_y)],
                   [0, 1, 0],
                   [-np.sin(angle_y), 0, np.cos(angle_y)]])

    Rx = np.array([[1, 0, 0],
                   [0, np.cos(angle_x), -np.sin(angle_x)],
                   [0, np.sin(angle_x),  np.cos(angle_x)]])

    # Transformar la orientación del eje del cilindro
    new_axis = np.dot(Rz, np.dot(Ry, np.dot(Rx, [0, 0, 3])))

    for part in rotating_parts:
        part.axis = vec(new_axis[0], new_axis[1], new_axis[2])

atmospheric_pressure_graph = graph(
    title="<b>Atmospheric Pressure</b>",
    xtitle="<b>Time (s)</b>",
    ytitle="<b>Pressure (Pa)</b>",
    xmin=0,
    ymin=90000,
    fast=True,
    align="right",
    background=color.black,  # Fondo negro
    foreground=color.black,  # Letras blancas
    width=750
)
atmospheric_pressure_curve = gcurve(graph=atmospheric_pressure_graph, color=color.red, width=4)

temperature_graph = graph(
    title="<b>Temperature</b>",
    xtitle="<b>Time (s)</b>",
    ytitle="<b>Temperature (°C)</b>",
    xmin=0,
    ymin=-10,
    fast=True,
    align="left",
    background=color.black, 
    foreground=color.black,
    width=750
)
temperature_curve = gcurve(graph=temperature_graph, color=color.cyan, width=4)

relative_humidity_graph = graph(
    title="<b>Relative Humidity</b>",
    xtitle="<b>Time (s)</b>",
    ytitle="<b>Humidity (%)</b>",
    xmin=0,
    ymin=0,
    ymax=100,
    fast=True,
    align="right",
    background=color.black,
    foreground=color.black,
    width=750
)
relative_humidity_curve = gcurve(graph=relative_humidity_graph, color=color.green, width=4)


# Data point index
i = 0

# Simulated data update loop
while True:
    # Generar nuevos valores de ángulos
    angle_x += random.uniform(-0.05, 0.05)
    angle_y += random.uniform(-0.05, 0.05)
    angle_z += random.uniform(-0.05, 0.05)

    # Aplicar la nueva orientación
    update_rotation()
    
    if out_of_date:
        warning_label.text = "⚠ Out of Date!"
    else:
        warning_label.text = ""

    # Generar valores de sensores simulados
    pressure = random.uniform(98000, 102000)
    temperature = random.uniform(15, 30)
    humidity = random.uniform(30, 80)

    # Agregar valores a las gráficas
    atmospheric_pressure_curve.plot(i, pressure)
    temperature_curve.plot(i, temperature)
    relative_humidity_curve.plot(i, humidity)

    # Increment index
    i += 1

    # Update frequency in Hz
    rate(10)  