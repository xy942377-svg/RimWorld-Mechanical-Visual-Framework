# 创意工坊发布资料 / Steam Workshop listing materials

本目录保存工坊条目使用的封面、标题和中英文介绍。框架版本为0.1.0-candidate1，发布资料修订为workshop1。当前材料已在本地准备，Steam条目尚未发布。

This folder contains the cover, title and bilingual listing text for framework version 0.1.0-candidate1, package revision workshop1. These are local upload materials; the Steam listing has not been published.

## 文件 / Files

|文件 / File|用途 / Purpose|
|---|---|
|[标题 / Title](Workshop_Title_v1.txt)|工坊条目名称 / Workshop item title|
|[中文介绍](Workshop_Description_ChineseSimplified_v1.txt)|简体中文介绍，使用Steam BBCode|
|[English description](Workshop_Description_English_v1.txt)|English listing description in Steam BBCode|
|[中文更新说明](Workshop_ChangeNotes_ChineseSimplified_v1.txt)|首次发布时填写“初次发布”|
|[English change note](Workshop_ChangeNotes_English_v1.txt)|Use “Initial Release” for the first publication|
|[上传用封面 / Upload cover](../Mod/About/Preview.png)|1024×576 PNG，已放入运行包 / Included in the runtime package|
|[封面原图 / Cover master](Artwork/Cover_v1.png)|1672×941 PNG，供后续修改 / Retained for future edits|
|[封面提示词 / Image prompt](Artwork/Prompt_v1.txt)|内置image_gen生成时使用的完整提示词 / Full prompt for built-in image_gen|
|[检查记录 / Review](Review_v1.md)|字节数、链接、文件清单及验证范围 / Text sizes, links, package scope and checks|

## 上传步骤

1. 在仓库根目录运行`python Tools/package.py`，或使用已经生成的`Releases/RMVF-0.1.0-candidate1-workshop1-Workshop.zip`。
2. 将运行包中的`MechanicalVisualFramework`文件夹解压到游戏的`Mods`目录。如果已有同包名的本地测试副本，先将该副本移出`Mods`，避免同时安装两份。
3. 启动通过Steam安装的RimWorld，在MOD页面选中框架，使用游戏提供的上传功能。封面来自该MOD的`About/Preview.png`。
4. 条目名称使用上表的标题。将中英文介绍分别填写到对应语言的描述中，粘贴完整BBCode文本。首次更新说明使用“初次发布”或“Initial Release”。
5. 游戏版本标记为1.6、1.7。本框架仅依赖Core，工坊“必需物品”无需添加其他框架。示例包和开发工具通过介绍中的GitHub链接获取。
6. 提交后检查实际页面中的标题、封面、段落、列表和链接。确认发布成功后，再将真实工坊链接加入仓库首页和发布说明，并更新发布状态。

## Upload steps

1. Run `python Tools/package.py` from the repository root, or use the existing `Releases/RMVF-0.1.0-candidate1-workshop1-Workshop.zip`.
2. Extract its `MechanicalVisualFramework` folder into the game's `Mods` directory. If a local test copy with the same package ID is already installed, move that copy out of `Mods` first.
3. Start your Steam installation of RimWorld, select the framework in the mod menu and use the game's upload function. The cover is read from `About/Preview.png` in that mod folder.
4. Use the supplied title and paste each complete BBCode description into its corresponding language field. Use “Initial Release” for the first change note.
5. Mark game versions 1.6 and 1.7. The framework only needs Core, so it has no other Workshop items to list as requirements. Examples and authoring tools are linked on GitHub.
6. After submitting, inspect the actual title, cover, paragraphs, lists and links. Once publication succeeds, add the real Workshop URL to the repository home page and release guide, and update the publication status.

## 参考 / References

介绍参考了[Harmony](https://steamcommunity.com/sharedfiles/filedetails/?id=2009463077)和[Vanilla Expanded Framework](https://steamcommunity.com/sharedfiles/filedetails/?id=2023507013)区分玩家与开发者用途的写法。封面参考这些条目及[HugsLib](https://steamcommunity.com/sharedfiles/filedetails/?id=818773962)的标题层级与小图可读性，机械图形为本项目新绘制的插画。已查看的参考图片保留在各自原目录，本项目不收录这些图片。

The descriptions take cues from how Harmony and Vanilla Expanded Framework address players and authors separately. The cover references their title hierarchy and HugsLib's thumbnail readability; its mechanical illustration was created for this project. Reference artwork remains in its original location and is not included here.

原图由内置image_gen生成；上传图仅缩小并导出为PNG，没有改动画面内容。封面表达机械运动主题，游戏内实际示例见仓库的验证截图与可选示例包。

The master was generated with built-in image_gen. The upload image is a resized PNG export of the same artwork. The cover illustrates mechanical motion; repository verification screenshots and the optional example mod show the actual in-game examples.

Steam预览图限制和文本格式参考：[预览图上传](https://partner.steamgames.com/doc/api/ISteamUGC#SetItemPreview)、[描述长度](https://partner.steamgames.com/doc/api/ISteamRemoteStorage#k_cchPublishedDocumentDescriptionMax)、[BBCode格式](https://steamcommunity.com/comment/Announcement/formattinghelp)。
