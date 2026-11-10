"""Create a standalone consumer mod; no C# compilation is needed for parameter/clip-only visuals."""
import argparse,json,re,shutil
from pathlib import Path
import xml.etree.ElementTree as ET
from assets import ROOT,build

def xml(path,root):
    path.parent.mkdir(parents=True,exist_ok=True);ET.indent(root)
    ET.ElementTree(root).write(path,encoding="utf-8",xml_declaration=True)

def metadata(mod,name,package,core=False):
    about=ET.Element("ModMetaData")
    for tag,val in [("name",name),("author","Grey·Oviin/OpenAI Assisted"),("packageId",package)]:
        ET.SubElement(about,tag).text=val
    versions=ET.SubElement(about,"supportedVersions")
    for v in ("1.6","1.7"):ET.SubElement(versions,"li").text=v
    if not core:
        dep=ET.SubElement(ET.SubElement(about,"modDependencies"),"li")
        ET.SubElement(dep,"packageId").text="greyoviin.mechanicalvisualframework"
        ET.SubElement(dep,"displayName").text="RimWorld Mechanical Visual Framework"
        ET.SubElement(dep,"downloadUrl").text="https://github.com/xy942377-svg/RimWorld-Mechanical-Visual-Framework"
        ET.SubElement(ET.SubElement(about,"loadAfter"),"li").text="greyoviin.mechanicalvisualframework"
    ET.SubElement(about,"description").text=("Rigid mechanical visuals, authoring tools and examples. See Guide/README.md.\n机械动态视觉框架；部件、转轴、动画与制作工具。参阅 Guide/README.md。" if core else "Optional mechanical visual examples. Not balanced combat buildings.\n可选机械视觉示例，不是正式战斗建筑。")
    xml(mod/"About/About.xml",about)

def thing(defs,name,label,description,size,autoplay=""):
    model=ET.SubElement(defs,"MechanicalVisualFramework.MechanicalModelDef")
    ET.SubElement(model,"defName").text="RMVF_"+name+"Model"
    ET.SubElement(model,"assetPath").text="Models/"+name+"/model.xml"
    t=ET.SubElement(defs,"ThingDef",ParentName="BuildingBase")
    fields={"defName":"RMVF_"+name,"label":label,"description":description,
        "thingClass":"MechanicalVisualFramework.Building_MechanicalDisplay","category":"Building",
        "tickerType":"Normal","drawerType":"RealtimeOnly","rotatable":"false","altitudeLayer":"Building",
        "passability":"Impassable","designationCategory":"Misc","fillPercent":"0.5"}
    for tag,val in fields.items():ET.SubElement(t,tag).text=val
    g=ET.SubElement(t,"graphicData")
    for tag,val in [("texPath","RMVF/Fallback"),("graphicClass","Graphic_Single"),("drawSize",f"({size}, {size})")]:ET.SubElement(g,tag).text=val
    ET.SubElement(t,"size").text=f"({size}, {size})"
    stats=ET.SubElement(t,"statBases")
    for tag,val in [("MaxHitPoints","300"),("WorkToBuild","100"),("Flammability","0")]:ET.SubElement(stats,tag).text=val
    ET.SubElement(ET.SubElement(t,"costList"),"Steel").text="10"
    ET.SubElement(ET.SubElement(t,"building"),"ai_chillDestination").text="false"
    comp=ET.SubElement(ET.SubElement(t,"comps"),"li",Class="MechanicalVisualFramework.CompProperties_MechanicalVisual")
    ET.SubElement(comp,"model").text="RMVF_"+name+"Model"
    if autoplay:ET.SubElement(comp,"autoplay").text=autoplay

def create(output,package,name):
    if not re.fullmatch(r"[a-z][a-z0-9]*(\.[a-z][a-z0-9]*)+",package):raise ValueError("package id example: yourname.yourmod (lowercase)")
    if output.exists():raise ValueError("Output already exists; choose a new folder to avoid overwriting work.")
    asset=package.replace(".","_")
    output.mkdir(parents=True)
    metadata(output,name,package)
    (output/"Authoring").mkdir()
    source=output/"Authoring"/"model.json";shutil.copyfile(ROOT/"Templates/model.json",source)
    build(source,output,asset)
    defs=ET.Element("Defs");thing(defs,asset,name,"A mechanical visual made with RMVF.",2,"spin")
    xml(output/"Defs/Mechanism.xml",defs)
    lang=ET.Element("LanguageData")
    ET.SubElement(lang,"RMVF_"+asset+".label").text=name
    ET.SubElement(lang,"RMVF_"+asset+".description").text="机械动态视觉示例。选中后打开动画控制，可修改参数并播放动画。"
    xml(output/"Languages/ChineseSimplified/DefInjected/ThingDef/Mechanism.xml",lang)
    lang=ET.Element("LanguageData")
    ET.SubElement(lang,"RMVF_"+asset+".label").text=name
    ET.SubElement(lang,"RMVF_"+asset+".description").text="A mechanical visual. Select it and open animation controls to adjust parameters and play clips."
    xml(output/"Languages/English/DefInjected/ThingDef/Mechanism.xml",lang)
    (output/"README.md").write_text("# "+name+"\n\nEnable RimWorld Core, RMVF, then this mod. Build the object under Misc.\nEdit Authoring/model.json, then run the framework tool:\n\n    python Tools/assets.py <this-mod>/Authoring/model.json <this-mod> "+asset+"\n\nKeep packageId and asset/Def names unique. No restart-free asset reload is provided.\n",encoding="utf-8")
    print("Created",output)
if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output",type=Path);parser.add_argument("--id",required=True);parser.add_argument("--name",required=True)
    a=parser.parse_args();create(a.output,a.id,a.name)

