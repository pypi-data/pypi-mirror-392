from typing import ClassVar, List, Optional

from jupyter_ai import BaseProvider
from jupyter_ai_magics.models.persona import JUPYTERNAUT_AVATAR_ROUTE, Persona
from langchain.prompts import PromptTemplate

from .llm import WekeoLLM

TEMPLATE = """
History: {{history}}
Human: {{input}}
"""


class WekeoProvider(BaseProvider, WekeoLLM):
    id: ClassVar[str] = "wekeo-provider"
    name: ClassVar[str] = "Wekeo Provider"
    models: ClassVar[List[str]] = ["server"]
    model_id_key: ClassVar[str] = "model_id_key"
    model_id_label: ClassVar[str] = "model_id_label"
    unsupported_slash_commands: ClassVar[set] = {"/learn", "/ask", "/generate", "/fix"}
    persona: ClassVar[Optional[Persona]] = Persona(
        name="WEkEO Experimental AI-based Assistant",
        avatar_route=JUPYTERNAUT_AVATAR_ROUTE,
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_chat_prompt_template(self) -> PromptTemplate:
        """
        Returns a formatted PromptTemplate that structures the chat prompt
        with placeholders for conversation history and current user input.
        """

        return PromptTemplate(
            input_variables=["history", "input"],
            template=TEMPLATE,
            template_format="jinja2",
        )
