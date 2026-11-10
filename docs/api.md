# 游戏逻辑如何驱动视觉

最少只需 XML：ThingDef 使用 `Building_MechanicalDisplay`，comps 包含 `CompProperties_MechanicalVisual`，指定 model 和可选 autoplay。参考 Examples/Mechanisms/Defs/Mechanisms.xml。tickerType 必须为 Normal，drawerType 必须为 RealtimeOnly；示例 rotatable=false，朝向由模型 yaw 参数控制。

已有自定义建筑可以保留自己的游戏逻辑和 ThingComp；调用组件绘制一次，避免原静态贴图、原炮塔头和新网格重复出现。不要再调用原版 turretTop.DrawTurret 来画同一炮塔，也不要让动态头部进入静态地图网格缓存，否则会产生残影。网格与物品遮挡由模型 layer 决定。

## 常用调用

```csharp
var visual = building.GetComp<MechanicalVisualFramework.CompMechanicalVisual>();
var animation = visual?.Animation;
animation?.SetTarget("yaw", desiredAngle);       // 按模型里的速度转向
animation?.SetTarget("left_elevation", 20f);    // 示例模型自定义的参数名
animation?.Play("recoil_left");                 // 开火逻辑确认成功后再触发
```

这些名字属于示例模型，不是框架内置炮塔规则。SetTarget/Play 遇到未知名称返回 false；资源失败时 Animation 为 null。不要反复每 tick 调用 Play 来“保持播放”，因为它会每次从零开始。普通目标追踪可每 tick 调用 SetTarget，但会主动取消对应动作。

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

CompMechanicalVisual 持有独立 VisualInstance/Animator。模型、准备后的几何和材质共享；姿态、网格缓冲、动作进度不共享。API 获取 Visual/Animation 会惰性创建资源。

不使用组件而直接创建 VisualInstance 时，调用者必须在物件移除或适配器结束时 Dispose；不要每帧创建。组件自身在 PostDeSpawn 中释放网格，重新生成时恢复状态。

参数按名称保存当前值、目标值；动作保存名称、播放时间、暂停状态。重排源节点/参数不会按错误数组索引还原。删除的名称会忽略；名称语义变更需要由作者决定迁移。模型网格不写入存档。

动画只由游戏 tick 推进。PostDraw 负责投影和绘制，不推进时间，不计算伤害、产电或命中。手动驱动的自定义宿主也必须遵守这条规则，避免不同帧率导致不同游戏结果。

## 限制

本版无通用瞄准反解。地图目标角度不能总是直接当作倾斜投影模型的 yaw；炮口有高度时需自行处理投影反算。TryAnchor 是视觉挂接点，不是碰撞体或三维弹道模拟。旋转建筑基座/载具运动、阵营染色等适配器由消费 MOD 实现。

公开数组为低开销读取接口，外部应通过 SetTarget/Play 操作状态；不要直接写入 NaN、无限数、未知播放索引或共享资产。

