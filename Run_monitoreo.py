#app.py
from flask import Flask, jsonify, render_template, request
import logging
import asyncio
import sqlite3
import threading
from monitoreo import get_ram_memory, init_db

app = Flask(__name__)

# Configurar el nivel de logging para suprimir las peticiones GET
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Inicializar la base de datos
init_db()

# Función asincrónica para ejecutar el monitoreo de memoria cada 5 minutos
async def monitor_system_resources(host):
    while True:
        await get_ram_memory(host=host)
        await asyncio.sleep(300)  # Esperar 5 minutos

# Ejecutar el monitoreo en un hilo separado p
def run_async_loop(host):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(monitor_system_resources(host))

# Iniciar el monitoreo en hilos independientes al iniciar la aplicación
def start_monitoring():
    # Hilo para el monitoreo local
    thread_local = threading.Thread(target=run_async_loop, args=('localhost',))
    thread_local.daemon = True
    thread_local.start()

    # Hilo para el monitoreo remoto
    thread_remote = threading.Thread(target=run_async_loop, args=('192.168.2.15',))
    thread_remote.daemon = True
    thread_remote.start()

# Llamada a la función de inicio del monitoreo al arrancar la app
start_monitoring()

# Función para obtener los datos más recientes de memoria desde la base de datos
def get_memory_data(host):
    with sqlite3.connect('Base_Datos.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM memoria WHERE host=? ORDER BY timestamp DESC LIMIT 1", (host,))
        row = cursor.fetchone()

    if row:
        return {
            'Memoria Total (MB)': row[3],
            'Memoria Usada (MB)': row[4],
            'Memoria Libre (MB)': row[5],
            'Timestamp': row[2]
        }
    return {}

@app.route('/memoria/<host>')
def memoria(host):
    memoria_data = get_memory_data(host)
    return jsonify(memoria_data)

@app.route('/memoria-historico/<host>')
def memory_history(host):
    start_date = request.args.get('start')
    with sqlite3.connect('Base_Datos.db') as conn:
        cursor = conn.cursor()
        query = "SELECT timestamp, memoria_total, memoria_usada, memoria_libre FROM memoria WHERE host=?"
        params = (host,)

        if start_date:
            query += " AND timestamp >= ? ORDER BY timestamp ASC"
            params = (host, start_date)
        else:
            query += " ORDER BY timestamp DESC LIMIT 100"

        cursor.execute(query, params)
        rows = cursor.fetchall()

    historico_data = [{'timestamp': row[0], 'total': row[1], 'usada': row[2], 'libre': row[3]} for row in rows]
    historico_data.reverse()  # Revertir para mostrar los datos más recientes primero

    return jsonify(historico_data)


@app.route('/')
def index():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)