"""Import rigid GLB 2.0 nodes into RMVF source JSON.
Subset: embedded buffer, triangles, POSITION float32, uniform positive TRS,
flat baseColorFactor. No textures/skin/morph/animation; unsupported features fail explicitly.
A modelling app may export this subset; runtime players do not need that app.
"""
import argparse,json,math,struct
from pathlib import Path
from assets import compile_source,require,number,vector

def convert(path):
    data=path.read_bytes();require(len(data)>=20,"The file is too short to contain a GLB header and chunk.")
    magic,version,length=struct.unpack_from("<III",data)
    require(magic==0x46546c67 and version==2 and length==len(data),"Expected a GLB 2.0 header whose declared length matches the file.")
    offset=12;doc=None;binary=None
    while offset<len(data):
        require(offset+8<=len(data),"The file ends before the next GLB chunk header is complete.")
        n,kind=struct.unpack_from("<II",data,offset);offset+=8
        require(n%4==0 and offset+n<=len(data),"A GLB chunk must fit inside the file and have a length divisible by four.")
        chunk=data[offset:offset+n];offset+=n
        if kind==0x4e4f534a:
            require(doc is None,"The GLB file contains more than one JSON chunk.");doc=json.loads(chunk)
        elif kind==0x004e4942:
            require(binary is None,"The GLB file contains more than one binary chunk.");binary=chunk
    require(doc is not None and binary is not None,"The GLB file must contain both a JSON chunk and an embedded binary chunk.")
    require(doc.get("asset",{}).get("version")=="2.0","The glTF asset must declare version 2.0.")
    for feature in ("skins","animations","textures","extensionsRequired"):
        require(not doc.get(feature),f"Unsupported GLB feature: {feature}. Export rigid parts without textures, animation or required extensions.")
    buffers=doc.get("buffers",[])
    require(len(buffers)==1 and "uri" not in buffers[0] and buffers[0]["byteLength"]<=len(binary),"Export exactly one embedded buffer, with no external URI and a length that fits the binary chunk.")
    binary=binary[:buffers[0]["byteLength"]]
    def access(index,expected):
        a=doc["accessors"][index]
        require(not a.get("sparse") and not a.get("normalized"),"Sparse and normalized accessors are not supported by this importer.")
        require(a["type"]==expected,"The accessor type does not match the expected vector or scalar layout.")
        ct=a["componentType"]
        if expected=="VEC3":require(ct==5126,"POSITION coordinates must use FLOAT (componentType 5126).");fmt="<3f"
        else:
            require(ct in (5121,5123,5125),"Triangle indices must use unsigned byte, unsigned short or unsigned int values.");fmt={5121:"<B",5123:"<H",5125:"<I"}[ct]
        view=doc["bufferViews"][a["bufferView"]];require(view["buffer"]==0,"The buffer view must reference the embedded buffer at index 0.")
        size=struct.calcsize(fmt);stride=view.get("byteStride",size)
        require(stride>=size and a["count"]>0,"An accessor needs a positive count and a stride large enough to hold each element.")
        start=view.get("byteOffset",0)+a.get("byteOffset",0)
        end=start+(a["count"]-1)*stride+size
        require(0<=start<end<=view.get("byteOffset",0)+view["byteLength"]<=len(binary),"Accessor data extends outside its buffer view or the embedded buffer.")
        return [struct.unpack_from(fmt,binary,start+i*stride) for i in range(a["count"])]
    palette=[];material_indices={}
    def material(index):
        if index in material_indices:return material_indices[index]
        m={} if index is None else doc["materials"][index]
        require(m.get("alphaMode","OPAQUE")=="OPAQUE" and not m.get("extensions"),"Use opaque materials without material extensions.")
        rgb=m.get("pbrMetallicRoughness",{}).get("baseColorFactor",[1,1,1,1])
        require(len(rgb)==4 and rgb[3]==1,"baseColorFactor must have four components with alpha equal to 1.")
        color=[]
        for c in rgb[:3]:
            require(0<=number(c)<=1,"Each base color component must be between 0 and 1.")
            color.append(round(255*(12.92*c if c<=.0031308 else 1.055*c**(1/2.4)-.055)))
        if color not in palette:palette.append(color)
        require(len(palette)<=15,"The model uses more than 15 colors. Reduce the material colors before exporting.")
        material_indices[index]=palette.index(color);return material_indices[index]
    # Right handed glTF (+Y up) -> right handed model (+Z up): (x, -z, y).
    def xyz(v):return [v[0],-v[2],v[1]]
    nodes=[];seen=set();names=set()
    def visit(idx,parent=None):
        require(idx not in seen,"The scene hierarchy contains a cycle or a node with multiple parents.");seen.add(idx)
        n=doc["nodes"][idx]
        require("matrix" not in n,"Matrix node transforms are unsupported. Export separate translation, rotation and scale values.")
        require("skin" not in n and not n.get("weights"),"Nodes must use rigid geometry without skins or morph weights.")
        name=n.get("name","node_"+str(idx));require(name and name not in names,"Each imported node needs a nonempty, unique name.");names.add(name)
        position=xyz(vector(n.get("translation",[0,0,0])))
        q=vector(n.get("rotation",[0,0,0,1]),4);scale=vector(n.get("scale",[1,1,1]))
        require(scale[0]>0 and max(scale)-min(scale)<1e-6,"Node scale must be positive and uniform. Apply nonuniform or negative scale to the geometry before export.")
        out=dict(name=name,position=position,rotation=[q[0],-q[2],q[1],q[3]],scale=scale[0],layer="raised",geometry=[])
        if parent is not None:out["parent"]=parent
        if "mesh" in n:
            mesh=doc["meshes"][n["mesh"]];require(not mesh.get("weights"),"Meshes with morph weights are not supported.")
            for prim in mesh["primitives"]:
                require(prim.get("mode",4)==4 and not prim.get("targets") and not prim.get("extensions"),"Export triangle primitives without morph targets or primitive extensions.")
                require(not any(k.startswith("JOINTS") or k.startswith("WEIGHTS") for k in prim["attributes"]),"Skinned vertex attributes are unsupported. Export rigid parts without JOINTS or WEIGHTS attributes.")
                verts=[xyz(v) for v in access(prim["attributes"]["POSITION"],"VEC3")]
                indices=[i[0] for i in access(prim["indices"],"SCALAR")] if "indices" in prim else list(range(len(verts)))
                require(len(indices)%3==0 and all(0<=i<len(verts) for i in indices),"Triangle indices must come in groups of three and reference existing vertices.")
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
    require(not args.output.exists(),"The output file already exists. Choose a new output filename.")
    result=convert(args.input);args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Imported",len(result["nodes"]),"nodes. Add parameters/bindings/clips before asset build:",args.output)

