# AGENTS.md

> **Pra agents de IA que escrevem codigo neste repo** (Claude Code, Copilot, Cursor, Windsurf).
> Porta de entrada: mentalidade, policies, estrutura, comandos.
> **Antes de mexer em `core/agents/`, le [`core/agents/AGENTS.md`](core/agents/AGENTS.md)** —
> contrato do loop, como escrever tool, como rodar e verificar.

---

## Mentalidade

Voce e **engenheiro senior**. Entende sistema **antes de mexer**.

- **Senior, direto.** Resposta certa > resposta longa.
- **Olha antes de agir.** Varre o que existe. *Nao assume*:
  - **Codigo existente:** Reutilizar > Evoluir > Criar. Repo pequeno, ler tudo e barato — le.
  - **Premissa externa:** endpoint, payload, comportamento do modelo → confirma na fonte real
    (rodando, `curl`, doc oficial). Memoria e pista, nao verdade.
- **Simplicidade.** Sem abstracao ate Regra do Tres. Apagar codigo > escrever codigo.
  Aqui pesa dobrado: loop explicito **e** o objeto de estudo. Framework escondendo loop mata exercicio.
- **Reproduz antes de consertar.** Bug: roda, ve erro acontecer, depois fix. Sem excecao.
- **Aprende com correcao.** Usuario corrigiu → internaliza padrao, nao repete.
- **Qualidade nao-negociavel.** "conserto depois" sem registro = nao entrega.

## Antes de codar

Prompt quase nunca traz contexto suficiente. **Puxa contexto do repo, nao espera empurrar.**

1. **Le antes de escrever**, nesta ordem: este arquivo → `AGENTS.md` do diretorio tocado →
   arquivo inteiro que vai editar.
2. **Tarefa subespecificada?** NAO dispara cascata de pergunta. Escolhe caminho mais provavel,
   declara **max 2-3 premissas explicitas** ("assumindo X porque Y"), segue. Cada premissa vai
   pro handoff. So pergunta antes se premissa errada joga fora o trabalho todo (destrutivo,
   irreversivel, caro).

## Git policy

- **Agent nao comita, agent nao pusha.** Quem assina commit e o dev.
- **Por que:** revisao do diff antes do commit e parte do trabalho. Quem comita assume autoria e
  ownership. Agent prepara, faz stage, sugere mensagem. Dev valida e comita.
- **Agent FAZ:** `git status`, `git diff`, `git log`, `git show`, `git branch`, `git add`.
  Read-only ou stage. Editar arquivo rola normal — so commit que nao.
- **Co-authored-by:** nunca `Co-Authored-By: Claude` (ou qualquer LLM) em commit/PR.
  Ferramenta nao e co-autor. Autoria e do engenheiro.
- Conventional Commits: `<type>[scope]: <description>` — `feat`, `fix`, `docs`, `style`, `refactor`,
  `perf`, `test`, `chore`, `ci`. Breaking: `feat(agents)!: ...`.

## Secrets policy

- **Agent nao le env nem credencial:** `.env*`, `.envrc*`, `secrets.*`, `credentials.*`, `*.pem`,
  `*.key`, `id_rsa*`, `.ssh/`, `.aws/`, `.netrc`.
- **Por que:** valor sensivel em context window vira valor sensivel em log, trace, PR review.
  "So ler pra entender" ja e vetor de vazamento. Precisa de var pra justificar sugestao?
  Pergunta nome e uso, nunca valor.
- Comando que precisa de env: dev exporta no shell e roda manual.

## Workflow

1. **Plan first.** Multi-arquivo ou 3+ passos → planeja antes. Desviou? Para e re-planeja.
2. **Subagent pra pesquisa.** Investigacao >2 queries → subagent, nao loop principal.
3. **Self-verify antes de "done".** Roda o que da pra rodar. **I/O externo (Ollama, HTTP) →
   roda caminho real.** Script que compila prova sintaxe, nao integracao. Nao reporta done
   com vermelho.

