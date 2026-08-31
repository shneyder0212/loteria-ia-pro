import os,json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse,JSONResponse,PlainTextResponse
from config import SALAS
from memoria import inicializar_db,contar,listar_predicciones_fecha,resumen_estado,leer_estado,ultimo_resultado
from verificador import verificar_sala,sincronizar_todas
from motor_ia import analizar_quiniela,analizar_kino,analizar_bolas
from backtesting import medir,medir_kino
from ranking_loterias import ranking_mejores_loterias
from estudios_diarios import ejecutar_corte,corte_actual,fecha_rd
from scheduler_app import iniciar_scheduler
from alerta_maestra import evaluar_alerta_roja
from alerta_kino import evaluar_alerta_kino
from evaluador import evaluar_fecha

app=FastAPI(title='Shneyder IA Pro - Memoria Viva Verificada')
inicializar_db(); iniciar_scheduler(); MAPA={x[0]:x for x in SALAS}

@app.get('/ping',response_class=PlainTextResponse)
def ping(): return 'OK - Memoria Viva Verificada'

@app.get('/api/estado',response_class=JSONResponse)
def api_estado():
    estado=resumen_estado(); estado['ultima_sincronizacion']=leer_estado('ultima_sincronizacion'); estado['corte_actual']=corte_actual(); return estado

@app.get('/api/verificar/{clave}',response_class=JSONResponse)
def api_verificar(clave:str,fecha:str|None=None): return verificar_sala(clave,fecha)

@app.get('/api/sincronizar',response_class=JSONResponse)
def api_sync(fecha:str|None=None): return sincronizar_todas(fecha)

@app.get('/api/memoria/{clave}',response_class=JSONResponse)
def api_memoria(clave:str): return {'loteria':clave,'resultados_verificados':contar(clave),'ultimo':ultimo_resultado(clave)}

@app.get('/api/alerta-roja/{clave}',response_class=JSONResponse)
def api_alerta_roja(clave:str): return evaluar_alerta_roja(clave)


@app.get('/api/alerta-kino',response_class=JSONResponse)
def api_alerta_kino():
    return evaluar_alerta_kino('kino_leidsa')

@app.get('/api/backtest-kino',response_class=JSONResponse)
def api_backtest_kino():
    return medir_kino('kino_leidsa')

@app.get('/api/corte/{nombre}',response_class=JSONResponse)
def api_corte(nombre:str): return ejecutar_corte(nombre)

@app.get('/api/estudios-hoy',response_class=JSONResponse)
def api_estudios_hoy():
    fecha=fecha_rd(); return {'fecha':fecha,'corte_actual':corte_actual(),'predicciones':listar_predicciones_fecha(fecha)}

@app.get('/api/evaluar-hoy',response_class=JSONResponse)
def api_evaluar_hoy():
    fecha=fecha_rd(); return {'fecha':fecha,'evaluaciones':evaluar_fecha(fecha)}

@app.get('/api/mejor-loteria',response_class=JSONResponse)
def api_mejor_loteria(): return ranking_mejores_loterias()

def _analisis(clave,tipo):
    if tipo=='quiniela': return analizar_quiniela(clave)
    if tipo=='kino': return analizar_kino(clave)
    if tipo=='primitiva': return analizar_bolas(clave,49,6)
    if tipo=='euromillones': return analizar_bolas(clave,50,5)
    return {'estado':'SIN_MODELO','muestras':0}

def panel(clave,tipo):
    d=_analisis(clave,tipo)
    if d.get('estado')!='OK': return f"<div class='box warn'><b>Memoria todavía insuficiente:</b> {d.get('mensaje','Sin datos')}<br>Muestras verificadas: {d.get('muestras',0)}</div>"
    alerta_html=''
    if tipo=='quiniela':
        alerta=evaluar_alerta_roja(clave)
        if alerta.get('activa'):
            nums=' - '.join(alerta['numeros']); pale=' - '.join(alerta['pale']); senales=' · '.join(alerta.get('senales',[]))
            alerta_html=f"""<div class='alerta-roja'><div class='alerta-titulo'>🚨 ALERTA ROJA — JUGADA MAESTRA</div><div class='maestra'>{nums}</div><div><b>Palé:</b> {pale}</div><div><b>Tripleta:</b> {nums}</div><div><b>Backtest Top 10 (2+):</b> {alerta['top10_2mas_backtest']}%</div><div><b>Muestras:</b> {alerta['muestras']}</div><div><b>Señales:</b> {senales}</div><div class='aviso'>Señal estadística fuerte; no es garantía de premio.</div></div>"""
    especial=''
    if tipo=='kino':
        ak=evaluar_alerta_kino(clave)
        kino_bt=medir_kino(clave)
        alerta_kino_html=''
        if ak.get('activa'):
            alerta_kino_html=f"""<div class='alerta-kino'><div class='alerta-titulo'>👑 ALERTA KINO — NÚCLEO FUERTE</div><div class='maestra'>{' - '.join(ak.get('nucleo_5',[]))}</div><div><b>Jugada 10:</b> {' - '.join(ak.get('jugada_10',[]))}</div><div><b>Promedio histórico Top10:</b> {ak.get('promedio_top10')} aciertos · referencia azar {ak.get('esperado_azar')}</div><div><b>5+ aciertos:</b> {ak.get('5mas_pct')}% · muestras {ak.get('muestras')}</div><div class='aviso'>Señal histórica medida; no garantiza premio.</div></div>"""
        btline=''
        if kino_bt.get('estado')=='OK':
            btline=f"<br><b>Backtest Kino:</b> Top10 promedio {kino_bt['top10']['promedio_aciertos']} (azar {kino_bt['top10']['esperado_azar']}) · 5+ {kino_bt['top10']['5mas']}% · 6+ {kino_bt['top10']['6mas']}%"
        especial=f"{alerta_kino_html}<div class='box'><b>👑 Núcleo Kino 5:</b> {' - '.join(d.get('nucleo_5',[]))}<br><b>Jugada Kino 10:</b> {' - '.join(d.get('jugada_10',[]))}<br><b>Top 15:</b> {' - '.join(d.get('top15',[]))}<br><b>Top 20:</b> {' - '.join(d.get('top20',[]))}{btline}</div>"
    if tipo in ('primitiva','euromillones'): especial=f"<div class='box'><b>Selección principal:</b> {' - '.join(d.get('seleccion',[]))}</div>"
    bt_html=''
    if tipo=='quiniela':
        bt=medir(clave)
        if bt.get('estado')=='OK': bt_html=f"<div class='box'><b>Backtesting:</b> {bt['muestras']} sorteos · Top5 2+ {bt['top5']['2mas']}% · Top10 2+ {bt['top10']['2mas']}% · Top20 2+ {bt['top20']['2mas']}%</div>"
    rows=''.join(f"<tr><td>#{i}</td><td class='num'>{x['num']}</td><td>{x['score']}</td><td>{', '.join(x.get('razones',[])) or 'estadística'}</td></tr>" for i,x in enumerate(d['ranking'][:20],1))
    return f"{alerta_html}{especial}<div class='box'><b>Memoria verificada:</b> {d['muestras']} sorteos.</div>{bt_html}<table><tr><th>#</th><th>Número</th><th>Score</th><th>Razones</th></tr>{rows}</table>"

