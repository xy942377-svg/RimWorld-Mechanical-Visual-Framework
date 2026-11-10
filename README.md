# RimWorld Mechanical Visual Framework
# 环世界机械动态视觉框架

[English](README.en.md) · [上手教程](docs/quickstart.md) · [模型格式](docs/model-format.md) · [接口说明](docs/api.md) · [开发交接](docs/handoff.md)

机械动态视觉框架为RimWorld中的机械模型提供连续转向、独立俯仰、后坐、升降和折叠动画。模型由多个部件组成，每个部件有自己的转轴，父部件的运动会带动子部件。游戏根据当前姿态绘制模型，并添加平面明暗和粗描边。

框架版本：**0.1.0-candidate1**；支持RimWorld **1.6 / 1.7**。本次资料修订为**docs2**，包含文字修订和护盾建模示例。作者：Grey·Oviin/OpenAI Assisted。

## 下载与安装

- [框架运行包](https://github.com/xy942377-svg/RimWorld-Mechanical-Visual-Framework/blob/main/Downloads/RMVF-0.1.0-candidate1-docs2-Workshop.zip)：解压后，将`MechanicalVisualFramework`文件夹放入游戏的`Mods`目录。
- [动画示例包](https://github.com/xy942377-svg/RimWorld-Mechanical-Visual-Framework/blob/main/Downloads/RMVF-0.1.0-candidate1-docs2-Examples.zip)：解压后，将`RMVFExamples`文件夹放入`Mods`，用于体验转臂、升降折叠机构和三联装炮塔。
- **完整开发资料**：使用本页的 **Code → Download ZIP**，包含源码、模型、制作工具和教程。下载后先解压，再运行工具。

在游戏中按 **Core → Mechanical Visual Framework → RMVF · Mechanical examples** 的顺序启用。框架仅依赖Core，示例包需要框架。框架本身提供绘制和动画功能；建筑及其玩法由使用框架的MOD添加。

创意工坊条目尚未发布，当前通过本仓库下载安装。

## 体验与制作

安装示例包后，在“杂项”菜单建造示例，选中建筑并打开“动画控制”。三联装炮塔演示连续转向、三根炮管的独立俯仰和后坐，不发射弹丸。

制作自己的MOD时，双击完整项目中的`Start.cmd`，先用 **Configure paths** 配置Python，再选择 **New mod**。修改生成的模型文件后，按[上手教程](docs/quickstart.md)构建资源并重启游戏。

玩家可直接使用预编译的运行文件。模型制作工具需要Python 3.10+；修改框架C#源码还需要Roslyn编译器和对应版本的游戏程序集。工具箱菜单使用英文，游戏内按钮和说明提供英文、简体中文。

## 功能与示例

|内容|用途|
|---|---|
|部件与转轴|设置父子关系、局部坐标和独立旋转中心|
|动画参数|控制转速、俯仰、位移和均匀缩放|
|动作片段|播放、循环、暂停和同时运行使用不同参数的动作|
|接口与存档|由游戏逻辑控制动画，查询炮口等挂接点，保存姿态和播放进度|
|制作工具|创建MOD模板、编译JSON模型、导入符合要求的GLB模型、校验和打包|
|运行示例|100个三角面的转臂、380个三角面的折叠机构、5344个三角面的三联装炮塔|
|[护盾建模示例](Modeling/ShieldGenerator/README.md)|用同一个构件生成四角结构，将基座与球盖分开导出|

框架适合由刚性部件组成的机械。部件可以旋转、平移和缩放；骨骼蒙皮、柔性变形和自动关节求解尚未实现。射击、产电、护盾拦截等玩法需要由对应MOD实现。GLB导入条件见[导入步骤](docs/quickstart.md#4-从建模软件接入)。

## 文档与许可

`Mod/`包含框架及源码；`Examples/`包含游戏示例；`Authoring/`包含示例源模型；`Modeling/`包含建模案例；`Templates/`提供起步模型；`Tools/`包含制作工具；`docs/`和`Verification/`分别存放说明与测试。

代码、工具、文档和原创示例采用[MIT许可](LICENSE)，允许修改、再发布和用于其他MOD，保留版权与许可说明。素材归属见[NOTICE](NOTICE.md)，测试环境和结果见[验证记录](docs/verification.md)。
