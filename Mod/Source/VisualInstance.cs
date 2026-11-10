using System;
using UnityEngine;

namespace MechanicalVisualFramework
{
    // One mutable instance per thing. Asset geometry/materials are shared by asset, buffers never are.
    public sealed class VisualInstance : IDisposable
    {
        public readonly Animator Animation;
        readonly ModelAsset model;readonly PreparedGeometry geometry;
        readonly MeshBuffers surface,outline;
        readonly PackedVertex[] surfaceVertices,outlineVertices;
        readonly int[] outlineIndices,lastRevision;
        readonly Quaternion[] lastRotation;
        readonly Vector3[] projected,partMin,partMax;
        readonly float[] shades;readonly bool[] facing,visible;
        static readonly Vector3 light=new Vector3(-.6f,-.7f,1.5f).normalized;
        static readonly Vector2 lineUV=new Vector2(.5f/32,15.5f/16);
        static readonly int[] edgeIndices={0,1,2,0,2,3,2,1,0,3,2,0};
        readonly Vector3 camera;
        bool initialized,disposed;int outlineCount;
        public int LastUpdatedNodeCount {get;private set;}
        public VisualInstance(ModelAsset asset)
        {
            model=asset;geometry=asset.Geometry;Animation=new Animator(asset);camera=new Vector3(0,-asset.CosCamera,asset.SinCamera);
            int nodes=asset.Nodes.Length;
            surfaceVertices=new PackedVertex[asset.Faces.Length*3];outlineVertices=new PackedVertex[geometry.Edges.Length*4];outlineIndices=new int[geometry.Edges.Length*12];
            lastRevision=new int[nodes];lastRotation=new Quaternion[nodes];partMin=new Vector3[nodes];partMax=new Vector3[nodes];
            projected=new Vector3[geometry.Points.Length];shades=new float[geometry.Normals.Length];facing=new bool[shades.Length];visible=new bool[geometry.Edges.Length];
            surface=new MeshBuffers("RMVF.Surface."+asset.Id,surfaceVertices.Length,geometry.SurfaceIndices.Length);
            try{outline=new MeshBuffers("RMVF.Outline."+asset.Id,outlineVertices.Length,outlineIndices.Length);surface.Indices(geometry.SurfaceIndices,geometry.SurfaceIndices.Length);}
            catch{surface.Dispose();if(outline!=null)outline.Dispose();throw;}
        }
        public void Update()
        {
            if(disposed)return;Animation.Prepare();LastUpdatedNodeCount=0;
            bool indexChanged=!initialized;int sMin=surfaceVertices.Length,sMax=-1,lMin=outlineVertices.Length,lMax=-1;
            for(int p=0;p<model.Nodes.Length;p++)
            {
                if(initialized&&lastRevision[p]==Animation.Revisions[p])continue;
                LastUpdatedNodeCount++;lastRevision[p]=Animation.Revisions[p];
                bool normalsChanged=!initialized||!lastRotation[p].Equals(Animation.Rotations[p]);lastRotation[p]=Animation.Rotations[p];
                var part=geometry.Parts[p];Vector3 min=new Vector3(float.PositiveInfinity,float.PositiveInfinity,float.PositiveInfinity),max=-min;
                foreach(int id in part.Points)
                {
                    var v=Animation.Project(Animation.Transform(geometry.Points[id],p),p);projected[id]=v;min=Vector3.Min(min,v);max=Vector3.Max(max,v);
                }
                partMin[p]=min;partMax[p]=max;
                if(normalsChanged)foreach(int id in part.Normals)
                {
                    var n=Animation.Rotations[p]*geometry.Normals[id];shades[id]=(Mathf.Round(Mathf.Clamp01(Vector3.Dot(n,light))*31)+.5f)/32;facing[id]=Vector3.Dot(n,camera)>0;
                }
                foreach(int id in part.Faces)
                {
                    var f=geometry.Faces[id];int v=id*3;var uv=new Vector2(shades[f.Normal],(model.Faces[id].Material+.5f)/16);
                    surfaceVertices[v]=new PackedVertex(projected[f.A],uv);surfaceVertices[v+1]=new PackedVertex(projected[f.B],uv);surfaceVertices[v+2]=new PackedVertex(projected[f.C],uv);
                    sMin=Math.Min(sMin,v);sMax=Math.Max(sMax,v+2);
                }
                foreach(int id in part.Edges)
                {
                    var e=geometry.Edges[id];bool fa=facing[e.NormalA],fb=e.NormalB>=0&&facing[e.NormalB],silhouette=fa!=fb;
                    bool active=silhouette||(e.Crease&&(fa||fb));Vector3 a=projected[e.A],b=projected[e.B];
                    float dx=b.x-a.x,dz=b.z-a.z,len=(float)Math.Sqrt(dx*dx+dz*dz);active&=len>=.0001f;
                    if(active!=visible[id])indexChanged=true;visible[id]=active;if(!active)continue;
                    float w=(silhouette?.035f:.018f)/len,ox=-dz*w,oz=dx*w;a.y+=.00035f;b.y+=.00035f;int v=id*4;
                    outlineVertices[v]=new PackedVertex(new Vector3(a.x-ox,a.y,a.z-oz),lineUV);outlineVertices[v+1]=new PackedVertex(new Vector3(a.x+ox,a.y,a.z+oz),lineUV);
                    outlineVertices[v+2]=new PackedVertex(new Vector3(b.x+ox,b.y,b.z+oz),lineUV);outlineVertices[v+3]=new PackedVertex(new Vector3(b.x-ox,b.y,b.z-oz),lineUV);
                    lMin=Math.Min(lMin,v);lMax=Math.Max(lMax,v+3);
                }
            }
            if(LastUpdatedNodeCount==0)return;
            if(indexChanged)
            {
                outlineCount=0;for(int i=0;i<visible.Length;i++)if(visible[i])foreach(int n in edgeIndices)outlineIndices[outlineCount++]=i*4+n;
                outline.Indices(outlineIndices,outlineCount);
            }
            Vector3 allMin=new Vector3(float.PositiveInfinity,float.PositiveInfinity,float.PositiveInfinity),allMax=-allMin;
            for(int p=0;p<model.Nodes.Length;p++)if(geometry.Parts[p].Points.Length>0){allMin=Vector3.Min(allMin,partMin[p]);allMax=Vector3.Max(allMax,partMax[p]);}
            var bounds=new Bounds((allMin+allMax)*.5f,allMax-allMin);
            if(sMax>=sMin)surface.Vertices(surfaceVertices,sMin,sMax-sMin+1);surface.Commit(geometry.SurfaceIndices.Length,bounds);
            if(lMax>=lMin)outline.Vertices(outlineVertices,lMin,lMax-lMin+1);
            outline.Commit(outlineCount,new Bounds(bounds.center,bounds.size+new Vector3(.071f,.001f,.071f)));initialized=true;
        }
        public void Draw(Vector3 position)
        {
            if(disposed)return;Update();Graphics.DrawMesh(surface.Mesh,position,Quaternion.identity,model.Material,0);
            if(outlineCount>0)Graphics.DrawMesh(outline.Mesh,position,Quaternion.identity,model.Material,0);
        }
        public void Dispose(){if(disposed)return;disposed=true;surface.Dispose();outline.Dispose();}
    }
}
