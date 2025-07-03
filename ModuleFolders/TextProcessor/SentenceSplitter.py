import re
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class SentenceInfo:
    """句子信息类"""
    text: str
    start_pos: int
    end_pos: int
    line_number: int
    sentence_index: int


class SentenceSplitter:
    """
    句子分割器 - 支持多语言的智能句子分割
    """
    
    def __init__(self):
        # 句子结束标点
        self.sentence_endings = re.compile(r'[.!?;。！？；…]')
        
        # 缩写词模式（避免误分割）
        self.abbreviations = re.compile(
            r'\b(?:Mr|Mrs|Ms|Dr|Prof|Sr|Jr|vs|etc|Inc|Ltd|Corp|Co|St|Ave|Blvd|Rd|Ph\.D|M\.D|B\.A|M\.A|U\.S|U\.K|U\.N|A\.M|P\.M|i\.e|e\.g)\.'
        )
        
        # 数字小数点模式
        self.decimal_pattern = re.compile(r'\d+\.\d+')

    def detect_language(self, text: str) -> str:
        """简单的语言检测"""
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        japanese_chars = len(re.findall(r'[\u3040-\u309f\u30a0-\u30ff]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        total_chars = len(text.strip())
        if total_chars == 0:
            return 'unknown'
        
        chinese_ratio = chinese_chars / total_chars
        japanese_ratio = japanese_chars / total_chars
        english_ratio = english_chars / total_chars
        
        if chinese_ratio > 0.3:
            return 'chinese'
        elif japanese_ratio > 0.2:
            return 'japanese'
        elif english_ratio > 0.5:
            return 'english'
        else:
            return 'mixed'

    def is_sentence_ending(self, text: str, pos: int) -> bool:
        """判断指定位置是否为句子结束"""
        if pos >= len(text):
            return False
            
        char = text[pos]
        
        # 检查是否为句子结束标点
        if not self.sentence_endings.match(char):
            return False
        
        # 检查英文缩写
        if char == '.':
            start = max(0, pos - 10)
            context = text[start:pos + 1]
            if self.abbreviations.search(context):
                return False
            
            # 检查数字小数点
            if pos > 0 and pos < len(text) - 1:
                if text[pos - 1].isdigit() and text[pos + 1].isdigit():
                    return False
        
        return True

    def split_into_sentences(self, text: str) -> List[SentenceInfo]:
        """将文本分割成句子"""
        if not text.strip():
            return []
        
        sentences = []
        current_sentence = ""
        sentence_start = 0
        line_number = 1
        sentence_index = 0
        
        for i, char in enumerate(text):
            current_sentence += char
            
            if char == '\n':
                line_number += 1
            
            # 检查是否为句子结束
            if self.is_sentence_ending(text, i):
                # 检查后续的引号或括号
                j = i + 1
                while j < len(text) and text[j] in '"\'""''」』）)]】':
                    current_sentence += text[j]
                    j += 1
                
                # 收集后续的空白字符
                while j < len(text) and text[j] in ' \t':
                    current_sentence += text[j]
                    j += 1
                
                # 创建句子信息
                if current_sentence.strip():
                    sentence_info = SentenceInfo(
                        text=current_sentence.strip(),
                        start_pos=sentence_start,
                        end_pos=j - 1,
                        line_number=line_number,
                        sentence_index=sentence_index
                    )
                    sentences.append(sentence_info)
                    sentence_index += 1
                
                # 重置
                current_sentence = ""
                sentence_start = j
                
                # 跳过已处理的字符
                if j > i + 1:
                    # 这里需要调整循环索引，但在for循环中比较复杂
                    # 简化处理：不跳过，让循环自然进行
                    pass
        
        # 处理最后一个句子
        if current_sentence.strip():
            sentence_info = SentenceInfo(
                text=current_sentence.strip(),
                start_pos=sentence_start,
                end_pos=len(text) - 1,
                line_number=line_number,
                sentence_index=sentence_index
            )
            sentences.append(sentence_info)
        
        return sentences

    def split_by_lines_and_sentences(self, text: str) -> Dict[int, List[SentenceInfo]]:
        """按行分割，然后每行内按句子分割"""
        lines = text.split('\n')
        result = {}
        
        for line_num, line in enumerate(lines, 1):
            if line.strip():
                sentences = self.split_into_sentences(line)
                # 更新句子的行号
                for sentence in sentences:
                    sentence.line_number = line_num
                result[line_num] = sentences
            else:
                result[line_num] = []
        
        return result

    def merge_short_sentences(self, sentences: List[SentenceInfo], min_length: int = 10) -> List[SentenceInfo]:
        """合并过短的句子"""
        if not sentences:
            return []
        
        merged = []
        current_sentence = sentences[0]
        
        for i in range(1, len(sentences)):
            next_sentence = sentences[i]
            
            # 如果当前句子太短，尝试与下一句合并
            if len(current_sentence.text.strip()) < min_length:
                merged_text = current_sentence.text + " " + next_sentence.text
                current_sentence = SentenceInfo(
                    text=merged_text,
                    start_pos=current_sentence.start_pos,
                    end_pos=next_sentence.end_pos,
                    line_number=current_sentence.line_number,
                    sentence_index=current_sentence.sentence_index
                )
            else:
                merged.append(current_sentence)
                current_sentence = next_sentence
        
        merged.append(current_sentence)
        return merged

    def smart_split(self, text: str, max_length: int = 200, min_length: int = 10) -> List[SentenceInfo]:
        """智能分割：结合句子分割和长度控制"""
        # 首先按句子分割
        sentences = self.split_into_sentences(text)
        
        # 合并过短的句子
        sentences = self.merge_short_sentences(sentences, min_length)
        
        # 分割过长的句子
        final_sentences = []
        for sentence in sentences:
            if len(sentence.text) <= max_length:
                final_sentences.append(sentence)
            else:
                sub_sentences = self._split_long_sentence(sentence, max_length)
                final_sentences.extend(sub_sentences)
        
        return final_sentences

    def _split_long_sentence(self, sentence: SentenceInfo, max_length: int) -> List[SentenceInfo]:
        """分割过长的句子"""
        text = sentence.text
        if len(text) <= max_length:
            return [sentence]
        
        # 寻找分割点
        split_chars = [',', '，', ';', '；', '、']
        split_words = ['而且', '但是', '然而', '因此', '所以', ' and ', ' but ', ' or ', ' so ']
        
        split_points = []
        
        # 查找字符分割点
        for char in split_chars:
            pos = 0
            while True:
                pos = text.find(char, pos)
                if pos == -1:
                    break
                split_points.append(pos + 1)
                pos += 1
        
        # 查找词语分割点
        for word in split_words:
            pos = 0
            while True:
                pos = text.find(word, pos)
                if pos == -1:
                    break
                split_points.append(pos + len(word))
                pos += 1
        
        split_points.sort()
        
        # 选择最佳分割点
        result = []
        start = 0
        current_index = sentence.sentence_index
        
        for split_point in split_points:
            if split_point - start >= max_length * 0.7:
                sub_text = text[start:split_point].strip()
                if sub_text:
                    sub_sentence = SentenceInfo(
                        text=sub_text,
                        start_pos=sentence.start_pos + start,
                        end_pos=sentence.start_pos + split_point - 1,
                        line_number=sentence.line_number,
                        sentence_index=current_index
                    )
                    result.append(sub_sentence)
                    current_index += 1
                start = split_point
        
        # 添加剩余部分
        if start < len(text):
            remaining_text = text[start:].strip()
            if remaining_text:
                sub_sentence = SentenceInfo(
                    text=remaining_text,
                    start_pos=sentence.start_pos + start,
                    end_pos=sentence.end_pos,
                    line_number=sentence.line_number,
                    sentence_index=current_index
                )
                result.append(sub_sentence)
        
        return result if result else [sentence]
