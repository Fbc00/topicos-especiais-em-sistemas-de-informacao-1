"""Agente minimo com function calling + experimento sobre a descricao da tool.

Uso:
    python simple_agent.py                      # descricao boa
    python simple_agent.py --vago               # descricao ruim na consulta_cep
    python simple_agent.py --vago --n 5         # 5 rodadas
"""

import argparse
import json
import urllib.request
from collections.abc import Callable
from datetime import datetime
from typing import Any, TypedDict, cast

MAX_PASSOS: int = 6
MODELO: str = "qwen2.5:7b"
OLLAMA: str = "http://localhost:11434/api/chat"
PERGUNTA: str = "Qual o bairro do CEP 01310-100?"


class ToolFunctionSchema(TypedDict):
    name: str
    description: str
    parameters: dict[str, Any]


class ToolSchema(TypedDict):
    type: str
    function: ToolFunctionSchema


class ToolCallFunction(TypedDict):
    name: str
    arguments: dict[str, Any]


class ToolCall(TypedDict):
    function: ToolCallFunction


class ChatMessage(TypedDict, total=False):
    role: str
    content: str
    name: str
    tool_calls: list[ToolCall]


class RunResult(TypedDict):
    passos: int
    chamadas: list[str]
    resposta: str


def hora_atual() -> str:
    """Retorna a data e a hora local atuais no formato ISO 8601."""
    return datetime.now().isoformat(timespec="seconds")


def consulta_cep(cep: str | int) -> dict[str, Any]:
    """Consulta um CEP brasileiro e retorna logradouro, bairro, cidade e UF."""
    cep = "".join(c for c in str(cep) if c.isdigit())
    url = f"https://viacep.com.br/ws/{cep}/json/"
    with urllib.request.urlopen(url, timeout=10) as r:
        return cast(dict[str, Any], json.load(r))


TOOLS: dict[str, Callable[..., Any]] = {"hora_atual": hora_atual, "consulta_cep": consulta_cep}

DESC_BOA: str = consulta_cep.__doc__ or ""
DESC_VAGA: str = "Faz uma consulta."


def schemas(vago: bool = False) -> list[ToolSchema]:
    return [
        {"type": "function", "function": {
            "name": "hora_atual",
            "description": hora_atual.__doc__ or "",
            "parameters": {"type": "object", "properties": {}, "required": []}}},
        {"type": "function", "function": {
            "name": "consulta_cep",
            "description": DESC_VAGA if vago else DESC_BOA,
            "parameters": {"type": "object", "properties": {
                "cep": {"type": "string", "description": "CEP com 8 digitos"}},
                "required": ["cep"]}}},
    ]


def chat(messages: list[ChatMessage], tools: list[ToolSchema]) -> ChatMessage:
    body = json.dumps({"model": MODELO, "messages": messages,
                       "tools": tools, "stream": False,
                       "options": {"temperature": 0}}).encode()
    req = urllib.request.Request(OLLAMA, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return cast(ChatMessage, json.load(r)["message"])


def rodar(pergunta: str, vago: bool = False, verbose: bool = True) -> RunResult:
    messages: list[ChatMessage] = [{"role": "user", "content": pergunta}]
    tools: list[ToolSchema] = schemas(vago)
    chamadas: list[str] = []

    for passo in range(1, MAX_PASSOS + 1):
        msg = chat(messages, tools)
        messages.append(msg)

        if not msg.get("tool_calls"):
            return {"passos": passo, "chamadas": chamadas, "resposta": msg.get("content", "")}

        for tc in msg["tool_calls"]:
            nome: str = tc["function"]["name"]
            args: dict[str, Any] = tc["function"]["arguments"]
            chamadas.append(nome)
            if verbose:
                print(f"  passo {passo}: {nome}({args})")
            out: Any
            try:
                out = TOOLS[nome](**args)
            except Exception as e:
                out = f"erro: {e}"
            messages.append({"role": "tool", "name": nome, "content": json.dumps(out, ensure_ascii=False)})

    return {"passos": MAX_PASSOS, "chamadas": chamadas, "resposta": "(estourou MAX_PASSOS)"}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--vago", action="store_true")
    p.add_argument("--n", type=int, default=1)
    p.add_argument("--pergunta", default=PERGUNTA)
    a = p.parse_args()

    print(f"descricao: {'VAGA' if a.vago else 'BOA'} | pergunta: {a.pergunta}\n")
    for i in range(a.n):
        print(f"rodada {i + 1}")
        r: RunResult = rodar(a.pergunta, a.vago)
        print(f"  -> {r['passos']} passos | tools: {' > '.join(r['chamadas']) or 'nenhuma'}")
        print(f"  -> {r['resposta'][:200]}\n")
