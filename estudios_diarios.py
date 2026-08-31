from datetime import datetime
from config import CORTES_RD, TZ_RD, SALAS
from memoria import guardar_prediccion_congelada, obtener_prediccion
from motor_ia import analizar_quiniela

MAPA={x[0]:x for x in SALAS}

def fecha_rd():
    return datetime.now(TZ_RD).date().isoformat()

def ejecutar_corte(corte, forzar=False):
    if corte not in CORTES_RD:
        return {"estado":"ERROR","mensaje":"Corte desconocido"}

    fecha=fecha_rd()
    cfg=CORTES_RD[corte]
    salida={}

    for clave in cfg["salas"]:
        if clave not in MAPA:
            salida[clave]={"estado":"NO_CONFIGURADA"}
            continue

        previa=obtener_prediccion(fecha,corte,clave)
        if previa and not forzar:
            salida[clave]={"estado":"CONGELADA","ranking":previa["ranking"][:10]}
            continue

        _,nombre,tipo,region=MAPA[clave]
        if tipo!="quiniela":
            salida[clave]={"estado":"SIN_MODELO_ESPECIFICO"}
            continue

        analisis=analizar_quiniela(clave)
        if analisis.get("estado")!="OK":
            salida[clave]=analisis
            continue

        ranking=analisis["ranking"]
        metadata={
            "titulo":cfg["titulo"],
            "muestras":analisis.get("muestras",0),
            "ultimo_resultado":analisis.get("ultimo",[]),
            "hora_programada":f'{cfg["hora"]:02d}:{cfg["minuto"]:02d} RD'
        }
        guardar_prediccion_congelada(fecha,corte,clave,ranking,metadata)
        salida[clave]={
            "estado":"GENERADA_Y_CONGELADA",
            "top5":ranking[:5],
            "top10":ranking[:10]
        }

    return {"estado":"OK","fecha":fecha,"corte":corte,"resultados":salida}

def corte_actual():
    ahora=datetime.now(TZ_RD)
    mins=ahora.hour*60+ahora.minute
    orden=[("manana",5*60),("tarde",13*60+15),("noche",19*60)]
    disponibles=[c for c,m in orden if mins>=m]
    return disponibles[-1] if disponibles else None
