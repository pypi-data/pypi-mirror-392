import os
import re
import uuid
from typing import Any, Iterator, List, Optional

from langchain.llms.base import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.outputs.generation import GenerationChunk
from langserve import RemoteRunnable


def extract_after_keyword(text, keyword):
    """Extract Human or History content from jupyter_ai_wekeo.jupyter_ai_wekeo.TEMPLATE.

    Args:
        text (str): formatted jupyter_ai_wekeo.jupyter_ai_wekeo.TEMPLATE
        keyword (str): "Human" or "History"

    Returns:
        str: returns the extracted contect after the keyword.
    """
    keyword_pos = text.find(keyword)
    if keyword_pos == -1:
        return None

    start_pos = keyword_pos + len(keyword)
    end_pos = text.find("Human:", start_pos)

    if end_pos == -1:
        end_pos = len(text)

    return text[start_pos:end_pos].strip()


def parse_chat_history(chat_string):
    """Convert a HumanMessage|AIMessage list string in a list of messages.

    Args:
        chat_string (str): string list of messages

    Returns:
        list: list of messages
    """

    pattern = r"(HumanMessage|AIMessage)\(content=['\"](.*?)['\"], additional_kwargs=(\{.*?\})\)"
    messages = []

    matches = re.findall(pattern, chat_string)

    for message_type, content, additional_kwargs in matches:
        additional_kwargs_dict = eval(additional_kwargs)

        if message_type == "HumanMessage":
            messages.append(
                HumanMessage(content=content, additional_kwargs=additional_kwargs_dict)
            )
        elif message_type == "AIMessage":
            messages.append(
                AIMessage(content=content, additional_kwargs=additional_kwargs_dict)
            )

    return messages


class WekeoLLM(LLM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session_id = str(uuid.uuid4())
        self.endpoint = kwargs.get("endpoint")
        self.chat = RemoteRunnable(self.endpoint)

    @property
    def _llm_type(self) -> str:
        return "custom_llm"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        whole_str = ""
        for chunk in self.chat.stream(
            {
                "user_id": os.environ.get("JUPYTERHUB_USER"),
                "question": prompt,
                "chat_history": [],
                "jupyter": True,
            }
        ):
            if isinstance(chunk, AIMessage):
                chunk = chunk.content
            whole_str += chunk
        return whole_str

    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        history_content = extract_after_keyword(prompt, "History:")
        human_content = extract_after_keyword(prompt, "Human:")
        history_content_list = parse_chat_history(history_content)

        for chunk in self.chat.stream(
            {
                "user_id": os.environ.get("JUPYTERHUB_USER"),
                "question": human_content,
                "chat_history": history_content_list,
                "jupyter": True,
            }
        ):
            if isinstance(chunk, AIMessage):
                chunk = chunk.content
            chunk = GenerationChunk(text=chunk)
            yield chunk
