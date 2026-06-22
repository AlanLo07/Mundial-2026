from matriz495 import RAW
lines=[l.strip() for l in RAW.splitlines() if l.strip()]
opts=[]
for line in lines:
    parts=line.split()
    try:
        int(parts[0])
    except:
        continue
    etiquetas=[p for p in parts[1:] if p.startswith('3')]
    if len(etiquetas)>=8:
        for e in etiquetas[:8]:
            if e.upper() in ["3A","3C","3E"]:
                break
        else:
            opts.append([e.upper() for e in etiquetas[:8]])
N=len(opts)
from collections import Counter
firsts=[opt[0] for opt in opts]
cnt=Counter(firsts)
for g in ['3C','3E','3F','3H','3I']:
    c=cnt.get(g,0)
    pct=(c/N*100) if N>0 else 0
    print(f"{g}: {c}/{N} = {pct:.2f}%")
print(f"Total opciones leidas: {N}")
