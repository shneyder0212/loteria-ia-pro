import sqlite3
import asyncio
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from scraper_loteria import ScraperLoteriasRD
from enjambre_loteria_ai import Enjambre100AgentesLoteria

app = FastAPI(title="Lotería IA Shneyder")
DB_PATH = "loteria_master_ai.db"

scraper = ScraperLoteriasRD(db_path=DB_PATH)
enjambre = Enjambre100AgentesLoteria(db_path=DB_PATH)

async def tarea_segundo_plano():
    while True:
        try:
            sorteos = scraper.sincronizar_todo()
            nuevos = [s for s in sorteos if s.get("nuevo")]
            for n in nuevos:
                enjambre.autoajustar_red(n["1ra"])
        except Exception as e:
            print(f"Error en escaneo: {e}")
        await asyncio.sleep(600)

@app.on_event("startup")
async def inicio():
    scraper.sincronizar_todo()
    asyncio.create_task(tarea_segundo_plano())

@app.get("/", response_class=HTMLResponse)
def inicio_app():
    reporte = enjambre.ejecutar_consenso_100_agentes()

    if "error" in reporte:
        scraper.sincronizar_todo()
        reporte = enjambre.ejecutar_consenso_100_agentes()

    if "error" in reporte:
        return f"""
        <html>
        <head><meta name="viewport" content="width=device-width, initial-scale=1.0"><meta http-equiv="refresh" content="10"></head>
        <body style="background:#0f172a;color:#f8fafc;font-family:sans-serif;text-align:center;padding:40px;">
            <h2>⏳ Descargando primeros sorteos...</h2>
            <p>La IA está recopilando los datos web. Esta página se recargará sola en 10 segundos.</p>
        </body></html>
        """

    sueltos = reporte.get("top_20_sueltos", reporte.get("top_5_lineas_fuertes", []))
    pales = reporte.get("top_20_pales", [])
    tripletas = reporte.get("top_20_tripletas", [])

    filas_top5 = "".join([f"<tr style='background:rgba(34,197,94,0.15);font-weight:bold;'><td style='padding:8px;border:1px solid #334155;'>#{i}</td><td style='padding:8px;border:1px solid #334155;color:#4ade80;font-size:18px;'>{item['numero']}</td><td style='padding:8px;border:1px solid #334155;'>{item['fuerza_ia']}%</td><td style='padding:8px;border:1px solid #334155;'>{item['loteria']}</td></tr>" for i, item in enumerate(sueltos[:5], 1)])
    filas_sueltos = "".join([f"<tr><td style='padding:6px;border:1px solid #334155;'>#{i:02d}</td><td style='padding:6px;border:1px solid #334155;font-weight:bold;color:#38bdf8;'>{item['numero']}</td><td style='padding:6px;border:1px solid #334155;'>{item['fuerza_ia']}%</td><td style='padding:6px;border:1px solid #334155;'>{item['loteria']}</td></tr>" for i, item in enumerate(sueltos[:20], 1)])
    filas_pales = "".join([f"<tr><td style='padding:6px;border:1px solid #334155;'>{i:02d}</td><td style='padding:6px;border:1px solid #334155;font-weight:bold;color:#facc15;'>{p['pale']}</td><td style='padding:6px;border:1px solid #334155;'>{p['fuerza']}%</td><td style='padding:6px;border:1px solid #334155;'>{p['loteria']}</td></tr>" for i, p in enumerate(pales[:20], 1)])
    filas_tripletas = "".join([f"<tr><td style='padding:6px;border:1px solid #334155;'>{i:02d}</td><td style='padding:6px;border:1px solid #334155;font-weight:bold;color:#f472b6;'>{t['tripleta']}</td><td style='padding:6px;border:1px solid #334155;'>{t['loteria']}</td></tr>" for i, t in enumerate(tripletas[:20], 1)])

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="refresh" content="60">
        <title>IA Loterías Shneyder</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b0f19; color: #e2e8f0; margin: 0; padding: 15px; }}
            .card {{ background: #1e293b; border-radius: 12px; padding: 15px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5); }}
            h1 {{ font-size: 20px; text-align: center; color: #38bdf8; margin-top: 5px; }}
            h2 {{ font-size: 16px; margin-top: 0; padding-bottom: 5px; border-bottom: 1px solid #475569; }}
            .pill {{ background: #0f172a; padding: 8px 12px; border-radius: 8px; text-align: center; font-size: 14px; margin-bottom: 15px; }}
            table {{ width: 100%; border-collapse: collapse; text-align: center; font-size: 13px; }}
        </style>
    </head>
    <body>
        <h1>🇩🇴 SISTEMA IA LOTERÍAS</h1>
        <div class="pill">
            🎯 <b>ÚLTIMO SALIDOR:</b> [{reporte.get('ultimo_salidor', '--')}]<br>
            🕒 <small>Actualizado: {datetime.now().strftime('%I:%M:%S %p')}</small>
        </div>

        <div class="card" style="border: 1px solid #22c55e;">
            <h2 style="color: #4ade80;">⭐ TOP 5 LÍNEAS ÉLITE</h2>
            <table>
                <tr style="color:#94a3b8;"><th>#</th><th>NÚMERO</th><th>FUERZA</th><th>JUGAR EN</th></tr>
                {filas_top5}
            </table>
        </div>

        <div class="card">
            <h2 style="color: #38bdf8;">📊 TOP 20 NÚMEROS SUELTOS</h2>
            <table>
                <tr style="color:#94a3b8;"><th>#</th><th>NÚMERO</th><th>FUERZA</th><th>JUGAR EN</th></tr>
                {filas_sueltos}
            </table>
        </div>

        <div class="card">
            <h2 style="color: #facc15;">🎯 TOP 20 PALÉS</h2>
            <table>
                <tr style="color:#94a3b8;"><th>#</th><th>PALÉ</th><th>FUERZA</th><th>JUGAR EN</th></tr>
                {filas_pales}
            </table>
        </div>

        <div class="card">
            <h2 style="color: #f472b6;">🏆 TOP 20 TRIPLETAS BLINDADAS</h2>
            <table>
                <tr style="color:#94a3b8;"><th>#</th><th>TRIPLETA</th><th>JUGAR EN</th></tr>
                {filas_tripletas}
            </table>
        </div>
    </body>
    </html>
    """
