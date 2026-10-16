import sys
from sexp import parse, find, find1
import design
net=parse(open(sys.argv[1]).read())[0]
nets=find1(net,'nets')
got={}
for n in find(nets,'net'):
    name=find1(n,'name')[1]
    for nd in find(n,'node'):
        got[(find1(nd,'ref')[1],find1(nd,'pin')[1])]=name.lstrip('/')
bad=0
for p in design.parts:
    for pin,netn in p['pins'].items():
        g=got.get((p['ref'],pin))
        if netn is None:
            if g and not g.startswith('unconnected'): print('NC but got',p['ref'],pin,g); bad+=1
        elif g!=netn: print('MISMATCH',p['ref'],pin,'want',netn,'got',g); bad+=1
print('nets:',len(find(nets,'net')),'checked pins:',sum(len(p['pins']) for p in design.parts),'bad:',bad)
