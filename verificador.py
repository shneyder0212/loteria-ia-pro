from datetime import datetime
from config import SALAS, TZ_RD, TZ_ES
from memoria import guardar_captura, guardar_verificado
from fuentes_rd import obtener_loteriadominicana, obtener_conectate
from fuentes_espana import obtener_oficial

MAPA={x[0]:x for x in SALAS}

def _fecha_iso(region):
    tz=TZ_ES if region=="esp" else TZ_RD
    return datetime.now(tz).date().isoformat()

def _yyyymmdd(fecha_iso):
    return fecha_iso.replace("-","")

def verificar_sala(clave, fecha=None):
    if clave not in MAPA:
        return {"estado":"ERROR","mensaje":"Sala desconocida"}

    _, nombre, tipo, region = MAPA[clave]
    fecha=fecha or _fecha_iso(region)

    if region=="esp":
        juego="primitiva" if tipo=="primitiva" else "euromillones"
        a=obtener_oficial(juego,_yyyymmdd(fecha))
        guardar_captura(clave,fecha,"SELAE",a.get("resultado"),"OK" if a.get("ok") else "ERROR",a.get("error",""))
        if a.get("ok"):
            guardar_verificado("esp",clave,nombre,tipo,fecha,a["resultado"],"OFICIAL",[a["fuente"]])
            return {"estado":"OFICIAL","guardado":True,"resultado":a["resultado"],"fuentes":[a["fuente"]]}
        return {"estado":"PENDIENTE","guardado":False,"fuentes":[a]}

    a=obtener_loteriadominicana(clave)
    b=obtener_conectate(clave)

    for x in (a,b):
        guardar_captura(clave,fecha,x.get("fuente","desconocida"),x.get("resultado"),
                        "OK" if x.get("ok") else "ERROR",x.get("error",""))

    valid=[x for x in (a,b) if x.get("ok") and x.get("resultado")]
    if len(valid)>=2 and valid[0]["resultado"]==valid[1]["resultado"]:
        result=valid[0]["resultado"]
        fuentes=[x["fuente"] for x in valid]
        guardar_verificado("rd",clave,nombre,tipo,fecha,result,"VERIFICADO",fuentes)
        return {"estado":"VERIFICADO","guardado":True,"resultado":result,"fuentes":fuentes}

    return {
        "estado":"PENDIENTE",
        "guardado":False,
        "mensaje":"No se guarda en memoria hasta que dos fuentes coincidan.",
        "fuentes":[a,b]
    }

def sincronizar_todas():
    salida={}
    for clave,_,_,_ in SALAS:
        salida[clave]=verificar_sala(clave)
    return salida
