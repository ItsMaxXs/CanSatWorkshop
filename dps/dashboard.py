from vpython import graph, gcurve, rate, color, canvas, cylinder, vec, label
import numpy as np 
import csv
import threading
import queue
import time

# 💡 IMPORTAR la lógica del procesador y el iniciador del hilo
# Esto nos trae: data_queue, start_data_thread, FIELD_NAMES, RECORD_SIZE
from data_processor_logic import start_data_thread, FIELD_NAMES

# --- Configuración Compartida e Inicialización ---
# 1. Creamos la cola que será usada por ambos archivos para comunicarse
data_queue = queue.Queue() 

fps = 10                  # Frecuencia de actualización de la gráfica (y de lectura de la cola)
visible_time = 10         
max_points = visible_time * fps 

# Datos decodificados más recientes. Inicialmente, todos en 0.
current_data = {name: 0.0 for name in FIELD_NAMES}
last_data_time = time.time() # Tiempo del último paquete recibido

# Angulos ya no son globales ni se generan al azar
angle_x = 0
angle_y = 0
angle_z = 0

# Flag de datos desactualizados
out_of_date = True       

# Data storage for CSV (Ahora guardará los datos reales)
removed_pressure = []
removed_temperature = []
removed_humidity = []
removed_time = []


# Layout container that the 3D model is placed inside of
cansat_canvas = canvas(align="left",background=vec(0.15, 0.15, 0.15), width = 750)
cansat_canvas.forward = vec(0, 1, 0) 

cansat_body = cylinder(
    canvas=cansat_canvas,
    pos=vec(0, 0, 0),
    axis=vec(0, 0, 3),
    radius=0.8,
    color=vec(1, 0.84, 0), 
    shininess=0.8,
    opacity=0.9
)

# Partes que deben girar con el cuerpo
rotating_parts = [cansat_body]

warning_label = label(
    pos=vec(0, 2, 0),
    text="",
    color=color.red,
    height=18,
    box=True,
    background=color.white * 0.1, 
    opacity=0.6
)

# --- Funciones de Lógica ---

def get_new_data():
    """
    Intenta obtener el paquete de datos más reciente de la cola.
    Consume todos los paquetes pendientes y se queda con el más reciente.
    """
    global current_data, out_of_date, last_data_time

    data_received_flag = False
    
    try:
        # Lee el paquete más antiguo, y sigue consumiendo hasta que la cola esté vacía
        while True:
            latest_packet = data_queue.get_nowait()
            current_data.update(latest_packet)
            data_received_flag = True
            
    except queue.Empty:
        # La cola está vacía, no hay más datos nuevos por ahora
        pass

    if data_received_flag:
        out_of_date = False
        last_data_time = time.time()
    
    # Si no se recibió nada en el último segundo, marca como desactualizado
    if time.time() - last_data_time > 1.0: 
        out_of_date = True


def update_rotation():
    """
    Actualiza la orientación del cuerpo del CanSat usando los valores de Pitch, Roll, Yaw 
    leídos de 'current_data'.
    """
    
    # 💡 Usamos los valores decodificados de la cola (en grados) y los convertimos a radianes
    angle_x = np.radians(current_data['Roll'])    # Roll (eje X)
    angle_y = np.radians(current_data['Pitch'])   # Pitch (eje Y)
    angle_z = np.radians(current_data['Yaw'])     # Yaw (eje Z)
    
    # Matrices de rotación (la lógica se mantiene igual)
    Rz = np.array([[np.cos(angle_z), -np.sin(angle_z), 0],
                   [np.sin(angle_z),  np.cos(angle_z), 0],
                   [0, 0, 1]])

    Ry = np.array([[np.cos(angle_y), 0, np.sin(angle_y)],
                   [0, 1, 0],
                   [-np.sin(angle_y), 0, np.cos(angle_y)]])

    Rx = np.array([[1, 0, 0],
                   [0, np.cos(angle_x), -np.sin(angle_x)],
                   [0, np.sin(angle_x),  np.cos(angle_x)]])

    # Aplicar Rz * Ry * Rx al eje inicial (0, 0, 3)
    new_axis = np.dot(Rz, np.dot(Ry, np.dot(Rx, [0, 0, 3])))

    for part in rotating_parts:
        part.axis = vec(new_axis[0], new_axis[1], new_axis[2])


# --- Configuración de Gráficas (sin cambios) ---

