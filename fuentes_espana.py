import re,requests
from bs4 import BeautifulSoup
BASE='https://www.loteriasyapuestas.es'; HEADERS={'User-Agent':'Mozilla/5.0 (compatible; ShneyderIA/2.0)'}
def _nums(text,low,high): return [int(x) for x in re.findall(r'(?<!\d)(\d{1,2})(?!\d)',text) if low<=int(x)<=high]
def _extraer_html(html,juego):
    soup=BeautifulSoup(html,'html.parser'); pieces=[soup.get_text(' ',strip=True)]
    for tag in soup.find_all(True):
        for a in ('alt','title','aria-label','value'):
            if tag.get(a): pieces.append(str(tag.get(a)))
    text=' '.join(pieces)
    if juego=='euromillones':
        m=re.search(r'(?:combinaci[oó]n|n[uú]meros).*?((?:\b\d{1,2}\b\D*){5,10})',text,re.I); nums=list(dict.fromkeys(_nums(m.group(1) if m else text,1,50))); em=re.search(r'estrellas?.*?((?:\b\d{1,2}\b\D*){2,5})',text,re.I); stars=list(dict.fromkeys(_nums(em.group(1),1,12))) if em else []
        if len(nums)>=5 and len(stars)>=2: return {'numeros':nums[:5],'estrellas':stars[:2]}
    if juego=='primitiva':
        m=re.search(r'(?:combinaci[oó]n|n[uú]meros).*?((?:\b\d{1,2}\b\D*){6,12})',text,re.I); nums=list(dict.fromkeys(_nums(m.group(1) if m else text,1,49))); mr=re.search(r'reintegro\D{0,20}([0-9])',text,re.I); rein=int(mr.group(1)) if mr else None
        if len(nums)>=6: return {'numeros':nums[:6],'reintegro':rein}
    return None
def obtener_oficial(juego,fecha_yyyymmdd):
    if juego=='euromillones': path=f'/f/loterias/resultados/euromillones.html?game_id=EMIL&fecha_sorteo={fecha_yyyymmdd}'
    elif juego=='primitiva': path=f'/f/loterias/resultados/primitiva.html?game_id=LAPR&fecha_sorteo={fecha_yyyymmdd}'
    else: return {'ok':False,'error':'juego no soportado'}
    url=BASE+path; fecha=f'{fecha_yyyymmdd[:4]}-{fecha_yyyymmdd[4:6]}-{fecha_yyyymmdd[6:]}'
    try:
        r=requests.get(url,headers=HEADERS,timeout=18); r.raise_for_status(); result=_extraer_html(r.text,juego)
        return {'ok':bool(result),'fuente':'SELAE','url':url,'fecha_fuente':fecha,'resultado':result,'error':None if result else 'No se pudo extraer una combinación válida'}
    except Exception as e: return {'ok':False,'fuente':'SELAE','url':url,'fecha_fuente':fecha,'error':str(e)}
