import struct
import threading
import queue
import time
import serial # Importamos la librería pyserial

port_name = 'COM14'  # <--- Cambia esto al puerto correcto

# --- 1. Definición del Formato Binario (struct) ---
# Basado en la imagen: 13 floats ('f') y 3 ints ('i')
# '<' indica Little-endian (el orden de bytes más común. Si falla, prueba con '>')
# 'f' = 4 bytes float
# 'i' = 4 bytes int
# Total: 16 variables * 4 bytes/variable = 64 bytes
DATA_FORMAT = '<f f f f f f f f f f i i f f f i'
RECORD_SIZE = struct.calcsize(DATA_FORMAT)
# Lista de nombres de campos en el orden exacto del struct para crear diccionarios de datos
FIELD_NAMES = [
    'Pitch', 'Roll', 'Yaw', 
    'Angular Speed X', 'Angular Speed Y', 'Angular Speed Z',
    'Angular accel X', 'Angular accel Y', 'Angular accel Z', 
    'Altitude', 
    'Temperature', 'Rel. humidity', 
    'Latitude', 'Longitude', 
    'Battery Voltage', 
    'Battery Current'
]

print(f"Decoder iniciado. Tamaño del registro esperado: {RECORD_SIZE} bytes.")

def serial_data_processor(data_queue, signal_queue, port_name='COM14', baud_rate=115200):
    """
    Lee datos binarios reales del puerto serial, los decodifica usando struct, 
    y coloca el diccionario de datos decimales en la cola.

    Argumentos:
        data_queue (queue.Queue): La cola compartida.
        port_name (str): Nombre del puerto serial (ej: COM3 en Windows, /dev/ttyUSB0 en Linux).
        baud_rate (int): Velocidad de comunicación serial (debe coincidir con la del CanSat).
    """

    print(f"Intentando abrir puerto serial: {'COM14'} @ {baud_rate}...")

    try:
        # Intenta abrir el puerto serial con un timeout de 1 segundo
        ser = serial.Serial('COM14', baud_rate, timeout=1)
        ser.flushInput() # Limpia el búfer de entrada antes de empezar
        print("Conexión serial establecida. Esperando datos...")
    except serial.SerialException as e:
        print(f"ERROR: No se pudo abrir el puerto serial '{'COM14'}'. Verifica la conexión y el nombre del puerto.")
        print(f"Detalles del error: {e}")
        return # Termina el hilo si la conexión falla
    
    # Búfer para acumular los bytes recibidos
    buffer = b'' 

    while True:
        try:
            # 1. Leer todos los bytes disponibles en el puerto de una vez
            if ser.in_waiting > 0:
                new_data = ser.read(ser.in_waiting)
                buffer += new_data
            
            # 2. Procesar el búfer y extraer paquetes completos
            # Esto maneja el caso donde los paquetes llegan fragmentados.
            while len(buffer) >= RECORD_SIZE:
                # Extrae el primer registro binario del búfer
                binary_record = buffer[:RECORD_SIZE]
                # Remueve el registro procesado del búfer
                buffer = buffer[RECORD_SIZE:]
                
                # --- Lógica de Decodificación con struct ---
                try:
                    # Desempaqueta los bytes en una tupla de valores decimales
                    decoded_values = struct.unpack(DATA_FORMAT, binary_record)
                    
                    # Crea un diccionario con nombre para cada valor decodificado
                    data_packet = dict(zip(FIELD_NAMES, decoded_values))
                    
                    # Envía el paquete decimal a la cola compartida
                    data_queue.put(data_packet)
                    
                    # --- Aquí señalizamos ---
                    signal_queue.put(("new_data", data_packet))
                    # Ejemplo: umbral de temperatura
                    if data_packet.get("Temperature", 0) > 40:
                        signal_queue.put(("threshold_exceeded", data_packet["Temperature"]))
                except struct.error as e:
                    # Esto ocurre si el formato no coincide o si hubo corrupción de datos.
                    print(f"Error de struct: {e}. Descartando primer byte del búfer para intentar resincronizar...")
                    buffer = buffer[1:] # Elimina el primer byte (posible byte corrupto) y busca el siguiente paquete válido
                    
                except struct.error as e:
                    # Esto ocurre si el formato no coincide o si hubo corrupción de datos.
                    print(f"Error de struct: {e}. Descartando primer byte del búfer para intentar resincronizar...")
                    buffer = buffer[1:] # Elimina el primer byte (posible byte corrupto) y busca el siguiente paquete válido

        except serial.SerialException as e:
            print(f"Error de comunicación serial: {e}")
            break
        except Exception as e:
            print(f"Error inesperado en el procesador: {e}")
            pass
        time.sleep(0.01) # Pequeña pausa para no saturar la CPU

    # 3. Cerrar el puerto serial al salir del bucle
    ser.close()
    print("Conexión serial cerrada.")


def start_data_thread(data_queue, signal_queue):
    """Inicializa y comienza el hilo del procesador de datos."""
    # 💡 NOTA: Puedes modificar 'port_name' y 'baud_rate' aquí si los conoces
    processor_thread = threading.Thread(
        target=serial_data_processor, 
        args=(data_queue, signal_queue, 'com14', 115200), 
        daemon=True
    )
    processor_thread.start()
    return processor_thread

# Si este archivo se ejecuta directamente, prueba la decodificación
if __name__ == '__main__':
    # 🚨 NOTA: Si ejecutas este archivo directamente, DEBE haber un dispositivo 
    # serial en /dev/ttyUSB0 que envíe datos binarios con el formato correcto.
    q = queue.Queue()
    start_data_thread(q)
    print("\nEjecutando en modo de prueba. Esperando datos seriales...")
    
    start_time = time.time()
    while time.time() - start_time < 5: # Espera 5 segundos para recibir datos
        if not q.empty():
            print("\nPaquete decodificado exitosamente:")
            print(q.get())
        time.sleep(0.5)
        
    print("\nFin de la prueba.")