atmospheric_pressure_graph = graph(
    title="<b>Atmospheric Pressure</b>",
    xtitle="<b>Time (s)</b>",
    ytitle="<b>Pressure (Pa)</b>",
    xmin=0, xmax=visible_time, ymin=90000, fast=True, align="right", background=color.black, foreground=color.white, width=750
)
atmospheric_pressure_curve = gcurve(graph=atmospheric_pressure_graph, color=color.red, width=3)

temperature_graph = graph(
    title="<b>Temperature</b>",
    xtitle="<b>Time (s)</b>",
    ytitle="<b>Temperature (°C)</b>",
    xmin=0, xmax=visible_time, ymin=10, ymax=50, fast=True, align="left", background=color.black, foreground=color.white, width=750
)
temperature_curve = gcurve(graph=temperature_graph, color=color.cyan, width=3)

relative_humidity_graph = graph(
    title="<b>Relative Humidity</b>",
    xtitle="<b>Time (s)</b>",
    ytitle="<b>Humidity (%)</b>",
    xmax=visible_time, xmin=0, ymin=0, ymax=100, fast=True, align="right", background=color.black, foreground=color.white, width=750
)
relative_humidity_curve = gcurve(graph=relative_humidity_graph, color=color.green, width=3)

# Data point index
i = 0

# --- ARRANQUE DEL SISTEMA ---
print(f"Iniciando CanSat Dashboard...")

# 1. Iniciar el hilo de procesamiento de datos
# Esto arranca la lectura serial en segundo plano
data_thread = start_data_thread(data_queue)

# 2. Bucle principal de VPython
while True:
    
    # 3. Leer los datos decodificados del hilo serial
    get_new_data() 
    
    # 4. Actualizar la rotación del modelo 3D
    update_rotation()
    
    # 5. Actualizar la etiqueta de advertencia/estado
    voltage = current_data.get('Battery Voltage', 0)
    
    if out_of_date:
        warning_label.text = "⚠ Out of Date! No data received."
    else:
        # Mostramos datos clave en el dashboard
        warning_label.text = (
            f"DATA LIVE | Alt: {current_data.get('Altitude', 0):.2f} m | "
            f"Temp: {current_data.get('Temperature', 0)}°C | "
            f"Batt: {voltage:.2f} V"
        )

    # 6. Obtener los valores decodificados para las gráficas
    # NOTA: Asumo que tu "Pressure" en la gráfica debe usar "Altitude" o 
    # si tienes un valor de presión explícito, ajusta la clave. Usaré 'Altitude' como ejemplo.
    pressure_or_altitude = current_data.get('Altitude', 0) 
    temperature = current_data.get('Temperature', 0)
    humidity = current_data.get('Rel. humidity', 0)

    # 7. Agregar valores a las gráficas (usando el tiempo real)
    current_time_sec = i / fps
    
    atmospheric_pressure_curve.plot(current_time_sec, pressure_or_altitude)
    temperature_curve.plot(current_time_sec, temperature)
    relative_humidity_curve.plot(current_time_sec, humidity)
    
    # 8. Desplazar la gráfica cuando alcanza el límite de tiempo (sin cambios)
    if i > max_points:
        shift_amount = 1 / fps
        temperature_graph.xmin += shift_amount
        temperature_graph.xmax += shift_amount
        atmospheric_pressure_graph.xmin += shift_amount
        atmospheric_pressure_graph.xmax += shift_amount
        relative_humidity_graph.xmin += shift_amount
        relative_humidity_graph.xmax += shift_amount

        # Lógica para guardar en CSV
        # Guardaremos el último paquete completo en el CSV cada 10 segundos
        if i % (10 * fps) == 0:
            csv_data = [
                current_time_sec, 
                current_data.get('Pitch', 0), 
                current_data.get('Roll', 0), 
                current_data.get('Yaw', 0), 
                current_data.get('Altitude', 0), 
                current_data.get('Temperature', 0), 
                current_data.get('Rel. humidity', 0), 
                current_data.get('Battery Voltage', 0), 
                current_data.get('Battery Current', 0),
                current_data.get('Latitude', 0),
                current_data.get('Longitude', 0)
            ]
            
            # Abrir archivo en modo append para agregar datos
            with open("cansat_telemetry_data.csv", "a", newline="") as file:
                writer = csv.writer(file)
                # Escribir encabezados si el archivo está vacío
                if file.tell() == 0:
                    writer.writerow(['Time (s)', 'Pitch', 'Roll', 'Yaw', 'Altitude (m)', 'Temperature (°C)', 'Humidity (%)', 'Battery Voltage (V)', 'Battery Current (mA)', 'Latitude', 'Longitude'])
                writer.writerow(csv_data)

    i += 1
    
    # Controla la velocidad de actualización de la pantalla
    rate(fps)
