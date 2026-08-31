from datetime import datetime,timedelta
from config import CORTES_RD,TZ_RD,TZ_ES,SALAS
from memoria import guardar_prediccion_congelada,obtener_prediccion
from motor_ia import analizar_quiniela,analizar_kino,analizar_bolas
from verificador import sincronizar_todas

MAPA={x[0]:x for x in SALAS}
def fecha_rd(): return datetime.now(TZ_RD).date().isoformat()
def _analizar(clave,tipo):
    if tipo=='quiniela': return analizar_quiniela(clave)
    if tipo=='kino': return analizar_kino(clave)
    if tipo=='primitiva': return analizar_bolas(clave,49,6)
    if tipo=='euromillones': return analizar_bolas(clave,50,5)
    return {'estado':'SIN_MODELO'}

def ejecutar_corte(corte,forzar=False):
    if corte not in CORTES_RD: return {'estado':'ERROR','mensaje':'Corte desconocido'}
    fecha=fecha_rd(); cfg=CORTES_RD[corte]; fecha_sync=(datetime.now(TZ_RD).date()-timedelta(days=1)).isoformat() if cfg.get('sincronizar_antes')=='ayer' else fecha; sync=sincronizar_todas(fecha_sync,region='rd'); salida={}
    for clave in cfg['salas']:
        if clave not in MAPA: salida[clave]={'estado':'NO_CONFIGURADA'}; continue
        previa=obtener_prediccion(fecha,corte,clave)
        if previa and not forzar: salida[clave]={'estado':'CONGELADA','ranking':previa['ranking'][:10]}; continue
        _,_,tipo,_=MAPA[clave]; analisis=_analizar(clave,tipo)
        if analisis.get('estado')!='OK': salida[clave]=analisis; continue
        ranking=analisis['ranking']; guardar_prediccion_congelada(fecha,corte,clave,ranking,{'titulo':cfg['titulo'],'muestras':analisis.get('muestras',0),'hora_programada':f"{cfg['hora']:02d}:{cfg['minuto']:02d} RD"}); salida[clave]={'estado':'GENERADA_Y_CONGELADA','top5':ranking[:5],'top10':ranking[:10]}
    return {'estado':'OK','fecha':fecha,'corte':corte,'sincronizacion_previa':{k:v.get('estado') for k,v in sync.items()},'resultados':salida}

def ejecutar_estudio_espana(clave):
    if clave not in MAPA: return {'estado':'ERROR'}
    ahora=datetime.now(TZ_ES); fecha=ahora.date().isoformat(); _,_,tipo,_=MAPA[clave]; dias={'primitiva':{0,3,5},'euromillones':{1,4}}
    if ahora.weekday() not in dias.get(tipo,set()): return {'estado':'NO_JUEGA_HOY'}
    previa=obtener_prediccion(fecha,'espana',clave)
    if previa: return {'estado':'CONGELADA','ranking':previa['ranking']}
    analisis=_analizar(clave,tipo)
    if analisis.get('estado')!='OK': return analisis
    guardar_prediccion_congelada(fecha,'espana',clave,analisis['ranking'],{'muestras':analisis.get('muestras',0),'hora_programada':'18:00 ES'}); return {'estado':'GENERADA_Y_CONGELADA','seleccion':analisis.get('seleccion')}

def corte_actual():
    ahora=datetime.now(TZ_RD); mins=ahora.hour*60+ahora.minute; orden=[('manana',300),('tarde',795),('noche',1140)]; d=[c for c,m in orden if mins>=m]; return d[-1] if d else None
