# AiNiee 项目详细目录结构说明

## 项目概述
AiNiee 是一个专业的 AI 翻译工具，采用模块化架构设计，支持多种文件格式的翻译任务，特别擅长游戏本地化翻译。

## 项目根目录
```
AiNiee/
├── AiNiee.py                    # 主程序入口文件
├── hyperscan.py                 # 高性能正则表达式库
├── LICENSE                      # 开源许可证
├── README.md                    # 中文说明文档
├── README_EN.md                 # 英文说明文档
├── requirements.txt             # Python依赖包列表
├── requirements_no_deps.txt     # 精简依赖包列表
├── .gitignore                   # Git忽略文件配置
```

## 核心模块目录 (ModuleFolders/)

### 1. 缓存管理模块 (Cache/)
```
Cache/
├── BaseCache.py                 # 缓存基类
├── CacheFile.py                 # 文件缓存类
├── CacheItem.py                 # 缓存项类
├── CacheManager.py              # 缓存管理器
└── CacheProject.py              # 项目缓存类
```
**功能**: 管理翻译进度缓存，支持断点续传和项目状态持久化

### 2. 文件访问器模块 (FileAccessor/)
```
FileAccessor/
├── BabeldocPdfAccessor.py       # PDF文档访问器
├── DocxAccessor.py              # Word文档访问器
├── EpubAccessor.py              # Epub电子书访问器
├── ZipUtil.py                   # ZIP工具类
└── README.md                    # 读写器系统编写指南
```
**功能**: 提供各种文件格式的底层访问接口

### 3. 文件转换器模块 (FileConverter/)
```
FileConverter/
├── BaseConverter.py             # 转换器基类
└── OfficeFileConverter.py       # Office文件转换器
```
**功能**: 处理文件格式转换

### 4. 文件输出器模块 (FileOutputer/)
```
FileOutputer/
├── AutoTypeWriter.py            # 自动类型写入器
├── BaseWriter.py                # 写入器基类
├── DirectoryWriter.py           # 目录写入器
├── FileOutputer.py              # 文件输出器主类
├── WriterUtil.py                # 写入工具类
├── BabeldocPdfWriter.py         # PDF写入器
├── DocxWriter.py                # Word文档写入器
├── EpubWriter.py                # Epub电子书写入器
├── I18nextWriter.py             # I18next本地化文件写入器
├── LrcWriter.py                 # LRC歌词文件写入器
├── MdWriter.py                  # Markdown文件写入器
├── MToolWriter.py               # Mtool游戏文件写入器
├── OfficeConversionWriter.py    # Office转换写入器
├── ParatranzWriter.py           # Paratranz项目写入器
├── PoWriter.py                  # Po本地化文件写入器
├── RenpyWriter.py               # Renpy游戏文件写入器
├── SrtWriter.py                 # SRT字幕文件写入器
├── TPPWriter.py                 # Translator++项目写入器
├── TransWriter.py               # Trans项目写入器
├── TxtWriter.py                 # 文本文件写入器
├── VntWriter.py                 # VNT文件写入器
└── VttWriter.py                 # VTT字幕文件写入器
```
**功能**: 支持多种文件格式的翻译结果输出

### 5. 文件读取器模块 (FileReader/)
```
FileReader/
├── AutoTypeReader.py            # 自动类型识别读取器
├── BaseReader.py                # 读取器基类
├── DirectoryReader.py           # 目录读取器
├── FileReader.py                # 文件读取器主类
├── ReaderUtil.py                # 读取工具类
├── BabeldocPdfReader.py         # PDF文档读取器
├── DocxReader.py                # Word文档读取器
├── EpubReader.py                # Epub电子书读取器
├── I18nextReader.py             # I18next本地化文件读取器
├── LrcReader.py                 # LRC歌词文件读取器
├── MdReader.py                  # Markdown文件读取器
├── MToolReader.py               # Mtool游戏文件读取器
├── OfficeConversionReader.py    # Office转换读取器
├── ParatranzReader.py           # Paratranz项目读取器
├── PoReader.py                  # Po本地化文件读取器
├── RenpyReader.py               # Renpy游戏文件读取器
├── SrtReader.py                 # SRT字幕文件读取器
├── TPPReader.py                 # Translator++项目读取器
├── TransReader.py               # Trans项目读取器
├── TxtReader.py                 # 文本文件读取器
├── VntReader.py                 # VNT文件读取器
├── VttReader.py                 # VTT字幕文件读取器
└── unused/
    └── LanguageDetectorONNX.py  # 废弃的ONNX语言检测器
```
**功能**: 支持多种文件格式的原文读取和解析

