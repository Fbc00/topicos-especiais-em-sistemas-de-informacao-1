# AGENTS.md

## O que e este projeto

Repositorio de estudos da disciplina **Topicos Especiais em Sistemas de Informacao 1** (faculdade).
O objetivo e didatico: entender como agentes de LLM funcionam por dentro, escrevendo o loop de
function calling na mao em vez de usar framework pronto.

Consequencias praticas disso:

- Clareza vale mais que abstracao. Codigo curto e legivel > arquitetura generica.
- Cada script deve rodar sozinho e mostrar o que esta acontecendo (print de cada passo).
- Experimentos comparativos fazem parte do conteudo (ex.: flag `--vago` compara o efeito
  da qualidade da descricao da tool no comportamento do modelo).

## Estrutura

```
README.md
AGENTS.md
core/
  __init__.py        vazio
  config.py          vazio (reservado para configuracao compartilhada)
  agents/
    simple_agent.py  agente minimo com function calling
diario/              anotacoes da disciplina (vazio)
```

`core/agents/` ainda nao tem `__init__.py`; os scripts sao executados diretamente, nao importados
como pacote.

## Stack

- Python 3.11
- Somente biblioteca padrao: `argparse`, `json`, `urllib.request`, `datetime`, `typing`
- LLM local via **Ollama** em `http://localhost:11434/api/chat`, modelo `qwen2.5:7b`
- API externa de exemplo: ViaCEP (`https://viacep.com.br/ws/{cep}/json/`)

Nao ha `requirements.txt`, `pyproject.toml`, gerenciador de ambiente nem suite de testes.
Nao adicione dependencia externa sem o usuario pedir — a ausencia delas e proposital.

## Como rodar

Ollama precisa estar rodando com o modelo baixado:

```bash
ollama pull qwen2.5:7b
```

Agente:

```bash
python core/agents/simple_agent.py                 # descricao boa da tool
python core/agents/simple_agent.py --vago          # descricao vaga da tool
python core/agents/simple_agent.py --vago --n 5    # 5 rodadas
python core/agents/simple_agent.py --pergunta "Que horas sao?"
```

Verificacao rapida sem rede/Ollama:

```bash
python -m py_compile core/agents/simple_agent.py
```

## Como o agente funciona (`simple_agent.py`)

Loop de no maximo `MAX_PASSOS` (6) iteracoes:

1. `chat()` envia `messages` + `tools` para o Ollama.
2. Se a resposta nao tem `tool_calls`, encerra e devolve `RunResult`.
3. Se tem, executa cada tool do dict `TOOLS`, anexa `{"role": "tool", ...}` em `messages` e repete.

Tools disponiveis: `hora_atual()` e `consulta_cep(cep)`. O schema enviado ao modelo vem de
`schemas(vago)`; a `description` de `consulta_cep` alterna entre o docstring real (`DESC_BOA`)
e `DESC_VAGA` para o experimento.

Erro de tool nao interrompe o loop: vira string `"erro: ..."` no historico e o modelo decide o
que fazer.

## Convencoes de codigo

- **Sem comentarios novos.** Comentario existente permanece intacto. O "porque" vai na mensagem
  de commit, nao no arquivo.
- **Docstrings sao codigo aqui**: o docstring de uma tool e enviado ao modelo como `description`.
  Nao remova nem reescreva sem intencao — muda o comportamento do agente.
- Tipagem completa: anotacoes em parametros, retornos, constantes de modulo e locais nao obvios.
  Estruturas de dado do protocolo usam `TypedDict` (`ToolSchema`, `ChatMessage`, `ToolCall`,
  `RunResult`); `json.load` retorna `Any`, entao use `cast`.
- Sintaxe moderna: `list[str]`, `dict[str, Any]`, `str | int`, `collections.abc.Callable`.
- Identificadores, docstrings e saida em portugues **sem acentos** (`hora_atual`, `passos`,
  `chamadas`, `descricao`).
- Constantes de configuracao em MAIUSCULAS no topo do modulo.
- Cada script tem bloco `if __name__ == "__main__":` com `argparse`.

## Ao mexer aqui

- Leia o arquivo inteiro antes de editar; prefira edicao pontual a reescrita.
- Mudanca em schema de tool ou no loop altera o resultado do experimento — rode o script e
  confira a saida antes de dizer que terminou.
- `diario/` e para anotacoes da materia em markdown, nao para codigo.
- Nao commite `__pycache__/`.
