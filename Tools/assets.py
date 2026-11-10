"""RMVF authoring compiler; Python 3.10+, standard library only.
Geometry stays in MODEL axes X right, Y back, Z up. Units are map cells.
Each node's mesh is LOCAL to its pivot, not a separate picture.
"""
import argparse, hashlib, json, math, struct, sys, zlib
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PALETTE = [[147,157,164],[177,187,192],[92,103,112],[57,65,72],
                   [32,37,42],[112,121,129],[194,197,191],[19,23,27],
                   [185,141,65],[0,200,232],[70,110,140],[190,80,60],
                   [100,160,110],[190,190,190],[90,90,90],[19,23,27]]

def require(ok, message):
    if not ok: raise ValueError(message)

def number(v):
    require(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v), "Expected a finite number, not a boolean, NaN or infinity.")
    return float(v)

def vector(v, n=3):
    require(isinstance(v,list) and len(v)==n, f"Expected a list of {n} numeric components.")
    return [number(x) for x in v]

def contained(root, relative):
    require(relative and not Path(relative).is_absolute(), "The output path must be nonempty and relative to the destination directory.")
    p=(root/relative).resolve()
    require(p.is_relative_to(root.resolve()) and p!=root.resolve(), "The output path must stay inside the destination directory.")
    return p

def box(center, size):
    x,y,z=center; a,b,c=[v/2 for v in size]
    vertices=[(x+dx*a,y+dy*b,z+dz*c) for dz in (-1,1) for dy in (-1,1) for dx in (-1,1)]
    # Outward winding matters for illumination and visible-edge tests (surfaces are double sided).
    quads=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)]
    return [[vertices[i] for i in tri] for a,b,c,d in quads for tri in ((a,b,c),(a,c,d))]

def cylinder(center, radius, length, segments, axis):
    require(axis in (0,1,2) and 3<=segments<=64 and radius>0 and length>0,"A cylinder needs axis 0, 1 or 2, 3 to 64 segments, and positive radius and length.")
    u=(axis+1)%3;v=(axis+2)%3
    rings=[]
    for side in (-1,1):
        ring=[]
        for i in range(segments):
            q=list(center);q[axis]+=side*length/2
            q[u]+=radius*math.cos(i*math.tau/segments);q[v]+=radius*math.sin(i*math.tau/segments);ring.append(q)
        rings.append(ring)
    faces=[]
    for i in range(segments):
        j=(i+1)%segments
        faces += [[rings[0][i],rings[0][j],rings[1][j]],[rings[0][i],rings[1][j],rings[1][i]]]
        for side,order in ((0,(j,i)),(1,(i,j))):
            q=list(center);q[axis]+=(-1 if side==0 else 1)*length/2
            faces.append([q,rings[side][order[0]],rings[side][order[1]]])
    return faces