### 6. LLM请求器模块 (LLMRequester/)
```
LLMRequester/
├── LLMRequester.py              # LLM请求器主类
├── LLMClientFactory.py          # LLM客户端工厂
├── AmazonbedrockRequester.py    # Amazon Bedrock请求器
├── AmazonTranslateRequester.py  # Amazon Translate请求器
├── AnthropicRequester.py        # Anthropic Claude请求器
├── CohereRequester.py           # Cohere请求器
├── DashscopeRequester.py        # 阿里云DashScope请求器
├── GoogleRequester.py           # Google Gemini请求器
├── LocalLLMRequester.py         # 本地LLM请求器
├── OpenaiRequester.py           # OpenAI GPT请求器
└── SakuraRequester.py           # Sakura专用请求器
```
**功能**: 支持多种AI翻译平台的API调用，包括传统机器翻译服务

### 7. 其他核心模块
```
NERProcessor/
└── NERProcessor.py              # 命名实体识别处理器

PromptBuilder/
├── PromptBuilder.py             # 基础提示词构建器
├── PromptBuilderEnum.py         # 提示词类型枚举
├── PromptBuilderFormat.py       # 格式化提示词构建器
├── PromptBuilderLocal.py        # 本地模型提示词构建器
├── PromptBuilderPolishing.py    # 润色提示词构建器
└── PromptBuilderSakura.py       # Sakura提示词构建器

RequestLimiter/
└── RequestLimiter.py            # 请求限制器

ResponseChecker/
├── AdvancedChecks.py            # 高级检查器
├── BaseChecks.py                # 基础检查器
└── ResponseChecker.py           # 响应检查器主类

ResponseExtractor/
├── FormatExtractor.py           # 格式提取器
└── ResponseExtractor.py         # 响应提取器主类

SimpleExecutor/
└── SimpleExecutor.py            # 简单执行器

TaskConfig/
├── TaskConfig.py                # 任务配置类
└── TaskType.py                  # 任务类型枚举

TaskExecutor/
├── TaskExecutor.py              # 任务执行器主类
├── PolisherTask.py              # 润色任务类
├── TranslatorTask.py            # 翻译任务类
└── TranslatorUtil.py            # 翻译工具函数

TextProcessor/
├── TextProcessor.py             # 文本处理器
└── PolishTextProcessor.py       # 润色文本处理器
```

## 基础框架目录 (Base/)
```
Base/
├── Base.py                      # 基础框架类
├── EventManager.py              # 事件管理器
└── PluginManager.py             # 插件管理器
```
**功能**: 提供应用程序的基础框架和事件系统

## 插件系统目录 (PluginScripts/)
```
PluginScripts/
├── PluginBase.py                # 插件基类
├── README.md                    # 插件编写指南
├── BilingualPlugin/
│   └── BilingualPlugin.py       # 双语输出插件
├── GeneralTextFilter/
│   └── GeneralTextFilter.py     # 通用文本过滤器
├── IncrementalFilePlugin/
│   └── IncrementalFilePlugin.py # 增量文件处理插件
├── IOPlugins/
│   └── CustomRegistry.py       # 自定义IO插件注册器
├── LanguageFilter/
│   └── LanguageFilter.py        # 语言过滤器插件
├── MToolOptimizer/
│   └── MToolOptimizer.py        # Mtool优化器插件
├── SpecialTextFilter/
│   └── SpecialTextFilter.py     # 特殊文本过滤器
├── TextLayoutRepairPlugin/
│   └── TextLayoutRepairPlugin.py # 文本布局修复插件
├── TextNormalizer/
│   └── TextNormalizer.py        # 文本规范化插件
└── TranslationCheckPlugin/
    └── TranslationCheckPlugin.py # 翻译检查插件
```
**功能**: 提供可扩展的插件系统，支持自定义功能扩展

### 插件事件系统
- **text_filter**: 文本预过滤事件
- **preprocess_text**: 文本预处理事件
- **normalize_text**: 发送前文本规范事件
- **postprocess_text**: 文本后处理事件
- **manual_export**: 手动导出事件
- **translation_completed**: 翻译完成事件

