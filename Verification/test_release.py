"""Exercise local/stable packaging and rejection of stale verification records."""
import hashlib,json,sys,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"Tools"))
from assets import ROOT
from package import file_hashes,pack,stable_check

class ReleaseTest(unittest.TestCase):
    def setUp(self):
        work=ROOT/"Work/UnitTests";work.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(prefix="release-",dir=work)
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.project={"version":"0.1.0","status":"Stable"}
        for name in ("Mod/About","Examples/Mechanisms/About","Local","Work","Verification/Evidence","Workshop","Downloads"):
            (self.root/name).mkdir(parents=True,exist_ok=True)
        for name in ("Mod/About/About.xml","Examples/Mechanisms/About/About.xml","README.md"):
            (self.root/name).write_text("fixture",encoding="utf-8")
        (self.root/"Local/private.txt").write_text("private")
        (self.root/"Workshop/Workshop_Title.txt").write_text("publisher draft")
        (self.root/"Downloads/README.md").write_text("publisher downloads")
        (self.root/"Verification/Evidence/result.txt").write_text("local result")
        (self.root/"project.json").write_text(json.dumps(self.project),encoding="utf-8")
        (self.root/"Verification/AssetHashes").mkdir()
        for rel in ("BuildManifest.json","AssetHashes/Starter.json","AssetHashes/Deployment.json","AssetHashes/TripleTurret.json"):
            (self.root/"Verification"/rel).write_text("{}",encoding="utf-8")
        # Legacy records must not leak into install archives even when present in an input folder.
        for rel in ("Mod/BuildManifest.json","Examples/Mechanisms/BuildHashes.json","Mod/ReleaseManifest.json"):
            (self.root/rel).write_text("{}",encoding="utf-8")

    def seal(self):
        (self.root/"Local/release-check.json").write_text(json.dumps({"version":"0.1.0","files":file_hashes(self.root)}),encoding="utf-8")

    def test_stable_requires_unchanged_verified_files(self):
        with self.assertRaises(ValueError):stable_check(self.root,self.project)
        self.seal();stable_check(self.root,self.project)
        (self.root/"README.md").write_text("unverified change",encoding="utf-8")
        with self.assertRaises(ValueError):stable_check(self.root,self.project)

    def test_local_names_and_stable_archive_contents(self):
        with patch("package.validate"):
            pack(self.root,label="experiment01")
            self.assertTrue((self.root/"Releases/RMVF-local-experiment01-Runtime.zip").is_file())
            self.assertFalse(list((self.root/"Releases").glob("RMVF-v*")))
            self.seal();pack(self.root,stable=True)
            runtime=self.root/"Releases/RMVF-v0.1.0-Runtime.zip"
            original=runtime.read_bytes()
            with self.assertRaises(ValueError):pack(self.root,stable=True)
            self.assertEqual(original,runtime.read_bytes())
        manifests=json.loads((self.root/"Releases/RMVF-v0.1.0-FileHashes.json").read_text(encoding="utf-8"))
        for path in (self.root/"Releases").glob("RMVF-v*.zip"):
            with zipfile.ZipFile(path) as z:
                names=z.namelist()
                self.assertFalse(any("/Local/" in n or "/Work/" in n or "/Evidence/" in n or "/Workshop/" in n or "/Downloads/" in n for n in names))
                manifest=manifests[path.name]
                self.assertEqual(set(manifest),set(names))
                for rel,expected in manifest.items():
                    self.assertEqual(expected,hashlib.sha256(z.read(rel)).hexdigest())
                if path.name.endswith("DeveloperKit.zip"):
                    self.assertIn("RMVF/Verification/BuildManifest.json",names)
                    self.assertIn("RMVF/Verification/AssetHashes/Starter.json",names)
                else:
                    self.assertFalse(any(Path(n).name in {"BuildManifest.json","BuildHashes.json","ReleaseManifest.json"} for n in names))

    def test_existing_hash_report_is_preserved(self):
        releases=self.root/"Releases";releases.mkdir()
        report=releases/"RMVF-local-previous-FileHashes.json";report.write_text("existing record")
        with patch("package.validate"):
            with self.assertRaises(ValueError):pack(self.root,label="previous")
        self.assertEqual(report.read_text(),"existing record")
        self.assertFalse(list(releases.glob("*.zip")))

    def test_candidate_or_unverified_status_cannot_be_stable(self):
        self.seal()
        for project in ({"version":"0.1.0-candidate1","status":"Stable"},{"version":"0.1.0","status":"Local verification"}):
            with self.assertRaises(ValueError):stable_check(self.root,project)

if __name__=="__main__":unittest.main()
