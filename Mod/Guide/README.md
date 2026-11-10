# Mechanical Visual Framework / 机械动态视觉框架

Version 0.1.0-candidate1. Author: Grey·Oviin/OpenAI Assisted. License: MIT (see ../LICENSE).

This is the player runtime for RimWorld 1.6 / 1.7. Enable it after Core and before mods which depend on it. It does not add ordinary gameplay buildings by itself.

这是运行框架，在 Core 后、依赖它的 MOD 前启用。框架本身不添加正式玩法建筑。英文和简体中文界面已内置。设置页可打开本说明、GitHub 仓库并复制版本信息。

完整源码、可选示例、制作工具、入门教程均位于同一个仓库：
https://github.com/xy942377-svg/RimWorld-Mechanical-Visual-Framework

在仓库中阅读 README.md、docs/quickstart.md、docs/model-format.md、docs/api.md。下载项目后，Examples/Mechanisms 是单独启用的示例 MOD：杂项菜单中的转臂、折叠机构和三联装炮塔视觉例子。示例炮塔不包含攻击逻辑。

模型作者可用开发工具包的 Start.cmd 创建自己的 MOD、导入刚性 GLB、编译资源和验证。仅使用框架的玩家不需要 Python、Blender 或编译器。Runtime dependencies: RimWorld Core only.

Source is included in Source/. To rebuild this standalone runtime, provide your existing compiler and owned game roots explicitly:
powershell -File Source/Build.ps1 -CompilerPath <csc.exe> -Game16Root <game16> -Game17Root <game17>

Do not distribute RimWorld assemblies. Do not copy this runtime DLL into every dependent mod; declare the dependency instead.

