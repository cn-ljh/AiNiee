import boto3
from botocore.exceptions import ClientError, BotoCoreError
from Base.Base import Base
from ModuleFolders.LLMRequester.LLMClientFactory import LLMClientFactory


class AmazonTranslateRequester(Base):
    """Amazon Translate服务请求器"""
    
    def __init__(self) -> None:
        super().__init__()

    def request_amazon_translate(self, messages, system_prompt, platform_config) -> tuple[bool, str | None, str | None, int | None, int | None]:
        """
        使用Amazon Translate服务进行翻译
        
        Args:
            messages: 消息列表，包含要翻译的文本
            system_prompt: 系统提示词（对于翻译服务可能不直接使用）
            platform_config: 平台配置信息
            
        Returns:
            tuple: (是否跳过, 思考过程, 翻译结果, 输入token数, 输出token数)
        """
        try:
            # 从翻译设置中获取语言配置
            config = self.load_config()
            source_language_setting = config.get("source_language", "auto")
            target_language_setting = config.get("target_language", "chinese_simplified")
            
            # 将翻译设置中的语言代码转换为Amazon Translate支持的语言代码
            source_language = self._convert_to_aws_language_code(source_language_setting)
            target_language = self._convert_to_aws_language_code(target_language_setting)
            
            # 获取AWS配置参数
            region = platform_config.get("region", "us-east-1")
            access_key = platform_config.get("access_key")
            secret_key = platform_config.get("secret_key")
            request_timeout = platform_config.get("request_timeout", 60)
            
            # 验证必要参数
            if not target_language:
                self.error("目标语言未配置")
                return True, None, None, None, None
                
            # 从工厂获取客户端
            client = LLMClientFactory().get_amazon_translate_client(platform_config)
            
            # 提取要翻译的文本和结构化信息
            raw_content, source_text_dict = self._extract_text_from_messages(messages)
            if not raw_content:
                self.error("没有找到要翻译的文本")
                return True, None, None, None, None
            
            # 如果源语言是auto，先检测语言
            if source_language == "auto":
                source_language = self._detect_language(client, raw_content, platform_config)
                if not source_language:
                    self.error("无法检测源语言")
                    return True, None, None, None, None
            
            # 执行结构化翻译
            formatted_translation = self._translate_structured_text(
                client, 
                source_text_dict, 
                source_language, 
                target_language
            )
            
            if not formatted_translation:
                self.error("翻译失败")
                return True, None, None, None, None
            
            # 计算大概的token数（简单估算）
            input_tokens = len(raw_content.split())
            output_tokens = len(formatted_translation.split())
            
            return False, "", formatted_translation, input_tokens, output_tokens
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            self.error(f"AWS客户端错误 [{error_code}]: {error_message}")
            return True, None, None, None, None
            
        except BotoCoreError as e:
            self.error(f"AWS核心错误: {str(e)}")
            return True, None, None, None, None
            
        except Exception as e:
            if self.is_debug():
                self.error(f"Amazon Translate请求错误: {str(e)}", e)
            else:
                self.error(f"Amazon Translate请求错误: {str(e)}")
            return True, None, None, None, None


    def _convert_to_aws_language_code(self, language_setting):
        """将翻译设置中的语言代码转换为Amazon Translate支持的语言代码"""
        language_mapping = {
            # 翻译设置中的语言代码 -> AWS Translate语言代码
            "auto": "auto",
            "japanese": "ja",
            "english": "en", 
            "korean": "ko",
            "russian": "ru",
            "german": "de",
            "french": "fr",
            "chinese_simplified": "zh",
            "chinese_traditional": "zh-TW",
            "spanish": "es",
        }
        
        return language_mapping.get(language_setting, "en")  # 默认返回英语

    def _extract_text_from_messages(self, messages):
        """从消息列表中提取要翻译的文本，并解析结构化内容"""
        if not messages:
            return "", {}
        
        # 获取最后一条用户消息作为翻译内容
        content = ""
        for message in reversed(messages):
            if isinstance(message, dict) and message.get('role') == 'user':
                content = message.get('content', '')
                break
        
        # 如果没有找到用户消息，使用最后一条消息
        if not content and messages and isinstance(messages[-1], dict):
            content = messages[-1].get('content', '')
        
        if not content:
            return "", {}
        
        # 解析结构化内容
        source_text_dict = self._parse_structured_content(content)
        
        # 如果解析失败，将整个内容作为单个文本处理
        if not source_text_dict:
            source_text_dict = {"0": content}
        
        return content, source_text_dict

    def _parse_structured_content(self, content):
        """解析结构化的翻译内容"""
        import re
        
        # 提取textarea标签内的内容
        textarea_match = re.search(r'<textarea.*?>(.*?)</textarea>', content, re.DOTALL)
        if not textarea_match:
            return {}
        
        textarea_content = textarea_match.group(1).strip()
        
        # 解析数字序号格式的文本
        source_dict = {}
        lines = textarea_content.split('\n')
        current_index = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 匹配数字序号格式 (如 "1.文本内容")
            match = re.match(r'^(\d+)\.(.*)$', line)
            if match:
                index = int(match.group(1)) - 1  # 转换为0基索引
                text = match.group(2).strip()
                source_dict[str(index)] = text
            else:
                # 如果没有数字序号，按顺序添加
                source_dict[str(current_index)] = line
                current_index += 1
        
        return source_dict

    def _detect_language(self, client, text, platform_config):
        """检测文本语言"""
        try:
            # 从工厂获取Comprehend客户端
            comprehend_client = LLMClientFactory().get_amazon_comprehend_client(platform_config)
            
            # 限制检测文本长度（Amazon Comprehend限制为5000字符）
            detection_text = text[:5000] if len(text) > 5000 else text
            
            response = comprehend_client.detect_dominant_language(Text=detection_text)
            
            if response.get('Languages'):
                # 获取置信度最高的语言
                dominant_language = max(response['Languages'], key=lambda x: x['Score'])
                return dominant_language['LanguageCode']
            
            return None
            
        except Exception as e:
            self.error(f"语言检测失败: {str(e)}")
            # 如果语言检测失败，默认使用英语
            self.info("语言检测失败，默认使用英语作为源语言")
            return "en"

    def _translate_text(self, client, text, source_language, target_language):
        """执行文本翻译"""
        try:
            # Amazon Translate单次请求限制为5000字符
            max_chunk_size = 5000
            
            if len(text) <= max_chunk_size:
                # 单次翻译
                response = client.translate_text(
                    Text=text,
                    SourceLanguageCode=source_language,
                    TargetLanguageCode=target_language
                )
                return response.get('TranslatedText', '')
            else:
                # 分块翻译
                return self._translate_long_text(client, text, source_language, target_language, max_chunk_size)
                
        except Exception as e:
            self.error(f"文本翻译失败: {str(e)}")
            return None

    def _translate_long_text(self, client, text, source_language, target_language, chunk_size):
        """翻译长文本（分块处理）"""
        try:
            # 按句子分割文本，尽量保持语义完整
            sentences = self._split_text_by_sentences(text)
            translated_parts = []
            current_chunk = ""
            
            for sentence in sentences:
                # 检查添加当前句子是否会超过限制
                if len(current_chunk + sentence) > chunk_size:
                    if current_chunk:
                        # 翻译当前块
                        response = client.translate_text(
                            Text=current_chunk.strip(),
                            SourceLanguageCode=source_language,
                            TargetLanguageCode=target_language
                        )
                        translated_parts.append(response.get('TranslatedText', ''))
                        current_chunk = sentence
                    else:
                        # 单个句子就超过限制，强制分割
                        chunk = sentence[:chunk_size]
                        response = client.translate_text(
                            Text=chunk,
                            SourceLanguageCode=source_language,
                            TargetLanguageCode=target_language
                        )
                        translated_parts.append(response.get('TranslatedText', ''))
                        current_chunk = sentence[chunk_size:]
                else:
                    current_chunk += sentence
            
            # 翻译最后一块
            if current_chunk.strip():
                response = client.translate_text(
                    Text=current_chunk.strip(),
                    SourceLanguageCode=source_language,
                    TargetLanguageCode=target_language
                )
                translated_parts.append(response.get('TranslatedText', ''))
            
            return ' '.join(translated_parts)
            
        except Exception as e:
            self.error(f"长文本翻译失败: {str(e)}")
            return None

    def _split_text_by_sentences(self, text):
        """按句子分割文本"""
        import re
        
        # 简单的句子分割正则表达式
        sentence_endings = r'[.!?。！？]\s+'
        sentences = re.split(sentence_endings, text)
        
        # 重新添加句子结束符
        result = []
        parts = re.findall(sentence_endings, text)
        
        for i, sentence in enumerate(sentences[:-1]):
            if i < len(parts):
                result.append(sentence + parts[i])
            else:
                result.append(sentence)
        
        # 添加最后一个句子
        if sentences[-1]:
            result.append(sentences[-1])
        
        return result

    def _translate_structured_text(self, client, source_text_dict, source_language, target_language):
        """翻译结构化文本并格式化输出"""
        try:
            translated_dict = {}
            
            # 逐个翻译文本条目
            for key, text in source_text_dict.items():
                if not text.strip():
                    translated_dict[key] = text
                    continue
                    
                # 翻译单个文本
                translated_text = self._translate_text(client, text, source_language, target_language)
                if translated_text:
                    translated_dict[key] = translated_text
                else:
                    # 翻译失败时保留原文
                    translated_dict[key] = text
            
            # 格式化为AiNiee期望的输出格式
            return self._format_translation_output(translated_dict)
            
        except Exception as e:
            self.error(f"结构化翻译失败: {str(e)}")
            return None

    def _format_translation_output(self, translated_dict):
        """将翻译结果格式化为AiNiee期望的输出格式"""
        try:
            # 构建带数字序号的翻译结果
            formatted_lines = []
            for key in sorted(translated_dict.keys(), key=lambda x: int(x)):
                text = translated_dict[key]
                # 添加数字序号格式 (从1开始)
                formatted_lines.append(f"{int(key) + 1}.{text}")
            
            # 包装在textarea标签中，模拟大语言模型的输出格式
            formatted_content = '\n'.join(formatted_lines)
            formatted_output = f"<textarea>\n{formatted_content}\n</textarea>"
            
            return formatted_output
            
        except Exception as e:
            self.error(f"格式化翻译输出失败: {str(e)}")
            return None

    def get_supported_languages(self, platform_config):
        """获取支持的语言列表"""
        try:
            client = LLMClientFactory().get_amazon_translate_client(platform_config)
            
            response = client.list_languages()
            return response.get('Languages', [])
            
        except Exception as e:
            self.error(f"获取支持语言列表失败: {str(e)}")
            return []
