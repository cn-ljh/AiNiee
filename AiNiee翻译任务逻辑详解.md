# AiNiee项目翻译任务逻辑详解

## 1. 整体架构概览

AiNiee采用**模块化架构**，翻译任务的执行流程涉及多个核心模块的协同工作：

```
TaskExecutor (任务执行器) 
    ↓
TranslatorTask (翻译任务类)
    ↓
TextProcessor (文本处理器) → PromptBuilder (提示词构建器) → LLMRequester (LLM请求器)
    ↓
ResponseExtractor (响应提取器) → ResponseChecker (响应检查器)
```

## 2. 翻译任务的完整生命周期

### 2.1 任务初始化阶段

**TaskExecutor.translation_start_target()** 方法负责整个翻译流程的启动：

1. **配置加载**：
   - 读取用户配置文件
   - 设置翻译平台信息（OpenAI、Claude、Gemini等）
   - 配置请求限制器（RPM/TPM限制）

2. **缓存数据分块**：
   ```python
   chunks, previous_chunks, file_paths = self.cache_manager.generate_item_chunks(
       "line" if self.config.tokens_limit_switch == False else "token",
       self.config.lines_limit if self.config.tokens_limit_switch == False else self.config.tokens_limit,
       self.config.pre_line_counts,
       TaskType.TRANSLATION
   )
   ```
   - 根据行数限制或Token限制将文本分块
   - 每个块包含待翻译文本和上文信息

3. **任务生成**：
   - 为每个文本块创建独立的TranslatorTask实例
   - 确定每个文件的源语言（支持多语言混合项目）

### 2.2 单个翻译任务执行流程

**TranslatorTask.unit_translation_task()** 是核心的单任务执行逻辑：

#### A. 文本预处理阶段 (prepare方法)

1. **插件事件触发**：
   ```python
   self.plugin_manager.broadcast_event("normalize_text", self.config, self.source_text_dict)
   ```

2. **文本处理链**：
   ```python
   self.source_text_dict, self.prefix_codes, self.suffix_codes, self.placeholder_order, self.affix_whitespace_storage = \
       self.text_processor.replace_all(self.config, self.source_lang, self.source_text_dict)
   ```

   **TextProcessor.replace_all()** 执行以下处理：
   - **译前替换**：用户自定义的文本替换规则
   - **前后缀处理**：提取并保存文本的前后缀（空格、换行、特殊符号）
   - **代码段处理**：自动识别和占位代码片段、标签等
   - **数字序号处理**：将"1."格式转换为"【1】"格式

3. **提示词构建**：
   根据不同平台调用相应的提示词构建器：
   - **Sakura模型**：PromptBuilderSakura
   - **本地模型**：PromptBuilderLocal  
   - **通用模型**：PromptBuilder

   **PromptBuilder.generate_prompt()** 构建完整的提示词结构：
   ```python
   # 系统提示词 + 术语表 + 禁翻表 + 角色设定 + 世界观 + 翻译示例
   system = PromptBuilder.build_system(config, source_lang)
   if config.prompt_dictionary_switch:
       system += PromptBuilder.build_glossary_prompt(config, source_text_dict)
   if config.exclusion_list_switch:
       system += PromptBuilder.build_ntl_prompt(config, source_text_dict)
   ```

#### B. API请求阶段

1. **请求限制检查**：
   ```python
   if self.request_limiter.check_limiter(self.request_tokens_consume):
       break
   ```
   - 检查RPM（每分钟请求数）和TPM（每分钟Token数）限制
   - 如果超限则等待

2. **发送请求**：
   ```python
   requester = LLMRequester()
   skip, response_think, response_content, prompt_tokens, completion_tokens = requester.sent_request(
       self.messages, self.system_prompt, platform_config
   )
   ```
   
   **LLMRequester** 根据平台类型分发到具体的请求器：
   - OpenAI系列：OpenaiRequester
   - Anthropic Claude：AnthropicRequester
   - Google Gemini：GoogleRequester
   - Amazon Bedrock：AmazonbedrockRequester
   - Amazon Translate：AmazonTranslateRequester
   - 本地模型：LocalLLMRequester
   - Sakura：SakuraRequester

