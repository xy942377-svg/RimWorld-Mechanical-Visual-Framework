# 开发交接说明

入口是仓库 README；不依赖任何先前聊天、旧 MOD 或私有路径。当前版本和发布状态在 project.json / docs/status.md。先读 architecture、model-format 和 api，再改对应实现。

## 建立环境

下载完整仓库。运行预编译示例不需要开发软件；制作模型需要已有 Python 3.10+；修改 C# 需要已有 Roslyn csc.exe 与本人持有的对应 RimWorld 安装。复制 ToolPaths.example.json 为 ToolPaths.local.json 或用 Start.cmd 的 Configure 填写。示例配置为空值，不假定任何盘符或开发者名字。

构建顺序：BuildAssets → BuildCode → Validate；随后顺序执行 Test16、Test17。测试器使用 Work/Runtime 下指向本人游戏的文件链接和独立 Work/Runs 存档，不改正常 ModsConfig。一次只运行一个版本；测试将在完成后退出。要手动体验可运行 Start-Examples.ps1 -Version 1.7 -Launch；自动测试用 -AutoTest -Launch。

首版 C# 构建器针对已验证游戏布局：1.6 的 Managed 子目录、1.7 的游戏根目录。游戏更新改变程序集/API 时，应检查实际安装，不能拿另一版 DLL 混用。

## 接口约定

- Actor 游戏逻辑只调用参数/动作/挂接点，不能塞入 Draw 或模型加载器。
- 带真实射击/能量/导航的例子放消费 MOD；Core 不内置武器规则。
- 资源路径属于消费 MOD，不能硬编码框架根目录或单个模型全局变量。
- 只共享不可变资产；实例动画和网格不能共享。
- Asset 格式改动要更新 version 并处理存档参数名语义；不要只改一个例子的转轴而不更新源模型。
- 1.7 原生缓冲不能与 Unity 兼容 setter 混用。
- 几何与贴图修改都必须重新构建并通过 BuildHashes / BuildManifest 核验。
- Node 坐标、轮廓和模型几何的说明写在相应源码；工具行为见各脚本顶部及 quickstart。

## 验证与交付

Tools/validate.py 检查 XML、语言键、几何、构建哈希、大小；Verification/test_tools.py 覆盖新项目生成、输入约束、可重复构建与 GLB 坐标/层级。FrameworkProbe.cs 在真实游戏中检查变换、关节隔离、播放状态、Scribe 恢复和游戏 tick 接线。修改绘制应再检查实际截图，不把数值通过当作画面通过。

源与 DLL 通过 Mod/BuildManifest.json 对应；每个版本的实际测试范围见 verification.md。纯网页链接/文字修改无需重跑机械运动测试，但须重编译变化的 C# 并校验哈希。

只用 Tools/package.py 白名单打包。Releases 已交付 ZIP 不覆盖；新版本改 project.json、FrameworkMod.Version 和 CHANGELOG 后重新打包。Downloads 保留可直接安装的版本 ZIP；GitHub Code → Download ZIP 下载完整项目。Steam 上传只选解压后的运行包，不包含工具、测试档或游戏链接。

Work 中的运行时链接绝不能作为普通子目录递归删除。清理前解析绝对路径、确认在项目 Work 下、检查链接；先保留必要证据，再删除没有链接的已结束 Runs 子目录。每版本最多留两次完成测试。预算详见根目录 AGENTS.md。

