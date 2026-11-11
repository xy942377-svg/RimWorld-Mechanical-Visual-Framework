# 版本与发布

[English](release.en.md) · [中文首页](../README.md) · [维护指南](handoff.md)

## 获取正式版

[Downloads](../Downloads/README.md)提供框架运行包、可选的动画示例包和SHA-256校验值。完整源码、模型、制作工具与教程可通过仓库首页的 **Code → Download ZIP** 获取。

运行包解压后的`MechanicalVisualFramework`文件夹放入游戏的`Mods`目录；示例包中的`RMVFExamples`放在同一目录。在游戏中按Core、框架、示例的顺序启用。

创意工坊条目尚未发布，目前通过GitHub下载安装。

## 本地开发与正式版本号

所有构建、测试和试验均在本地进行。GitHub只接收已完成本地检查、游戏测试和包内容检查的正式版。测试脚本可以随源码提供，测试日志、存档、临时图片和工作记录留在本地；不在GitHub Actions中运行测试。

正式版统一使用`主版本.次版本.修订号`，对应Git标签`v主版本.次版本.修订号`。首个正式版为`v0.1.0`。小修订使用`v0.1.1`、`v0.1.2`；新增功能使用下一次版本；不兼容的接口变更使用下一主版本。文档或资源发生公开更新时，也分配新的正式版本号，不覆盖已有交付文件。

正式包统一命名：

- `RMVF-v0.1.0-Runtime.zip`
- `RMVF-v0.1.0-Examples.zip`
- `RMVF-v0.1.0-DeveloperKit.zip`

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

生成文件位于`Releases`。核对ZIP内的文件清单、内容和哈希后，将运行包与示例包复制到`Downloads`，更新该目录的校验值和下载说明。最后再提交到GitHub并创建对应正式标签。失败或未完成的测试文件继续留在本地。

制作本地临时包时使用：

```text
python Tools/package.py --label check01
```

不指定参数时，打包工具使用时间戳作为本地标签。工具箱的Package选项也只生成本地包。

## 工坊发布

工坊上传使用运行包中的MOD目录。封面位于`About/Preview.png`，中英文正文见[工坊介绍](../Workshop/README.md)。首次发布的更新说明使用“初次发布”或“Initial Release”。

发布后核对实际页面中的图片、标题、列表和链接，再将工坊地址加入仓库首页。工坊运行包保留C#源码、许可证和必要使用说明；开发工具、建模案例和测试工具随GitHub完整项目提供。
