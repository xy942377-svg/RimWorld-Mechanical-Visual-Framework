"""Validate portable assets, XML, translations, source/assembly parity and size budgets."""
import hashlib,json,re,struct,sys
from pathlib import Path
import xml.etree.ElementTree as ET
from assets import ROOT,compile_source,require

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest().upper()
def validate(root=ROOT,assemblies=True):
    for mod in (root/"Mod",root/"Examples/Mechanisms"):
        for f in mod.rglob("*.xml"):ET.parse(f)
        en=mod/"Languages/English";zh=mod/"Languages/ChineseSimplified"
        def keys(d):return {str(f.relative_to(d))+":"+e.tag for f in d.rglob("*.xml") for e in ET.parse(f).getroot()}
        require(keys(en)==keys(zh),"English/Chinese key sets differ: "+str(mod))
    for name in ("Starter","Deployment","TripleTurret"):
        src=json.loads((root/"Authoring"/(name+".json")).read_text(encoding="utf-8"))
        faces=compile_source(src)
        expected=struct.pack("<ii",0x31564D52,len(faces))+b"".join(struct.pack("<ii9f",*f) for f in faces)
        require((root/"Examples/Mechanisms/Models"/name/"geometry.bin").read_bytes()==expected,"Compiled geometry differs from the source model. Rebuild: "+name)
        hashes=json.loads((root/"Verification/AssetHashes"/(name+".json")).read_text(encoding="utf-8"))
        require(hashes.pop("sourceSHA256").upper()==sha(root/"Authoring"/(name+".json")),"The recorded source hash is outdated. Rebuild model assets for: "+name)
        for rel,hash_value in hashes.items():require(sha(root/"Examples/Mechanisms"/rel)==hash_value.upper(),"The asset does not match its recorded hash. Rebuild: "+rel)
    if assemblies:
        manifest=json.loads((root/"Verification/BuildManifest.json").read_text(encoding="utf-8-sig"))
        version=json.loads((root/"project.json").read_text(encoding="utf-8-sig"))["version"]
        source_version=re.search(r'const string Version="([^"]+)"',(root/"Mod/Source/FrameworkMod.cs").read_text(encoding="utf-8"))[1]
        require(version==source_version==manifest["Build"],"Project, source and build manifest versions differ.")
        actual={p.name:sha(p) for p in (root/"Mod/Source").glob("*.cs")}
        require(actual=={s["Name"]:s["SHA256"] for s in manifest["Sources"]},"C# sources do not match Verification/BuildManifest.json. Rebuild both framework DLLs.")
        require({t["Version"] for t in manifest["Targets"]}=={"1.6","1.7"},"The release needs builds for both 1.6 and 1.7.")
        for t in manifest["Targets"]:
            require(sha(root/"Mod"/t["Version"]/"Assemblies/MechanicalVisualFramework.dll")==t["AssemblySHA256"],"A DLL does not match Verification/BuildManifest.json. Rebuild both framework DLLs.")
    # Exclude work/runtime links BEFORE traversal, never descend into a linked game installation.
    payload=[]
    for entry in root.iterdir():
        if entry.name in ("Work","Local","Releases",".git") or entry.is_symlink():continue
        if entry.is_file():payload.append(entry)
        elif entry.is_dir():payload.extend(f for f in entry.rglob("*") if f.is_file() and "__pycache__" not in f.parts)
    require(sum(f.stat().st_size for f in payload)<64*1024**2,"Release files exceed the 64 MiB size limit.")
    require(sum(f.stat().st_size for f in (root/"Mod").rglob("*") if f.is_file())<16*1024**2,"The runtime Mod folder exceeds the 16 MiB size limit.")
    print("PASS XML, bilingual keys, three authored models, DLL/source hashes, size budgets")
if __name__=="__main__":validate()

