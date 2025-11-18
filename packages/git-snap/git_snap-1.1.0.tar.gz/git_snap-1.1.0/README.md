# GitSnap

[![PyPI version](https://badge.fury.io/py/git-snap.svg)](https://badge.fury.io/py/git-snap)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**GitSnap** é uma aplicação gráfica (GUI) que transforma o `git` numa ferramenta de "snapshots" intuitiva e poderosa. Foi desenhada para simplificar o versionamento, focando-se na segurança e na facilidade de uso, tanto para projetos locais como para sincronização com o GitHub.

![GitSnap Interface](https://i.imgur.com/v8D4215.png)

---

## O Conceito: Snapshots

Em vez do ciclo `add -> commit -> tag -> push`, o GitSnap utiliza o conceito de **Snapshot**: uma "fotografia" completa do estado do seu projeto num determinado momento. Isto torna o processo de guardar e restaurar versões muito mais simples.

## Funcionalidades Principais

### Gestão de Snapshots Locais
-   **Criar Snapshot:** Salve o estado atual de todos os ficheiros do seu projeto com uma única ação.
-   **Listar e Visualizar:** Veja um histórico limpo de todos os snapshots, com mensagens, datas e autores.
-   **Restaurar Snapshot:** Volte a um estado anterior de forma segura. O GitSnap cria um backup automático das suas alterações atuais antes de restaurar, garantindo que nada é perdido.

### Sincronização com o GitHub
-   **Push de Snapshots:** Envie um ou mais snapshots para um repositório remoto no GitHub para os manter seguros e partilhá-los com a sua equipa.
-   **Pull de Snapshots:** Descarregue snapshots de um repositório do GitHub para o seu ambiente local, sincronizando o seu trabalho.

### Importar e Exportar
-   **Exportar para Ficheiro:** Exporte um ou vários snapshots para um único ficheiro `.bundle`. Ideal para backups offline ou para partilhar versões de um projeto sem usar o GitHub.
-   **Importar de Ficheiro:** Importe snapshots a partir de um ficheiro `.bundle`, restaurando o histórico noutra máquina.

## Integração com o GitHub: Como usar Tokens

Para sincronizar snapshots com o GitHub, o GitSnap utiliza um **Personal Access Token**. Isto é mais seguro do que usar a sua palavra-passe.

#### Como gerar um Token no GitHub:
1.  Vá à sua conta do GitHub e aceda a **Settings** > **Developer settings** > **Personal access tokens** > **Tokens (classic)**.
2.  Clique em **Generate new token** (e depois **Generate new token (classic)**).
3.  **Note:** Dê um nome ao token, como `gitsnap-token`.
4.  **Expiration:** Defina uma data de expiração (ex: 90 dias).
5.  **Select scopes:** Marque a caixa `repo`. Isto dá permissões para aceder e modificar repositórios.
    ![GitHub Token Scopes](https://i.imgur.com/A6W303r.png)
6.  Clique em **Generate token** e **copie o token gerado**. Guarde-o num local seguro.

O GitSnap irá pedir este token na primeira vez que tentar fazer uma operação com o GitHub.

## Instalação

A forma recomendada de instalar o `git-snap` é através do `pipx`:
```bash
pipx install git-snap
```
Para executar a aplicação, basta usar o comando:
```bash
git-snap
```
