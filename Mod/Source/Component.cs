using System;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace MechanicalVisualFramework
{
    public sealed class CompProperties_MechanicalVisual : CompProperties
    {
        public MechanicalModelDef model;
        public string autoplay;
        public bool showControls=true;
        public CompProperties_MechanicalVisual(){compClass=typeof(CompMechanicalVisual);}
    }
    // This optional host suppresses vanilla's static graphic. A custom building may instead call
    // its own Comps_PostDraw, but must do so once only. Models contain the foundation as well.
    public class Building_MechanicalDisplay : Building
    {
        protected override void DrawAt(Vector3 drawLoc,bool flip=false)
        {
            var c=GetComp<CompMechanicalVisual>();
            if(c==null||!c.Ready){base.DrawAt(drawLoc,flip);return;}
            Comps_PostDraw();
        }
    }
    public sealed class CompMechanicalVisual : ThingComp
    {
        VisualInstance visual;
        bool failed,restored;
        List<string> names,clipNames;
        List<float> values,targets,times;
        List<bool> paused;
        CompProperties_MechanicalVisual Props {get{return (CompProperties_MechanicalVisual)props;}}
        public Animator Animation {get{return Ensure()?visual.Animation:null;}}
        public bool Ready {get{return Ensure();}}
        public VisualInstance Visual {get{return Ensure()?visual:null;}}
        bool Ensure()
        {
            if(failed)return false;if(visual!=null)return true;
            try
            {
                var asset=Assets.Get(Props.model);if(asset==null){failed=true;return false;}
                visual=new VisualInstance(asset);
                if(names!=null)Restore();
                else if(!restored&&!string.IsNullOrEmpty(Props.autoplay))visual.Animation.Play(Props.autoplay);
                restored=true;return true;
            }
            catch(Exception e){Disable(e);return false;}
        }
        void Disable(Exception e)
        {
            if(!failed)Log.Error("[RMVF] "+parent.def.defName+" visual disabled: "+e);
            failed=true;if(visual!=null)visual.Dispose();visual=null;
        }
        public override void PostSpawnSetup(bool respawningAfterLoad){base.PostSpawnSetup(respawningAfterLoad);Ensure();}
        public override void CompTick()
        {
            if(!Ensure())return;try{visual.Animation.Tick();}catch(Exception e){Disable(e);}
        }
        public override void PostDraw()
        {
            if(!Ensure())return;try{visual.Draw(parent.DrawPos);}catch(Exception e){Disable(e);}
        }
        public override void PostDeSpawn(Map map,DestroyMode mode=DestroyMode.Vanish)
        {
            // Map transfer/temporary despawn must not reset parameters or leak native meshes.
            Capture();if(visual!=null)visual.Dispose();visual=null;base.PostDeSpawn(map,mode);
        }
        void Capture()
        {
            if(visual==null)return;var a=visual.Animation;
            names=new List<string>();values=new List<float>();targets=new List<float>();
            foreach(var p in a.Asset.Parameters)names.Add(p.Name);
            values.AddRange(a.Values);targets.AddRange(a.Targets);
            clipNames=new List<string>();times=new List<float>();paused=new List<bool>();
            foreach(var c in a.Playing){clipNames.Add(a.Asset.Clips[c.Clip].Name);times.Add(c.Time);paused.Add(c.Paused);}
        }
        void Restore()
        {
            // Save names, not array indices: adding/reordering nodes/parameters does not misbind old saves.
            var a=visual.Animation;
            for(int i=0;i<names.Count;i++)
            {
                int id=a.Asset.FindParameter(names[i]);
                if(id<0||values==null||targets==null||i>=values.Count||i>=targets.Count||!Assets.Finite(values[i])||!Assets.Finite(targets[i]))continue;
                a.SetTarget(names[i],values[i],true);a.SetTarget(names[i],targets[i]);
            }
            if(clipNames!=null)for(int i=0;i<clipNames.Count;i++)
            {
                int id=a.Asset.FindClip(clipNames[i]);
                if(id<0||times==null||i>=times.Count||!Assets.Finite(times[i]))continue;
                a.Play(clipNames[i]);var s=a.Playing[a.Playing.Count-1];var clip=a.Asset.Clips[id];
                s.Time=clip.Loop?Mathf.Repeat(times[i],clip.Duration):Mathf.Clamp(times[i],0,clip.Duration);
                s.Paused=paused!=null&&i<paused.Count&&paused[i];
            }
            // Play starts at t=0. Saved values take precedence until the next game tick.
            for(int i=0;i<names.Count;i++)
            {
                int id=a.Asset.FindParameter(names[i]);
                if(id<0||values==null||targets==null||i>=values.Count||i>=targets.Count||!Assets.Finite(values[i])||!Assets.Finite(targets[i]))continue;
                var p=a.Asset.Parameters[id];
                a.Values[id]=p.Wrap?Mathf.Repeat(values[i]-p.Min,360)+p.Min:Mathf.Clamp(values[i],p.Min,p.Max);
                a.Targets[id]=p.Wrap?Mathf.Repeat(targets[i]-p.Min,360)+p.Min:Mathf.Clamp(targets[i],p.Min,p.Max);
            }
            names=null;values=null;targets=null;clipNames=null;times=null;paused=null;
        }
        public override void PostExposeData()
        {
            base.PostExposeData();if(Scribe.mode==LoadSaveMode.Saving)Capture();
            Scribe_Collections.Look(ref names,"rmvfParameters",LookMode.Value);
            Scribe_Collections.Look(ref values,"rmvfValues",LookMode.Value);
            Scribe_Collections.Look(ref targets,"rmvfTargets",LookMode.Value);
            Scribe_Collections.Look(ref clipNames,"rmvfClips",LookMode.Value);
            Scribe_Collections.Look(ref times,"rmvfTimes",LookMode.Value);
            Scribe_Collections.Look(ref paused,"rmvfPaused",LookMode.Value);
        }
        public override IEnumerable<Gizmo> CompGetGizmosExtra()
        {
            if(Props.showControls&&Ensure())yield return new Command_Action
            {
                defaultLabel="RMVF_Controls".Translate(),defaultDesc="RMVF_ControlsDesc".Translate(),
                icon=TexButton.OpenInspector,action=()=>Find.WindowStack.Add(new MechanicalControls(this))
            };
        }
    }
    public sealed class MechanicalControls : Window
    {
        readonly CompMechanicalVisual comp;Vector2 scroll;bool pause;
        public override Vector2 InitialSize {get{return new Vector2(580,640);}}
        public MechanicalControls(CompMechanicalVisual c){comp=c;doCloseButton=true;doCloseX=true;absorbInputAroundWindow=true;}
        public override void DoWindowContents(Rect rect)
        {
            var a=comp.Animation;if(a==null)return;rect.height-=45;
            var view=new Rect(0,0,rect.width-20,70+a.Asset.Parameters.Length*68+a.Asset.Clips.Length*34);
            Widgets.BeginScrollView(rect,ref scroll,view);float y=0;
            Widgets.Label(new Rect(0,y,view.width,30),a.Asset.Id);y+=34;
            foreach(var p in a.Asset.Parameters)
            {
                int id=a.Asset.FindParameter(p.Name);
                Widgets.Label(new Rect(0,y,view.width,25),p.Name+": "+a.Values[id].ToString("0.00"));y+=27;
                float next=Widgets.HorizontalSlider(new Rect(0,y,view.width,24),a.Targets[id],p.Min,p.Max);
                if(Math.Abs(next-a.Targets[id])>.0001f)a.SetTarget(p.Name,next);y+=35;
            }
            foreach(var c in a.Asset.Clips)
            {
                if(Widgets.ButtonText(new Rect(0,y,view.width,29),"RMVF_Play".Translate(c.Name)))a.Play(c.Name);y+=34;
            }
            if(Widgets.ButtonText(new Rect(0,y,view.width*.48f,29),(pause?"RMVF_Resume":"RMVF_Pause").Translate())){pause=!pause;a.PauseAll(pause);}
            if(Widgets.ButtonText(new Rect(view.width*.52f,y,view.width*.48f,29),"RMVF_Stop".Translate()))a.StopAll();
            Widgets.EndScrollView();
        }
    }
}

