# 游戏逻辑如何驱动视觉

[English](api.en.md) · [中文首页](../README.md) · [模型格式](model-format.md) · [运行时结构](architecture.md)

如果只需展示模型和播放动画，可以直接配置 XML：将 ThingDef 的 `thingClass` 设为 `Building_MechanicalDisplay`，在 `comps` 中添加 `CompProperties_MechanicalVisual`，填写 `model`；如需生成建筑后自动播放动作，再填写 `autoplay`。完整示例见 [Mechanisms.xml](../Examples/Mechanisms/Defs/Mechanisms.xml)。tickerType必须为Normal，drawerType必须为RealtimeOnly；示例rotatable=false，朝向由模型yaw参数控制。

`showControls` 默认开启，用于调节模型参数和测试动作。发布面向玩家的建筑时，可在该组件的XML配置中设置 `<showControls>false</showControls>` 隐藏通用面板，再由自己的操作按钮或游戏逻辑调用动画。

已有自定义建筑可以保留自己的游戏逻辑和ThingComp；调用组件绘制一次，避免原静态贴图、原炮塔头和新网格重复出现。不要再调用原版turretTop.DrawTurret来画同一炮塔，也不要让动态头部进入静态地图网格缓存，否则会产生残影。网格与物品遮挡由模型layer决定。

## 常用调用

参数用于设置转向角度、升降高度等数值；动作是一段预先定义的参数变化，例如后坐；挂接点是模型上命名的位置，例如炮口，供发射特效等功能查询坐标。

```csharp
var visual = building.GetComp<MechanicalVisualFramework.CompMechanicalVisual>();
var animation = visual?.Animation;
animation?.SetTarget("yaw", desiredAngle);       // 按模型里的速度转向
animation?.SetTarget("left_elevation", 20f);    // 示例模型自定义的参数名
animation?.Play("recoil_left");                 // 开火逻辑确认成功后再触发
```

这些名字属于示例模型，不是框架内置炮塔规则。SetTarget/Play遇到未知名称返回false；模型资源加载失败时，`Animation` 为 `null`。每次调用 `Play` 都会从头播放，因此应在动作开始时调用一次。目标追踪可在每个游戏更新周期调用 `SetTarget`，这会停止占用该参数的动作。

```csharp
UnityEngine.Vector3 position, direction;
if (animation != null &&
    animation.TryAnchor("muzzle_left", building.DrawPos, out position, out direction))
{
    // position 与画面炮口使用同一套父子变换和投影。
    // 把它交给你自己的发射/特效逻辑；direction 是地图平面的投影方向。
}
```

## 所有权和保存

CompMechanicalVisual持有独立VisualInstance/Animator。模型资源、预处理后的几何和材质共享；姿态、网格缓冲、动作进度不共享。首次通过 API 获取 `Visual` 或 `Animation` 时，才会创建所需的实例资源。

不使用组件而直接创建VisualInstance时，调用者必须在物件移除或适配器结束时Dispose；不要每帧创建。组件自身在PostDeSpawn中释放网格，重新生成时恢复状态。

参数按名称保存当前值、目标值；动作保存名称、播放时间、暂停状态。重排源节点/参数不会按错误数组索引还原。删除的名称会忽略；名称语义变更需要由作者决定迁移。模型网格不写入存档。

动画时间只在游戏逻辑更新（tick）时推进。PostDraw负责投影和绘制，不推进时间，不计算伤害、产电或命中。手动驱动的自定义宿主也必须遵守这条规则，避免不同帧率导致不同游戏结果。

## 限制

本版没有自动根据地图目标位置计算模型转角的通用瞄准功能。地图目标角度不能总是直接当作倾斜投影模型的yaw；炮口有高度时需自行处理投影反算。TryAnchor是视觉挂接点，不是碰撞体或三维弹道模拟。旋转建筑基座/载具运动、阵营染色等适配器由使用框架的MOD实现。

公开数组供调用方读取。通过SetTarget、Play等方法修改动画状态，模型资源由多个实例共享，应保持只读。

