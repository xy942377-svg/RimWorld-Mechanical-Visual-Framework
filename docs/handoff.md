# 开发交接说明

[English](handoff.en.md) · [中文首页](../README.md) · [当前版本](status.md) · [验证记录](verification.md) · [发布与下载](release.md)

当前框架版本为0.1.0-candidate1，发布资料修订为workshop1（2026-11-11）。入口为仓库README，版本与发布状态记录于project.json和[当前版本](status.md)。修改前阅读[运行时结构](architecture.md)、[模型格式](model-format.md)和[接口说明](api.md)。

本次修订加入工坊封面、中英文条目介绍和上传说明，见[工坊发布资料](../Workshop/README.md)。运行包包含上传用封面；发布文案和封面原图只随开发资料提供。C#源码、DLL、模型、依赖和存档字段均沿用docs3版本。

## 建立环境

下载完整仓库。运行预编译示例不需要开发软件；制作模型需要已有Python 3.10+；修改C# 需要已有Roslyn csc.exe与本人持有的对应RimWorld安装。复制ToolPaths.example.json为ToolPaths.local.json或用Start.cmd的Configure填写。在配置中填写本机实际路径。

构建顺序：BuildAssets → BuildCode → Validate；随后顺序执行Test16、Test17。这些是Tools/Toolbox.ps1的操作，也可通过Start.cmd菜单运行。测试器使用Work/Runtime下指向本人游戏的文件链接和独立Work/Runs存档，不改正常ModsConfig。一次只运行一个版本；自动测试将在完成后退出。

手动体验时，在仓库根目录运行：

```text
powershell -File Tools/Start-Examples.ps1 -Version 1.7 -Launch
```

加入`-AutoTest`可运行自动测试；将版本改为`-Version 1.6`可选择另一版游戏。

首版C# 构建器针对已验证游戏布局：1.6的Managed子目录、1.7的游戏根目录。游戏更新改变程序集/API时，应检查实际安装，不能拿另一版DLL混用。

## 接口约定

- 游戏逻辑通过参数、动作和挂接点接口控制视觉；绘制函数和模型加载器只处理显示与资源。
- 射击、能量和导航功能由使用框架的MOD实现。
- 资源路径属于使用框架的MOD，不能硬编码框架根目录或单个模型全局变量。
- 只共享不可变资产；实例动画和网格不能共享。
- 模型格式改变时更新version，并检查已有存档中的参数名是否仍表示相同含义。转轴和几何的改动保存在源模型中，然后重新构建。
- 1.7原生缓冲不能与Unity兼容setter混用。
- 几何与贴图修改都必须重新构建并通过BuildHashes / BuildManifest核验。
- 节点坐标、轮廓和模型几何的说明写在相应源码；工具行为见各脚本顶部及quickstart。

## 验证与交付

Tools/validate.py检查XML、语言键、几何、构建哈希、大小；Verification/test_tools.py覆盖新项目生成、输入约束、可重复构建与GLB坐标/层级。FrameworkProbe.cs在真实游戏中检查变换、关节隔离、播放状态、Scribe恢复和游戏更新驱动动画的过程。修改绘制应再检查实际截图，不把数值通过当作画面通过。

源与DLL通过Mod/BuildManifest.json对应；每个版本的实际测试范围见verification.md。纯网页链接/文字修改无需重跑机械运动测试，但须重编译变化的C# 并校验哈希。

只用Tools/package.py白名单打包。Releases已交付ZIP不覆盖；框架版本变更时同步project.json、FrameworkMod.Version和CHANGELOG；仅修订文档、说明文字或建模资料时更新project.json中的revision和CHANGELOG，保留框架版本。Downloads保留可直接安装的版本ZIP；GitHub Code → Download ZIP下载完整项目。Steam上传使用解压后的运行包。Modeling目录随开发资料提供，不放入运行包或动画示例包。

护盾建模案例运行：

```text
python Modeling/ShieldGenerator/build_model.py --output Work/ShieldModel
```

生成OBJ、材质和结构检查结果。模型生成使用Python标准库；制作贴图的方法见[案例说明](../Modeling/ShieldGenerator/README.md)。

Work中的运行时链接绝不能作为普通子目录递归删除。清理前解析绝对路径、确认在项目Work下、检查链接；先保留必要证据，再删除没有链接的已结束Runs子目录。每版本最多留两次完成测试。预算详见根目录AGENTS.md。

