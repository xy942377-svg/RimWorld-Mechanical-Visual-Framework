using System;
using System.Collections.Generic;
using UnityEngine;
using Verse;

namespace MechanicalVisualFramework
{
    public sealed class Playback { public int Clip; public float Time; public bool Paused; }
    public sealed class Animator
    {
        public readonly ModelAsset Asset;
        public readonly float[] Values,Targets;
        public readonly List<Playback> Playing=new List<Playback>();
        public readonly Vector3[] Positions;
        public readonly Quaternion[] Rotations;
        public readonly float[] Scales;
        public readonly bool[] Dirty;
        public readonly int[] Revisions;
        readonly Vector3[] localOffsets;
        readonly Quaternion[] localRotations;
        readonly float[] localScales;
        readonly bool[] owned;
        bool prepared;
        public Animator(ModelAsset asset)
        {
            Asset=asset;Values=new float[asset.Parameters.Length];Targets=new float[Values.Length];owned=new bool[Values.Length];
            for(int i=0;i<Values.Length;i++)Values[i]=Targets[i]=asset.Parameters[i].Default;
            int n=asset.Nodes.Length;Positions=new Vector3[n];Rotations=new Quaternion[n];Scales=new float[n];Dirty=new bool[n];Revisions=new int[n];
            localOffsets=new Vector3[n];localRotations=new Quaternion[n];localScales=new float[n];
        }
        // Parameter names are the stable external contract; callers never depend on a model's node count.
        public bool SetTarget(string name,float value,bool immediate=false)
        {
            int p=Asset.FindParameter(name);if(p<0||!Assets.Finite(value))return false;
            for(int i=Playing.Count-1;i>=0;i--)if(Owns(Asset.Clips[Playing[i].Clip],p))Playing.RemoveAt(i);
            var def=Asset.Parameters[p];value=def.Wrap?Mathf.Repeat(value-def.Min,360)+def.Min:Mathf.Clamp(value,def.Min,def.Max);
            Targets[p]=value;if(immediate)Values[p]=value;return true;
        }
        public bool Play(string name)
        {
            int id=Asset.FindClip(name);if(id<0)return false;var clip=Asset.Clips[id];
            // Latest command owns overlapping parameters. Unrelated clips (e.g. independent guns) coexist.
            for(int i=Playing.Count-1;i>=0;i--)
                foreach(var track in clip.Tracks)if(Owns(Asset.Clips[Playing[i].Clip],track.Parameter)){Playing.RemoveAt(i);break;}
            var p=new Playback{Clip=id};Playing.Add(p);Apply(p);return true;
        }
        public void StopAll(){Playing.Clear();Array.Copy(Values,Targets,Values.Length);}
        public void PauseAll(bool paused){foreach(var p in Playing)p.Paused=paused;}
        static bool Owns(Clip c,int p){foreach(var t in c.Tracks)if(t.Parameter==p)return true;return false;}
        public void Tick(float seconds=1f/60f)
        {
            if(!Assets.Finite(seconds)||seconds<=0)return;
            Array.Clear(owned,0,owned.Length);
            for(int i=Playing.Count-1;i>=0;i--)
            {
                var p=Playing[i];var clip=Asset.Clips[p.Clip];foreach(var t in clip.Tracks)owned[t.Parameter]=true;
                if(p.Paused)continue;p.Time+=seconds;
                if(clip.Loop)p.Time=Mathf.Repeat(p.Time,clip.Duration);
                Apply(p);if(!clip.Loop&&p.Time>=clip.Duration)Playing.RemoveAt(i);
            }
            for(int i=0;i<Values.Length;i++)if(!owned[i])
            {
                var p=Asset.Parameters[i];Values[i]=p.Speed<=0?Targets[i]:p.Wrap?Mathf.MoveTowardsAngle(Values[i],Targets[i],p.Speed*seconds):Mathf.MoveTowards(Values[i],Targets[i],p.Speed*seconds);
                if(p.Wrap)Values[i]=Mathf.Repeat(Values[i]-p.Min,360)+p.Min;
            }
        }
        void Apply(Playback playing)
        {
            var c=Asset.Clips[playing.Clip];float time=Math.Min(playing.Time,c.Duration);
            foreach(var t in c.Tracks)
            {
                int k=0;while(k<t.Times.Length-1&&time>t.Times[k+1])k++;
                float value=k==t.Times.Length-1?t.Values[k]:Mathf.Lerp(t.Values[k],t.Values[k+1],Mathf.InverseLerp(t.Times[k],t.Times[k+1],time));
                Values[t.Parameter]=Targets[t.Parameter]=value;
            }
        }
        public void Prepare()
        {
            for(int i=0;i<Asset.Nodes.Length;i++){localOffsets[i]=Vector3.zero;localRotations[i]=Asset.Nodes[i].Rotation;localScales[i]=Asset.Nodes[i].Scale;}
            foreach(var b in Asset.Bindings)
            {
                float v=Values[b.Parameter]*b.Factor;
                if(b.Kind=="rotation")localRotations[b.Node]=localRotations[b.Node]*Quaternion.AngleAxis(v,b.Axis);
                else if(b.Kind=="translation")localOffsets[b.Node]+=b.Axis*v;
                else localScales[b.Node]*=1+v;
            }
            // Translation axes follow the node's rotated local axes; this is required for recoil at elevation.
            // Parents precede children in the asset. No recursive traversal or temporary matrices per frame.
            for(int i=0;i<Asset.Nodes.Length;i++)
            {
                Node n=Asset.Nodes[i];Vector3 pos=n.Position+localRotations[i]*localOffsets[i];Quaternion rot=localRotations[i];float scale=localScales[i];
                if(n.Parent>=0){pos=Positions[n.Parent]+Rotations[n.Parent]*(pos*Scales[n.Parent]);rot=Rotations[n.Parent]*rot;scale*=Scales[n.Parent];}
                Dirty[i]=!prepared||!pos.Equals(Positions[i])||!rot.Equals(Rotations[i])||scale!=Scales[i];
                if(Dirty[i])Revisions[i]++;Positions[i]=pos;Rotations[i]=rot;Scales[i]=scale;
            }
            prepared=true;
        }
        public Vector3 Transform(Vector3 local,int node){return Positions[node]+Rotations[node]*(local*Scales[node]);}
        public Vector3 Project(Vector3 v,int node)
        {
            float band=Asset.Nodes[node].Raised?Verse.AltitudeLayer.ItemImportant.AltitudeFor()-Verse.AltitudeLayer.Building.AltitudeFor():0;
            return new Vector3(v.x,band+.06f+(-v.y*Asset.CosCamera+v.z*Asset.SinCamera)*.02f,v.y*Asset.SinCamera+v.z*Asset.CosCamera);
        }
        // Position and direction share exactly the model/animation/projection path used by the renderer.
        public bool TryAnchor(string name,Vector3 drawOrigin,out Vector3 position,out Vector3 direction)
        {
            Prepare();foreach(var a in Asset.Anchors)if(a.Name==name)
            {
                Vector3 v=Transform(a.Position,a.Node);position=drawOrigin+Project(v,a.Node);
                Vector3 d=Rotations[a.Node]*a.Direction;direction=new Vector3(d.x,0,d.y*Asset.SinCamera+d.z*Asset.CosCamera).normalized;return true;
            }
            position=drawOrigin;direction=Vector3.zero;return false;
        }
    }
}
