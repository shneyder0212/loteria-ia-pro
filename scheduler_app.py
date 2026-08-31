import threading,time
from datetime import datetime,timedelta
from config import TZ_RD,TZ_ES,SYNC_JOBS_RD
from estudios_diarios import ejecutar_corte,ejecutar_estudio_espana
from verificador import sincronizar_claves,sincronizar_todas
from evaluador import evaluar_fecha
from cargador_historico import cargar_historico_incremental

_started=False
_lock=threading.Lock()
_done=set()
_startup_historico_hecho=False

def _mark_and_run(key,fn):
    with _lock:
        if key in _done: return
        _done.add(key)
        # evita crecimiento infinito: solo conservamos claves recientes
        if len(_done)>200:
            hoy=datetime.now(TZ_RD).date().isoformat(); viejas=[x for x in _done if hoy not in x]
            for x in viejas[:100]: _done.discard(x)
    try: fn()
    except Exception as e: print(f'[scheduler] {key}: {e}')

def _sync_eval(claves):
    fecha=datetime.now(TZ_RD).date().isoformat(); sincronizar_claves(claves,fecha); evaluar_fecha(fecha)

def _sync_ayer():
    fecha=(datetime.now(TZ_RD).date()-timedelta(days=1)).isoformat(); sincronizar_todas(fecha,region='rd'); evaluar_fecha(fecha)

def _loop():
    global _startup_historico_hecho
    inicio=time.time()
    while True:
        rd=datetime.now(TZ_RD); es=datetime.now(TZ_ES); d=rd.date().isoformat(); de=es.date().isoformat()
        hhmm=(rd.hour,rd.minute)
        # One small historical batch about a minute after each process start.
        if not _startup_historico_hecho and time.time()-inicio>=60:
            _startup_historico_hecho=True
            _mark_and_run(f'{d}:historico_inicio',lambda:cargar_historico_incremental(3,3))
        # Small daily historical batch; rate limiter/cache avoid hammering sources.
        if hhmm==(3,30):
            _mark_and_run(f'{d}:historico_diario',lambda:cargar_historico_incremental(6,6))
        if hhmm==(4,50): _mark_and_run(f'{d}:sync_ayer',_sync_ayer)
        if hhmm==(5,0): _mark_and_run(f'{d}:corte_manana',lambda:ejecutar_corte('manana'))
        if hhmm==(13,15): _mark_and_run(f'{d}:corte_tarde',lambda:ejecutar_corte('tarde'))
        if hhmm==(19,0): _mark_and_run(f'{d}:corte_noche',lambda:ejecutar_corte('noche'))
        for idx,(h,m,claves) in enumerate(SYNC_JOBS_RD):
            if hhmm==(h,m): _mark_and_run(f'{d}:sync_{idx}',lambda c=claves:_sync_eval(c))
        if (es.hour,es.minute)==(18,0): _mark_and_run(f'{de}:primitiva',lambda:ejecutar_estudio_espana('primitiva_esp'))
        if (es.hour,es.minute)==(18,2): _mark_and_run(f'{de}:euromillones',lambda:ejecutar_estudio_espana('euromillones'))
        if (es.hour,es.minute)==(23,0): _mark_and_run(f'{de}:sync_espana',_sync_espana)
        time.sleep(20)


def _sync_espana():
    fecha=datetime.now(TZ_ES).date().isoformat(); sincronizar_todas(fecha,region='esp'); evaluar_fecha(fecha)

def iniciar_scheduler():
    global _started
    with _lock:
        if _started: return
        _started=True
    threading.Thread(target=_loop,name='shneyder-scheduler',daemon=True).start()
