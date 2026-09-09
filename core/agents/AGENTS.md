# AGENTS.md — core/agents

Regras deste diretorio. Contexto geral do projeto e convencoes de codigo: `AGENTS.md` na raiz.

## O que mora aqui

Um arquivo por agente, executavel direto. Cada script e autocontido: define suas tools, monta o
schema, roda o loop e imprime o resultado. Nao ha modulo compartilhado entre agentes — duplicar
uma funcao curta e preferivel a criar abstracao que esconda o loop, que e justamente o objeto de
estudo.

Nao ha `__init__.py`: estes arquivos sao rodados (`python core/agents/x.py`), nao importados.

Arquivos:

- `simple_agent.py` — agente minimo com function calling + experimento de descricao de tool

## Como rodar

Ollama precisa estar no ar com o modelo baixado:

```bash
ollama pull qwen2.5:7b
```

```bash
python core/agents/simple_agent.py                 # descricao boa da tool
python core/agents/simple_agent.py --vago          # descricao vaga da tool
python core/agents/simple_agent.py --vago --n 5    # 5 rodadas
python core/agents/simple_agent.py --pergunta "Que horas sao?"
```

## Anatomia de um agente

Ordem fixa no arquivo:

1. Docstring do modulo com secao `Uso:` listando as invocacoes possiveis
2. Imports (stdlib apenas)
3. Constantes MAIUSCULAS: `MAX_PASSOS`, `MODELO`, `OLLAMA`, `PERGUNTA`
4. `TypedDict`s do protocolo: `ToolSchema`, `ChatMessage`, `ToolCall`, `RunResult`
5. Funcoes-tool
6. `TOOLS: dict[str, Callable[..., Any]]`
7. `schemas()` — schema JSON enviado ao modelo
8. `chat()` — uma chamada HTTP ao Ollama
9. `rodar()` — o loop
10. `if __name__ == "__main__":` com `argparse`

## Contrato do loop

`rodar()` itera no maximo `MAX_PASSOS` (6) vezes:

1. `chat()` envia `messages` + `tools` ao Ollama e devolve a `message` da resposta
2. resposta sem `tool_calls` → encerra e devolve `RunResult`
3. resposta com `tool_calls` → executa cada tool do dict `TOOLS`, anexa
   `{"role": "tool", "name": ..., "content": ...}` em `messages` e repete
4. estourou os passos → devolve `resposta: "(estourou MAX_PASSOS)"`

Invariantes:

- `messages` cresce sempre: a mensagem do assistente entra **antes** de executar as tools
- excecao de tool nao aborta o loop — vira `f"erro: {e}"` no historico e o modelo decide o proximo
  passo. Nao troque isso por `raise`
- `content` de mensagem tool e sempre `json.dumps(out, ensure_ascii=False)`
- `temperature: 0` e `stream: False` no body — o experimento depende de saida reprodutivel
- toda tool executada e registrada em `chamadas`, na ordem, inclusive quando falha

Tools atuais: `hora_atual()` e `consulta_cep(cep)`.

## Escrever uma tool

- Docstring da funcao **e** a `description` enviada ao modelo. Escreva para o LLM ler: o que faz e
  o que retorna, uma linha. Ela nao e documentacao interna — remover ou reescrever muda o
  comportamento do agente.
- Registre a funcao em `TOOLS` e adicione a entrada correspondente em `schemas()`. As duas listas
  precisam bater: `TOOLS[nome]` e chamado com `**args` vindos do modelo.
- Parametros do schema descrevem o formato esperado (`"CEP com 8 digitos"`). A tool ainda assim
  normaliza/valida a entrada — o modelo manda o que quiser.
- Retorno tem que ser serializavel por `json.dumps`.
- Chamada de rede: `timeout` explicito sempre.

## Experimentos

Comparacao faz parte do conteudo. Padrao atual: `--vago` troca a `description` de `consulta_cep`
entre `DESC_BOA` (docstring real) e `DESC_VAGA`, e `--n` repete a rodada para ver a variacao.

Ao criar um experimento novo, mantenha o formato: uma flag booleana que altera **uma** variavel,
`--n` para repeticao, e saida por rodada com passos + sequencia de tools.

## Verificar antes de dizer que terminou

Mudanca em schema de tool ou no loop altera o resultado do experimento — rode e confira a saida.

```bash
python -m py_compile core/agents/simple_agent.py
python core/agents/simple_agent.py --pergunta "Que horas sao?"
```

A primeira nao precisa de Ollama. A segunda precisa e exercita o loop completo sem depender de
rede externa alem do proprio modelo.
