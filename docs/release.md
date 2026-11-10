# 发布与下载

[English](release.en.md) · [中文首页](../README.md) · [开发交接](handoff.md)

## 安装游戏内容

在仓库首页下载框架运行包和可选的动画示例包。解压后，分别将`MechanicalVisualFramework`和`RMVFExamples`文件夹放入游戏的`Mods`目录，按Core、框架、示例的顺序启用。

框架支持RimWorld 1.6和1.7。玩家运行时只需游戏及所用MOD的依赖。

## 获取开发资料

使用GitHub的 **Code → Download ZIP** 获取完整项目。解压后可阅读教程、编辑模型并使用工具箱。护盾建模案例位于`Modeling/ShieldGenerator`。

`Downloads/`提供可直接安装的运行包和示例包，以及这两个下载文件的SHA-256校验值。完整开发资料从仓库下载；`DeveloperKit.zip`由本地打包工具生成。

## 维护发布包

完成[开发交接说明](handoff.md)中的检查后，在仓库根目录运行：

```text
python Tools/package.py
```

工具在`Releases/`生成运行包、示例包和完整开发包。每个ZIP包含文件校验清单，同目录生成三个压缩包的SHA-256清单。

框架版本记录于`project.json`的`version`。文档、示例资料、说明文字或封面修订使用独立的`revision`，并加入压缩包文件名；当前为`workshop1`。已交付的同名压缩包保留原文件，新修订使用新文件名。

创意工坊上传使用运行包解压后的MOD目录。封面已放在`Mod/About/Preview.png`；中英文介绍、标题、首次发布说明和操作步骤见[工坊发布资料](../Workshop/README.md)。该目录只随完整开发资料提供。当前条目尚未发布。
