"""Run checks locally and record the exact files approved for stable packaging."""
import json,subprocess,sys,hashlib
from assets import ROOT,require
from package import file_hashes
from validate import validate

def check(root=ROOT):
    validate(root)
    subprocess.run([sys.executable,"-m","unittest","discover","-s","Verification","-p","test_*.py"],cwd=root,check=True)
    project=json.loads((root/"project.json").read_text(encoding="utf-8-sig"))
    version=project["version"]
    tested={}
    for game in ("1.6","1.7"):
        dll=root/"Mod"/game/"Assemblies/MechanicalVisualFramework.dll"
        sha=hashlib.sha256(dll.read_bytes()).hexdigest().upper()
        for run in sorted((root/"Work/Runs").glob(game+"-*"),reverse=True):
            if not (run/"run.json").is_file() or not (run/"results.txt").is_file():continue
            metadata=json.loads((run/"run.json").read_text(encoding="utf-8-sig"))
            results=(run/"results.txt").read_text(encoding="utf-8-sig")
            if metadata.get("AutoTest") and metadata.get("DllSHA256")==sha and "COMPLETE "+version+" / "+game+"." in results and "FAIL" not in results:
                tested[game]=sha;break
        require(game in tested,"Run a successful local "+game+" AutoTest using the current DLL before stable packaging.")
    local=root/"Local";local.mkdir(exist_ok=True)
    (local/"release-check.json").write_text(json.dumps({"version":version,"gameDlls":tested,"files":file_hashes(root)},indent=2),encoding="utf-8")
    print("PASS local tools and matching game tests. Saved Local/release-check.json.")

if __name__=="__main__":check()
