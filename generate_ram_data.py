import sqlite3
import random
from datetime import datetime, timedelta

# Función para generar datos simulados para los próximos 3 días
def generate_simulated_data():
    # Definir la fecha de inicio (hace tres días)
    start_date = datetime.now() - timedelta(days=3)
    
    # Definir hosts y sus características
    hosts = [
        {"host": "localhost", "memoria_total": 12188.25},  # Memoria total fija de localhost
        {"host": "192.168.2.15", "memoria_total": 8192.0}  # Memoria total fija de 8 GB (8192 MB)
    ]
    
    # Conectar a la base de datos
    conn = sqlite3.connect('Base_Datos.db')
    cursor = conn.cursor()
    
    # Generar y agregar datos para 3 días (3 días * 24 horas * 12 períodos de 5 minutos)
    for i in range(3 * 24 * 12):  # 3 días, 24 horas, 12 períodos de 5 minutos por hora
        timestamp = start_date + timedelta(minutes=i * 5)  # Cada 5 minutos
        
        for host_info in hosts:
            host = host_info["host"]
            memoria_total = host_info["memoria_total"]
            
            if host == "localhost":
                # Generar valores para localhost (uso más variable)
                memoria_usada = random.uniform(0, memoria_total)  # Usada entre 0 y el total
            elif host == "192.168.2.15":
                # Generar valores para el segundo equipo (bajo uso de RAM en reposo)
                memoria_usada = random.uniform(2048, 4096)  # Usada entre 0.5 GB y 2 GB
            
            memoria_libre = memoria_total - memoria_usada  # Libre es el resto
            
            # Insertar los datos en la tabla de memoria
            cursor.execute('''INSERT INTO memoria (timestamp, memoria_total, memoria_usada, memoria_libre, host) 
                              VALUES (?, ?, ?, ?, ?)''',
                           (timestamp, memoria_total, memoria_usada, memoria_libre, host))
    
    # Guardar los cambios y cerrar la conexión
    conn.commit()
    conn.close()

# Llamada para generar los datos simulados
generate_simulated_data()
print("Datos simulados generados y añadidos a la base de datos.")
