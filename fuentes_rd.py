import re, requests
from bs4 import BeautifulSoup
from config import RD_NOMBRES, CONECTATE_URLS

HEADERS={"User-Agent":"Mozilla/5.0 (compatible; ShneyderIA/1.0)"}

def _tripleta(text):
    # Require labels or a compact 3-number window to reduce accidental extraction.
    labels=re.search(
        r'(?<!\d)(\d{2})(?!\d)\s*(?:1ro|1ra|primera).*?'
        r'(?<!\d)(\d{2})(?!\d)\s*(?:2do|2da|segunda).*?'
        r'(?<!\d)(\d{2})(?!\d)\s*(?:3ro|3ra|tercera)',
        text,re.I|re.S
    )
    if labels:
        return [labels.group(1),labels.group(2),labels.group(3)]
    return None

def obtener_loteriadominicana(clave):
    url="https://www.loteriadominicana.com.do/"
    try:
        r=requests.get(url,headers=HEADERS,timeout=15)
        if not r.ok:
            return {"ok":False,"fuente":"loteriadominicana.com.do","url":url,"status":r.status_code}
        soup=BeautifulSoup(r.text,"html.parser")
        nombres=RD_NOMBRES.get(clave,[])
        headings=soup.find_all(["h3","h4","h5"])
        for h in headings:
            title=" ".join(h.stripped_strings)
            if any(n.lower() in title.lower() for n in nombres):
                chunks=[title]
                for sib in h.find_all_next(limit=35):
                    if sib is h: continue
                    if sib.name in ("h3","h4","h5") and sib is not h:
                        break
                    t=" ".join(sib.stripped_strings)
                    if t: chunks.append(t)
                res=_tripleta(" ".join(chunks))
                if res:
                    return {"ok":True,"fuente":"loteriadominicana.com.do","url":url,"resultado":{"numeros":res}}
        # fallback around raw text after known lottery name
        text=soup.get_text(" ",strip=True)
        for n in nombres:
            pos=text.lower().find(n.lower())
            if pos>=0:
                res=_tripleta(text[pos:pos+800])
                if res:
                    return {"ok":True,"fuente":"loteriadominicana.com.do","url":url,"resultado":{"numeros":res}}
        return {"ok":False,"fuente":"loteriadominicana.com.do","url":url,"error":"resultado no localizado"}
    except Exception as e:
        return {"ok":False,"fuente":"loteriadominicana.com.do","url":url,"error":str(e)}

def obtener_conectate(clave):
    url=CONECTATE_URLS.get(clave)
    if not url:
        return {"ok":False,"fuente":"Conectate","error":"sin adaptador específico para esta sala"}
    try:
        r=requests.get(url,headers=HEADERS,timeout=15)
        if not r.ok:
            return {"ok":False,"fuente":"Conectate","url":url,"status":r.status_code}
        soup=BeautifulSoup(r.text,"html.parser")
        text=soup.get_text(" ",strip=True)
        res=_tripleta(text)
        if res:
            return {"ok":True,"fuente":"Conectate","url":url,"resultado":{"numeros":res}}
        # Some result widgets render bare two-digit values near 'Resultados'
        marker=re.search(r'(?:resultados?|n[uú]meros ganadores)',text,re.I)
        if marker:
            section=text[marker.start():marker.start()+1200]
            vals=re.findall(r'(?<!\d)(\d{2})(?!\d)',section)
            # only accept if at least 3 and no obvious date/time tokens dominate
            if len(vals)>=3:
                candidate=vals[:3]
                if all(0<=int(x)<=99 for x in candidate):
                    return {"ok":True,"fuente":"Conectate","url":url,"resultado":{"numeros":candidate}}
        return {"ok":False,"fuente":"Conectate","url":url,"error":"resultado no localizado"}
    except Exception as e:
        return {"ok":False,"fuente":"Conectate","url":url,"error":str(e)}
