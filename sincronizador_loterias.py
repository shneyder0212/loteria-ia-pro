import sqlite3
import requests
from bs4 import BeautifulSoup

# Lista de las 3 fuentes oficiales proporcionadas por Shneyder
FUENTES_OFICIALES = [
    "https://loteriasdominicanas.com/",
    "https://www.loteriadominicana.com.do/",
    "https://loterias.conectate.com.do/"
]

def inicializar_base_datos():
    """Crea la base de datos local aislada para el historial de resultados."""
    conn = sqlite3.connect("historial_jaladeras.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resultados_reales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            loteria TEXT,
            primer_premio TEXT,
            segundo_premio TEXT,
            tercer_premio TEXT,
            fuente_origen TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("Base de datos local 'historial_jaladeras.db' inicializada correctamente.")

def probar_conexion_fuentes():
    """Prueba las fuentes en cascada con sistema de respaldo (Failover)."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    for url in FUENTES_OFICIALES:
        try:
            print(loc := f"Conectando de forma segura a: {url}...")
            respuesta = requests.get(url, headers=headers, timeout=10)
            if respuesta.status_code == 200:
                print(f"¡Conexión exitosa con la fuente: {url}!")
                soup = BeautifulSoup(respuesta.text, 'html.parser')
                # Aquí prepararemos el analizador para extraer los bloques de premios de la web
                return soup, url
            else:
                print(f"La fuente {url} respondió con código HTTP: {respuesta.status_code}")
        except Exception as e:
            print(f"Aviso de seguridad: No se pudo conectar a {url} ({e}). Probando siguiente fuente...")
            
    print("Modo de seguridad activado: Ninguna fuente externa respondió. El sistema se mantiene con el motor cuántico.")
    return None, None

if __name__ == "__main__":
    inicializar_base_datos()
    soup_resultado, fuente_activa = probar_conexion_fuentes()
    if soup_resultado:
        print(f"Listo para procesar los datos extraídos de: {fuente_activa}")
    else:
        print("Operación completada sin alterar el funcionamiento del servidor principal.")
