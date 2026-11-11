# 维护指南

[English](handoff.en.md) · [中文首页](../README.md) · [本地验证](verification.md) · [版本与发布](release.md)

本指南介绍如何在本机重建框架、运行测试和维护资源。项目版本记录于`project.json`。修改实现前，阅读[运行时结构](architecture.md)、[模型格式](model-format.md)和[接口说明](api.md)。

## 配置环境

下载完整项目。制作模型需要Python 3.10+；修改C#需要Roslyn的`csc.exe`和对应版本的RimWorld安装。通过`Start.cmd`的Configure paths填写工具路径，或复制`ToolPaths.example.json`为`ToolPaths.local.json`后编辑。该配置仅保存在本地。

构建器使用1.6的`RimWorldWin64_Data/Managed`程序集，以及1.7游戏根目录的程序集。游戏更新改变文件布局或接口时，应检查实际安装，分别构建两个版本。

## 构建与测试

在工具箱中依次运行Build sample assets、Build framework DLLs和Validate。Validate检查资源与源码对应关系，并运行Python工具测试。

自动游戏测试命令：

```text
powershell -File Tools/Start-Examples.ps1 -Version 1.6 -AutoTest -Launch
powershell -File Tools/Start-Examples.ps1 -Version 1.7 -AutoTest -Launch
```

两条命令依次执行，等待前一次游戏退出后再开始下一次。测试器使用`Work/Runtime`中的游戏文件链接和`Work/Runs`中的独立配置，不修改日常游戏配置。测试结果写入对应运行目录的`results.txt`；自动测试完成后退出。

手动检查模型和控制面板时使用：

```text
powershell -File Tools/Start-Examples.ps1 -Version 1.7 -Launch
```

源码与DLL通过`Mod/BuildManifest.json`对应。模型、贴图或几何变化后重新生成资源，并通过BuildHashes核验。修改绘制逻辑后要检查实机画面，测试数值不代替视觉检查。

## 实现约定

- 游戏逻辑通过参数、动作和挂接点控制视觉。射击、能量和导航由使用框架的MOD实现。
- 模型路径属于声明该模型的MOD。只共享不可变资源，每个实例独立保存动画和网格。
- 1.7原生缓冲不与Unity兼容setter混用。
- 改变模型格式或参数含义时，检查旧存档中的名称与数值是否仍有效。
- 注释说明坐标、资源归属、版本差异和需要保留的约束。

## 本地文件与发布

测试过程、日志和工作记录存放在`Work`或`Local`，不会进入仓库和发布包。公开版本号与本地构建标签分别管理；具体检查、命名和上传顺序见[版本与发布](release.md)。

`Work/Runtime`包含指向游戏的链接，清理时不能递归进入这些链接。每个游戏版本最多保留两次已结束的测试；保留必要结果后清理旧测试目录。已交付压缩包保存在`Releases`，不覆盖或删除。容量预算见根目录`AGENTS.md`。
