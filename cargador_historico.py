import os, re, json
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from config import SALAS, RD_NOMBRES, CONECTATE_URLS
from memoria import guardar_captura, guardar_verificado, guardar_observado, guardar_estado, leer_estado, reconciliar_capturas_rd, contar, contar_trabajo
from safe_http import CLIENT
from fuentes_rd import _section_tokens, _fallback
from fuentes_espana import _extraer_html

MAPA={x[0]:x for x in SALAS}
LOTDOM_HOME="https://www.loteriadominicana.com.do/"
SELAE_BASE="https://www.loteriasyapuestas.es"

def _state_json(key, default):
    r=leer_estado(key)
    if not r:
        return default
    try:
        return json.loads(r["valor"])
    except Exception:
        return default

def _same_domain(a,b):
    return urlparse(a).netloc.lower()==urlparse(b).netloc.lower()

def _archive_links(html, base_url, limit=100):
    soup=BeautifulSoup(html,"html.parser")
    out=[]
    for a in soup.find_all("a", href=True):
        href=urljoin(base_url,a["href"])
        q=href.lower()
        if not _same_domain(href,base_url):
            continue
        # only links that look like a historical date/archive selector
        if ("?d=" in q or "&d=" in q or "fecha=" in q or "date=" in q):
            if href not in out:
                out.append(href)
        if len(out)>=limit:
            break
    return out

def _parse_rd_page(html, claves=None):
    soup=BeautifulSoup(html,"html.parser")
    resultados={}
    claves=claves or [c for c,_,t,r in SALAS if r=="rd"]
    for clave in claves:
        names=RD_NOMBRES.get(clave,[])
        if not names:
            continue
        expected=20 if clave=="kino_leidsa" else 3
        nums,fecha=_section_tokens(soup,names,expected)
        if not nums:
            nums,fecha=_fallback(soup,names,expected)
        if nums and fecha:
            resultados[clave]={"fecha":fecha,"resultado":{"numeros":nums}}
    return resultados

def _guardar_rd_resultados(resultados, fuente):
    guardados=0
    verificados=0
    for clave,item in resultados.items():
        if clave not in MAPA:
            continue
        _,nombre,tipo,region=MAPA[clave]
        fecha=item["fecha"]
        resultado=item["resultado"]
        guardar_captura(clave,fecha,fecha,fuente,resultado,"OK","carga histórica")
        guardar_observado('rd',clave,nombre,tipo,fecha,resultado,fuente,fecha)
        guardados+=1
        if reconciliar_capturas_rd(clave,fecha,nombre,tipo):
            verificados+=1
    return guardados,verificados

def cargar_rd_incremental(max_paginas=6):
    max_paginas=max(1,min(int(max_paginas),12))
    visitados=set(_state_json("historico_rd_visitados",[]))
    pendientes=_state_json("historico_rd_pendientes",[])
    if not pendientes:
        pendientes=[LOTDOM_HOME]
        # Add one starting page per Conectate lottery. The crawler follows only date/archive links.
        for clave,url in CONECTATE_URLS.items():
            if url and url not in pendientes:
                pendientes.append(url)

    procesadas=0
    capturas=0
    verificados=0
    errores=[]

    while pendientes and procesadas<max_paginas:
        url=pendientes.pop(0)
        if url in visitados:
            continue
        try:
            resp=CLIENT.get(url,use_cache=True)
            html=resp["text"]
            fuente="loteriadominicana.com.do" if "loteriadominicana.com.do" in urlparse(url).netloc else "Conectate"
            if fuente=="loteriadominicana.com.do":
                resultados=_parse_rd_page(html)
            else:
                # Conectate pages are normally one game per URL; parsing all known names is still safe.
                resultados=_parse_rd_page(html)
            c,v=_guardar_rd_resultados(resultados,fuente)
            capturas+=c
            verificados+=v

            for link in _archive_links(html,url,100):
                if link not in visitados and link not in pendientes:
                    pendientes.append(link)
            visitados.add(url)
            procesadas+=1
        except Exception as e:
            errores.append({"url":url,"error":str(e)})
            visitados.add(url)
            procesadas+=1

    # Bound state size.
    visitados_list=list(visitados)[-1500:]
    pendientes=pendientes[:1500]
    guardar_estado("historico_rd_visitados",visitados_list)
    guardar_estado("historico_rd_pendientes",pendientes)
    resultado={
        "procesadas":procesadas,
        "capturas":capturas,
        "verificados_nuevos_o_actualizados":verificados,
        "pendientes":len(pendientes),
        "errores":errores[:10],
    }
    guardar_estado("historico_rd_ultima_carga",resultado)
    return resultado

def _sel_url(juego,fecha):
    ymd=fecha.strftime("%Y%m%d")
    if juego=="primitiva":
        return f"{SELAE_BASE}/f/loterias/resultados/primitiva.html?game_id=LAPR&fecha_sorteo={ymd}"
    return f"{SELAE_BASE}/f/loterias/resultados/euromillones.html?game_id=EMIL&fecha_sorteo={ymd}"

def cargar_espana_incremental(max_fechas=8, dias_atras=365):
    max_fechas=max(1,min(int(max_fechas),12))
    estado=_state_json("historico_esp_estado",{"offset":1})
    offset=max(1,int(estado.get("offset",1)))
    hoy=datetime.now().date()
    hechos=0
    guardados=0
    errores=[]

    while hechos<max_fechas and offset<=dias_atras:
        fecha=hoy-timedelta(days=offset)
        weekday=fecha.weekday()
        tareas=[]
        if weekday in (0,3,5): # L/J/S
            tareas.append(("primitiva_esp","La Primitiva","primitiva","primitiva"))
        if weekday in (1,4): # M/V
            tareas.append(("euromillones","Euromillones","euromillones","euromillones"))

        for clave,nombre,tipo,juego in tareas:
            if hechos>=max_fechas:
                break
            url=_sel_url(juego,fecha)
            try:
                resp=CLIENT.get(url,use_cache=True)
                result=_extraer_html(resp["text"],juego)
                if result:
                    iso=fecha.isoformat()
                    guardar_verificado("esp",clave,nombre,tipo,iso,result,"OFICIAL",["SELAE"])
                    guardados+=1
            except Exception as e:
                errores.append({"fecha":fecha.isoformat(),"juego":juego,"error":str(e)})
            hechos+=1
        offset+=1

    guardar_estado("historico_esp_estado",{"offset":offset})
    salida={"consultas":hechos,"guardados":guardados,"siguiente_offset":offset,"errores":errores[:10]}
    guardar_estado("historico_esp_ultima_carga",salida)
    return salida

def cargar_historico_incremental(rd_paginas=4, esp_fechas=4):
    salida={
        "rd":cargar_rd_incremental(rd_paginas),
        "espana":cargar_espana_incremental(esp_fechas),
    }
    salida["memoria_verificada"]=contar(); salida["memoria_utilizable"]=contar_trabajo()
    guardar_estado("historico_ultima_carga",salida)
    return salida
