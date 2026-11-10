"""Test the Python tools with generated model and GLB fixtures."""
import copy,json,math,struct,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"Tools"))
from assets import ROOT,build,compile_source,contained
from import_glb import convert
from new_project import create
class AssetsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_root=(ROOT/"Work/UnitTests").resolve();cls.temp_root.mkdir(parents=True,exist_ok=True)
    def temp_dir(self):
        return tempfile.TemporaryDirectory(prefix="rmvf-",dir=self.temp_root)
    def setUp(self):
        self.source=json.loads((ROOT/"Templates/model.json").read_text(encoding="utf-8"))
    def test_parent_order(self):
        self.source["nodes"][0]["parent"]="arm"
        with self.assertRaises(ValueError):compile_source(self.source)
    def test_wrapped_parameter_range(self):
        self.source["parameters"][0]["max"]=100
        with self.assertRaises(ValueError):compile_source(self.source)
    def test_scale_collapse(self):
        self.source["bindings"].append(dict(node="arm",parameter="yaw",kind="scale",factor=-.1))
        with self.assertRaises(ValueError):compile_source(self.source)
    def test_degenerate_and_nonfinite(self):
        self.source["nodes"][0]["geometry"]=[dict(type="triangles",material=0,triangles=[[[0,0,0]]*3])]
        with self.assertRaises(ValueError):compile_source(self.source)
        self.source["nodes"][0]["position"]=[math.nan,0,0]
        with self.assertRaises(ValueError):compile_source(self.source)
    def test_clip_contracts(self):
        self.source["clips"][0]["tracks"][0]["keys"]=[[1,0],[0,100]]
        with self.assertRaises(ValueError):compile_source(self.source)
    def test_output_containment(self):
        with self.temp_dir() as d:
            with self.assertRaises(ValueError):contained(Path(d),"../escape")
    def test_new_mod_and_reproducible_build(self):
        with self.temp_dir() as d:
            mod=Path(d)/"MyMod";create(mod,"test.mechanism","My mechanism")
            source=mod/"Authoring/model.json"
            binary=mod/"Models/test_mechanism/geometry.bin";before=binary.read_bytes()
            build(source,mod,"test_mechanism");self.assertEqual(before,binary.read_bytes())
            self.assertTrue((mod/"Languages/ChineseSimplified/DefInjected/ThingDef/Mechanism.xml").exists())
            with self.assertRaises(ValueError):create(mod,"test.mechanism","Do not overwrite")
    def test_glb_axes_hierarchy_and_unsupported(self):
        binary=struct.pack("<9f",0,0,0,1,0,0,0,1,0)
        doc=dict(asset={"version":"2.0"},buffers=[{"byteLength":36}],
            bufferViews=[{"buffer":0,"byteLength":36}],
            accessors=[dict(bufferView=0,componentType=5126,count=3,type="VEC3")],
            meshes=[{"primitives":[{"attributes":{"POSITION":0}}]}],
            nodes=[dict(name="parent",translation=[1,2,3],rotation=[0,math.sqrt(.5),0,math.sqrt(.5)],children=[1]),
                dict(name="arm",mesh=0,translation=[0,1,0])],scenes=[{"nodes":[0]}],scene=0)
        def write(path):
            j=json.dumps(doc).encode();j+=b" "*((-len(j))%4)
            path.write_bytes(struct.pack("<III",0x46546c67,2,28+len(j)+len(binary))+struct.pack("<II",len(j),0x4e4f534a)+j+struct.pack("<II",len(binary),0x004e4942)+binary)
        with self.temp_dir() as d:
            path=Path(d)/"fixture.glb";write(path);result=convert(path)
            self.assertEqual(result["nodes"][0]["position"],[1,-3,2])
            self.assertEqual(result["nodes"][1]["parent"],"parent")
            self.assertEqual(result["nodes"][1]["position"],[0,0,1])
            self.assertAlmostEqual(result["nodes"][0]["rotation"][2],math.sqrt(.5))
            self.assertEqual(result["nodes"][1]["geometry"][0]["triangles"][0][2],[0,0,1])
            doc["nodes"][1]["scale"]=[1,2,1];write(path)
            with self.assertRaises(ValueError):convert(path)
            del doc["nodes"][1]["scale"];doc["animations"]=[{}];write(path)
            with self.assertRaises(ValueError):convert(path)
if __name__=="__main__":unittest.main()

