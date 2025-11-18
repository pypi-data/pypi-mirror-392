import subprocess
import os
import re
from .errors import GitRepositoryError
from .config import load_config
from .git_repo import ensure_on_branch

def pull_from_remote(repo_url: str, token: str) -> tuple[str, str]:
    """
    Pulls changes from a remote repository using 'git pull --rebase'.
    Ensures it's running on the 'master' branch.
    """
    try:
        ensure_on_branch("master")
        
        url_parts = re.match(r"https://github.com/([^/]+)/([^/]+?)(?:\.git)?$", repo_url)
        if not url_parts:
            return "error", "URL do repositório inválida. Formato esperado: https://github.com/user/repo.git"
        
        owner, repo = url_parts.groups()
        remote_url = f"https://{token}@github.com/{owner}/{repo}.git"

        pull_command = ["git", "pull", "--rebase", remote_url, "master"]
        result = subprocess.run(pull_command, capture_output=True, text=True)

        stderr = result.stderr.lower()
        stdout = result.stdout.lower()

        if result.returncode != 0:
            if "conflict" in stdout or "conflict" in stderr:
                subprocess.run(["git", "rebase", "--abort"], capture_output=True)
                return "conflict", "Conflito de merge detectado. Resolva os conflitos manualmente e tente novamente."
            if "authentication failed" in stderr:
                return "error", "Falha na autenticação durante o pull. Verifique o seu token."
            if "couldn't find remote ref" in stderr:
                return "error", "A branch remota 'master' não foi encontrada. Faça um push primeiro para criá-la."
            return "error", f"Erro desconhecido durante o pull: {result.stderr}"

        return "success", "Pull do repositório remoto concluído com sucesso."

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        stderr = e.stderr.decode() if isinstance(e.stderr, bytes) else e.stderr
        return "error", f"Erro ao executar comando git durante o pull: {stderr}"
    except Exception as e:
        return "error", f"Ocorreu um erro inesperado durante o pull: {e}"

def push_snapshot(snapshot_tag: str, repo_url: str, token: str, push_message: str | None = None) -> tuple[str, str]:
    """
    Pushes a snapshot. Amends the commit message if provided.
    Handles detached HEAD and push failures.
    """
    try:
        ensure_on_branch("master")

        config = load_config()
        user_name = config.get("username")
        user_email = config.get("email")

        if not user_name or not user_email:
            return "error", "Username e Email não configurados. Por favor, configure-os na página de Settings."

        subprocess.run(["git", "config", "user.name", user_name], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", user_email], check=True, capture_output=True)

        tags_result = subprocess.run(["git", "tag"], capture_output=True, text=True, check=True)
        if snapshot_tag not in tags_result.stdout.splitlines():
            return "error", f"Snapshot '{snapshot_tag}' não encontrada localmente."

        if push_message:
            commit_sha_result = subprocess.run(["git", "rev-parse", f"{snapshot_tag}^{{commit}}"], capture_output=True, text=True, check=True)
            commit_sha = commit_sha_result.stdout.strip()
            subprocess.run(["git", "reset", "--soft", commit_sha], check=True, capture_output=True)
            subprocess.run(["git", "commit", "--amend", "-m", push_message], check=True, capture_output=True)
            subprocess.run(["git", "tag", "-d", snapshot_tag], check=True, capture_output=True)
            subprocess.run(["git", "tag", "-a", snapshot_tag, "-m", push_message], check=True, capture_output=True)

        url_parts = re.match(r"https://github.com/([^/]+)/([^/]+?)(?:\.git)?$", repo_url)
        if not url_parts:
            return "error", "URL do repositório inválida. Formato esperado: https://github.com/user/repo.git"
        
        owner, repo = url_parts.groups()
        remote_url = f"https://{token}@github.com/{owner}/{repo}.git"

        push_command = ["git", "push", remote_url, "master", f"refs/tags/{snapshot_tag}"]
        result = subprocess.run(push_command, capture_output=True, text=True)
        stderr = result.stderr.lower()

        if result.returncode != 0:
            if "non-fast-forward" in stderr or "rejected" in stderr:
                print("Push inicial falhou. A tentar com --force...")
                force_push_command = ["git", "push", "--force", remote_url, "master", f"refs/tags/{snapshot_tag}"]
                result = subprocess.run(force_push_command, capture_output=True, text=True)
                stderr = result.stderr.lower()

            if result.returncode != 0:
                if "authentication failed" in stderr:
                    return "error", "Falha na autenticação. Verifique o seu token."
                return "error", f"Erro desconhecido ao fazer push: {result.stderr}"

        if "everything up-to-date" in stderr:
            return "already_up_to_date", f"A snapshot '{snapshot_tag}' já está atualizada no repositório remoto."

        return "success", f"Snapshot '{snapshot_tag}' enviada com sucesso para {repo_url}"

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        stderr = e.stderr.decode() if isinstance(e.stderr, bytes) else e.stderr
        return "error", f"Erro ao executar comando git: {stderr}"
    except GitRepositoryError as e:
        return "error", str(e)
    except Exception as e:
        return "error", f"Ocorreu um erro inesperado: {e}"

def sync_with_remote(snapshot_tag: str, repo_url: str, token: str, push_message: str | None = None) -> tuple[str, str]:
    """
    Synchronizes with the remote repository by pulling first, then pushing.
    """
    try:
        ensure_on_branch("master")
        
        pull_status, pull_message = pull_from_remote(repo_url, token)
        if pull_status != "success":
            return pull_status, f"A sincronização falhou na fase de pull: {pull_message}"

        push_status, push_message_out = push_snapshot(snapshot_tag, repo_url, token, push_message)
        
        if push_status == "success" or push_status == "already_up_to_date":
            return "success", "Sincronização completa: Pull e Push bem-sucedidos."
        
        return push_status, f"Pull bem-sucedido, mas a sincronização falhou na fase de push: {push_message_out}"
    except Exception as e:
        return "error", f"Ocorreu um erro inesperado durante a sincronização: {e}"
