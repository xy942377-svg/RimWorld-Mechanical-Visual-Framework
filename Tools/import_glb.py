"""Import rigid GLB 2.0 nodes into RMVF source JSON.
Subset: embedded buffer, triangles, POSITION float32, uniform positive TRS,
flat baseColorFactor. No textures/skin/morph/animation; unsupported features fail explicitly.
A modelling app may export this subset; runtime players do not need that app.
"""
import argparse,json,math,struct
from pathlib import Path
from assets import compile_source,require,number,vector

def convert(path):
    data=path.read_bytes();require(len(data)>=20,"GLB header missing")
    magic,version,length=struct.unpack_from("<III",data)
    require(magic==0x46546c67 and version==2 and length==len(data),"GLB 2.0 header")
    offset=12;doc=None;binary=None
    while offset<len(data):
        require(offset+8<=len(data),"truncated chunk")
        n,kind=struct.unpack_from("<II",data,offset);offset+=8
        require(n%4==0 and offset+n<=len(data),"chunk length/alignment")
        chunk=data[offset:offset+n];offset+=n
        if kind==0x4e4f534a:
            require(doc is None,"duplicate JSON chunk");doc=json.loads(chunk)
        elif kind==0x004e4942:
            require(binary is None,"duplicate binary chunk");binary=chunk
    require(doc is not None and binary is not None,"JSON and embedded BIN required")
    require(doc.get("asset",{}).get("version")=="2.0","glTF version")
    for feature in ("skins","animations","textures","extensionsRequired"):
        require(not doc.get(feature),f"{feature} unsupported: export rigid, untextured rest pose")
    buffers=doc.get("buffers",[])
    require(len(buffers)==1 and "uri" not in buffers[0] and buffers[0]["byteLength"]<=len(binary),"one embedded buffer required")
    binary=binary[:buffers[0]["byteLength"]]
    def access(index,expected):
        a=doc["accessors"][index]
        require(not a.get("sparse") and not a.get("normalized"),"sparse/normalized accessor unsupported")
        require(a["type"]==expected,"accessor shape")
        ct=a["componentType"]
        if expected=="VEC3":require(ct==5126,"POSITION must be FLOAT");fmt="<3f"
        else:
            require(ct in (5121,5123,5125),"unsigned triangle indices required");fmt={5121:"<B",5123:"<H",5125:"<I"}[ct]
        view=doc["bufferViews"][a["bufferView"]];require(view["buffer"]==0,"buffer reference")
        size=struct.calcsize(fmt);stride=view.get("byteStride",size)
        require(stride>=size and a["count"]>0,"accessor stride/count")
        start=view.get("byteOffset",0)+a.get("byteOffset",0)
        end=start+(a["count"]-1)*stride+size
        require(0<=start<end<=view.get("byteOffset",0)+view["byteLength"]<=len(binary),"accessor range")
        return [struct.unpack_from(fmt,binary,start+i*stride) for i in range(a["count"])]
    palette=[];material_indices={}
    def material(index):
        if index in material_indices:return material_indices[index]
        m={} if index is None else doc["materials"][index]
        require(m.get("alphaMode","OPAQUE")=="OPAQUE" and not m.get("extensions"),"opaque basic material required")
        rgb=m.get("pbrMetallicRoughness",{}).get("baseColorFactor",[1,1,1,1])
        require(len(rgb)==4 and rgb[3]==1,"transparent materials unsupported")
        color=[]
        for c in rgb[:3]:
            require(0<=number(c)<=1,"base color range")
            color.append(round(255*(12.92*c if c<=.0031308 else 1.055*c**(1/2.4)-.055)))
        if color not in palette:palette.append(color)
        require(len(palette)<=15,"at most 15 flat colors; simplify palette")
        material_indices[index]=palette.index(color);return material_indices[index]
    # Right handed glTF (+Y up) -> right handed model (+Z up): (x, -z, y).
    def xyz(v):return [v[0],-v[2],v[1]]
    nodes=[];seen=set();names=set()
    def visit(idx,parent=None):
        require(idx not in seen,"cycle or node with multiple parents");seen.add(idx)
        n=doc["nodes"][idx]
        require("matrix" not in n,"matrix nodes unsupported; export decomposed TRS")
        require("skin" not in n and not n.get("weights"),"rigid nodes only")
        name=n.get("name","node_"+str(idx));require(name and name not in names,"unique nonempty node names required");names.add(name)
        position=xyz(vector(n.get("translation",[0,0,0])))
        q=vector(n.get("rotation",[0,0,0,1]),4);scale=vector(n.get("scale",[1,1,1]))
        require(scale[0]>0 and max(scale)-min(scale)<1e-6,"apply nonuniform/negative scale in modeller before export")
        out=dict(name=name,position=position,rotation=[q[0],-q[2],q[1],q[3]],scale=scale[0],layer="raised",geometry=[])
        if parent is not None:out["parent"]=parent
        if "mesh" in n:
            mesh=doc["meshes"][n["mesh"]];require(not mesh.get("weights"),"morph weights unsupported")
            for prim in mesh["primitives"]:
                require(prim.get("mode",4)==4 and not prim.get("targets") and not prim.get("extensions"),"plain triangles only")
                require(not any(k.startswith("JOINTS") or k.startswith("WEIGHTS") for k in prim["attributes"]),"skinned vertex attributes unsupported")
                verts=[xyz(v) for v in access(prim["attributes"]["POSITION"],"VEC3")]
                indices=[i[0] for i in access(prim["indices"],"SCALAR")] if "indices" in prim else list(range(len(verts)))
                require(len(indices)%3==0 and all(0<=i<len(verts) for i in indices),"triangle indices")
                triangles=[[verts[j] for j in indices[i:i+3]] for i in range(0,len(indices),3)]
                out["geometry"].append(dict(type="triangles",material=material(prim.get("material")),triangles=triangles))
        nodes.append(out)
        for child in n.get("children",[]):visit(child,name)
    scene=doc["scenes"][doc.get("scene",0)]
    for idx in scene["nodes"]:visit(idx)
    result=dict(version=1,camera=55,palette=palette,nodes=nodes,parameters=[],bindings=[],clips=[],anchors=[])
    compile_source(result);return result

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("input",type=Path);parser.add_argument("output",type=Path)
    args=parser.parse_args()
    require(not args.output.exists(),"choose a new output file; importer will not overwrite your rig")
    result=convert(args.input);args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Imported",len(result["nodes"]),"nodes. Add parameters/bindings/clips before asset build:",args.output)

