# AGENTS.md — core/agents

Regras deste diretorio. Contexto geral do projeto e convencoes de codigo: `AGENTS.md` na raiz.

## O que mora aqui

Um arquivo por agente, executavel direto. Cada script e autocontido: define suas tools, monta o
schema, roda o loop e imprime o resultado. Nao ha modulo compartilhado entre agentes — duplicar
uma funcao curta e preferivel a criar abstracao que esconda o loop, que e justamente o objeto de
estudo.

Nao ha `__init__.py`: estes arquivos sao rodados (`python core/agents/x.py`), nao importados.

Arquivos:

- `simple_agent.py` — agente minimo com function calling

O que cada agente faz e como usar esta no docstring do proprio script, secao `Uso:`.

## Como rodar

Ollama precisa estar no ar com o modelo baixado (`ollama pull qwen2.5:7b`).

```bash
python core/agents/simple_agent.py --help
```

## Escrever um agente

Estrutura do arquivo, nesta ordem: docstring de modulo com secao `Uso:`, imports (stdlib apenas),
constantes MAIUSCULAS, `TypedDict`s do protocolo, funcoes-tool, dict `TOOLS`, `schemas()`,
`chat()`, `rodar()`, bloco `if __name__ == "__main__":` com `argparse`.

Regras do loop:

- limite de passos explicito, com resposta propria quando estoura
- a mensagem do assistente entra no historico **antes** de executar as tools
- excecao de tool nao aborta o loop: vira texto de erro no historico e o modelo decide o proximo
  passo. Nao troque por `raise`
- `content` de mensagem tool serializado com `json.dumps(..., ensure_ascii=False)`
- `temperature: 0` e `stream: False` — a saida precisa ser reprodutivel
- registre as tools chamadas, na ordem, inclusive quando falham

## Escrever uma tool

- Docstring da funcao **e** a `description` enviada ao modelo. Escreva para o LLM ler: o que faz e
  o que retorna, uma linha. Ela nao e documentacao interna — remover ou reescrever muda o
  comportamento do agente.
- Registre a funcao em `TOOLS` e adicione a entrada correspondente em `schemas()`. As duas listas
  precisam bater: `TOOLS[nome]` e chamado com `**args` vindos do modelo.
- O schema descreve o formato esperado, mas a tool normaliza/valida a entrada — o modelo manda o
  que quiser.
- Retorno tem que ser serializavel por `json.dumps`.
- Chamada de rede: `timeout` explicito sempre.

## Experimentos

Comparacao faz parte do conteudo: uma flag booleana altera **uma** variavel, `--n` repete a
rodada, e a saida por rodada mostra passos + sequencia de tools.

## Verificar antes de dizer que terminou

Mudanca em schema de tool ou no loop altera o resultado do experimento — rode e confira a saida.

```bash
python -m py_compile core/agents/simple_agent.py
python core/agents/simple_agent.py
```

A primeira nao precisa de Ollama.
