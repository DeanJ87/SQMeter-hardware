import re
TOK = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')
class Sym(str):
    """bare atom"""
def parse(text):
    stack=[[]]
    for m in TOK.finditer(text):
        t=m.group(0)
        if t=='(':
            stack.append([])
        elif t==')':
            x=stack.pop(); stack[-1].append(x)
        elif t[0]=='"':
            stack[-1].append(t[1:-1].replace('\\"','"').replace('\\\\','\\'))
        else:
            stack[-1].append(Sym(t))
    return stack[0]
def q(s):
    return '"'+str(s).replace('\\','\\\\').replace('"','\\"')+'"'
def dump(x, ind=0):
    if isinstance(x, list):
        if not x: return '()'
        simple = all(not isinstance(e,list) for e in x)
        if simple:
            return '(' + ' '.join(dump(e) for e in x) + ')'
        out='(' + dump(x[0])
        for e in x[1:]:
            out += '\n' + '  '*(ind+1) + dump(e, ind+1)
        return out + '\n' + '  '*ind + ')'
    if isinstance(x, Sym): return str(x)
    if isinstance(x, bool): return 'yes' if x else 'no'
    if isinstance(x, (int,float)):
        s=('%.4f'%x).rstrip('0').rstrip('.')
        return s if s not in ('-0','') else '0'
    return q(x)
def find(x, key):
    return [e for e in x if isinstance(e,list) and e and e[0]==key]
def find1(x,key):
    r=find(x,key); return r[0] if r else None