## 用户界面目录 (UserInterface/)
```
UserInterface/
├── AppFluentWindow.py           # 主窗口类
├── BaseNavigationItem.py        # 基础导航项
├── EditView/                    # 编辑视图页面
│   ├── BasicTablePage.py        # 基础表格页面
│   ├── EditViewPage.py          # 编辑视图主页面
│   ├── MonitoringPage.py        # 监控页面
│   ├── ScheduledDialogPage.py   # 计划对话页面
│   ├── SearchDialog.py          # 搜索对话框
│   ├── SearchResultPage.py      # 搜索结果页面
│   ├── StartupPage.py           # 启动页面
│   ├── TermExtractionDialog.py  # 术语提取对话框
│   ├── TermResultPage.py        # 术语结果页面
│   └── TextViewPage.py          # 文本视图页面
├── Extraction_Tool/             # 提取工具页面
│   ├── Export_Source_Text.py    # 导出原文工具
│   ├── Export_Update_Text.py    # 导出更新文本工具
│   └── Import_Translated_Text.py # 导入译文工具
├── FormatSettings/              # 格式设置页面
│   ├── FormatReferencePage.py   # 格式参考页面
│   └── FormatSystemPromptPage.py # 格式系统提示页面
├── NameExtractor/
│   └── NameExtractor.py         # 名称提取器
├── Platform/                    # 平台管理页面
│   ├── APIEditPage.py           # API编辑页面
│   ├── ArgsEditPage.py          # 参数编辑页面
│   ├── LimitEditPage.py         # 限制编辑页面
│   └── PlatformPage.py          # 平台主页面
├── PolishingSettings/           # 润色设置页面
│   ├── PolishingBasicSettingsPage.py # 润色基础设置
│   ├── PolishingStylePromptPage.py   # 润色风格提示页面
│   └── PolishingSystemPromptPage.py  # 润色系统提示页面
├── Settings/                    # 应用设置页面
│   ├── AppSettingsPage.py       # 应用设置页面
│   ├── OutputSettingsPage.py    # 输出设置页面
│   ├── PluginsSettingsPage.py   # 插件设置页面
│   └── TaskSettingsPage.py      # 任务设置页面
├── Table/                       # 表格管理页面
│   ├── ExclusionListPage.py     # 禁翻表页面
│   ├── PromptDictionaryPage.py  # 术语表页面
│   ├── TextReplaceAPage.py      # 译前替换页面
│   └── TextReplaceBPage.py      # 译后替换页面
├── TableHelper/
│   └── TableHelper.py          # 表格助手
├── TranslationSettings/         # 翻译设置页面
│   ├── CharacterizationPromptPage.py    # 角色介绍提示页面
│   ├── SystemPromptPage.py              # 系统提示页面
│   ├── TranslationExamplePromptPage.py  # 翻译示例提示页面
│   ├── TranslationSettingsPage.py       # 翻译设置主页面
│   ├── WorldBuildingPromptPage.py       # 世界观设定提示页面
│   └── WritingStylePromptPage.py        # 写作风格提示页面
└── VersionManager/
    └── VersionManager.py        # 版本管理器
```
**功能**: 基于 PyQt5 和 Fluent Design 的现代化用户界面

## UI组件目录 (Widget/)
```
Widget/
├── ActionCard.py                # 动作卡片组件
├── APITypeCard.py               # API类型卡片
├── CombinedLineCard.py          # 组合行卡片
├── ComboBoxCard.py              # 下拉框卡片
├── CommandBarCard.py            # 命令栏卡片
├── DashboardCard.py             # 仪表板卡片
├── EditableComboBoxCard.py      # 可编辑下拉框卡片
├── EmptyCard.py                 # 空卡片
├── FlowCard.py                  # 流式卡片
├── FolderDropCard.py            # 文件夹拖拽卡片
├── GameDropCard.py              # 游戏拖拽卡片
├── GroupCard.py                 # 分组卡片
├── InterfaceDropZoneWidget.py   # 界面拖拽区域组件
├── LineEditCard.py              # 行编辑卡片
├── LineEditMessageBox.py        # 行编辑消息框
├── PlainTextEditCard.py         # 纯文本编辑卡片
├── ProgressRingCard.py          # 进度环卡片
├── PushButtonCard.py            # 按钮卡片
├── SliderCard.py                # 滑块卡片
├── SpinCard.py                  # 数字输入卡片
├── SwitchButtonCard.py          # 开关按钮卡片
├── VerticalSeparator.py         # 垂直分隔符
└── WaveformCard.py              # 波形卡片
```
**功能**: 提供丰富的自定义UI组件

