"""Package local builds or verified stable releases. Outputs stay under Releases."""
import argparse,datetime,hashlib,json,re,zipfile
from pathlib import Path
from assets import ROOT,require
from validate import validate

ROOT_FILES={"README.md","README.en.md","LICENSE","NOTICE.md","CHANGELOG.md","AGENTS.md","project.json","ToolPaths.example.json","Start.cmd",".gitignore",".gitattributes"}
ROOT_DIRS={"Mod","Examples","Authoring","Templates","Tools","docs","Verification",".github","Modeling"}
BUILD_RECORDS={"BuildManifest.json","AssetHashes/Starter.json","AssetHashes/Deployment.json","AssetHashes/TripleTurret.json"}
INSTALL_EXCLUDES={"BuildManifest.json","BuildHashes.json","ReleaseManifest.json"}

def portable_files(root):
    for folder in sorted(ROOT_DIRS):
        base=root/folder
        if not base.exists():continue
        for f in sorted(base.rglob("*")):
            if not f.is_file() or f.is_symlink() or "__pycache__" in f.parts or f.suffix in (".pyc",".pdb"):continue
            rel=f.relative_to(base)
            # Tests are reusable tools; run logs, screenshots and editorial notes stay local.
            if folder=="Verification":
                reusable_test=len(rel.parts)==1 and f.suffix in (".py",".cs")
                if not reusable_test and rel.as_posix() not in BUILD_RECORDS:continue
            yield f
    for name in sorted(ROOT_FILES):
        if (root/name).is_file():yield root/name

def file_hashes(root):
    return {f.relative_to(root).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in portable_files(root)}

def stable_check(root,project):
    require(re.fullmatch(r"\d+\.\d+\.\d+",project["version"]) is not None,"Stable versions must use major.minor.patch, for example 0.1.0.")
    require(project.get("status")=="Stable","Complete local verification before marking the project Stable.")
    receipt=root/"Local/release-check.json"
    require(receipt.exists(),"Run python Tools/check_release.py after completing both local game tests.")
    check=json.loads(receipt.read_text(encoding="utf-8"))
    require(check.get("version")==project["version"],"The local verification record belongs to another version.")
    require(check.get("files")==file_hashes(root),"Files changed after local verification. Run Tools/check_release.py again.")

def pack(root=ROOT,stable=False,label=None):
    validate(root)
    project=json.loads((root/"project.json").read_text(encoding="utf-8-sig"))
    if stable:
        require(label is None,"--label is only for local builds.")
        stable_check(root,project)
        version="v"+project["version"]
    else:
        label=label or datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        require(re.fullmatch(r"[A-Za-z0-9_-]+",label) is not None,"A local label may contain letters, digits, underscores and hyphens.")
        version="local-"+label
    releases=root/"Releases";releases.mkdir(exist_ok=True)
    files=list(portable_files(root))
    # Development records are useful in the source kit, but are never installed with a mod.
    install=[f for f in files if f.name not in INSTALL_EXCLUDES]
    plans=[("RMVF-"+version+"-DeveloperKit.zip",files,"RMVF"),
           ("RMVF-"+version+"-Runtime.zip",[f for f in install if f.relative_to(root).parts[0]=="Mod"],"MechanicalVisualFramework"),
           ("RMVF-"+version+"-Examples.zip",[f for f in install if f.relative_to(root).parts[:2]==("Examples","Mechanisms")],"RMVFExamples")]
    report=releases/("SHA256-"+version+".txt")
    details=releases/("RMVF-"+version+"-FileHashes.json")
    require(not report.exists() and not details.exists() and all(not (releases/name).exists() for name,_,_ in plans),"These release files already exist. Use a new local label or the next stable version.")
    entries=[];manifests={}
    for name,selected,prefix in plans:
        dest=releases/name
        with zipfile.ZipFile(dest,"x",zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            manifest={}
            for f in selected:
                rel=f.relative_to(root)
                if prefix=="MechanicalVisualFramework":rel=Path(*rel.parts[1:])
                elif prefix=="RMVFExamples":rel=Path(*rel.parts[2:])
                archive_path=prefix+"/"+rel.as_posix()
                z.write(f,archive_path)
                manifest[archive_path]=hashlib.sha256(f.read_bytes()).hexdigest()
            manifests[name]=manifest
        require(dest.stat().st_size<64*1024**2,"The archive exceeds the 64 MiB size limit.")
        with zipfile.ZipFile(dest) as z:require(z.testzip() is None,"Archive integrity verification failed.")
        entries.append(hashlib.sha256(dest.read_bytes()).hexdigest()+"  "+name)
        print(name,dest.stat().st_size,"bytes")
    # One sidecar covers all three archives; no checksum table is added to an install folder.
    details.write_text(json.dumps(manifests,indent=2),encoding="utf-8")
    entries.append(hashlib.sha256(details.read_bytes()).hexdigest()+"  "+details.name)
    report.write_text("\n".join(entries)+"\n",encoding="ascii")

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stable",action="store_true",help="Require a current local verification record and use the public version.")
    parser.add_argument("--label",help="Optional local build name; default is a timestamp.")
    args=parser.parse_args();pack(stable=args.stable,label=args.label)

