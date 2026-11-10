using System;
using System.Runtime.InteropServices;
using UnityEngine;
#if RW16
using UnityEngine.Rendering;
#else
using Native=Waylith.Graphics.Meshes;
#endif

namespace MechanicalVisualFramework
{
    // 两个后端共用 20 字节顶点布局；UV 选择色板单元，双面索引由 PreparedGeometry 提供。
    [StructLayout(LayoutKind.Sequential)]
    public struct PackedVertex
    {
        public Vector3 Position;
        public Vector2 UV;
        public PackedVertex(Vector3 position,Vector2 uv){Position=position;UV=uv;}
    }
    internal sealed class MeshBuffers : IDisposable
    {
        internal readonly Mesh Mesh=new Mesh();
        readonly int vertexCapacity,indexCapacity;
#if RW16
        const MeshUpdateFlags Flags=MeshUpdateFlags.DontRecalculateBounds|MeshUpdateFlags.DontValidateIndices;
#else
        readonly Native.Mesh native;
        readonly Native.CpuMeshData data;
#endif
        internal MeshBuffers(string name,int vertices,int indices)
        {
            if(Marshal.SizeOf(typeof(PackedVertex))!=20)throw new InvalidOperationException("Unexpected mechanical vertex layout");
            vertexCapacity=vertices;indexCapacity=indices;
            Mesh.name=name;Mesh.MarkDynamic();
#if RW16
            Mesh.SetVertexBufferParams(vertices,
                new VertexAttributeDescriptor(VertexAttribute.Position,VertexAttributeFormat.Float32,3),
                new VertexAttributeDescriptor(VertexAttribute.TexCoord0,VertexAttributeFormat.Float32,2));
            Mesh.SetIndexBufferParams(indices,IndexFormat.UInt32);Mesh.subMeshCount=1;
#else
            // 1.7 的普通 vertices/uv/List setter 会克隆数组。直接持有该实例自己的引擎缓冲，
            // 初始化后不再混用 Unity 兼容 setter/Clear，以免陈旧兼容缓存覆盖新数据。
            native=Mesh.EngineMesh;
            data=new Native.CpuMeshData();
            data.SetVertexLayout(new Native.VertexLayout(new[]{
                new Native.VertexAttribute(Native.VertexAttributeSemantic.Position,Native.VertexAttributeFormat.Float32,3),
                new Native.VertexAttribute(Native.VertexAttributeSemantic.TexCoord0,Native.VertexAttributeFormat.Float32,2)}),vertices);
            data.SetIndexBufferParams(indices,Native.MeshIndexFormat.UInt32);data.SetSubMeshCount(1);
            native.ReplaceCpuStorage(data);
#endif
        }
        internal void Vertices(PackedVertex[] source,int start,int count)
        {
            if(count==0)return;
            if(start<0||count<0||start+count>vertexCapacity||start+count>source.Length)throw new ArgumentOutOfRangeException("vertex range");
#if RW16
            Mesh.SetVertexBufferData(source,start,start,count,0,Flags);
#else
            // 容量只在构造时分配；范围验证在指针写入前完成。MarkChanged 在整次提交结束时调用。
            unsafe{fixed(PackedVertex* p=&source[start])
                Buffer.MemoryCopy(p,(byte*)data.GetVertexStream(0).Pointer+start*20,(vertexCapacity-start)*20,count*20);}
#endif
        }
        internal void Indices(int[] source,int count)
        {
            if(count<0||count>indexCapacity||count>source.Length)throw new ArgumentOutOfRangeException("index count");
            if(count==0)return;
#if RW16
            Mesh.SetIndexBufferData(source,0,0,count,Flags);
#else
            Marshal.Copy(source,0,data.GetIndexBuffer().Pointer,count);
#endif
        }
        internal void Commit(int indexCount,Bounds bounds)
        {
#if RW16
            Mesh.bounds=bounds;
            Mesh.SetSubMesh(0,new SubMeshDescriptor(0,indexCount,MeshTopology.Triangles){bounds=bounds,vertexCount=vertexCapacity},Flags);
#else
            Vector3 min=bounds.min,max=bounds.max;
            var b=new Native.MeshBounds(min.x,min.y,min.z,max.x,max.y,max.z);
            data.Bounds=b;data.SetSubMesh(0,new Native.SubMesh(0,indexCount,Native.MeshTopology.Triangles,0,b));
            native.MarkCpuStorageChanged();
#endif
        }
        public void Dispose(){UnityEngine.Object.Destroy(Mesh);}
    }
}