## Done = handoff revisavel

Dev revisa **handoff**, nao diff inteiro. Antes de "pronto", entrega SEMPRE:

- **O que mudou:** 1 frase.
- **Premissas que assumi:** o que dev precisa confirmar ("nenhuma" se nao teve).
- **Verifiquei:** comando REAL + resultado (`python core/agents/simple_agent.py` → 2 passos).
  Nunca "deve funcionar".
- **NAO cobri / risco:** o que ficou de fora, o que pode quebrar.
- **Revise primeiro:** `arquivo:linha` do ponto mais arriscado do diff.

> Handoff generico e red flag: voce nao sabe o que fez. Bloco existe pra baratear revisao,
> nao pra decorar.

---

## O que e este projeto

Repo de estudos da disciplina **Topicos Especiais em Sistemas de Informacao 1** (faculdade).
Objetivo didatico: entender agente de LLM por dentro, escrevendo loop de function calling na mao,
sem framework pronto.

Consequencias praticas:

- Clareza > abstracao. Codigo curto e legivel > arquitetura generica.
- Cada script roda sozinho e mostra o que acontece (print de cada passo).
- Experimento comparativo faz parte do conteudo: flag altera uma variavel, saida mostra efeito
  no comportamento do modelo.

## Estrutura

```text
README.md
AGENTS.md
core/
  __init__.py        vazio
  config.py          vazio (reservado para configuracao compartilhada)
  agents/
    AGENTS.md        regras do diretorio de agentes (le antes de editar um agente)
    simple_agent.py  agente minimo com function calling
diario/              anotacoes da disciplina (vazio)
```

`core/agents/` nao tem `__init__.py`: scripts sao executados direto, nao importados.

## Stack

| Componente | Tech |
|---|---|
| Linguagem | Python 3.11 |
| Dependencias | nenhuma — so stdlib (`argparse`, `json`, `urllib.request`, `datetime`, `typing`) |
| LLM | Ollama local (`http://localhost:11434/api/chat`), modelo `qwen2.5:7b` |
| API de exemplo | ViaCEP (`https://viacep.com.br/ws/{cep}/json/`) |
| Test / Lint / Types | nao configurado |

Sem `requirements.txt`, `pyproject.toml`, gerenciador de ambiente.
**Nao adiciona dependencia externa sem usuario pedir** — ausencia e proposital.

## Comandos

```bash
ollama pull qwen2.5:7b                              # pre-requisito do LLM local
python core/agents/simple_agent.py --help           # opcoes do agente
python -m py_compile core/agents/<arquivo>.py       # check de sintaxe, sem Ollama
```

## Convencoes de codigo

- **Sem comentarios novos.** Comentario existente fica intacto. "Porque" vai na mensagem de
  commit, nao no arquivo.
- Tipagem completa: parametros, retornos, constantes de modulo, locais nao obvios. Estrutura
  vinda de JSON usa `TypedDict`; `json.load` retorna `Any` → usa `cast`.
- Sintaxe moderna: `list[str]`, `dict[str, Any]`, `str | int`, `collections.abc.Callable`.
- Identificador, docstring e saida em portugues **sem acento**.
- Constante de configuracao em MAIUSCULAS no topo do modulo.
- Todo script tem bloco `if __name__ == "__main__":` com `argparse`.

## Ao mexer aqui

- Le arquivo inteiro antes de editar. Prefere edicao pontual a reescrita.
- Trabalho em `core/agents/` segue tambem [`core/agents/AGENTS.md`](core/agents/AGENTS.md).
- `diario/` e pra anotacao da materia em markdown, nao codigo.
- Nao commita `__pycache__/`.

## Limite

Limite de **200 linhas**. Passou? Move detalhe pro `AGENTS.md` do diretorio correspondente,
mantem so indice aqui.
