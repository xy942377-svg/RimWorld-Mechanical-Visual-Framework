# 版本与发布

[English](release.en.md) · [中文首页](../README.md) · [维护指南](handoff.md)

## 获取正式版

完整源码、模型、制作工具与教程可通过仓库首页的 **Code → Download ZIP** 获取。工坊发布用的成品包、介绍文本和上传资料在本地整理交付。

手动安装时，将仓库中的`Mod`文件夹复制到游戏的`Mods`目录并改名为`MechanicalVisualFramework`。可选示例位于`Examples/Mechanisms`，复制后改名为`RMVFExamples`。在游戏中按Core、框架、示例的顺序启用。

创意工坊条目尚未发布。GitHub保留开发者需要的代码、运行资源、工具、教程和示例；工坊文案及成品压缩包不提交到仓库。

## 本地开发与正式版本号

所有构建、测试和试验均在本地进行。GitHub只接收已完成本地检查、游戏测试和包内容检查的正式版。测试脚本可以随源码提供，测试日志、存档、临时图片和工作记录留在本地；不在GitHub Actions中运行测试。

正式版统一使用`主版本.次版本.修订号`，对应Git标签`v主版本.次版本.修订号`。首个正式版为`v0.1.0`。小修订使用`v0.1.1`、`v0.1.2`；新增功能使用下一次版本；不兼容的接口变更使用下一主版本。文档或资源发生公开更新时，也分配新的正式版本号，不覆盖已有交付文件。

正式包统一命名：

- `RMVF-v0.1.1-Runtime.zip`
- `RMVF-v0.1.1-Examples.zip`
- `RMVF-v0.1.1-DeveloperKit.zip`

本地构建使用独立标签，例如`RMVF-local-check01-Runtime.zip`。这些标签不占用正式版本号，也不上传GitHub。

## 本地检查与打包

1. 按[维护指南](handoff.md)构建模型和两版DLL，运行工具测试、1.6与1.7实机测试，并检查模型画面。
2. 检查文档、链接、作者信息、许可证和待发布文件内容；将最终正式版本号同步到`project.json`、`FrameworkMod.Version`、文档和更新记录。修改C#后重新编译和测试。
3. 确认检查通过后，将`project.json`中的`status`设为`Stable`。执行：

```text
python Tools/check_release.py
python Tools/package.py --stable
```

检查工具核对当前源码、DLL、模型和本地游戏测试结果，在`Local/release-check.json`记录这次检查对应的文件。正式打包时再次比对；文件发生变化就需要重新检查。

生成文件位于本地`Releases`。核对ZIP内的文件清单、内容和哈希后，在本地交付压缩包。工坊介绍等编辑文件存放在`Local/Workshop`，与待上传的MOD目录一并交付。GitHub只提交检查通过的源码、运行资源、工具、教程和示例，并创建对应正式标签。

制作本地临时包时使用：

```text
python Tools/package.py --label check01
```

不指定参数时，打包工具使用时间戳作为本地标签。工具箱的Package选项也只生成本地包。
