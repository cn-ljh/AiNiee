from Base.Base import Base
from ModuleFolders.LLMRequester.LLMClientFactory import LLMClientFactory


# 接口请求器
class LocalLLMRequester(Base):
    def __init__(self) -> None:
        pass

    # 发起请求
    def request_LocalLLM(self, messages, system_prompt, platform_config) -> tuple[bool, str, str, int, int]:
        try:
            model_name = platform_config.get("model_name")
            request_timeout = platform_config.get("request_timeout", 60)
            temperature = platform_config.get("temperature", 1.0)
            top_p = platform_config.get("top_p", 1.0)
            frequency_penalty = platform_config.get("frequency_penalty", 0)
            think_switch = platform_config.get("think_switch")

            # 参数基础配置
            base_params = {
                "model": model_name,
                "messages": messages,
                "timeout": request_timeout
            }

            # 按需添加参数
            if temperature != 1:
                base_params.update({
                    "temperature": temperature,
                })

            if top_p != 1:
                base_params.update({
                    "top_p": top_p,
                })

            if frequency_penalty != 0:
                base_params.update({
                    "frequency_penalty": frequency_penalty
                })

            # 假如打开了思考开关
            if think_switch:
                base_params.update({
                    "extra_body": {"enable_thinking": "true"}
                })


            # 插入系统消息
            if system_prompt:
                messages.insert(
                    0,
                    {
                        "role": "system",
                        "content": system_prompt
                    })

            # 从工厂获取客户端
            client = LLMClientFactory().get_openai_client_local(platform_config)

            response = client.chat.completions.create(**base_params)

            # 提取回复内容
            message = response.choices[0].message

            # 自适应提取推理过程
            if "</think>" in message.content:
                splited = message.content.split("</think>")
                response_think = splited[0].removeprefix("<think>").replace("\n\n", "\n")
                response_content = splited[-1]
            else:
                try:
                    response_think = message.reasoning_content
                    if not response_think:
                        response_think = ""
                except Exception:
                    response_think = ""
                response_content = message.content

        except Exception as e:
            self.error(f"请求任务错误 ... {e}", e if self.is_debug() else None)
            return True, None, None, None, None

        # 获取指令消耗
        try:
            prompt_tokens = int(response.usage.prompt_tokens)
        except Exception:
            prompt_tokens = 0

        # 获取回复消耗
        try:
            completion_tokens = int(response.usage.completion_tokens)
        except Exception:
            completion_tokens = 0

        return False, response_think, response_content, prompt_tokens, completion_tokens
