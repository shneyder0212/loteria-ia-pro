from datetime import datetime
from config import SALAS,TZ_RD,TZ_ES
from memoria import guardar_captura,guardar_verificado,guardar_observado,guardar_estado
from fuentes_rd import obtener_loteriadominicana,obtener_conectate
from fuentes_espana import obtener_oficial

MAPA={x[0]:x for x in SALAS}
def _fecha_iso(region): return datetime.now(TZ_ES if region=='esp' else TZ_RD).date().isoformat()
def _yyyymmdd(fecha): return fecha.replace('-','')
def _fecha_valida(fuente,objetivo):
    ff=fuente.get('fecha_fuente'); return ff is None or ff==objetivo

def verificar_sala(clave,fecha=None):
    if clave not in MAPA: return {'estado':'ERROR','mensaje':'Sala desconocida'}
    _,nombre,tipo,region=MAPA[clave]; fecha=fecha or _fecha_iso(region)
    if region=='esp':
        juego='primitiva' if tipo=='primitiva' else 'euromillones'; a=obtener_oficial(juego,_yyyymmdd(fecha)); ok=a.get('ok') and _fecha_valida(a,fecha)
        guardar_captura(clave,fecha,a.get('fecha_fuente'),'SELAE',a.get('resultado'),'OK' if ok else 'ERROR',a.get('error',''))
        if ok:
            guardar_verificado('esp',clave,nombre,tipo,fecha,a['resultado'],'OFICIAL',[a['fuente']]); return {'estado':'OFICIAL','guardado':True,'resultado':a['resultado'],'fuentes':[a['fuente']]}
        return {'estado':'PENDIENTE','guardado':False,'fuentes':[a]}
    a=obtener_loteriadominicana(clave); b=obtener_conectate(clave)
    for x in (a,b):
        ok=x.get('ok') and _fecha_valida(x,fecha); detalle=x.get('error','')
        if x.get('ok') and not _fecha_valida(x,fecha): detalle=f"fecha fuente {x.get('fecha_fuente')} != objetivo {fecha}"
        guardar_captura(clave,fecha,x.get('fecha_fuente'),x.get('fuente','desconocida'),x.get('resultado'),'OK' if ok else 'ERROR',detalle)
    valid=[x for x in (a,b) if x.get('ok') and x.get('resultado') and _fecha_valida(x,fecha)]
    fecha_confirmada=[x for x in valid if x.get('fecha_fuente')==fecha]

    # Any source that explicitly confirms the target date is useful as OBSERVED memory.
    for x in fecha_confirmada:
        guardar_observado('rd',clave,nombre,tipo,fecha,x['resultado'],x.get('fuente','desconocida'),x.get('fecha_fuente'))

    if len(valid)>=2 and valid[0]['resultado']==valid[1]['resultado'] and fecha_confirmada:
        result=valid[0]['resultado']
        fuentes=[x['fuente'] for x in valid]
        guardar_verificado('rd',clave,nombre,tipo,fecha,result,'VERIFICADO',fuentes)
        return {'estado':'VERIFICADO','guardado':True,'resultado':result,'fuentes':fuentes,'modo_memoria':'FUERTE'}

    if fecha_confirmada:
        x=fecha_confirmada[0]
        return {
            'estado':'OBSERVADO',
            'guardado':True,
            'resultado':x['resultado'],
            'fuentes':[x.get('fuente')],
            'mensaje':'Dato con fecha correcta guardado para estudio provisional; espera segunda fuente para verificación.',
            'modo_memoria':'PROVISIONAL'
        }

    return {'estado':'PENDIENTE','guardado':False,'mensaje':'Aún no hay una fuente que confirme explícitamente la fecha objetivo.','fuentes':[a,b]}

def sincronizar_claves(claves,fecha=None):
    salida={}
    for clave in claves:
        try: salida[clave]=verificar_sala(clave,fecha)
        except Exception as e: salida[clave]={'estado':'ERROR','mensaje':str(e)}
    guardar_estado('ultima_sincronizacion',{'fecha':fecha,'claves':list(claves),'resultado':{k:v.get('estado') for k,v in salida.items()}})
    return salida

def sincronizar_todas(fecha=None,region=None):
    return sincronizar_claves([c for c,_,_,r in SALAS if region is None or r==region],fecha)
