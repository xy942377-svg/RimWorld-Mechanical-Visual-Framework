# 从空目录到会动的建筑

本教程介绍如何安装示例、创建自己的MOD、修改模型并导入建模软件制作的部件。命令行步骤使用完整仓库作为工作目录。

## 1. 运行示例

安装仓库的`Mod`和`Examples/Mechanisms`两个目录为两个MOD，按Core、框架、示例排序。进入开发测试地图，在杂项菜单建造示例；“动画控制”可调参数并播放动作。启用开发者模式时也可通过生成建筑功能放置`RMVF_Starter`、`RMVF_Deployment`、`RMVF_TripleTurret`。

暂停游戏会停止动画时钟。直接拖动参数改变的是目标值，部件按配置速度逐渐移动。播放动作会接管其使用的参数；手动修改该参数会停止占用它的动作。

作者控制面板保留yaw、left_elevation等参数/动作标识符，方便与源模型逐项对应；通用按钮与说明提供英文、简体中文。

## 2. 配置工具

双击根目录`Start.cmd`，选择Configure。填写已有Python 3.10+ 的可执行文件路径；若命令行可以运行Python，也可以填`python`。只有要编译框架或运行自动游戏测试时才需要填写游戏目录与Roslyn的`csc.exe`。配置保存在`ToolPaths.local.json`，不会进入发布包。

不使用菜单时，以下命令都从仓库根目录运行。将`python`换成自己的Python可执行文件也可以：

```text
python Tools/new_project.py D:/MyMechanicalMod --id yourname.mechanism --name "My Mechanism"
```

输出目录必须不存在，避免覆盖已有作品。生成的目录是完整的MOD，使用本框架提供动画与绘制功能；将它放入游戏Mods，依赖框架运行。修改About中的作者、名称和说明；保留复用代码/素材所需的原作者版权说明。**不要将框架DLL复制进每个使用框架的MOD**。

## 3. 第一个改动

打开新MOD的`Authoring/model.json`。起步模型只有底座和一个可旋转的子部件。修改`arm`的box尺寸、材料或`yaw.speed`，再执行：

```text
python Tools/assets.py D:/MyMechanicalMod/Authoring/model.json D:/MyMechanicalMod yourname_mechanism
```

最后一个参数必须与该MOD的`Models/...`路径一致；新建工具将packageId中的点改为下划线得到这个名称。构建生成模型XML、二进制几何和色板。退出并重启游戏后查看结果，首版没有热重载。

先做小规模改动，再添加子部件。转轴位置写在节点position中，网格顶点必须相对于这个转轴；把整个模型的世界坐标直接当局部坐标，会造成部件绕错误的位置旋转。

## 4. 从建模软件接入

在支持GLB 2.0的建模软件中，将每个需要独立运动的刚性部件设为独立节点，并设置父子关系与原点。将非均匀缩放应用到几何后，导出静止模型，**关闭动画和纹理导出**。导出文件还需满足下列格式条件。

```text
python Tools/import_glb.py D:/model.glb D:/MyMechanicalMod/Authoring/imported.json
```

支持：一个内嵌二进制缓冲、三角形、FLOAT类型的POSITION顶点坐标、由平移和旋转及正值均匀缩放组成的节点变换（TRS）、最多15种纯色材质。保留层级和节点原点，并把glTF的Y向上转为框架的Z向上。仅导入所选场景。

不支持：矩阵节点、非均匀/负缩放、稀疏访问器、纹理、透明材质、骨骼、形变目标、GLB动画和文件声明为必需的扩展。遇到这些情况明确报错；应在建模软件导出前处理。基础颜色转换成色板，原PBR光照和材质质感不会保留。所有面采用框架的平面光照与轮廓。

导入后，补写parameters、bindings、clips、anchors。将贴地底座节点的layer改成foundation，其余按遮挡需要使用raised。再用assets.py编译。**GLB文件只在制作阶段使用，游戏运行读取的是编译后的资源。**

GLB格式依据[Khronos glTF 2.0规范](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html)。

## 5. 参考哪一个例子

- Starter：学习坐标、父子节点、旋转参数。
- Deployment：学习一个旋转父节点下的多关节折叠，同时播放独立升降/旋转。
- TripleTurret：学习独立俯仰、旋转后的局部后坐和三个炮口挂接点。需要攻击功能时，由自己的游戏逻辑调用动画接口。
- [ShieldGenerator建模案例](../Modeling/ShieldGenerator/README.md)：学习统一构件的四角装配、正交投影，以及球盖与基座的分层导出。

自行建模的面数从数百开始。运行开销主要受三角面数、轮廓边数和活动部件数影响。制作尺寸与游戏占地独立设置；调整ThingDef.size不会缩放模型。

