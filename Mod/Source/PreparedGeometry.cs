using System;
using System.Collections.Generic;
using UnityEngine;

namespace MechanicalVisualFramework
{
    // 只在加载资产时建立索引；位置按精确 float 合并，保留原色块接缝与面顺序。
    internal sealed class PreparedGeometry
    {
        internal struct Key : IEquatable<Key>
        {
            readonly int part;
            readonly Vector3 v;
            public Key(int p,Vector3 value){part=p;v=value;}
            public bool Equals(Key k){return part==k.part&&v.x.Equals(k.v.x)&&v.y.Equals(k.v.y)&&v.z.Equals(k.v.z);}
            public override bool Equals(object obj){return obj is Key&&Equals((Key)obj);}
            public override int GetHashCode(){unchecked{return (((part*397)^v.x.GetHashCode())*397^v.y.GetHashCode())*397^v.z.GetHashCode();}}
        }
        internal struct FaceMap {public int A,B,C,Normal;}
        internal struct EdgeMap {public int A,B,NormalA,NormalB;public bool Crease;}
        internal sealed class Part
        {
            public int[] Points,Normals,Faces,Edges;
        }
        internal readonly Vector3[] Points,Normals;
        internal readonly FaceMap[] Faces;
        internal readonly EdgeMap[] Edges;
        internal readonly Part[] Parts;
        internal readonly int[] SurfaceIndices;
        public PreparedGeometry(ModelAsset model)
        {
            Parts=new Part[model.Nodes.Length]; var modelEdges=BuildEdges(model); var points=new List<Vector3>();var normals=new List<Vector3>();
            var pi=new Dictionary<Key,int>();var ni=new Dictionary<Key,int>();
            var pp=Lists(Parts.Length);var pn=Lists(Parts.Length);var pf=Lists(Parts.Length);var pe=Lists(Parts.Length);
            Faces=new FaceMap[model.Faces.Length];
            SurfaceIndices=new int[Faces.Length*6];
            for(int i=0;i<Faces.Length;i++)
            {
                Face f=model.Faces[i];int p=f.Node;
                Faces[i]=new FaceMap{A=Index(pi,points,pp[p],p,f.A),B=Index(pi,points,pp[p],p,f.B),
                    C=Index(pi,points,pp[p],p,f.C),Normal=Index(ni,normals,pn[p],p,f.N)};
                pf[p].Add(i);int j=i*6,v=i*3;
                SurfaceIndices[j]=v;SurfaceIndices[j+1]=v+1;SurfaceIndices[j+2]=v+2;
                SurfaceIndices[j+3]=v+2;SurfaceIndices[j+4]=v+1;SurfaceIndices[j+5]=v;
            }
            Edges=new EdgeMap[modelEdges.Length];
            for(int i=0;i<Edges.Length;i++)
            {
                Edge e=modelEdges[i];
                Edges[i]=new EdgeMap{A=pi[new Key(e.Node,e.A)],B=pi[new Key(e.Node,e.B)],
                    NormalA=Faces[e.FaceA].Normal,NormalB=e.FaceB<0?-1:Faces[e.FaceB].Normal,
                    Crease=e.FaceB>=0&&Vector3.Dot(model.Faces[e.FaceA].N,model.Faces[e.FaceB].N)<.60f};
                pe[e.Node].Add(i);
            }
            Points=points.ToArray();Normals=normals.ToArray();
            for(int p=0;p<Parts.Length;p++)Parts[p]=new Part{Points=pp[p].ToArray(),Normals=pn[p].ToArray(),Faces=pf[p].ToArray(),Edges=pe[p].ToArray()};
        }
        static string PositionKey(Vector3 v){return Mathf.RoundToInt(v.x*100000)+","+Mathf.RoundToInt(v.y*100000)+","+Mathf.RoundToInt(v.z*100000);}
        static Edge[] BuildEdges(ModelAsset model)
        {
            var edges=new Dictionary<string,Edge>();
            for(int i=0;i<model.Faces.Length;i++)
            {
                var f=model.Faces[i];var points=new[]{f.A,f.B,f.C};
                for(int k=0;k<3;k++)
                {
                    Vector3 a=points[k],b=points[(k+1)%3];string ka=PositionKey(a),kb=PositionKey(b);
                    string key=f.Node+":"+(string.CompareOrdinal(ka,kb)<0?ka+"/"+kb:kb+"/"+ka);
                    Edge edge;if(edges.TryGetValue(key,out edge))edge.FaceB=i;else edges.Add(key,new Edge{A=a,B=b,Node=f.Node,FaceA=i});
                }
            }
            var result=new List<Edge>();
            foreach(var e in edges.Values)if(e.FaceB<0||Vector3.Dot(model.Faces[e.FaceA].N,model.Faces[e.FaceB].N)<.9999f||model.Faces[e.FaceA].Material!=model.Faces[e.FaceB].Material)result.Add(e);
            return result.ToArray();
        }
        static List<int>[] Lists(int count){var v=new List<int>[count];for(int i=0;i<count;i++)v[i]=new List<int>();return v;}
        static int Index(Dictionary<Key,int> index,List<Vector3> values,List<int> part,int p,Vector3 v)
        {
            var key=new Key(p,v);int id;
            if(index.TryGetValue(key,out id))return id;
            id=values.Count;index.Add(key,id);values.Add(v);part.Add(id);return id;
        }
    }
}

