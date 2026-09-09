# AGENTS.md

Guia para agentes de IA que trabalham neste repositorio.

> **Antes de mexer em `core/agents/`, leia [`core/agents/AGENTS.md`](core/agents/AGENTS.md).**
> Ele tem o contrato do loop, como escrever uma tool, como rodar e como verificar.

## O que e este projeto

Repositorio de estudos da disciplina **Topicos Especiais em Sistemas de Informacao 1** (faculdade).
O objetivo e didatico: entender como agentes de LLM funcionam por dentro, escrevendo o loop de
function calling na mao em vez de usar framework pronto.

Consequencias praticas disso:

- Clareza vale mais que abstracao. Codigo curto e legivel > arquitetura generica.
- Cada script deve rodar sozinho e mostrar o que esta acontecendo (print de cada passo).
- Experimentos comparativos fazem parte do conteudo: uma flag altera uma variavel e a saida
  mostra o efeito no comportamento do modelo.

## Estrutura

```
README.md
AGENTS.md
core/
  __init__.py        vazio
  config.py          vazio (reservado para configuracao compartilhada)
  agents/
    AGENTS.md        regras do diretorio de agentes (leia antes de editar um agente)
    simple_agent.py  agente minimo com function calling
diario/              anotacoes da disciplina (vazio)
```

`core/agents/` nao tem `__init__.py`; os scripts sao executados diretamente, nao importados
como pacote.

## Stack

- Python 3.11
- Somente biblioteca padrao: `argparse`, `json`, `urllib.request`, `datetime`, `typing`
- LLM local via **Ollama** em `http://localhost:11434/api/chat`, modelo `qwen2.5:7b`
- API externa de exemplo: ViaCEP (`https://viacep.com.br/ws/{cep}/json/`)

Nao ha `requirements.txt`, `pyproject.toml`, gerenciador de ambiente nem suite de testes.
Nao adicione dependencia externa sem o usuario pedir — a ausencia delas e proposital.

## Convencoes de codigo

- **Sem comentarios novos.** Comentario existente permanece intacto. O "porque" vai na mensagem
  de commit, nao no arquivo.
- Tipagem completa: anotacoes em parametros, retornos, constantes de modulo e locais nao obvios.
  Estruturas vindas de JSON usam `TypedDict`; `json.load` retorna `Any`, entao use `cast`.
- Sintaxe moderna: `list[str]`, `dict[str, Any]`, `str | int`, `collections.abc.Callable`.
- Identificadores, docstrings e saida em portugues **sem acentos** (`hora_atual`, `passos`,
  `chamadas`, `descricao`).
- Constantes de configuracao em MAIUSCULAS no topo do modulo.
- Cada script tem bloco `if __name__ == "__main__":` com `argparse`.

## Ao mexer aqui

- Leia o arquivo inteiro antes de editar; prefira edicao pontual a reescrita.
- Trabalho em `core/agents/` segue tambem [`core/agents/AGENTS.md`](core/agents/AGENTS.md).
- `diario/` e para anotacoes da materia em markdown, nao para codigo.
- Nao commite `__pycache__/`.
