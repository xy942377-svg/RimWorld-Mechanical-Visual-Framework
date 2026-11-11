# Mechanical Visual Framework / 机械动态视觉框架

框架版本：0.1.0。
作者：Grey·Oviin/OpenAI Assisted。许可：MIT，见上级目录的LICENSE。

## 中文说明

框架为机械模型提供连续转向、俯仰、后坐、升降和折叠动画，支持RimWorld 1.6和1.7。

将本MOD放在Core之后、使用框架的MOD之前启用。框架本身提供绘制和动画功能，建筑及其玩法由对应MOD添加。玩家无需安装Python、建模软件或编译器。

在MOD设置中可打开本说明和GitHub仓库。仓库提供源码、制作工具、教程与可选示例：
https://github.com/xy942377-svg/RimWorld-Mechanical-Visual-Framework

示例包包含转臂、折叠机构和三联装炮塔。在“杂项”菜单建造示例，选中后打开“动画控制”。示例炮塔演示转向、俯仰和后坐，不发射弹丸。

制作步骤见[中文上手教程](https://github.com/xy942377-svg/RimWorld-Mechanical-Visual-Framework/blob/main/docs/quickstart.md)。

## English

Framework version: 0.1.0.
Author: Grey·Oviin/OpenAI Assisted. License: MIT; see LICENSE in the parent folder.

The framework provides continuous rotation, elevation, recoil, lift and folding for mechanical models in RimWorld 1.6 / 1.7. Load it after Core and before mods that use it. Buildings and gameplay are supplied by those mods. Players do not need Python, modeling software or a compiler.

The settings page opens this guide and the GitHub repository above. The repository contains source, tools, tutorials and optional examples. Build examples under Misc and open Animation controls. The example turret demonstrates motion and does not fire projectiles.

For authoring steps, read the [English quick start](https://github.com/xy942377-svg/RimWorld-Mechanical-Visual-Framework/blob/main/docs/quickstart.en.md).

## 编译源码 / Build source

C#源码位于本MOD的`Source/`。在本MOD根目录运行以下命令，填写Roslyn编译器和两版游戏的实际路径。
C# source is in `Source/`. Run this command from the mod root with paths to Roslyn and the two game installations:

```text
powershell -File Source/Build.ps1 -CompilerPath <csc.exe> -Game16Root <game16> -Game17Root <game17>
```

其他MOD通过依赖声明使用框架DLL。发布自己的MOD时，保留该依赖，不再复制框架DLL。
Other mods reference the framework as a dependency and use its installed DLL.