@app.get('/',response_class=HTMLResponse)
def index(sala:str|None=None):
    clave=sala if sala in MAPA else SALAS[0][0]; _,nombre,tipo,region=MAPA[clave]
    tabs=''.join(f"<a class='tab {'active' if s[0]==clave else ''}' href='/?sala={s[0]}'>{s[1]}</a>" for s in SALAS)
    body=panel(clave,tipo); estudio=ranking_mejores_loterias(); mejor=estudio.get('mejor')
    if mejor:
        razones=' · '.join(mejor.get('razones',[])); mejor_html=f"<div class='box best'><b>🎯 LOTERÍA RD CON MEJOR RENDIMIENTO MEDIDO:</b> {mejor['nombre']}<br>Score de estudio: {mejor['score_estudio']} · Muestras: {mejor['muestras']}<br>Top5 (2+): {mejor['reciente']['top5']['2mas']}% · Top10 (2+): {mejor['reciente']['top10']['2mas']}%<br><small>Por qué: {razones}</small></div>"
    else: mejor_html="<div class='box warn'><b>🎯 Mejor lotería:</b> aún faltan suficientes resultados verificados para compararlas.</div>"
    estado=resumen_estado(); ultima=leer_estado('ultima_sincronizacion'); lasttxt=ultima['actualizado_en'] if ultima else 'todavía no registrada'
    html=f"""<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Shneyder IA Pro</title><style>
    body{{background:#080d1a;color:#e2e8f0;font-family:Arial;margin:0;padding:12px}}.wrap{{max-width:1050px;margin:auto}}.tabs{{display:flex;overflow-x:auto;gap:6px;padding-bottom:10px}}.tab{{background:#1f2937;color:#fff;padding:9px;border-radius:8px;text-decoration:none;white-space:nowrap}}.active{{background:#38bdf8;color:#0f172a}}.card{{background:#131d31;border:1px solid #233249;border-radius:12px;padding:15px}}.box{{background:#0f172a;border:1px solid #38bdf8;border-radius:8px;padding:10px;margin:10px 0;line-height:1.6}}.warn{{border-color:#facc15}}.best{{border-color:#10b981}}table{{width:100%;border-collapse:collapse}}th,td{{padding:8px;border-bottom:1px solid #233249;text-align:center}}.num{{color:#38bdf8;font-weight:900}}.alerta-kino{{background:#16213b;border:3px solid #a78bfa;border-radius:12px;padding:14px;margin:12px 0}}.alerta-roja{{background:#3f0a0a;border:3px solid #ef4444;border-radius:12px;padding:14px;margin:12px 0}}.alerta-titulo{{color:#fecaca;font-size:19px;font-weight:900;text-align:center}}.maestra{{font-size:27px;font-weight:900;color:#fff;text-align:center;margin:10px}}.aviso{{color:#fecaca;font-size:11px;margin-top:10px}}a.btn{{display:inline-block;background:#10b981;color:#04130e;padding:9px 12px;border-radius:8px;text-decoration:none;font-weight:bold}}
    </style></head><body><div class='wrap'><h1>SHNEYDER IA PRO — TOTAL VIGILANCIA</h1><div class='tabs'>{tabs}</div><div class='box'><b>🧠 Estado:</b> {estado['resultados_totales']} resultados verificados · Última sincronización: {lasttxt}<br><b>🕒 Cortes RD:</b> 05:00 · 13:15 · 19:00. Antes de cada estudio se intenta actualizar la memoria.</div>{mejor_html}<div class='card'><h2>{nombre}</h2><p><a class='btn' href='/api/verificar/{clave}'>Verificar ahora</a></p>{body}</div></div></body></html>"""
    return HTMLResponse(html)

if __name__=='__main__':
    import uvicorn; uvicorn.run('servidor_movil:app',host='0.0.0.0',port=int(os.getenv('PORT','10000')))
