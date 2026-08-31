import re, requests
from bs4 import BeautifulSoup

BASE="https://www.loteriasyapuestas.es"
HEADERS={"User-Agent":"Mozilla/5.0 (compatible; ShneyderIA/1.0)"}

def _nums(text, low, high):
    vals=[]
    for x in re.findall(r'(?<!\d)(\d{1,2})(?!\d)', text):
        n=int(x)
        if low <= n <= high:
            vals.append(n)
    return vals

def _extraer_html(html, juego):
    soup=BeautifulSoup(html,"html.parser")
    # text + alt/title attributes because SELAE sometimes renders result imagery
    pieces=[soup.get_text(" ",strip=True)]
    for tag in soup.find_all(True):
        for a in ("alt","title","aria-label"):
            if tag.get(a):
                pieces.append(str(tag.get(a)))
    text=" ".join(pieces)

    if juego=="euromillones":
        # Prefer explicit combination regions if labels exist
        m=re.search(r'(?:combinaci[oó]n|n[uú]meros).*?((?:\b\d{1,2}\b\D*){5,8})',text,re.I)
        target=m.group(1) if m else text
        nums=_nums(target,1,50)
        # de-duplicate preserving order
        nums=list(dict.fromkeys(nums))
        em=re.search(r'estrellas?.*?((?:\b\d{1,2}\b\D*){2,4})',text,re.I)
        stars=_nums(em.group(1),1,12) if em else []
        stars=list(dict.fromkeys(stars))
        if len(nums)>=5 and len(stars)>=2:
            return {"numeros":nums[:5],"estrellas":stars[:2]}

    if juego=="primitiva":
        m=re.search(r'(?:combinaci[oó]n|n[uú]meros).*?((?:\b\d{1,2}\b\D*){6,10})',text,re.I)
        target=m.group(1) if m else text
        nums=list(dict.fromkeys(_nums(target,1,49)))
        rein=None
        mr=re.search(r'reintegro\D{0,20}([0-9])',text,re.I)
        if mr: rein=int(mr.group(1))
        if len(nums)>=6:
            return {"numeros":nums[:6],"reintegro":rein}
    return None

def obtener_oficial(juego, fecha_yyyymmdd):
    if juego=="euromillones":
        path=f"/f/loterias/resultados/euromillones.html?game_id=EMIL&fecha_sorteo={fecha_yyyymmdd}"
    elif juego=="primitiva":
        path=f"/f/loterias/resultados/primitiva.html?game_id=LAPR&fecha_sorteo={fecha_yyyymmdd}"
    else:
        return {"ok":False,"error":"juego no soportado"}
    url=BASE+path
    try:
        r=requests.get(url,headers=HEADERS,timeout=15)
        if not r.ok:
            return {"ok":False,"fuente":"SELAE","url":url,"status":r.status_code}
        result=_extraer_html(r.text,juego)
        return {"ok":bool(result),"fuente":"SELAE","url":url,"resultado":result,
                "error":None if result else "No se pudo extraer una combinación válida"}
    except Exception as e:
        return {"ok":False,"fuente":"SELAE","url":url,"error":str(e)}
