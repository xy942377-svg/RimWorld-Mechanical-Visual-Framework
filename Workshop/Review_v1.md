# 工坊发布资料检查 / Workshop material review

日期：2026-11-11。框架：0.1.0-candidate1。资料修订：workshop1。
基线：docs3，Git提交`1d3b093682ed9041acec58dcba9e683ad4820122`。

Date: 2026-11-11. Framework: 0.1.0-candidate1. Package revision: workshop1.
Baseline: docs3 at the commit above.

## 内容依据 / Content checked

|介绍中的内容 / Listing claim|项目依据 / Source|
|---|---|
|转向、俯仰、后坐、升降、折叠 / Mechanical motion|[框架组件](../Mod/Source/Component.cs)、[模型格式](../docs/model-format.md)|
|动作播放、参数控制、状态保存 / Playback, parameters and saving|[接口说明](../docs/api.md)、[验证记录](../docs/verification.md)|
|仅依赖Core，支持1.6、1.7 / Core dependency and game versions|[MOD元数据](../Mod/About/About.xml)、[构建清单](../Mod/BuildManifest.json)|
|玩家运行包与开发工具分开 / Runtime and authoring files|[打包脚本](../Tools/package.py)、[下载说明](../docs/release.md)|
|三个动画示例，炮塔不发射 / Three visual examples; no turret firing|[示例定义](../Examples/Mechanisms/Defs)、[上手教程](../docs/quickstart.md)|
|护盾建模案例仅作开发参考 / Offline shield modeling case|[案例说明](../Modeling/ShieldGenerator/README.md)|
|作者与许可 / Attribution and license|[LICENSE](../LICENSE)、[NOTICE](../NOTICE.md)|

中英文介绍逐段审读，按“用途—安装—动画功能—制作工具—示例—作者”组织。具体操作使用完整句子，工具和按钮使用实际名称。已核对两种语言的功能范围、依赖、加载顺序和下载方式；文本没有把示例动画写成战斗功能，也没有加入无依据的兼容性或性能承诺。

Both descriptions were read paragraph by paragraph. They cover purpose, installation, animation, authoring tools, examples and attribution. Instructions use complete sentences and actual tool names. Feature scope, dependencies, load order and downloads agree across languages.

## 文本格式 / Text format

以下统计包含全部BBCode、链接和换行。文件为UTF-8，无BOM。LF与CRLF两种换行下均低于本项目每种语言7500字节的上限。

Counts include all BBCode, URLs and line breaks. Files use UTF-8 without a BOM and remain below the project's 7,500-byte limit per language with either LF or CRLF endings.

|文本 / Text|实际文件字节 / Raw bytes|LF字节|CRLF字节|BOM字节|
|---|---:|---:|---:|---:|
|简体中文 / Chinese|3595|3595|3636|0|
|英文 / English|3889|3889|3930|0|

标题为54个UTF-8字节。每种介绍使用5个真实`[h1]`标题、1组列表和6个链接；标签配对检查通过。作者名称均为Grey·Oviin/OpenAI Assisted。

The title is 54 UTF-8 bytes. Each description has five `[h1]` headings, one list and six links. BBCode tags are balanced. Both include Grey·Oviin/OpenAI Assisted.

两份介绍共使用7个不同的公开GitHub地址：项目首页、中文与英文上手教程、Downloads目录、护盾建模案例、LICENSE和Issues。已通过GitHub连接逐项读取对应资源，返回成功；本地路径也已核对。

The descriptions use seven distinct public GitHub targets: the repository, both quick-start guides, Downloads, the shield modeling case, LICENSE and Issues. Each target was checked through the GitHub connection, and local repository paths were checked.

## 封面 / Cover

- 原图：1672×941，内置image_gen生成，提示词见[Prompt_v1.txt](Artwork/Prompt_v1.txt)。
- 上传图：1024×576 PNG，891563字节，保留原图构图。
- 已检查完整图和320×180缩略图，标题拼写、边距和机械图形均可辨认。
- 上传图位于`Mod/About/Preview.png`。原图和提示词只随开发资料提供。

The master was generated with built-in image_gen. The 1024×576 upload export is 891,563 bytes. Full-size and 320×180 thumbnail inspections confirmed readable titles and margins. The master and prompt are authoring materials; only the upload preview is included in the runtime package.

上传图SHA-256：
`44dadc0a7c72705d42b3e0874a0179104e6827d8e2f5fc8689816489a8dae30f`

## 验证范围 / Validation scope

已执行`Tools/validate.py`，XML、双语键、三个模型资源、源码与两版DLL哈希及容量预算检查通过。本次未修改C#源码、DLL、模型、依赖或存档字段，因此沿用docs3构建及已有1.6.4871、1.7.5000实机记录，没有重新运行游戏动画测试。

`Tools/validate.py` passed XML parsing, translation-key parity, all three model checks, source/DLL hashes and size budgets. Runtime code, DLLs, models, dependencies and save fields are unchanged. The docs3 builds and existing game tests apply; no new in-game animation test was run for this artwork and documentation revision.

打包使用`Tools/package.py`白名单。运行包仅包含`Mod`；示例包仅包含`Examples/Mechanisms`；工坊文案、封面原图和提示词只进入开发包。压缩包和文件哈希由打包工具写入校验清单；交付文件位于`Releases`。

Packages use the `Tools/package.py` whitelist. Runtime and example archives contain only their respective mod folders. Publisher text, the master cover and its prompt belong to the developer package. Packaging produces archive and file checksum manifests under `Releases`.

Steam条目尚未上传；BBCode在实际工坊页面中的显示和最终发布状态，留待上传后核对。Steam规则来源见[发布资料说明](README.md#参考--references)。

The Steam listing has not been uploaded. Actual Workshop rendering and publication status must be checked after upload. Steam documentation links are in the [publisher guide](README.md#参考--references).
