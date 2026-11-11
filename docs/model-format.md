# 模型、坐标与动画格式

[English](model-format.en.md) · [中文首页](../README.md) · [上手教程](quickstart.md) · [接口说明](api.md)

模型源文件采用 UTF-8 编码的 JSON，顶层字段 `version` 为 `1`；生成的模型 XML 也使用格式版本 `1`。[Templates/model.json](../Templates/model.json) 提供一个可以直接构建的最小示例。请保存并维护源文件，游戏使用的资源文件可通过 `Tools/assets.py` 重新生成。

## 坐标和层级

模型X向右、Y向后、Z向上，单位为一个地图格；中立朝向为 -Y。相机俯角默认55°。

每个节点代表一个部件或转轴。节点列表中，父节点必须排在子节点前面。`position` 是节点原点相对于父节点的位置；`rotation` 使用单位四元数 `[x,y,z,w]` 表示朝向；`scale` 是三个方向相同、且大于零的缩放倍率。几何中心和顶点都以本节点原点为基准，这就是节点的局部坐标。节点可以没有网格，作为纯转轴；整个模型至少有一个非退化三角形。

计算部件姿态时，先应用节点在模型中设定的初始旋转，再按 `bindings` 的顺序追加参数控制的旋转。平移偏移沿**完成旋转后的本地轴**，因此抬高炮管时后坐也沿炮管方向。需要“先平移、后旋转”或多个不同转轴时，显式添加中间父节点，而不是更改这条规则。

子节点世界姿态：
`位置 = 父位置 + 父旋转 × (子局部位置 × 父缩放)`；
`旋转 = 父旋转 × 子旋转`；缩放相乘。

投影：
`屏幕横向 = X`；`地图纵向 = Y·sin(camera) + Z·cos(camera)`。
Unity/兼容绘制坐标的Y仅用于深度排序：基础高度 + layer高度带 + `(-Y·cos(camera)+Z·sin(camera))×0.02`。
foundation使用Building高度带，raised位于ItemImportant之上。这些高度层决定绘制的前后顺序，不参与碰撞计算。极高/大型模型应实测与人物、杂物、其他建筑的交叠关系。

## 数据字段

|字段|含义|
|---|---|
|camera|作者设置的正交投影俯角，15°—85°，默认55°；修改后重新构建并重启游戏|
|nodes|name、可选parent、position、rotation、scale、layer、geometry|
|geometry|box(center,size)、cylinder(center,radius,length,axis,segments)、triangles；每项material=0..14|
|parameters|name、min、max、default、speed、wrap；speed单位为参数单位/秒，0表示直接到目标|
|bindings|node、parameter、kind(rotation/translation/scale)、axis、factor|
|clips|name、duration(秒)、loop、tracks；每条track指parameter，keys是 [时间,数值] 列表|
|anchors|name、node、position、direction；默认方向 -Y|
|palette|最多16行RGB字节颜色；0..14为材料，15保留给深色描边|

rotation使用度数；translation是地图格；scale将节点缩放乘以1+参数×factor，不能为零或负数。wrap参数跨度必须正好360°，目标跟随使用最短角差。

关键帧按时间严格递增，使用线性插值。首个关键帧之前保持首值，末帧之后保持末值；循环在duration回到起点。若要循环角度平滑，示例以0→360的连续数值轨道表示一整圈。

同一参数同时只归一个动作所有。Play启动的新动作会停止任何与其参数重叠的旧动作；不相交动作可并行。SetTarget会停止占用该参数的动作。PauseAll暂停动作轨道，不暂停普通参数朝目标移动；游戏暂停会同时停止两者。StopAll保持当前姿态。

## 编译产物

MechanicalModelDef.assetPath相对**声明它的使用框架的MOD**目录。每个模型有model.xml、geometry.bin、BuildHashes.json；色板位于全局唯一的Textures路径。多个使用框架的MOD必须避免Def名、packageId、贴图路径重复。

geometry.bin为小端：int32 magic=0x31564D52、int32三角形数；每面int32节点号、int32材料号、9个float32顶点分量，共44字节。法线由顶点绕序计算。面的外法线用于明暗和轮廓，所以双面绘制不能修复错误绕序。

上限：256节点、256参数、50000面。它们是输入限制，不是性能推荐值。同一模型共用一份材质；每个放置在地图上的对象分别持有表面和轮廓两份可更新网格。不要直接修改加载后的ModelAsset数组；它们在多个实例间共享。

