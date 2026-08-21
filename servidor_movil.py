import json
import random
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()

# [MOTOR DE JALADERAS DINÁMICO]
JALADERAS_MODELO = {
    "25": ["50", "75", "00"], "11": ["12", "22", "66"], 
    "44": ["99", "49", "11"], "48": ["93", "84", "24"]
}

def obtener_jaladera_evolutiva(num):
    return JALADERAS_MODELO.get(num, ["{:02d}".format((int(num)+10)%100), "{:02d}".format((int(num)+25)%100)])

@app.get("/", response_class=HTMLResponse)
async def root():
    # 1. Definición inicial de variables para evitar 'not defined'
    analisis = {}
    ahora = datetime.utcnow() - timedelta(hours=6)
    
    # 2. Lógica de mantenimiento
    if ahora.hour == 4 and ahora.minute >= 30:
        return "<h1>MANTENIMIENTO DEL SISTEMA: RECALIBRANDO MOTORES (4:30 AM)... VUELVA EN INSTANTES</h1>"

    # 3. Procesamiento de motores
    try:
        es_martes = ahora.weekday() == 1
        factor = 1.05 if es_martes else 1.0
        salas = ["real", "gana_mas", "leidsa", "loteka", "nacional", "anguila_9pm"]
        
        for clave in salas:
            rng = random.Random(f"{ahora.strftime('%Y%m%d')}{clave}")
            n_base = "{:02d}".format(rng.randint(0, 99))
            analisis[clave] = {
                "nombre": clave.upper(),
                "directo": n_base,
                "jaladeras": obtener_jaladera_evolutiva(n_base),
                "fuerza": round(98.0 * factor, 2)
            }
        
        # 4. Renderizado seguro con los datos definidos
        datos_json = json.dumps(analisis)
        
        return f"""
        <html><body style="background:#050a14; color:#fff; font-family:sans-serif; padding:20px;">
            <h1>SHNEYDER IA PRO RD (v90.2 - BLINDADO)</h1>
            <div id="app"></div>
            <script>
                let data = {datos_json};
                let html = "";
                for(let k in data) {{
                    html += `<div style='background:#0f172a; border-left: 5px solid #38bdf8; padding:15px; margin-bottom:10px; border-radius:8px;'>
                        <h2>${{data[k].nombre}}</h2>
                        <p>Foco: <b style='font-size:20px; color:#facc15;'>${{data[k].directo}}</b></p>
                        <p>Jaladeras: ${{data[k].jaladeras.join(' - ')}}</p>
                    </div>`;
                }}
                document.getElementById('app').innerHTML = html;
            </script>
        </body></html>
        """
    except Exception as e:
        return f"<h1>Error de Ejecución: {str(e)}</h1>"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
