"""Beveled solid primitives for the shield-generator example. Coordinates are local to the part."""
tris=[]
def tri(a,b,c,mat,part):tris.append((tuple(tuple(float(x) for x in v) for v in (a,b,c)),mat,part))
def quad(a,b,c,d,mat,part):
    tri(a,b,c,mat,part);tri(a,c,d,mat,part)
def rect(hx,hy,b):
    return [(-hx+b,-hy),(hx-b,-hy),(hx,-hy+b),(hx,hy-b),(hx-b,hy),(-hx+b,hy),(-hx,hy-b),(-hx,-hy+b)]
def loft(levels,mat,part):
    # Each level: z, centre x/y, halfwidth x/y, corner chamfer
    rings=[[(cx+x,cy+y,z) for x,y in rect(hx,hy,b)] for z,cx,cy,hx,hy,b in levels]
    for lo,hi in zip(rings,rings[1:]):
        for i in range(8):quad(lo[i],lo[(i+1)%8],hi[(i+1)%8],hi[i],mat,part)
    for face in (rings[0][::-1],rings[-1]):
        mid=tuple(sum(v[k] for v in face)/len(face) for k in range(3))
        for i in range(8):tri(mid,face[i],face[(i+1)%8],mat,part)
def box(cx,cy,hx,hy,z0,z1,mat,part,b=.025):
    b=min(b,hx*.4,hy*.4)
    loft([(z0,cx,cy,hx,hy,b),(z1,cx,cy,hx,hy,b)],mat,part)
