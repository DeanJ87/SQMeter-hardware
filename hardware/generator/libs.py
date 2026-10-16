import copy, os
from sexp import parse, find, find1, Sym
SYMDIR='/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols'
_cache={}
def lib(name):
    if name not in _cache:
        _cache[name]=parse(open(f'{SYMDIR}/{name}.kicad_sym').read())[0]
    return _cache[name]
def raw(lib_id):
    l,n=lib_id.split(':')
    for s in find(lib(l),'symbol'):
        if s[1]==n: return s
    raise KeyError(lib_id)
def flat(lib_id):
    """flattened symbol with name = lib_id"""
    l,n=lib_id.split(':')
    s=copy.deepcopy(raw(lib_id))
    ext=find1(s,'extends')
    if ext:
        parent=flat(f'{l}:{ext[1]}')
        pname=ext[1]
        s=[e for e in s if not (isinstance(e,list) and e and e[0]=='extends')]
        props={p[1]:p for p in find(s,'property')}
        new=[Sym('symbol'), lib_id]
        for e in parent[2:]:
            if isinstance(e,list) and e[0]=='property' and e[1] in props:
                new.append(props.pop(e[1]))
            elif isinstance(e,list) and e[0]=='symbol':
                e=copy.deepcopy(e); e[1]=e[1].replace(pname.split(':')[-1], n,1); new.append(e)
            else:
                new.append(copy.deepcopy(e))
        for p in props.values(): new.insert(-1,p)
        return new
    s[1]=lib_id
    return s
def pins(lib_id):
    s=flat(lib_id); out=[]
    def walk(x,unit):
        for e in x:
            if isinstance(e,list) and e:
                if e[0]=='symbol':
                    u=int(e[1].split('_')[-2]) if e[1].count('_')>=2 else 0
                    walk(e,u)
                elif e[0]=='pin':
                    at=find1(e,'at'); nm=find1(e,'name')[1]; num=find1(e,'number')[1]
                    out.append(dict(num=num,name=nm,x=float(at[1]),y=float(at[2]),rot=float(at[3]) if len(at)>3 else 0,type=str(e[1]),unit=unit))
    walk(s,0); return out