3. **重试机制**：
   如果主接口失败，会尝试使用重试接口：
   ```python
   if skip == True:
       return self.try_retry_translation()
   ```

#### C. 响应处理阶段

1. **内容提取**：
   ```python
   response_dict = ResponseExtractor.text_extraction(self, self.source_text_dict, response_content)
   ```
   - 从AI回复中提取翻译结果
   - 处理多行文本的格式

2. **质量检查**：
   ```python
   check_result, error_content = ResponseChecker.check_response_content(
       self, self.config, self.placeholder_order, response_content, response_dict, 
       self.source_text_dict, self.source_lang
   )
   ```
   - 检查翻译结果的完整性
   - 验证占位符是否正确还原
   - 检查行数是否匹配

3. **文本后处理**：
   ```python
   restore_response_dict = self.text_processor.restore_all(
       self.config, restore_response_dict, self.prefix_codes, 
       self.suffix_codes, self.placeholder_order, self.affix_whitespace_storage
   )
   ```
   
   **TextProcessor.restore_all()** 执行还原操作：
   - 还原占位符为原始代码段
   - 还原前后缀（空格、换行等）
   - 执行译后替换规则
   - 还原数字序号格式

4. **结果保存**：
   ```python
   for item, response in zip(self.items, restore_response_dict.values()):
       with item.atomic_scope():
           item.model = self.config.model
           item.translated_text = response
           item.translation_status = TranslationStatus.TRANSLATED
   ```

## 3. 多轮翻译机制

AiNiee支持多轮翻译来处理失败的任务：

```python
for current_round in range(self.config.round_limit + 1):
    # 获取未翻译的条目数量
    item_count_status_untranslated = self.cache_manager.get_item_count_by_status(TranslationStatus.UNTRANSLATED)
    
    if item_count_status_untranslated == 0:
        break  # 全部翻译完成
        
    # 第二轮开始减半处理
    if current_round > 0:
        self.config.lines_limit = max(1, int(self.config.lines_limit / 2))
        self.config.tokens_limit = max(1, int(self.config.tokens_limit / 2))
```

## 4. 并发处理机制

使用线程池实现并发翻译：

```python
with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.actual_thread_counts) as executor:
    for task in tasks_list:
        future = executor.submit(task.start)
        future.add_done_callback(self.task_done_callback)
```

## 5. 特殊功能

### 5.1 智能文本处理
- **多行文本处理**：保持原始换行符格式
- **日语特殊处理**：针对日语字符的前后缀提取
- **代码段保护**：自动识别并保护代码、标签等内容

### 5.2 上下文关联翻译
- 支持携带上文信息提高翻译连贯性
- 可配置上文行数

### 5.3 动态示例生成
- 根据待翻译内容自动生成相似格式的翻译示例
- 支持Few-shot学习提高翻译质量

### 5.4 简繁转换
```python
if self.config.response_conversion_toggle:
    converter = opencc.OpenCC(self.config.opencc_preset)
    for item in cache_list:
        if item.translation_status == TranslationStatus.TRANSLATED:
            item.translated_text = converter.convert(item.translated_text)
```

## 6. 错误处理和监控

### 6.1 多轮翻译失败时的信息记录

当翻译任务在多轮尝试后仍然失败时，AiNiee会记录以下详细信息：

#### A. 项目统计信息记录
```python
# CacheProjectStatistics 记录的统计信息
class CacheProjectStatistics:
    total_requests: int = 0      # 总请求数
    error_requests: int = 0      # 错误请求数
    start_time: float           # 开始时间
    total_line: int = 0         # 总行数
    line: int = 0              # 已处理行数
    token: int = 0             # 消耗的Token数
    total_completion_tokens: int = 0  # 完成Token数
    time: float = 0.0          # 总耗时
```