def compile_source(src):
    require(src.get("version")==1,"The source model must declare version 1.")
    require(15<=number(src.get("camera",55))<=85,"Camera elevation must be between 15 and 85 degrees.")
    nodes=src.get("nodes",[]);require(1<=len(nodes)<=256,"The model must contain 1 to 256 nodes.")
    names={};faces=[]
    for n in nodes:
        name=n.get("name");require(isinstance(name,str) and name and name not in names,"Each node needs a nonempty, unique name.")
        require(not n.get("parent") or n["parent"] in names,"A parent node must exist and appear before its child in the node list.")
        idx=len(names);names[name]=idx
        vector(n.get("position",[0,0,0]));q=vector(n.get("rotation",[0,0,0,1]),4)
        require(abs(sum(x*x for x in q)-1)<.002,"Rotation must be a normalized quaternion [x, y, z, w].")
        require(0<number(n.get("scale",1))<=100,"Node scale must be greater than 0 and at most 100.")
        require(n.get("layer","raised") in ("raised","foundation"),"Node layer must be raised or foundation.")
        for primitive in n.get("geometry",[]):
            mat=primitive.get("material",0);require(type(mat)==int and 0<=mat<15,"Material index must be an integer from 0 to 14; index 15 is reserved for outlines.")
            kind=primitive.get("type")
            if kind=="box":
                center=vector(primitive.get("center",[0,0,0]));size=vector(primitive["size"]);require(all(x>0 for x in size),"All three box dimensions must be greater than zero.")
                triangles=box(center,size)
            elif kind=="cylinder":
                triangles=cylinder(vector(primitive.get("center",[0,0,0])),number(primitive["radius"]),number(primitive["length"]),primitive.get("segments",16),primitive.get("axis",2))
            elif kind=="triangles": triangles=primitive["triangles"]
            else: raise ValueError("Geometry type must be box, cylinder or triangles.")
            for tri in triangles:
                require(len(tri)==3,"Each triangle must contain exactly three vertices.")
                a,b,c=[vector(list(v)) for v in tri]
                ab=[b[i]-a[i] for i in range(3)];ac=[c[i]-a[i] for i in range(3)]
                cross=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]]
                require(sum(x*x for x in cross)>1e-16,"A triangle has zero or near-zero area; remove it or correct its vertices.")
                faces.append((idx,mat,*a,*b,*c))
    require(0<len(faces)<=50000,"The model must contain 1 to 50,000 valid triangles.")
    params={}
    for p in src.get("parameters",[]):
        name=p.get("name");require(isinstance(name,str) and name and name not in params,"Each parameter needs a nonempty, unique name.")
        low=number(p.get("min",0));high=number(p.get("max",1));default=number(p.get("default",0))
        require(low<high and low<=default<=high and number(p.get("speed",0))>=0,"A parameter needs min < max, a default within that range, and speed >= 0.")
        require(not p.get("wrap") or abs(high-low-360)<.001,"A wrapped parameter must have a range spanning exactly 360 degrees.")
        params[name]=p
    require(len(params)<=256,"A model can contain at most 256 parameters.")
    for b in src.get("bindings",[]):
        require(b["node"] in names and b["parameter"] in params,"A binding must name an existing node and parameter.")
        require(b["kind"] in ("rotation","translation","scale"),"Binding kind must be rotation, translation or scale.")
        axis=vector(b.get("axis",[0,0,1]));require(sum(v*v for v in axis)>1e-10,"A binding axis must be a nonzero vector.")
        factor=number(b.get("factor",1));p=params[b["parameter"]]
        if b["kind"]=="scale": require(1+min(p.get("min",0)*factor,p.get("max",1)*factor)>.001,"The scale multiplier must stay above 0.001 across the full parameter range.")
    clips=set()
    for c in src.get("clips",[]):
        require(c["name"] and c["name"] not in clips,"Each clip needs a nonempty, unique name.");clips.add(c["name"])
        duration=number(c["duration"]);require(duration>0 and c["tracks"],"A clip needs a positive duration and at least one track.")
        seen=set()
        for t in c["tracks"]:
            name=t["parameter"];require(name in params and name not in seen,"Each track must name an existing parameter, used only once within that clip.");seen.add(name)
            p=params[name];last=-1;require(t["keys"],"Each track needs at least one keyframe.")
            for k in t["keys"]:
                time,value=vector(k,2);require(last<time<=duration and time>=0,"Keyframe times must increase strictly and stay between 0 and the clip duration.")
                require(p.get("min",0)<=value<=p.get("max",1),"A keyframe value is outside its parameter range.");last=time
    anchors=set()
    for a in src.get("anchors",[]):
        require(a["name"] and a["name"] not in anchors and a["node"] in names,"Each anchor needs a unique name and must reference an existing node.");anchors.add(a["name"])
        vector(a.get("position",[0,0,0]));d=vector(a.get("direction",[0,-1,0]));require(sum(v*v for v in d)>1e-10,"An anchor direction must be a nonzero vector.")
    palette=src.get("palette",DEFAULT_PALETTE)
    require(1<=len(palette)<=16,"The palette must contain 1 to 16 colors.")
    for rgb in palette: require(len(rgb)==3 and all(type(x)==int and 0<=x<=255 for x in rgb),"Each palette color must contain three integers from 0 to 255.")
    return faces

