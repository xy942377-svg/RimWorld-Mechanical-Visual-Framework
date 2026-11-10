using System;
using System.IO;
using System.Linq;
using System.Reflection;
using UnityEngine;
using Verse;
using RimWorld;
using MechanicalVisualFramework;
using Anim=MechanicalVisualFramework.Animator;

// Isolated test mod only. No Harmony or hooks in the framework/player mod.
public sealed class FrameworkProbe : GameComponent
{
    int frame,scheduledTicks;float scheduledStart;CompMechanicalVisual starter,deploy,turret;bool complete;MechanicalControls controls;
    static string Dir {get{return GenFilePaths.SaveDataFolderPath;}}
    public FrameworkProbe(Game game){}
    static void Write(string text){File.AppendAllText(Path.Combine(Dir,"results.txt"),text+"\n");Log.Message("[RMVF.Test] "+text);}
    static void Check(bool ok,string text){if(!ok)throw new Exception(text);}
    public override void GameComponentUpdate()
    {
        if(complete||Find.CurrentMap==null)return;
        frame++;if(frame<430)Find.TickManager.Pause();
        try
        {
            if(frame==30)
            {
                var map=Find.CurrentMap;var center=map.Center;
                foreach(var cell in GenRadial.RadialCellsAround(center,17,true).Where(c=>c.InBounds(map)))
                {
                    foreach(var t in cell.GetThingList(map).ToList())if(!(t is Pawn)&&t.def.destroyable)t.Destroy();
                    map.roofGrid.SetRoof(cell,null);map.terrainGrid.SetTerrain(cell,TerrainDefOf.Concrete);
                }
                starter=Spawn("Starter",center+new IntVec3(-6,0,4));
                deploy=Spawn("Deployment",center+new IntVec3(1,0,4));
                turret=Spawn("TripleTurret",center+new IntVec3(0,0,-5));
                Find.CameraDriver.SetRootPosAndSize(center.ToVector3Shifted(),15);
                RunTests();
            }
            if(frame<30)return;
            if(frame<430){starter.Animation.Tick();deploy.Animation.Tick();turret.Animation.Tick();}
            if(frame==430){scheduledStart=starter.Animation.Playing[0].Time;Find.TickManager.CurTimeSpeed=TimeSpeed.Normal;}
            // Each playback set is independent; the turret uses the same API as the folding device.
            if(frame==100){turret.Animation.SetTarget("yaw",60);turret.Animation.SetTarget("left_elevation",25);turret.Animation.SetTarget("right_elevation",-5);deploy.Animation.Play("spin");}
            if(frame==200)turret.Animation.Play("recoil_center");
            if(frame==270){turret.Animation.SetTarget("yaw",220);turret.Animation.Play("recoil_left");}
            if(frame==320){controls=new MechanicalControls(turret);Find.WindowStack.Add(controls);}
            if(frame==360)Shot("RMVF_Controls");
            if(frame==400)controls.Close();
            if(frame==70||frame==220||frame==420)Shot("RMVF_"+frame);
            if(frame>=460&&scheduledTicks>=10)
            {
                Check(starter.Animation.Playing[0].Time!=scheduledStart,"native ticker did not animate comp");
                Write("PASS native normal-ticker integration: "+scheduledTicks+" scheduled game ticks.");
                Write("PASS three model definitions rendered concurrently; animation and screenshots captured.");
                Write("COMPLETE "+FrameworkMod.Version+" / "+VersionControl.CurrentVersionString);
                starter.Visual.Dispose();deploy.Visual.Dispose();turret.Visual.Dispose();
                complete=true;Verse.Root.Shutdown();
            }
            if(frame>4000)throw new Exception("native ticker timeout");
        }
        catch(Exception e){Write("FAIL "+e);complete=true;Verse.Root.Shutdown();}
    }
    public override void GameComponentTick(){if(frame>=430)scheduledTicks++;}
    static CompMechanicalVisual Spawn(string name,IntVec3 cell)
    {
        var t=(ThingWithComps)ThingMaker.MakeThing(DefDatabase<ThingDef>.GetNamed("RMVF_"+name));t.SetFaction(Faction.OfPlayer);
        GenSpawn.Spawn(t,cell,Find.CurrentMap);var c=t.GetComp<CompMechanicalVisual>();Check(c.Ready,"model not ready "+name);return c;
    }
    void RunTests()
    {
        var a=turret.Animation;a.StopAll();a.SetTarget("yaw",0,true);
        foreach(string n in new[]{"left","center","right"}){a.SetTarget(n+"_elevation",0,true);a.SetTarget(n+"_recoil",0,true);}
        turret.Visual.Update();turret.Visual.Update();Check(turret.Visual.LastUpdatedNodeCount==0,"idle pose rebuilt");
        a.SetTarget("center_recoil",.3f,true);
        Vector3 anchor,direction;
        Check(a.TryAnchor("muzzle_center",Vector3.zero,out anchor,out direction),"anchor missing");
        // An anchor query must NOT consume geometry's dirty revision.
        turret.Visual.Update();Check(turret.Visual.LastUpdatedNodeCount==1,"recoil dirtied unrelated nodes or anchor consumed change");
        int barrel=a.Asset.FindNode("center");
        Check((a.Transform(new Vector3(0,-4.26f,0),barrel)-new Vector3(0,-5.11f,1.25f)).magnitude<.0001f,"recoil pivot");
        a.SetTarget("yaw",90,true);a.Prepare();
        Check((a.Transform(Vector3.zero,barrel)-new Vector3(.85f,0,1.25f)).magnitude<.0001f,"parent yaw composition");
        turret.Visual.Update();Check(turret.Visual.LastUpdatedNodeCount==4,"parent rotation dirty propagation");
        a.SetTarget("center_elevation",30,true);a.Prepare();
        Check(a.Transform(new Vector3(0,-4.26f,0),barrel).z>3.1f,"elevation axis/sign");
        Write("PASS pivots, parent composition, anchors and dirty revisions (idle=0/recoil=1/yaw=4).");
        var other=new Anim(a.Asset);Check(other.Values[a.Asset.FindParameter("yaw")]==0,"mutable state shared");
        a.SetTarget("yaw",359,true);a.SetTarget("yaw",1);a.Tick(1f/24);Check(Mathf.Abs(Mathf.DeltaAngle(a.Values[0],0))<.001f,"shortest path rotation");
        a.Play("recoil_left");a.Play("recoil_right");Check(a.Playing.Count==2,"unrelated clips conflict");
        a.Tick(.1f);a.PauseAll(true);float before=a.Playing[0].Time;a.Tick(.1f);Check(a.Playing[0].Time==before,"pause failed");
        a.PauseAll(false);a.SetTarget("left_recoil",0);Check(a.Playing.Count==1,"parameter ownership cancellation");
        a.Tick(1);Check(a.Playing.Count==0,"one shot did not finish");
        deploy.Animation.Tick(24.5f);Check(deploy.Animation.Playing[0].Time<12,"loop did not wrap");
        Write("PASS independent instances, angular speed/shortest path, concurrent clips, pause, ownership, loop and completion.");
        a.SetTarget("yaw",137,true);a.SetTarget("center_elevation",17,true);a.Play("recoil_center");a.Tick(.2f);a.PauseAll(true);
        string file=Path.Combine(Dir,"component-save.xml");
        Scribe.saver.InitSaving(file,"RMVF");turret.PostExposeData();Scribe.saver.FinalizeSaving();
        var copy=(ThingWithComps)ThingMaker.MakeThing(DefDatabase<ThingDef>.GetNamed("RMVF_TripleTurret"));
        var restored=copy.GetComp<CompMechanicalVisual>();
        Scribe.loader.InitLoading(file);restored.PostExposeData();Scribe.loader.FinalizeLoading();
        var b=restored.Animation;Check(b!=null,"restore asset");
        for(int i=0;i<a.Values.Length;i++){Check(Mathf.Abs(a.Values[i]-b.Values[i])<.0001,"save value");Check(Mathf.Abs(a.Targets[i]-b.Targets[i])<.0001,"save target");}
        Check(b.Playing.Count==a.Playing.Count&&b.Playing[0].Paused&&Mathf.Abs(b.Playing[0].Time-a.Playing[0].Time)<.0001,"save playback");
        restored.Visual.Dispose();
        a.StopAll();
        Write("PASS Scribe roundtrip of parameter names/current/target values and paused playback time.");
        var oldAsset=a.Asset;turret.parent.DeSpawn();GenSpawn.Spawn(turret.parent,Find.CurrentMap.Center+new IntVec3(0,0,-5),Find.CurrentMap);
        Check(turret.Ready&&turret.Animation.Asset==oldAsset&&Mathf.Abs(turret.Animation.Values[0]-137)<.001,"despawn restore");
        Write("PASS despawn/respawn retains animation and reuses immutable asset.");
    }
    static void Shot(string name)
    {
        typeof(ScreenshotTaker).GetField("suppressMessage",BindingFlags.NonPublic|BindingFlags.Public|BindingFlags.Static).SetValue(null,true);
        typeof(ScreenshotTaker).GetMethod("TakeNonSteamShot",BindingFlags.NonPublic|BindingFlags.Public|BindingFlags.Static).Invoke(null,new object[]{name});
    }
}

