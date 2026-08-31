from bs4 import BeautifulSoup
from fuentes_rd import _section_tokens
from fuentes_espana import _extraer_html

html='''<h4>Anguila 10AM</h4><div>56</div><div>1ro</div><div>65</div><div>2do</div><div>23</div><div>3ro</div><div>31-08-2026</div><h4>Otra</h4>'''
nums,fecha=_section_tokens(BeautifulSoup(html,'html.parser'),['Anguila 10AM'],3)
assert nums==['56','65','23'],(nums,fecha)
assert fecha=='2026-08-31', fecha

html_k='<h4>Super Kino TV</h4>'+''.join(f'<span>{i:02d}</span>' for i in range(1,21))+'<div>31-08-2026</div><h4>Loto</h4>'
nums,_=_section_tokens(BeautifulSoup(html_k,'html.parser'),['Super Kino TV'],20)
assert nums==[f'{i:02d}' for i in range(1,21)]

assert _extraer_html('<div>Combinación 01 02 03 04 05 06 Reintegro 7</div>','primitiva')['numeros']==[1,2,3,4,5,6]
print('OK parsers')
