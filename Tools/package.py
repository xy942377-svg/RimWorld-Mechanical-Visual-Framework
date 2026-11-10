"""Whitelist release outputs. No player saves, game DLLs, local paths/config, Work or .git."""
import hashlib,json,zipfile
from pathlib import Path
from assets import ROOT,require
from validate import validate

ROOT_FILES={"README.md","README.en.md","LICENSE","NOTICE.md","CHANGELOG.md","AGENTS.md","project.json","ToolPaths.example.json","Start.cmd",".gitignore"}
ROOT_DIRS={"Mod","Examples","Authoring","Templates","Tools","docs","Verification",".github"}
def portable_files(root):
    for folder in sorted(ROOT_DIRS):
        base=root/folder
        if not base.exists():continue
        for f in sorted(base.rglob("*")):
            if f.is_file() and "__pycache__" not in f.parts and f.suffix not in (".pyc",".pdb") and not f.is_symlink():yield f
    for name in sorted(ROOT_FILES):
        if (root/name).is_file():yield root/name
def pack(root=ROOT):
    validate(root)
    project=json.loads((root/"project.json").read_text(encoding="utf-8-sig"));version=project["version"]
    releases=root/"Releases";releases.mkdir(exist_ok=True)
    plans=[("RMVF-"+version+"-DeveloperKit.zip",list(portable_files(root)),"RMVF"),
           ("RMVF-"+version+"-Workshop.zip",[f for f in portable_files(root) if f.relative_to(root).parts[0]=="Mod"],"MechanicalVisualFramework"),
           ("RMVF-"+version+"-Examples.zip",[f for f in portable_files(root) if f.relative_to(root).parts[:2]==("Examples","Mechanisms")],"RMVFExamples")]
    entries=[]
    for name,files,prefix in plans:
        dest=releases/name;require(not dest.exists(),"immutable release already exists: "+str(dest))
        with zipfile.ZipFile(dest,"x",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for f in files:
                rel=f.relative_to(root)
                if prefix=="MechanicalVisualFramework":rel=Path(*rel.parts[1:])
                elif prefix=="RMVFExamples":rel=Path(*rel.parts[2:])
                z.write(f,prefix+"/"+rel.as_posix())
            z.writestr(prefix+"/ReleaseManifest.json",json.dumps({str(f.relative_to(root)).replace("\\","/"):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},indent=2))
        require(dest.stat().st_size<64*1024**2,"archive size budget")
        with zipfile.ZipFile(dest) as z:require(z.testzip() is None,"archive CRC")
        entries.append(hashlib.sha256(dest.read_bytes()).hexdigest()+"  "+name)
        print(name,dest.stat().st_size,"bytes")
    report=releases/("SHA256-"+version+".txt");require(not report.exists(),"immutable checksum report exists")
    report.write_text("\n".join(entries)+"\n",encoding="ascii")
if __name__=="__main__":pack()

