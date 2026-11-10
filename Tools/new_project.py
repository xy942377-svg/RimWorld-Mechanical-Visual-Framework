"""Create a mod with an editable model, bilingual descriptions and an RMVF dependency."""
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
    ET.SubElement(about,"description").text=("Animation and rendering for mechanical models. Tools and examples are available on GitHub. See Guide/README.md.\n为机械模型提供动画与绘制功能。制作工具和示例可从GitHub获取，参阅Guide/README.md。" if core else "A mechanical animation model using RMVF. Select the building and open Animation controls.\n使用RMVF的机械动画模型。选中建筑后打开“动画控制”查看动作。")
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
    if not re.fullmatch(r"[a-z][a-z0-9]*(\.[a-z][a-z0-9]*)+",package):raise ValueError("Use a lowercase package ID such as yourname.yourmod. Each dot-separated segment must start with a letter and contain only letters or digits.")
    if output.exists():raise ValueError("Output already exists; choose a new folder to avoid overwriting work.")
    asset=package.replace(".","_")
    output.mkdir(parents=True)
    metadata(output,name,package)
    (output/"Authoring").mkdir()
    source=output/"Authoring"/"model.json";shutil.copyfile(ROOT/"Templates/model.json",source)
    build(source,output,asset)
    defs=ET.Element("Defs");thing(defs,asset,name,"A mechanical model animated by RMVF. Select the building and open Animation controls.",2,"spin")
    xml(output/"Defs/Mechanism.xml",defs)
    lang=ET.Element("LanguageData")
    ET.SubElement(lang,"RMVF_"+asset+".label").text=name
    ET.SubElement(lang,"RMVF_"+asset+".description").text="使用 RMVF 制作的机械模型。选中建筑后打开“动画控制”，可调节参数并播放动作。"
    xml(output/"Languages/ChineseSimplified/DefInjected/ThingDef/Mechanism.xml",lang)
    lang=ET.Element("LanguageData")
    ET.SubElement(lang,"RMVF_"+asset+".label").text=name
    ET.SubElement(lang,"RMVF_"+asset+".description").text="A mechanical model animated by RMVF. Select the building and open Animation controls to adjust parameters and play clips."
    xml(output/"Languages/English/DefInjected/ThingDef/Mechanism.xml",lang)
    command=f'python Tools/assets.py "{source.as_posix()}" "{output.as_posix()}" {asset}'
    (output/"README.md").write_text(
        "# "+name+"\n\n"
        "## English\n\n"
        "Put this folder in RimWorld's Mods directory. Enable Core, Mechanical Visual Framework, then this mod. "
        "Build the example under Misc, select it and open Animation controls.\n\n"
        "Edit Authoring/model.json to change the model. From the full framework project's root directory, run:\n\n"
        "```text\n"+command+"\n```\n\n"
        "The command regenerates model XML, geometry and the palette. Restart the game to load the updated files. "
        "If you move this mod, update the two paths in the command.\n\n"
        "Before publishing, set your author, name and description in About/About.xml. "
        "Keep the package ID, definition names and asset paths unique. Use the installed framework dependency; do not bundle its DLL.\n\n"
        "## 中文\n\n"
        "将本文件夹放入 RimWorld 的 Mods 目录，按 Core、Mechanical Visual Framework、本 MOD 的顺序启用。"
        "在“杂项”菜单建造示例，选中后打开“动画控制”。\n\n"
        "编辑 Authoring/model.json 修改模型，然后在完整框架项目的根目录执行：\n\n"
        "```text\n"+command+"\n```\n\n"
        "命令会重新生成模型 XML、几何文件和色板贴图。重启游戏后加载更新后的文件。"
        "如果移动了本 MOD，请同步修改命令中的两个路径。\n\n"
        "发布前，在 About/About.xml 中填写自己的作者、名称和说明。"
        "确保 packageId、定义名称和资源路径不与其他 MOD 重复。保留对框架的依赖，不要另行打包框架 DLL。\n",
        encoding="utf-8")
    print("Created",output)
if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output",type=Path,help="New mod directory; it must not already exist.")
    parser.add_argument("--id",required=True,help="Unique lowercase package ID, such as yourname.yourmod.")
    parser.add_argument("--name",required=True,help="Display name shown in the game mod list.")
    a=parser.parse_args();create(a.output,a.id,a.name)

