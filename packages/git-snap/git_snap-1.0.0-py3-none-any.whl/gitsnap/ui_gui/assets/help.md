# Ajuda do GitSnap

O GitSnap é uma ferramenta para guardar "fotografias" (snapshots) do seu projeto de forma simples.

## Funcionalidades Principais

### Criar Snapshot
Guarda o estado atual de todos os ficheiros do seu projeto. Pode criar um snapshot mesmo que não tenha feito alterações. Ser-lhe-á pedida uma mensagem para o descrever.

### Restaurar Snapshot
Reverte todos os ficheiros do projeto para o estado de um snapshot selecionado. **Atenção:** as suas alterações atuais serão guardadas numa branch de backup, mas o seu diretório de trabalho será modificado.

### Eliminar Snapshot
Apaga o registo do snapshot. Esta ação não pode ser desfeita.

### Comparar com Local
Abre uma janela que mostra as diferenças entre um snapshot e os ficheiros atuais no seu disco.

### Comparar 2 Snapshots
Abre uma janela que mostra as diferenças entre dois snapshots selecionados.

## Sincronização com GitHub

### Pull do GitHub
Puxa as alterações mais recentes do repositório remoto para o seu ambiente local. É uma boa prática fazer 'Pull' antes de começar a trabalhar.

### Push para o GitHub
Envia um snapshot local para o repositório remoto no GitHub.

### Sincronizar
Executa um 'Pull' e depois um 'Push' numa única ação, garantindo que o seu ambiente local e o remoto ficam alinhados.

### URL do Repositório
O endereço do seu projeto no GitHub. Deve usar o formato HTTPS, por exemplo: `https://github.com/seu-usuario/seu-projeto.git`.

### Mensagem de Push
Esta é a mensagem que aparecerá no histórico de commits do GitHub. Por defeito, é a mesma do snapshot, mas pode alterá-la antes de enviar.

### Token de Acesso Pessoal
O GitHub requer um token para autenticação. Crie um em `GitHub > Settings > Developer settings > Personal access tokens` com o escopo **repo**.

## Erros Comuns

#### Falha na autenticação
O seu token está incorreto, expirou ou não tem as permissões necessárias (escopo 'repo'). Verifique o token no GitHub.

#### Conflito de Merge
Ocorreu um conflito durante um 'Pull' ou 'Sync' porque as alterações remotas e as suas alterações locais não puderam ser combinadas automaticamente. O GitSnap cancelou a operação. Para resolver, deve usar uma ferramenta de Git externa (como a linha de comando ou o VS Code) para resolver os conflitos e depois tentar novamente.
