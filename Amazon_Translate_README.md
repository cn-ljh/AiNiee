# Amazon Translate 功能说明

## 概述

AiNiee项目现已集成Amazon Translate服务，为用户提供高质量的机器翻译功能。Amazon Translate是AWS提供的神经网络机器翻译服务，支持多种语言之间的翻译。

## 功能特性

### 核心功能
- **自动语言检测**: 支持自动检测源语言
- **多语言支持**: 支持75+种语言的翻译
- **长文本处理**: 自动分块处理超过5000字符的长文本
- **高质量翻译**: 基于神经网络的机器翻译技术
- **批量翻译**: 支持批量文本翻译任务

### 技术特性
- **客户端缓存**: 使用LLMClientFactory进行客户端缓存管理
- **错误处理**: 完善的错误处理和重试机制
- **语言检测**: 内置语言检测功能
- **分块翻译**: 智能分句处理长文本

## 配置说明

### 平台配置

在`Resource/platforms/preset.json`中已添加Amazon Translate的配置：

```json
{
    "amazontranslate": {
        "tag": "amazontranslate",
        "group": "online",
        "name": "Amazon Translate",
        "region": "us-east-1",
        "access_key": "",
        "secret_key": "",
        "source_language": "auto",
        "target_language": "zh",
        "request_timeout": 60,
        "rpm_limit": 100,
        "tpm_limit": 5000000
    }
}
```

### 配置参数说明

| 参数 | 说明 | 默认值 | 必填 |
|------|------|--------|------|
| `region` | AWS区域 | us-east-1 | 是 |
| `access_key` | AWS访问密钥ID | - | 是 |
| `secret_key` | AWS秘密访问密钥 | - | 是 |
| `source_language` | 源语言代码 | auto | 否 |
| `target_language` | 目标语言代码 | zh | 是 |
| `request_timeout` | 请求超时时间(秒) | 60 | 否 |
| `rpm_limit` | 每分钟请求限制 | 100 | 否 |
| `tpm_limit` | 每分钟字符限制 | 5000000 | 否 |

### 支持的AWS区域

- `us-east-1` (美国东部-弗吉尼亚北部)
- `us-east-2` (美国东部-俄亥俄)
- `us-west-2` (美国西部-俄勒冈)
- `eu-west-1` (欧洲-爱尔兰)
- `ap-southeast-1` (亚太地区-新加坡)
- `ap-southeast-2` (亚太地区-悉尼)
- `ap-northeast-1` (亚太地区-东京)

### 支持的语言代码

#### 常用语言
- `auto` - 自动检测
- `zh` - 中文(简体)
- `zh-TW` - 中文(繁体)
- `en` - 英语
- `ja` - 日语
- `ko` - 韩语
- `fr` - 法语
- `de` - 德语
- `es` - 西班牙语
- `it` - 意大利语
- `pt` - 葡萄牙语
- `ru` - 俄语
- `ar` - 阿拉伯语
- `hi` - 印地语
- `th` - 泰语
- `vi` - 越南语

## 使用方法

### 1. 配置AWS凭证

#### 方法一：环境变量
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

#### 方法二：配置文件
在平台配置中填入AWS凭证：
```json
{
    "access_key": "your_access_key",
    "secret_key": "your_secret_key",
    "region": "us-east-1"
}
```

### 2. 配置翻译语言

Amazon Translate使用AiNiee的翻译设置功能中的语言配置：

1. 打开AiNiee应用程序
2. 进入"翻译设置"页面
3. 设置"原文语言"（支持自动检测）
4. 设置"译文语言"
5. 这些设置将自动应用到Amazon Translate服务

### 3. 在AiNiee中使用

1. 在平台设置中选择"Amazon Translate"
2. 配置AWS凭证和区域
3. 语言设置会自动从翻译设置中获取
4. 开始翻译任务

### 3. 编程接口使用

