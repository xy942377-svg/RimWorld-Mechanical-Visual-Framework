# 发布与下载

项目只使用 Steam Workshop 与本 GitHub。仓库的 README、docs、Source 和 Tools 是同一份维护来源。

面向玩家：Downloads 中的 Workshop ZIP；解压目录直接放入 Mods。示例是单独的 Examples ZIP，按需启用。
面向作者：GitHub 的 Code → Download ZIP，或者下载开发包。下载完整项目即可离线读教程并编辑模型；首次配置本机工具路径后可重建。

本地运行 `python Tools/package.py` 生成三份内容选择不同的 ZIP：
Workshop（纯运行 MOD，附源码和简明说明）、Examples（可选示例 MOD）、DeveloperKit（完整开发项目）。
这三份是同一 GitHub 项目的下载选项，不是三套网站或独立维护工程。
打包前验证资源/程序集哈希；ZIP 内含文件校验清单，Releases 中有 SHA256 清单。历史 ZIP 不原地重写。

Steam 条目建议标题：Mechanical Visual Framework / 机械动态视觉框架。
说明应列明 1.6/1.7、Core 依赖、这是供其他 MOD 使用的刚性机械视觉框架，并附本仓库地址。
不应把视觉例子描述为已经平衡完成的战斗炮塔，也不应宣传尚未实现的蒙皮/物理/IK 功能。
正式上传前用可见游戏窗口检查两版外观，准备适当的封面，并确认发布说明与实际候选状态相符。

许可证：MIT，保留 Grey·Oviin/OpenAI Assisted 署名和许可文本。玩家运行不需要下载建模软件或 Python。