#### B. 任务级别的错误记录
在 `task_done_callback` 中记录：
```python
def task_done_callback(self, future: concurrent.futures.Future) -> None:
    result = future.result()
    with self.project_status_data.atomic_scope():
        self.project_status_data.total_requests += 1
        self.project_status_data.error_requests += 0 if result.get("check_result") else 1
        # 失败的任务会增加 error_requests 计数
```

#### C. 详细的错误日志记录
每个失败的翻译任务都会生成详细日志：

1. **错误类型分类**：
   - **【行数错误】**：行数不一致、无法对应、出现错行串行
   - **【换行符数】**：译文换行符数量不一致
   - **【返回原文】**：译文与原文完全相同
   - **【翻译残留】**：译文中残留部分原文
   - **【自动处理】**：未正确保留全部的占位符
   - **模型拒绝翻译**：接口拒绝或格式错误

2. **日志内容包含**：
   ```python
   def generate_log_rows(self, error: str, start_time: int, prompt_tokens: int, 
                        completion_tokens: int, source: list[str], translated: list[str], 
                        extra_log: list[str]):
       # 记录错误信息
       if error != "":
           rows.append(error)
       
       # 记录原文和译文对比
       for s, t in zip(source, translated):
           pair += f"{s} [bright_blue]-->[/] {t}\n"
   ```

3. **模型回复记录**：
   ```python
   # 记录模型思考过程（如果有）
   if response_think:
       self.extra_log.append("模型思考内容：\n" + response_think)
   
   # 记录模型原始回复（调试模式）
   if self.is_debug():
       self.extra_log.append("模型回复内容：\n" + response_content)
   ```

#### D. 缓存项状态保持
失败的翻译任务不会更新缓存项的状态：
```python
# 只有成功的翻译才会更新状态
if check_result == True:
    for item, response in zip(self.items, restore_response_dict.values()):
        with item.atomic_scope():
            item.model = self.config.model
            item.translated_text = response
            item.translation_status = TranslationStatus.TRANSLATED
# 失败的任务保持 UNTRANSLATED 状态，等待下一轮处理
```

#### E. 多轮处理机制
```python
for current_round in range(self.config.round_limit + 1):
    # 获取仍未翻译的条目数量
    item_count_status_untranslated = self.cache_manager.get_item_count_by_status(TranslationStatus.UNTRANSLATED)
    
    # 达到最大轮次时的警告记录
    if item_count_status_untranslated > 0 and current_round == self.config.round_limit:
        self.warning("已达到最大翻译轮次，仍有部分文本未翻译，请检查结果 ...")
        break
    
    # 第二轮开始减半处理（降低批次大小）
    if current_round > 0:
        self.config.lines_limit = max(1, int(self.config.lines_limit / 2))
        self.config.tokens_limit = max(1, int(self.config.tokens_limit / 2))
```

#### F. 重试接口记录
如果配置了重试接口，还会记录重试过程：
```python
def try_retry_translation(self) -> dict:
    # 记录重试接口的使用
    self.info("主翻译接口失败，尝试使用重试接口进行翻译...")
    
    # 记录重试接口的回复
    if response_think:
        self.extra_log.append("重试接口思考内容：\n" + response_think)
    if self.is_debug():
        self.extra_log.append("重试接口回复内容：\n" + response_content)
    
    # 记录重试结果
    if check_result == False:
        self.error(f"重试接口译文也未通过检查 - {error_content}")
    else:
        self.success("重试接口翻译成功")
```

### 6.2 其他监控功能

- **实时进度监控**：通过事件系统更新翻译进度
- **错误统计**：记录失败请求数量和成功率
- **详细日志**：记录每个任务的执行情况
- **断点续传**：支持任务中断后继续翻译
- **缓存持久化**：定期保存翻译进度到缓存文件

## 7. 详细的文本处理流程

### 7.1 文本预处理详解

**TextProcessor** 类负责复杂的文本预处理工作：

