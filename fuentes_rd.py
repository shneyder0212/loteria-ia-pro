import re, requests
from bs4 import BeautifulSoup
from config import RD_NOMBRES,CONECTATE_URLS,LOTERIA_DOMINICANA_URLS

HEADERS={'User-Agent':'Mozilla/5.0 (compatible; ShneyderIA/2.0; +result-verifier)'}
DATE_RE=re.compile(r'\b(\d{1,2})[-/](\d{1,2})[-/](\d{4})\b')

def _iso_date(text):
    m=DATE_RE.search(text or '')
    if not m: return None
    d,mn,y=m.groups(); return f'{int(y):04d}-{int(mn):02d}-{int(d):02d}'

def _section_tokens(soup,names,expected):
    names_l=[n.lower() for n in names]
    for h in soup.find_all(['h2','h3','h4','h5','strong']):
        title=' '.join(h.stripped_strings).strip()
        if not title or not any(n in title.lower() for n in names_l): continue
        vals=[]; fecha=None
        for el in h.find_all_next(limit=120):
            if el is h: continue
            if el.name in ('h2','h3','h4','h5'):
                t=' '.join(el.stripped_strings).strip()
                if t: break
            for t in el.stripped_strings:
                if DATE_RE.search(t):
                    fecha=_iso_date(t)
                    break
                if len(vals)<expected and re.fullmatch(r'\d{1,2}',t.strip()):
                    n=int(t); vals.append(f'{n:02d}')
            if fecha: break
        if len(vals)>=expected: return vals[:expected],fecha
    return None,None

def _fallback(soup,names,expected):
    text=soup.get_text(' ',strip=True)
    for tag in soup.find_all(True):
        for a in ('alt','title','aria-label','value','data-result','data-number'):
            if tag.get(a): text+=' '+str(tag.get(a))
    lower=text.lower()
    for name in names:
        pos=lower.find(name.lower())
        if pos<0: continue
        block=text[pos:pos+3000]; fecha=_iso_date(block)
        if fecha:
            m=DATE_RE.search(block); block=block[:m.start()]
        if expected==3:
            m=re.search(r'(?<!\d)(\d{1,2})(?!\d)\s*1(?:ro|ra).*?(?<!\d)(\d{1,2})(?!\d)\s*2(?:do|da).*?(?<!\d)(\d{1,2})(?!\d)\s*3(?:ro|ra)',block,re.I|re.S)
            if m: return [f'{int(x):02d}' for x in m.groups()],fecha
        vals=[f'{int(x):02d}' for x in re.findall(r'(?<!\d)(\d{1,2})(?!\d)',block) if 0<=int(x)<=99]
        if len(vals)>=expected: return vals[:expected],fecha
    return None,None

def _fetch(url):
    r=requests.get(url,headers=HEADERS,timeout=18); r.raise_for_status(); return BeautifulSoup(r.text,'html.parser')

def _obtener(clave,url,fuente):
    expected=20 if clave=='kino_leidsa' else 3; names=RD_NOMBRES.get(clave,[])
    try:
        soup=_fetch(url); nums,fecha=_section_tokens(soup,names,expected)
        if not nums: nums,fecha=_fallback(soup,names,expected)
        if nums: return {'ok':True,'fuente':fuente,'url':url,'fecha_fuente':fecha,'resultado':{'numeros':nums}}
        return {'ok':False,'fuente':fuente,'url':url,'error':'resultado no localizado'}
    except Exception as e: return {'ok':False,'fuente':fuente,'url':url,'error':str(e)}

def obtener_loteriadominicana(clave):
    return _obtener(clave,LOTERIA_DOMINICANA_URLS.get(clave,'https://www.loteriadominicana.com.do/'),'loteriadominicana.com.do')

def obtener_conectate(clave):
    url=CONECTATE_URLS.get(clave)
    if not url: return {'ok':False,'fuente':'Conectate','error':'sin URL configurada'}
    return _obtener(clave,url,'Conectate')
