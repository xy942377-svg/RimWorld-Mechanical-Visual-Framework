using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Xml;
using UnityEngine;
using Verse;

namespace MechanicalVisualFramework
{
    // Assets belong to the consuming mod, not the framework's installation directory.
    public sealed class MechanicalModelDef : Def { public string assetPath; }
    public sealed class Node
    {
        public string Name; public int Parent; public Vector3 Position; public Quaternion Rotation;
        public float Scale; public bool Raised;
    }
    public sealed class Parameter { public string Name; public float Min,Max,Default,Speed; public bool Wrap; }
    public sealed class Binding { public int Node,Parameter; public string Kind; public Vector3 Axis; public float Factor; }
    public sealed class Track { public int Parameter; public float[] Times,Values; }
    public sealed class Clip { public string Name; public float Duration; public bool Loop; public Track[] Tracks; }
    public sealed class Anchor { public string Name; public int Node; public Vector3 Position,Direction; }
    public struct Face { public int Node,Material; public Vector3 A,B,C,N; }
    internal sealed class Edge { public int Node,FaceA,FaceB=-1; public Vector3 A,B; }
    public sealed class ModelAsset
    {
        public string Id; public Node[] Nodes; public Parameter[] Parameters; public Binding[] Bindings;
        public Clip[] Clips; public Anchor[] Anchors; public Face[] Faces; public Material Material;
        public float SinCamera,CosCamera;
        internal PreparedGeometry Geometry;
        internal Dictionary<string,int> ParameterNames,NodeNames,ClipNames;
        public int FindParameter(string name){int i;return name!=null&&ParameterNames.TryGetValue(name,out i)?i:-1;}
        public int FindNode(string name){int i;return name!=null&&NodeNames.TryGetValue(name,out i)?i:-1;}
        public int FindClip(string name){int i;return name!=null&&ClipNames.TryGetValue(name,out i)?i:-1;}
    }
    public static class Assets
    {
        static readonly Dictionary<MechanicalModelDef,ModelAsset> cache=new Dictionary<MechanicalModelDef,ModelAsset>();
        static readonly HashSet<MechanicalModelDef> failed=new HashSet<MechanicalModelDef>();
        public static ModelAsset Get(MechanicalModelDef def)
        {
            if(def==null||failed.Contains(def))return null;
            ModelAsset a;if(cache.TryGetValue(def,out a))return a;
            try{a=Load(def);cache.Add(def,a);return a;}
            catch(Exception e){failed.Add(def);Log.Error("[RMVF] Asset '"+def.defName+"' disabled: "+e.Message);return null;}
        }
        // Validate resource data once when loading it; drawing reuses the checked asset.
        static ModelAsset Load(MechanicalModelDef def)
        {
            string root=Path.GetFullPath(def.modContentPack.RootDir);
            string path=Contained(root,def.assetPath);
            var doc=new XmlDocument{XmlResolver=null};
            using(var reader=XmlReader.Create(path,new XmlReaderSettings{DtdProcessing=DtdProcessing.Prohibit,XmlResolver=null}))doc.Load(reader);
            XmlElement top=doc.DocumentElement;Require(top!=null&&top.Name=="mechanicalModel"&&top.GetAttribute("version")=="1","Expected a mechanicalModel XML root with version 1.");
            var a=new ModelAsset{Id=def.defName};
            float angle=Number(top,"camera",55);Require(angle>=15&&angle<=85,"Camera elevation must be between 15 and 85 degrees.");
            a.SinCamera=Mathf.Sin(angle*Mathf.Deg2Rad);a.CosCamera=Mathf.Cos(angle*Mathf.Deg2Rad);
            var nodes=new List<Node>();var names=new Dictionary<string,int>();
            foreach(XmlElement e in top.SelectNodes("nodes/node"))
            {
                string name=Name(e);Require(!names.ContainsKey(name),"duplicate node "+name);
                string parent=e.GetAttribute("parent");int pi=-1;
                Require(parent.Length==0||names.TryGetValue(parent,out pi),"parent must precede child: "+name);
                float scale=Number(e,"scale",1);Require(scale>0&&scale<=100,"Node scale must be greater than 0 and at most 100.");
                Quaternion q=Quat(e.GetAttribute("rotation"));
                nodes.Add(new Node{Name=name,Parent=pi,Position=Vector(e,"position",Vector3.zero),Rotation=q,Scale=scale,Raised=e.GetAttribute("layer")=="raised"});names.Add(name,nodes.Count-1);
            }
            Require(nodes.Count>0&&nodes.Count<=256,"A model must contain 1 to 256 nodes.");a.Nodes=nodes.ToArray();
            var ps=new List<Parameter>();var paramNames=new Dictionary<string,int>();
            foreach(XmlElement e in top.SelectNodes("parameters/parameter"))
            {
                string name=Name(e);Require(!paramNames.ContainsKey(name),"duplicate parameter "+name);
                var p=new Parameter{Name=name,Min=Number(e,"min",0),Max=Number(e,"max",1),Default=Number(e,"default",0),Speed=Number(e,"speed",0),Wrap=e.GetAttribute("wrap")=="true"};
                Require(p.Max>p.Min&&p.Default>=p.Min&&p.Default<=p.Max&&p.Speed>=0,"A parameter needs min < max, a default within that range, and speed >= 0: "+name);
                Require(!p.Wrap||Math.Abs(p.Max-p.Min-360)<.001f,"wrapped range must span 360 degrees");
                paramNames.Add(name,ps.Count);ps.Add(p);
            }
            Require(ps.Count<=256,"A model can contain at most 256 parameters.");a.Parameters=ps.ToArray();
            var bs=new List<Binding>();
            foreach(XmlElement e in top.SelectNodes("bindings/binding"))
            {
                int ni,pi;Require(names.TryGetValue(e.GetAttribute("node"),out ni)&&paramNames.TryGetValue(e.GetAttribute("parameter"),out pi),"A binding must name an existing node and parameter.");
                // Short-circuit validation does not establish definite assignment for the compiler.
                pi=paramNames[e.GetAttribute("parameter")];
                var b=new Binding{Node=ni,Parameter=pi,Kind=e.GetAttribute("kind"),Axis=Vector(e,"axis",Vector3.forward),Factor=Number(e,"factor",1)};
                Require(b.Kind=="rotation"||b.Kind=="translation"||b.Kind=="scale","Binding kind must be rotation, translation or scale.");
                Require(b.Axis.sqrMagnitude>1e-10f,"A binding axis must be a nonzero vector.");
                if(b.Kind=="rotation")b.Axis=b.Axis.normalized;
                if(b.Kind=="scale")Require(1+Math.Min(ps[pi].Min*b.Factor,ps[pi].Max*b.Factor)>.001f,"The scale multiplier must stay above 0.001 across the full parameter range.");
                bs.Add(b);
            }
            a.Bindings=bs.ToArray();
            var clips=new List<Clip>();var clipNames=new HashSet<string>();
            foreach(XmlElement e in top.SelectNodes("clips/clip"))
            {
                string name=Name(e);Require(clipNames.Add(name),"duplicate clip "+name);
                var c=new Clip{Name=name,Duration=Number(e,"duration",1),Loop=e.GetAttribute("loop")=="true"};Require(c.Duration>0,"Clip duration must be greater than zero.");
                var tracks=new List<Track>();var used=new HashSet<int>();
                foreach(XmlElement t in e.SelectNodes("track"))
                {
                    int pi;Require(paramNames.TryGetValue(t.GetAttribute("parameter"),out pi)&&used.Add(pi),"Each track must name an existing parameter, used only once within that clip.");
                    var times=new List<float>();var values=new List<float>();
                    foreach(XmlElement key in t.SelectNodes("key"))
                    {
                        float time=Number(key,"time",0),value=Number(key,"value",0);
                        Require(time>=0&&time<=c.Duration&&(times.Count==0||time>times[times.Count-1]),"Keyframe times must increase strictly and stay between 0 and the clip duration.");
                        Require(value>=ps[pi].Min&&value<=ps[pi].Max,"A keyframe value is outside its parameter range.");times.Add(time);values.Add(value);
                    }
                    Require(times.Count>=1,"Each track needs at least one keyframe.");tracks.Add(new Track{Parameter=pi,Times=times.ToArray(),Values=values.ToArray()});
                }
                Require(tracks.Count>0,"Each clip needs at least one track.");c.Tracks=tracks.ToArray();clips.Add(c);
            }
            a.Clips=clips.ToArray();a.NodeNames=names;a.ParameterNames=paramNames;a.ClipNames=new Dictionary<string,int>();
            for(int i=0;i<a.Clips.Length;i++)a.ClipNames.Add(a.Clips[i].Name,i);
            var anchors=new List<Anchor>();var anchorNames=new HashSet<string>();
            foreach(XmlElement e in top.SelectNodes("anchors/anchor"))
            {
                string name=Name(e);int ni;Require(anchorNames.Add(name)&&names.TryGetValue(e.GetAttribute("node"),out ni),"Each anchor needs a unique name and must reference an existing node.");ni=names[e.GetAttribute("node")];
                var direction=Vector(e,"direction",new Vector3(0,-1,0));Require(direction.sqrMagnitude>1e-10f,"An anchor direction must be a nonzero vector.");
                anchors.Add(new Anchor{Name=name,Node=ni,Position=Vector(e,"position",Vector3.zero),Direction=direction.normalized});
            }
            a.Anchors=anchors.ToArray();
            string geometry=Contained(Path.GetDirectoryName(path),top.GetAttribute("geometry"));
            using(var r=new BinaryReader(File.OpenRead(geometry)))
            {
                Require(r.ReadInt32()==0x31564D52,"The geometry file header does not match the RMVF format.");int count=r.ReadInt32();Require(count>0&&count<=50000,"The geometry file must contain 1 to 50,000 triangles.");
                Require(r.BaseStream.Length==8+44L*count,"Geometry file length does not match its declared triangle count.");a.Faces=new Face[count];
                for(int i=0;i<count;i++)
                {
                    var f=new Face{Node=r.ReadInt32(),Material=r.ReadInt32(),A=Read(r),B=Read(r),C=Read(r)};
                    Require(f.Node>=0&&f.Node<a.Nodes.Length&&f.Material>=0&&f.Material<16,"A triangle references an invalid node or material index.");
                    f.N=Vector3.Cross(f.B-f.A,f.C-f.A);Require(f.N.sqrMagnitude>1e-16f,"A triangle has zero or near-zero area; rebuild the model with valid vertices.");f.N=f.N.normalized;a.Faces[i]=f;
                }
            }
            var tex=ContentFinder<Texture2D>.Get(top.GetAttribute("palette"),true);Require(tex!=null,"The model palette texture could not be loaded.");tex.filterMode=FilterMode.Point;
            a.Material=MaterialPool.MatFrom(new MaterialRequest(tex,ShaderDatabase.Cutout));a.Geometry=new PreparedGeometry(a);return a;
        }
        static string Contained(string root,string relative)
        {
            Require(!string.IsNullOrWhiteSpace(relative)&&!Path.IsPathRooted(relative),"The asset path must be nonempty and relative to its resource directory.");
            string p=Path.GetFullPath(Path.Combine(root,relative));Require(p.StartsWith(root.TrimEnd(Path.DirectorySeparatorChar)+Path.DirectorySeparatorChar,StringComparison.OrdinalIgnoreCase),"The asset path must stay inside its resource directory.");return p;
        }
        static string Name(XmlElement e){string s=e.GetAttribute("name");Require(!string.IsNullOrWhiteSpace(s),"The XML element needs a nonempty name attribute.");return s;}
        static float Number(XmlElement e,string key,float fallback){string s=e.GetAttribute(key);return s.Length==0?fallback:Float(s);}
        static float Float(string s){float v=float.Parse(s,CultureInfo.InvariantCulture);Require(!float.IsNaN(v)&&!float.IsInfinity(v),"Numeric values must be finite; NaN and infinity are invalid.");return v;}
        static Vector3 Vector(XmlElement e,string key,Vector3 fallback){string s=e.GetAttribute(key);if(s.Length==0)return fallback;var n=s.Split(' ');Require(n.Length==3,"A vector needs three space-separated numbers.");return new Vector3(Float(n[0]),Float(n[1]),Float(n[2]));}
        static Quaternion Quat(string s){if(s.Length==0)return Quaternion.identity;var n=s.Split(' ');Require(n.Length==4,"A rotation needs four space-separated numbers: x y z w.");var q=new Quaternion(Float(n[0]),Float(n[1]),Float(n[2]),Float(n[3]));float len=(float)Math.Sqrt(q.x*q.x+q.y*q.y+q.z*q.z+q.w*q.w);Require(Math.Abs(len-1)<.001,"The rotation quaternion must have unit length.");return q;}
        static Vector3 Read(BinaryReader r){var v=new Vector3(r.ReadSingle(),r.ReadSingle(),r.ReadSingle());Require(Finite(v.x)&&Finite(v.y)&&Finite(v.z),"Vertex coordinates must be finite; NaN and infinity are invalid.");return v;}
        internal static bool Finite(float v){return !float.IsNaN(v)&&!float.IsInfinity(v);}
        static void Require(bool ok,string message){if(!ok)throw new InvalidDataException(message);}
    }
}
