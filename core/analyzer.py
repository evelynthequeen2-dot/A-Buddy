"""A-Buddy 作业图片解析模块。"""
import base64
import json
import os
import re
from typing import Any

from dotenv import load_dotenv
from zhipuai import ZhipuAI

load_dotenv()

MODEL_NAME = "glm-4v"

ANALYSIS_PROMPT = """你是一个严格的机器接口。请你逐字逐句阅读图片中的所有文字。
任务要求：

图片里有几条考核要求，你就必须拆解出几个 task！**绝对禁止只提取第一条就停止！**绝对禁止遗漏！

你的输出必须是合法的 JSON 格式。不能有任何多余的开头问候或结尾解释。

JSON 格式如下：
{
"deadline": "【警告】绝对不允许猜测、推断或自己编造日期！如果图片中没有明确印着具体的年月日，必须原封不动地返回 '未写明' 三个字！",
"tasks": [
{"step": 1, "task_name": "完整任务名1", "details": "详细描述1"},
{"step": 2, "task_name": "完整任务名2", "details": "详细描述2"}
]
}
注意：JSON 的 key 和 value 必须使用双引号。
"""


def clean_and_parse_json(raw_text: str):
    try:
        return json.loads(raw_text)
    except Exception:
        pass

    match = re.search(r"\{[\s\S]*\}", raw_text)
    if match:
        candidate = match.group(0)
        candidate = candidate.replace("\r", " ").replace("\n", " ").replace("\t", " ")
        candidate = re.sub(r"[\x00-\x1f\x7f]", "", candidate).strip()
        try:
            return json.loads(candidate)
        except Exception:
            return {"error": "parse_failed", "raw_content": raw_text}

    return {"error": "parse_failed", "raw_content": raw_text}



def get_api_key() -> str:
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key or not api_key.strip():
        raise ValueError("未找到 ZHIPU_API_KEY，请在项目根目录的 .env 文件中配置。")
    return api_key.strip()


def _extract_json_text(raw_text: str) -> str:
    text = raw_text.strip()

    codeblock_match = re.search(r"```json\s*(.*?)\s*```", text, re.IGNORECASE | re.DOTALL)
    if codeblock_match:
        return codeblock_match.group(1).strip()

    generic_codeblock_match = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
    if generic_codeblock_match:
        candidate = generic_codeblock_match.group(1).strip()
        if candidate.startswith("{") and candidate.endswith("}"):
            return candidate

    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    if json_match:
        return json_match.group(0).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1].strip()

    raise ValueError("模型返回内容中未找到有效 JSON。")


def parse_analysis_json(raw_text: str) -> dict[str, Any]:
    """安全解析模型返回的 JSON 文本。"""
    parsed = clean_and_parse_json(raw_text)

    if isinstance(parsed, dict) and parsed.get("error") == "parse_failed":
        return parsed

    if not isinstance(parsed, dict):
        return {"error": "parse_failed", "raw_content": raw_text}

    deadline = parsed.get("deadline", "未写明")
    tasks = parsed.get("tasks", [])

    if not isinstance(deadline, str):
        deadline = str(deadline)

    if not isinstance(tasks, list):
        return {"error": "parse_failed", "raw_content": raw_text}

    normalized_tasks = []
    for index, item in enumerate(tasks, start=1):
        if not isinstance(item, dict):
            return {"error": "parse_failed", "raw_content": raw_text}

        step = item.get("step", index)
        task_name = item.get("task_name", "")
        details = item.get("details", "")

        normalized_tasks.append(
            {
                "step": int(step),
                "task_name": str(task_name),
                "details": str(details),
            }
        )

    return {"deadline": deadline, "tasks": normalized_tasks}


def analyze_assignment_image(image_bytes: bytes, mime_type: str | None = None) -> dict[str, Any]:
    """将作业图片传入模型，并返回解析后的 JSON 字典。"""
    client = ZhipuAI(api_key=get_api_key())

    img_b64 = base64.b64encode(image_bytes).decode("utf-8")
    if mime_type and mime_type.startswith("image/"):
        img_url = f"data:{mime_type};base64,{img_b64}"
    else:
        img_url = f"data:image/png;base64,{img_b64}"

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": ANALYSIS_PROMPT},
                {"type": "image_url", "image_url": {"url": img_url}},
            ],
        }
    ]

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        timeout=60,
        temperature=0.2,
        max_tokens=2048,
    )

    if not response.choices or not response.choices[0].message.content:
        raise ValueError("模型未返回有效内容，请换一张更清晰的图片后重试。")

    raw_text = response.choices[0].message.content.strip()
    return parse_analysis_json(raw_text)