1. **换行符标准化**：
   ```python
   def _normalize_line_endings(self, text: str) -> Tuple[str, List[Tuple[int, str]]]:
       # 统一换行符为 \n，并记录每个换行符的原始类型和位置
   ```

2. **多行文本处理**：
   ```python
   def _process_multiline_text(self, text: str, source_lang: str) -> Tuple[str, Dict]:
       # 按行分割，处理空行和纯空白行
       # 提取前后缀（空格、换行、特殊符号）
   ```

3. **正则表达式预编译**：
   - 译前替换规则预编译
   - 译后替换规则预编译
   - 自动处理正则预编译

### 7.2 提示词构建详解

**PromptBuilder** 类构建复杂的提示词结构：

1. **系统提示词选择**：
   - 通用提示词（COMMON）
   - 思维链提示词（COT）
   - 思考提示词（THINK）
   - 自定义提示词

2. **动态内容构建**：
   ```python
   # 术语表构建
   def build_glossary_prompt(config: TaskConfig, input_dict: dict) -> str:
       # 筛选在输入词典中出现过的条目
   
   # 禁翻表构建
   def build_ntl_prompt(config: TaskConfig, source_text_dict) -> str:
       # 处理正则匹配和标记符
   
   # 角色设定构建
   def build_characterization(config: TaskConfig, input_dict: dict) -> str:
       # 根据文本内容筛选相关角色
   ```

3. **动态示例生成**：
   ```python
   def build_adaptive_translation_sample(config: TaskConfig, input_dict: dict, conv_source_lang: str):
       # 根据源语言和待翻译内容生成相似格式的翻译示例
   ```

## 8. 支持的AI平台和特殊处理

### 8.1 支持的平台
- **OpenAI系列**：GPT-3.5, GPT-4, GPT-4o等
- **Anthropic**：Claude系列模型
- **Google**：Gemini系列模型
- **Amazon Bedrock**：AWS托管的各种模型
- **Amazon Translate**：AWS神经网络机器翻译服务
- **阿里云DashScope**：通义千问等模型
- **本地模型**：支持各种开源模型
- **Sakura**：专门针对日语翻译优化的模型

### 8.2 特殊平台处理
- **Sakura模型**：使用特殊的占位符格式（↓符号）
- **本地模型**：使用专门的提示词格式
- **Amazon Translate**：直接调用机器翻译API，无需提示词

## 9. 缓存和状态管理

### 9.1 翻译状态
```python
class TranslationStatus:
    UNTRANSLATED = "untranslated"    # 未翻译
    TRANSLATED = "translated"        # 已翻译
    POLISHED = "polished"           # 已润色
```

### 9.2 缓存机制
- **CacheItem**：单个文本条目的缓存
- **CacheManager**：缓存管理器，负责读写缓存文件
- **CacheProject**：项目级别的缓存和统计信息

## 10. 插件系统

AiNiee提供了丰富的插件事件钩子：

- **text_filter**：文本预过滤事件
- **normalize_text**：发送前文本规范事件
- **preprocess_text**：文本预处理事件
- **postprocess_text**：文本后处理事件
- **manual_export**：手动导出事件
- **translation_completed**：翻译完成事件

## 总结

AiNiee的翻译逻辑设计非常完善，具有以下特点：

1. **模块化设计**：各功能模块职责清晰，易于维护和扩展
2. **智能文本处理**：自动处理各种文本格式和特殊内容
3. **多平台支持**：统一接口支持多种AI翻译服务
4. **质量保证**：多重检查机制确保翻译质量
5. **用户友好**：丰富的配置选项和实时监控
6. **容错性强**：多轮重试和错误恢复机制
7. **高度可配置**：支持术语表、禁翻表、角色设定等高级功能
8. **插件扩展**：完整的插件系统支持功能扩展

这种设计使得AiNiee能够处理复杂的翻译任务，特别适合游戏本地化等专业翻译场景。通过模块化的架构和丰富的配置选项，用户可以根据具体需求调整翻译策略，获得最佳的翻译效果。
