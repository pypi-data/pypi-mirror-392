# GitSnap

[![PyPI version](https://badge.fury.io/py/git-snap.svg)](https://badge.fury.io/py/git-snap)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**GitSnap** é uma ferramenta com interface gráfica (TUI) que simplifica o uso do Git, transformando-o numa máquina de "snapshots" segura e fácil de usar. Foi desenhada para quem quer versionar projetos sem a complexidade dos comandos tradicionais do Git.

![placeholder-screenshot](https://user-images.githubusercontent.com/12345/234567890-placeholder.png)
*(Nota: Imagem de placeholder. Uma captura de ecrã real da aplicação será adicionada aqui.)*

---

## Funcionalidades Principais

-   **Interface Gráfica Intuitiva:** Gestão de snapshots através de uma TUI simples e direta.
-   **Snapshots com Um Clique:** Salve o estado atual do seu projeto com uma única ação.
-   **Restauração Segura:** Volte a um estado anterior sem medo de perder trabalho. Um backup é criado automaticamente.
-   **Inicialização Automática:** Se o seu projeto ainda não é um repositório Git, o GitSnap trata disso por si.
-   **Modo CLI:** Para quem prefere, também existe uma interface de linha de comando.

## Instalação

A forma recomendada de instalar o `git-snap` é através do `pipx`, que instala a ferramenta num ambiente isolado.

```bash
pipx install git-snap
```

Após a instalação, pode executar a aplicação com o comando `git-snap`.

## Como Usar

### Interface Gráfica (Recomendado)

Para iniciar a interface principal, basta executar:

```bash
git-snap
```

### Interface de Linha de Comando (CLI)

Para tarefas automatizadas ou para quem prefere o terminal, os seguintes comandos estão disponíveis:

-   **Salvar um snapshot:**
    ```bash
    git-snap-cli save "A minha mensagem de snapshot"
    ```

-   **Listar todos os snapshots:**
    ```bash
    git-snap-cli list
    ```

-   **Restaurar um snapshot (usando o hash curto):**
    ```bash
    git-snap-cli restore <hash_do_snapshot>
    ```

## Licença

Este projeto está licenciado sob a Licença MIT. Consulte o ficheiro `LICENSE` para mais detalhes.
