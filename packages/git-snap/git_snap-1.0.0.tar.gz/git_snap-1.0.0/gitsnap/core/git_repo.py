import os
import subprocess
from .errors import GitRepositoryError, RepositoryNotInitializedError

def is_git_repo(path: str = ".") -> bool:
    """Checks if the given path is a git repository."""
    git_dir = os.path.join(path, ".git")
    return os.path.isdir(git_dir)

def check_repo_ready(path: str = "."):
    """
    Checks if the repo is initialized and has at least one commit.
    Raises RepositoryNotInitializedError if not.
    """
    if not is_git_repo(path):
        raise RepositoryNotInitializedError("Nenhum repositório Git detectado.")
    
    # Check if there are any commits. An empty repo is not considered "ready".
    result = subprocess.run(["git", "rev-parse", "--verify", "HEAD"], cwd=path, capture_output=True)
    if result.returncode != 0:
        raise RepositoryNotInitializedError("Repositório Git inicializado mas vazio.")

def initialize_and_setup_repo(path: str = "."):
    """
    Initializes a git repository and creates an initial empty commit
    to establish the main branch.
    """
    try:
        subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
        # Create an initial empty commit to make the repo "ready"
        subprocess.run(
            ["git", "commit", "--allow-empty", "-m", "Initial commit by GitSnap"],
            cwd=path, check=True, capture_output=True
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        raise GitRepositoryError(f"Erro ao inicializar e configurar repositório: {e}") from e

def ensure_on_branch(branch_name: str, path: str = "."):
    """
    Ensures the repository is on the specified branch, creating it if it
    doesn't exist or checking it out if it does. Handles detached HEAD state.
    """
    try:
        # This command creates the branch pointing to HEAD if it doesn't exist,
        # or checks it out if it does. It's a safe way to ensure we're on a branch.
        subprocess.run(["git", "checkout", "-B", branch_name], cwd=path, check=True, capture_output=True)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        raise GitRepositoryError(f"Erro ao garantir que está na branch '{branch_name}': {e}") from e

def init_repo(path: str = "."):
    """Runs 'git init' in the specified path."""
    try:
        subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True, text=True)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        raise GitRepositoryError(f"Erro ao inicializar repositório: {e}") from e

def discard_changes(path: str = "."):
    """Discards all changes in the working directory."""
    if not is_git_repo(path):
        raise GitRepositoryError("Not a git repository.")
    try:
        subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=path, check=True, capture_output=True)
        subprocess.run(["git", "clean", "-fd"], cwd=path, check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise GitRepositoryError(f"Erro ao descartar alterações: {e}") from e

def get_git_user_name(path: str = ".") -> str:
    """Gets the git user name."""
    if not is_git_repo(path):
        raise GitRepositoryError("Not a git repository.")
    try:
        result = subprocess.run(["git", "config", "user.name"], cwd=path, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise GitRepositoryError(f"Erro ao obter nome de utilizador do Git: {e}") from e

def get_git_user_email(path: str = ".") -> str:
    """Gets the git user email."""
    if not is_git_repo(path):
        raise GitRepositoryError("Not a git repository.")
    try:
        result = subprocess.run(["git", "config", "user.email"], cwd=path, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise GitRepositoryError(f"Erro ao obter email de utilizador do Git: {e}") from e
