from pathlib import Path
from typing import List

from ModuleFolders.Cache.CacheFile import CacheFile
from ModuleFolders.Cache.CacheItem import CacheItem
from ModuleFolders.Cache.CacheProject import ProjectType
from ModuleFolders.FileReader.BaseReader import (
    BaseSourceReader,
    InputConfig,
    PreReadMetadata
)
from ModuleFolders.TextProcessor.SentenceSplitter import SentenceSplitter, SentenceInfo


class TxtSentenceReader(BaseSourceReader):
    """
    支持按句子分割的TXT文件读取器
    """
    
    def __init__(self, input_config: InputConfig, sentence_mode: bool = False, 
                 max_sentence_length: int = 200, min_sentence_length: int = 10):
        super().__init__(input_config)
        self.sentence_mode = sentence_mode  # 是否启用句子分割模式
        self.max_sentence_length = max_sentence_length
        self.min_sentence_length = min_sentence_length
        self.sentence_splitter = SentenceSplitter() if sentence_mode else None

    @classmethod
    def get_project_type(cls):
        return ProjectType.TXT

    @property
    def support_file(self):
        return "txt"

    def on_read_source(self, file_path: Path, pre_read_metadata: PreReadMetadata) -> CacheFile:
        """读取单个txt文件的文本及其他信息"""
        items = []
        
        # 读取文件内容
        content = file_path.read_text(encoding=pre_read_metadata.encoding)
        
        if self.sentence_mode and self.sentence_splitter:
            # 按句子分割模式
            items = self._process_by_sentences(content)
        else:
            # 传统按行分割模式
            items = self._process_by_lines(content)
        
        return CacheFile(items=items)

    def _process_by_lines(self, content: str) -> List[CacheItem]:
        """传统的按行处理模式"""
        items = []
        lines = content.splitlines()
        
        for i, line in enumerate(lines):
            # 跳过空行（除了文本开头）
            if not line.strip() and i != 0:
                continue

            # 去掉文本开头的BOM
            line_lstrip = line.lstrip("\ufeff")
            extra = {
                "line_break": self._count_next_empty_line(lines, i),
                "processing_mode": "line"
            }
            item = CacheItem(source_text=line_lstrip, extra=extra)
            items.append(item)
        
        return items

    def _process_by_sentences(self, content: str) -> List[CacheItem]:
        """按句子处理模式"""
        items = []
        
        # 使用智能分割获取句子
        if self.sentence_splitter:
            sentences = self.sentence_splitter.smart_split(
                content, 
                max_length=self.max_sentence_length,
                min_length=self.min_sentence_length
            )
        else:
            sentences = []
        
        for sentence_info in sentences:
            # 计算该句子后面的空行数（基于原始位置）
            line_break_count = self._estimate_line_breaks_after_sentence(
                content, sentence_info
            )
            
            extra = {
                "line_break": line_break_count,
                "processing_mode": "sentence",
                "original_line_number": sentence_info.line_number,
                "sentence_index": sentence_info.sentence_index,
                "start_pos": sentence_info.start_pos,
                "end_pos": sentence_info.end_pos
            }
            
            item = CacheItem(source_text=sentence_info.text, extra=extra)
            items.append(item)
        
        return items

    def _estimate_line_breaks_after_sentence(self, content: str, sentence_info: SentenceInfo) -> int:
        """估算句子后面的换行数量"""
        # 获取句子结束位置到下一个非空白字符之间的换行数
        end_pos = sentence_info.end_pos
        if end_pos >= len(content) - 1:
            return 0
        
        # 从句子结束位置开始查找
        line_breaks = 0
        pos = end_pos + 1
        
        while pos < len(content):
            char = content[pos]
            if char == '\n':
                line_breaks += 1
            elif char not in ' \t\r':
                # 遇到非空白字符，停止计数
                break
            pos += 1
        
        return line_breaks

    def _count_next_empty_line(self, lines: List[str], line_index: int) -> int:
        """检查后续行是否连续空行（用于行模式）"""
        empty_line_index = line_index
        for empty_line_index in range(line_index + 1, len(lines)):
            if lines[empty_line_index].strip() != '':
                empty_line_index -= 1
                break
        return empty_line_index - line_index

    def get_processing_statistics(self, cache_file: CacheFile) -> dict:
        """获取处理统计信息"""
        total_items = len(cache_file.items)
        
        if self.sentence_mode:
            sentence_items = sum(1 for item in cache_file.items 
                               if item.extra.get("processing_mode") == "sentence")
            return {
                "total_items": total_items,
                "sentence_items": sentence_items,
                "processing_mode": "sentence",
                "max_sentence_length": self.max_sentence_length,
                "min_sentence_length": self.min_sentence_length
            }
        else:
            line_items = sum(1 for item in cache_file.items 
                           if item.extra.get("processing_mode") == "line")
            return {
                "total_items": total_items,
                "line_items": line_items,
                "processing_mode": "line"
            }