def png_palette(colors):
    colors=(colors+DEFAULT_PALETTE[len(colors):])[:16]
    colors[15]=[19,23,27]
    # PNG scanlines start at top; Unity UV y=0 is bottom, hence reverse material rows.
    raw=b""
    for rgb in reversed(colors):
        raw+=b"\0"+b"".join(bytes(round(c*(.48+.52*i/31)) for c in rgb)+b"\xff" for i in range(32))
    def chunk(kind,data): return struct.pack(">I",len(data))+kind+data+struct.pack(">I",zlib.crc32(kind+data)&0xffffffff)
    return b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",32,16,8,6,0,0,0))+chunk(b"IDAT",zlib.compress(raw,9))+chunk(b"IEND",b"")

def attrs(obj, keys):
    def value(v):
        if isinstance(v,list): return " ".join(format(float(x),".9g") for x in v)
        if isinstance(v,bool): return str(v).lower()
        return str(v)
    return {k:value(obj[k]) for k in keys if k in obj}

def build(source, mod, asset_name):
    src=json.loads(source.read_text(encoding="utf-8-sig"));faces=compile_source(src)
    require(asset_name.replace("_","").isalnum() and asset_name.isascii(),"The asset name must use ASCII letters, digits or underscores and contain at least one letter or digit.")
    directory=contained(mod,"Models/"+asset_name);directory.mkdir(parents=True,exist_ok=True)
    top=ET.Element("mechanicalModel",version="1",camera=str(src.get("camera",55)),geometry="geometry.bin",palette="RMVF/"+asset_name+"/Palette")
    for group,tag,keys in (
        ("nodes","node",["name","parent","position","rotation","scale","layer"]),
        ("parameters","parameter",["name","min","max","default","speed","wrap"]),
        ("bindings","binding",["node","parameter","kind","axis","factor"]),
        ("anchors","anchor",["name","node","position","direction"])):
        parent=ET.SubElement(top,group)
        for obj in src.get(group,[]):
            if group=="nodes": obj=dict(obj,layer=obj.get("layer","raised"))
            ET.SubElement(parent,tag,attrs(obj,keys))
    clips=ET.SubElement(top,"clips")
    for c in src.get("clips",[]):
        clip=ET.SubElement(clips,"clip",attrs(c,["name","duration","loop"]))
        for t in c["tracks"]:
            track=ET.SubElement(clip,"track",parameter=t["parameter"])
            for time,value in t["keys"]: ET.SubElement(track,"key",time=str(time),value=str(value))
    ET.indent(top)
    ET.ElementTree(top).write(directory/"model.xml",encoding="utf-8",xml_declaration=True)
    with (directory/"geometry.bin").open("wb") as f:
        f.write(struct.pack("<ii",0x31564D52,len(faces)))
        for face in faces:f.write(struct.pack("<ii9f",*face))
    texture=contained(mod,"Textures/RMVF/"+asset_name+"/Palette.png");texture.parent.mkdir(parents=True,exist_ok=True)
    texture.write_bytes(png_palette(src.get("palette",DEFAULT_PALETTE)))
    hashes={str(f.relative_to(mod)).replace("\\","/"):hashlib.sha256(f.read_bytes()).hexdigest() for f in (directory/"model.xml",directory/"geometry.bin",texture)}
    hashes["sourceSHA256"]=hashlib.sha256(source.read_bytes()).hexdigest()
    (directory/"BuildHashes.json").write_text(json.dumps(hashes,indent=2),encoding="utf-8")
    print(f"{asset_name}: {len(src['nodes'])} nodes, {len(faces)} triangles -> {mod}")
    return len(faces)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source",type=Path);parser.add_argument("mod",type=Path);parser.add_argument("name")
    a=parser.parse_args();build(a.source,a.mod,a.name)
if __name__=="__main__":
    try:main()
    except (ValueError,KeyError,OSError) as e: print("ERROR:",e,file=sys.stderr);sys.exit(1)

