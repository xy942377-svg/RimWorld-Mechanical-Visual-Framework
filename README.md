# RimWorld Mechanical Visual Framework
# 环世界机械动态视觉框架

[English](README.en.md) · [上手教程](docs/quickstart.md) · [模型格式](docs/model-format.md) · [接口说明](docs/api.md) · [开发交接](docs/handoff.md)

这个框架用于在 RimWorld 中显示可以活动的机械模型。MOD 作者可以分别设置各个部件的旋转中心，制作炮塔转向、炮管抬升与后坐、平台升降和机械折叠等动画。部件之间可以建立父子关系，例如炮塔转动时，安装在它上面的炮管会一起转动。

游戏运行时，框架根据各部件的位置和角度，将三维模型投影到地图画面上，并按各个面的朝向计算明暗、绘制粗描边。

框架版本：**0.1.0-candidate1**；支持RimWorld **1.6 / 1.7**。本次发布资料修订为**workshop1**，加入工坊封面、中英文介绍和上传说明。作者：Grey·Oviin/OpenAI Assisted。

## 下载与安装

- [框架运行包](https://github.com/xy942377-svg/RimWorld-Mechanical-Visual-Framework/blob/main/Downloads/RMVF-0.1.0-candidate1-workshop1-Workshop.zip)：解压后，将`MechanicalVisualFramework`文件夹放入游戏的`Mods`目录。
- [动画示例包](https://github.com/xy942377-svg/RimWorld-Mechanical-Visual-Framework/blob/main/Downloads/RMVF-0.1.0-candidate1-workshop1-Examples.zip)：解压后，将`RMVFExamples`文件夹放入`Mods`，用于体验转臂、升降折叠机构和三联装炮塔。
- **完整开发资料**：使用本页的 **Code → Download ZIP**，包含源码、模型、制作工具和教程。下载后先解压，再运行工具。

在游戏中按 **Core → Mechanical Visual Framework → RMVF · Mechanical examples** 的顺序启用。框架仅依赖Core，示例包需要框架。框架本身提供绘制和动画功能；建筑及其玩法由使用框架的MOD添加。

创意工坊条目尚未发布，当前通过本仓库下载安装。

## 体验与制作

安装示例包后，在“杂项”菜单建造示例，选中建筑并打开“动画控制”。三联装炮塔演示连续转向、三根炮管的独立俯仰和后坐，不发射弹丸。

制作自己的 MOD 时，按以下步骤操作：

1. 下载并解压完整项目，双击其中的 `Start.cmd` 打开工具箱。
2. 选择 **Configure paths（配置路径）**，填写 Python 程序的位置，例如 `C:/Python312/python.exe`。
3. 再次打开工具箱，选择 **New mod（新建 MOD）**，填写新 MOD 的保存目录、唯一标识和名称。
4. 编辑新 MOD 中的 `Authoring/model.json`，按[上手教程](docs/quickstart.md)中的命令生成游戏所需的资源文件。
5. 将新 MOD 放入游戏的 `Mods` 目录，在框架之后启用。修改模型并重新生成资源后，重启游戏查看效果。

玩家可直接使用预编译的运行文件。模型制作工具需要Python 3.10+；修改框架C#源码还需要Roslyn编译器和对应版本的游戏程序集。工具箱菜单使用英文，游戏内按钮和说明提供英文、简体中文。

## 功能与示例

|内容|用途|
|---|---|
|部件与转轴|设置父子关系、局部坐标和独立旋转中心|
|动画参数|控制转速、俯仰、位移和均匀缩放|
|动作片段|将一组参数变化保存为动作，支持播放、循环、暂停和同时播放互不冲突的动作|
|接口与存档|由游戏逻辑控制动画，获取炮口等指定位置的坐标，保存部件状态和播放进度|
|制作工具|创建MOD模板、编译JSON模型、导入符合要求的GLB模型、校验和打包|
|运行示例|100个三角面的转臂、380个三角面的折叠机构、5344个三角面的三联装炮塔|
|[护盾建模示例](Modeling/ShieldGenerator/README.md)|用同一个构件生成四角结构，将基座与球盖分开导出|

框架适合由刚性部件组成的机械。部件可以旋转、平移和缩放；骨骼蒙皮、柔性变形和自动关节求解尚未实现。射击、产电、护盾拦截等玩法需要由对应MOD实现。GLB导入条件见[导入步骤](docs/quickstart.md#4-从建模软件接入)。

## 文档与许可

详细指南均提供中英文版本，可从每页顶部切换语言。

|指南|内容|
|---|---|
|[上手教程](docs/quickstart.md)|安装、创建MOD、编辑模型和导入GLB|
|[模型格式](docs/model-format.md)|坐标、层级、参数、动作和编译产物|
|[接口说明](docs/api.md)|游戏逻辑调用、挂接点、资源所有权和保存|
|[运行时结构](docs/architecture.md)|加载、动画、绘制缓冲和性能测量|
|[开发交接](docs/handoff.md)|环境配置、构建、测试和维护约定|
|[发布与下载](docs/release.md)|获取文件、打包和创意工坊发布|
|[当前版本](docs/status.md)|版本、发布状态和后续工作|
|[验证记录](docs/verification.md)|测试环境、检查项目和已验证范围|

`Mod/`包含框架及源码；`Examples/`包含游戏示例；`Authoring/`包含示例源模型；`Modeling/`包含建模案例；`Templates/`提供起步模型；`Tools/`包含制作工具；`docs/`和`Verification/`分别存放说明与测试。

代码、工具、文档和原创示例采用[MIT许可](LICENSE)，允许修改、再发布和用于其他MOD，保留版权与许可说明。素材归属见[NOTICE](NOTICE.md)，测试环境和结果见[验证记录](docs/verification.md)。
