using System;
using System.IO;
using UnityEngine;
using Verse;
using RimWorld;
namespace MechanicalVisualFramework
{
    public sealed class FrameworkMod : Mod
    {
        public const string Version="0.1.0-candidate1";
        // Filled only after an actual repository exists. Never send users to a guessed account or URL.
        public const string Repository="https://github.com/xy942377-svg/RimWorld-Mechanical-Visual-Framework";
        public FrameworkMod(ModContentPack content):base(content){}
        public override string SettingsCategory(){return "RMVF_Title".Translate();}
        public override void DoSettingsWindowContents(Rect rect)
        {
            var list=new Listing_Standard();list.Begin(rect);
            list.Label("RMVF_About".Translate(Version));list.Gap(12);
            if(list.ButtonText("RMVF_LocalGuide".Translate()))Application.OpenURL(Path.Combine(Content.RootDir,"Guide","README.md"));
            if(!string.IsNullOrEmpty(Repository)&&list.ButtonText("RMVF_Repository".Translate()))Application.OpenURL(Repository);
            if(list.ButtonText("RMVF_CopyVersion".Translate()))GUIUtility.systemCopyBuffer="RMVF "+Version+" / RimWorld "+VersionControl.CurrentVersionString;
            list.Label("RMVF_ExamplesNote".Translate());list.End();
        }
    }
}