## 资源目录 (Resource/)
```
Resource/
├── config.json                  # 全局配置文件
├── Localization/                # 多语言本地化文件
│   ├── APIManagement.json       # API管理界面文本
│   ├── AppFluentWindow.json     # 主窗口界面文本
│   ├── ApplicationSettings.json # 应用设置界面文本
│   ├── BasicTablePage.json      # 基础表格页面文本
│   ├── EditView.json            # 编辑视图界面文本
│   ├── MonitoringPage.json      # 监控页面文本
│   ├── OutputSettings.json      # 输出设置界面文本
│   ├── PolishingSettings.json   # 润色设置界面文本
│   ├── PromptSettings.json      # 提示词设置界面文本
│   ├── StartupPage.json         # 启动页面文本
│   ├── TableSettings.json       # 表格设置界面文本
│   ├── TaskSettings.json        # 任务设置界面文本
│   ├── TranslationSettings.json # 翻译设置界面文本
│   └── VersionManager.json      # 版本管理器文本
├── Logo/                        # 应用图标资源
│   ├── Avatar.png               # 头像图标
│   ├── launch.png               # 启动图标
│   └── logo.png                 # 主Logo
├── Models/                      # AI模型文件
│   ├── language_detection-ONNX/ # ONNX语言检测模型
│   ├── mediapipe/               # MediaPipe模型
│   │   └── language_detector.tflite
│   └── ner/                     # 命名实体识别模型
│       └── ja_core_news_md/     # 日语NER模型
├── platforms/                   # 平台配置
│   ├── preset.json              # 预设平台配置
│   └── Icon/                    # 平台图标
│       ├── amazonbedrock.png    # Amazon Bedrock图标
│       ├── anthropic.png        # Anthropic图标
│       ├── cohere.png           # Cohere图标
│       ├── dashscope.png        # DashScope图标
│       ├── deepseek.png         # DeepSeek图标
│       ├── google.png           # Google图标
│       ├── LocalLLM.png         # 本地LLM图标
│       ├── moonshot.png         # Moonshot图标
│       ├── openai.png           # OpenAI图标
│       ├── sakura.png           # Sakura图标
│       ├── volcengine.png       # 火山引擎图标
│       ├── xai.png              # xAI图标
│       ├── yi.png               # 零一万物图标
│       └── zhipu.png            # 智谱AI图标
├── Prompt/                      # 提示词模板
│   ├── Format/                  # 格式化提示词
│   │   └── format_system_zh.txt
│   ├── Local/                   # 本地模型提示词
│   │   ├── local_system_en.txt
│   │   └── local_system_zh.txt
│   ├── Polishing/               # 润色提示词
│   │   ├── common_system_zh_s.txt
│   │   └── common_system_zh_t.txt
│   ├── Sakura/                  # Sakura模型提示词
│   │   └── sakura_system_zh.txt
│   └── Translate/               # 翻译提示词
│       ├── common_system_en.txt
│       ├── common_system_zh.txt
│       ├── cot_system_en.txt
│       ├── cot_system_zh.txt
│       ├── think_system_en.txt
│       └── think_system_zh.txt
├── Regex/                       # 正则表达式配置
│   ├── check_regex.json         # 检查正则表达式
│   └── regex.json               # 主正则表达式库
└── Updater/
    └── updater.exe              # 更新程序
```
**功能**: 存储应用程序的各种资源文件

## 特殊工具目录

### StevExtraction/ - RPG Maker游戏文本提取工具
```
StevExtraction/
├── 更新记录.txt                 # 更新记录
├── 使用说明.md                  # 使用说明
├── 自动换行.js                  # 自动换行脚本
├── config.yaml                  # 配置文件
├── jtpp.py                      # 主处理脚本
├── main.py                      # 主程序
├── main更新记录.txt             # 主程序更新记录
├── rpgmaker_codes.txt           # RPG Maker代码
└── scratchpad.py                # 临时脚本
```
**功能**: 专门用于RPG Maker游戏的文本提取和处理

### Tools/ - 开发工具
```
Tools/
├── pyinstall.py                 # Python打包脚本
└── rust_updater/                # Rust更新器
```
**功能**: 开发和部署相关的工具

### Example image/ - 示例图片和教程截图
```
Example image/
├── logo.png                     # Logo图片
├── 表格介绍/                    # 表格功能介绍截图
├── 翻译设置/                    # 翻译设置截图
├── 三步走/                      # 三步走教程截图
├── 提示词设置/                  # 提示词设置截图
├── Extraction/                  # 文本提取截图
├── logo备份/                    # Logo备份
├── Mtool/                       # Mtool教程截图
├── Paratranz/                   # Paratranz教程截图
├── PinHaoFan/                   # 品好饭相关截图
├── Sakura/                      # Sakura模型截图
├── Sponsor/                     # 赞助相关图片
├── Tpp/                         # Translator++教程截图
└── Tpp_trans/                   # Translator++翻译截图
```
**功能**: 提供用户教程和界面展示图片