```python
from ModuleFolders.LLMRequester.AmazonTranslateRequester import AmazonTranslateRequester

# 创建请求器
requester = AmazonTranslateRequester()

# 配置参数
platform_config = {
    "region": "us-east-1",
    "access_key": "your_access_key",
    "secret_key": "your_secret_key",
    "source_language": "auto",
    "target_language": "zh",
    "request_timeout": 60
}

# 准备翻译内容
messages = [
    {
        "role": "user",
        "content": "Hello, how are you today?"
    }
]

# 执行翻译
skip, think, result, input_tokens, output_tokens = requester.request_amazon_translate(
    messages, "", platform_config
)

if not skip:
    print(f"翻译结果: {result}")
```

## 测试功能

项目根目录下提供了测试脚本`test_amazon_translate.py`：

```bash
python test_amazon_translate.py
```

测试脚本会：
1. 测试基本翻译功能
2. 获取支持的语言列表
3. 验证配置是否正确

## 费用说明

Amazon Translate按使用量计费：
- **文本翻译**: 每100万字符 $15.00
- **语言检测**: 每100万字符 $15.00
- **免费套餐**: 每月200万字符(12个月)

详细费用信息请参考[AWS定价页面](https://aws.amazon.com/translate/pricing/)。

## 限制说明

### 服务限制
- 单次请求最大文本长度: 5,000字符
- 支持的文件格式: 纯文本
- 最大请求频率: 因区域而异

### 功能限制
- 不支持自定义术语表(需要额外配置)
- 不支持实时翻译
- 批量翻译有配额限制

## 错误处理

常见错误及解决方案：

### 1. 认证错误
```
AWS客户端错误 [InvalidSignatureException]: 签名不匹配
```
**解决方案**: 检查AWS访问密钥和秘密密钥是否正确

### 2. 权限错误
```
AWS客户端错误 [AccessDeniedException]: 用户无权限
```
**解决方案**: 确保AWS用户具有`translate:TranslateText`权限

### 3. 配额超限
```
AWS客户端错误 [ThrottlingException]: 请求频率过高
```
**解决方案**: 降低请求频率或申请提高配额

### 4. 区域错误
```
AWS客户端错误 [InvalidParameterValueException]: 不支持的区域
```
**解决方案**: 使用支持Amazon Translate的AWS区域

## 最佳实践

### 1. 性能优化
- 使用就近的AWS区域减少延迟
- 合理设置请求超时时间
- 批量处理小文本以提高效率

### 2. 成本控制
- 监控翻译字符数使用量
- 使用CloudWatch设置费用告警
- 考虑使用预留容量降低成本

### 3. 质量提升
- 针对特定领域使用自定义术语表
- 预处理文本去除不必要的格式
- 后处理结果进行质量检查

## 技术架构

### 文件结构
```
ModuleFolders/LLMRequester/
├── AmazonTranslateRequester.py    # Amazon Translate请求器
├── LLMClientFactory.py            # 客户端工厂(已更新)
└── LLMRequester.py                # 主请求分发器(已更新)

Resource/platforms/
└── preset.json                    # 平台配置(已更新)
```

### 类关系
- `AmazonTranslateRequester`: 核心翻译逻辑
- `LLMClientFactory`: 客户端缓存管理
- `LLMRequester`: 请求路由分发

## 更新日志

### v1.0.0 (2025-01-03)
- ✅ 添加Amazon Translate支持
- ✅ 实现自动语言检测
- ✅ 支持长文本分块翻译
- ✅ 集成到LLM请求器框架
- ✅ 添加平台配置支持
- ✅ 提供测试脚本

## 支持与反馈

如果在使用过程中遇到问题，请：
1. 检查AWS凭证配置
2. 验证网络连接
3. 查看错误日志
4. 参考AWS官方文档

## 相关链接

- [Amazon Translate官方文档](https://docs.aws.amazon.com/translate/)
- [AWS SDK for Python文档](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/translate.html)
- [支持的语言列表](https://docs.aws.amazon.com/translate/latest/dg/what-is-languages.html)
- [AWS定价信息](https://aws.amazon.com/translate/pricing/)
