from vpython import graph, gcurve, rate, color, canvas, cylinder, vec
import random

max_points = 100  # Número máximo de puntos antes de eliminar los más antiguos
visible_time = 10  # Mostrar los últimos 10 segundos
fps = 10  # Frecuencia de actualización de la gráfica
max_points = visible_time * fps  # Máximo de puntos antes de desplazar

# Layout container that the 3D model is placed inside of
cansat_canvas = canvas(
    align="left"
)

# CanSat-ish 3D model
cansat = cylinder(
    canvas=cansat_canvas,
    axis=vec(3, 0, 0)
)

<<<<<<< Updated upstream
# Layout component for a 2D plot
=======
# Partes que deben girar con el cuerpo
rotating_parts = [cansat_body]

# Ángulos iniciales de rotación (en radianes)
angle_x = 0
angle_y = 0
angle_z = 0

# Flag de datos desactualizados
out_of_date = True  # Cambia esto a True para ver la advertencia

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

>>>>>>> Stashed changes
atmospheric_pressure_graph = graph(
    title="Atmospheric Pressure",
    xtitle="Time (s)",
    ytitle="Pressure (Pa)",
    xmin=0,
    xmax=visible_time,
    ymin=90000,
    fast=True,
    align="right" # Place right of CanSat model
)

# Actual plot
atmospheric_pressure_curve = gcurve(graph=atmospheric_pressure_graph, color=color.red)

# Crear la gráfica con fondo negro
temperature_graph = graph(
<<<<<<< Updated upstream
    title="Temperature",
    xtitle="Time (s)",
    ytitle="Temperature (°C)",
    xmin=0,
    ymin=-10,
=======
    title="<b>Temperature</b>",
    xtitle="<b>Time (s)</b>",
    ytitle="<b>Temperature (°C)</b>",
    xmin=0,  # Tiempo inicial
    xmax=visible_time,  # Mantener solo 10s en pantalla
    ymin=10, ymax=50,  # Ajusta según tu rango de temperatura
>>>>>>> Stashed changes
    fast=True,
    align="left"
)
<<<<<<< Updated upstream
temperature_curve = gcurve(graph=temperature_graph, color=color.blue)
=======

# Crear la curva de temperatura
temperature_curve = gcurve(graph=temperature_graph, color=color.cyan, width=3)
>>>>>>> Stashed changes

# Relative Humidity Graph
relative_humidity_graph = graph(
<<<<<<< Updated upstream
    title="Relative Humidity",
    xtitle="Time (s)",
    ytitle="Humidity (%)",
=======
    title="<b>Relative Humidity</b>",
    xtitle="<b>Time (s)</b>",
    ytitle="<b>Humidity (%)</b>",
    xmax=visible_time,
>>>>>>> Stashed changes
    xmin=0,
    ymin=0,
    ymax=100,
    fast=True,
    align="right"
)
relative_humidity_curve = gcurve(graph=relative_humidity_graph, color=color.green)

# Data point index
i = 0

# Simulated data update loop
while True:
    # Generate random test values
    pressure = random.uniform(98000, 102000)
    temperature = random.uniform(15, 30)
    humidity = random.uniform(30, 80)
    # Should be pitch, roll, yaw, but for now rotation
    cansat_rot_x = random.uniform(0, 0.28)
    cansat_rot_y = random.uniform(0, 0.28)
    cansat_rot_z = random.uniform(0, 0.28)

<<<<<<< Updated upstream
    # Append to 2D plots
    atmospheric_pressure_curve.plot(i, pressure)
    temperature_curve.plot(i, temperature)
    relative_humidity_curve.plot(i, humidity)
    # Rotate 3D model
    cansat.rotate(axis=vec(1, 0, 0), angle=cansat_rot_x)
    cansat.rotate(axis=vec(0, 1, 0), angle=cansat_rot_y)
    cansat.rotate(axis=vec(0, 0, 1), angle=cansat_rot_z)
=======
    # Agregar valores a las gráficas
    atmospheric_pressure_curve.plot(i/fps, pressure)
    temperature_curve.plot(i / fps, temperature)  # Normaliza el tiempo en segundos
    relative_humidity_curve.plot(i/fps, humidity)
    
    # Desplazar la gráfica cuando alcanza el límite de tiempo
    if i > max_points:
        temperature_graph.xmin += 1 / fps  # Mueve el eje X a la izquierda
        temperature_graph.xmax += 1 / fps  # Mantiene la ventana de 10s
        atmospheric_pressure_graph.xmin += 1 / fps
        atmospheric_pressure_graph.xmax += 1 / fps
        relative_humidity_graph.xmin += 1 / fps
        relative_humidity_graph.xmax += 1 / fps
>>>>>>> Stashed changes

    # Increment index
    i += 1

    # Update frequency in Hz
<<<<<<< Updated upstream
    rate(10)
=======
    rate(fps)  
>>>>>>> Stashed changes