### 其他目录
```
skimage/                         # 图像处理模块
└── metrics.py                   # 图像度量工具

ainiee/                          # Python虚拟环境
├── CHANGES.rst                  # 变更记录
├── pyvenv.cfg                   # 虚拟环境配置
├── README.rst                   # 说明文档
├── bin/                         # 可执行文件
├── include/                     # 头文件
├── lib/                         # 库文件
└── share/                       # 共享文件
```

## 支持的文件格式

### 游戏文件格式
- **Mtool**: RPG游戏文本文件
- **Renpy**: Renpy引擎游戏文件
- **Translator++**: T++项目文件
- **ParaTranzr**: 协作翻译平台文件
- **VNText**: 视觉小说文本文件
- **Trans**: Trans项目文件

### 文档格式
- **TXT**: 纯文本文件
- **Docx**: Word文档
- **PDF**: PDF文档（通过BabeldocPdf）
- **Markdown**: MD文档
- **Epub**: 电子书格式

### 字幕格式
- **SRT**: SubRip字幕文件
- **VTT**: WebVTT字幕文件
- **LRC**: 歌词文件

### 本地化格式
- **I18next**: 国际化JSON文件
- **Po**: GNU gettext文件

## 支持的AI平台

### 商业平台
- **OpenAI**: GPT系列模型
- **Anthropic**: Claude系列模型
- **Google**: Gemini系列模型
- **Amazon Bedrock**: AWS托管的各种模型
- **Amazon Translate**: AWS神经网络机器翻译服务
- **阿里云DashScope**: 通义千问等模型
- **Cohere**: Cohere模型
- **DeepSeek**: DeepSeek模型
- **火山引擎**: 字节跳动的AI服务
- **智谱AI**: ChatGLM系列
- **零一万物**: Yi系列模型
- **Moonshot**: 月之暗面模型
- **xAI**: Grok模型

### 专用/本地平台
- **Sakura**: 专门针对日语翻译优化的模型
- **LocalLLM**: 本地部署的各种开源模型

## 核心技术特性

### 1. 智能翻译技术
- **轻盈翻译格式**: 优化的翻译输入格式
- **思维链翻译（CoT）**: 提高翻译推理能力
- **上下文关联翻译**: 保持文本连贯性
- **AI术语表支持**: 专业术语一致性
- **双子星翻译功能**: 双重验证提高质量
- **神经网络机器翻译**: 支持Amazon Translate高质量机器翻译
- **自动语言检测**: 集成Amazon Comprehend智能语言识别
- **长文本分块处理**: 自动处理超长文本的智能分割翻译

### 2. 高效处理机制
- **多线程并发处理**: 提高翻译效率
- **请求速率限制**: 遵守API限制
- **自动重试机制**: 处理网络异常
- **断点续传支持**: 支持任务中断恢复

### 3. 质量保证系统
- **翻译结果检查**: 自动验证翻译质量
- **文本规范化处理**: 统一文本格式
- **简繁体转换**: 支持中文字体转换
- **双语对照输出**: 便于校对检查

### 4. 扩展性设计
- **插件系统架构**: 支持功能扩展
- **自定义接口支持**: 支持用户自定义API
- **模块化组件设计**: 便于维护和扩展
- **事件驱动架构**: 灵活的事件处理机制

## 应用场景

1. **游戏本地化翻译** - 主要应用场景，支持多种游戏引擎
2. **电子书翻译** - 支持Epub、TXT等格式
3. **字幕翻译** - 视频字幕处理和翻译
4. **文档翻译** - 办公文档和技术文档翻译
5. **软件本地化** - 应用程序界面翻译
6. **协作翻译** - 支持团队协作翻译项目

## 项目特点总结

1. **模块化架构**: 采用清晰的模块化设计，各功能模块职责明确
2. **插件系统**: 支持插件扩展，提供丰富的事件钩子
3. **多格式支持**: 支持游戏、电子书、字幕、文档等多种文件格式
4. **多平台兼容**: 支持多种AI翻译平台和本地模型
5. **用户友好**: 提供完整的GUI界面和多语言支持
6. **高度可配置**: 丰富的配置选项和自定义功能
7. **专业工具**: 特别针对游戏本地化翻译进行了优化
8. **开源生态**: 完整的开源项目，支持社区贡献

AiNiee 是一个功能完整、架构清晰的专业AI翻译工具，特别适合游戏本地化、文档翻译等专业翻译场景，具有良好的扩展性和可维护性。
