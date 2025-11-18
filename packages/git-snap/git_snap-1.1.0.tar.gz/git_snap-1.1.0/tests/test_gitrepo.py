import pytest
import subprocess
from gitsnap.core import git_repo
from gitsnap.core.errors import GitRepositoryError

def test_is_git_repo_true(monkeypatch):
    """Test that is_git_repo returns True when .git directory exists."""
    monkeypatch.setattr('os.path.isdir', lambda path: True)
    assert git_repo.is_git_repo() is True

def test_is_git_repo_false(monkeypatch):
    """Test that is_git_repo returns False when .git directory does not exist."""
    monkeypatch.setattr('os.path.isdir', lambda path: False)
    assert git_repo.is_git_repo() is False

def test_init_repo_success(mocker):
    """Test that init_repo succeeds."""
    mock_run = mocker.patch('subprocess.run')
    git_repo.init_repo()
    mock_run.assert_called_once_with(
        ["git", "init"], cwd=".", check=True, capture_output=True, text=True
    )

def test_init_repo_failure(mocker):
    """Test that init_repo raises GitRepositoryError on failure."""
    mocker.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, "cmd"))
    with pytest.raises(GitRepositoryError):
        git_repo.init_repo()

def test_discard_changes_success(mocker):
    """Test that discard_changes succeeds."""
    mocker.patch('gitsnap.core.git_repo.is_git_repo', return_value=True)
    mock_run = mocker.patch('subprocess.run')
    
    git_repo.discard_changes()
    
    assert mock_run.call_count == 2
    mock_run.assert_any_call(["git", "reset", "--hard", "HEAD"], cwd=".", check=True, capture_output=True)
    mock_run.assert_any_call(["git", "clean", "-fd"], cwd=".", check=True, capture_output=True)

def test_discard_changes_failure(mocker):
    """Test that discard_changes raises GitRepositoryError on failure."""
    mocker.patch('gitsnap.core.git_repo.is_git_repo', return_value=True)
    mocker.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, "cmd"))
    
    with pytest.raises(GitRepositoryError):
        git_repo.discard_changes()

def test_discard_changes_not_a_repo(mocker):
    """Test that discard_changes raises GitRepositoryError if not a git repo."""
    mocker.patch('gitsnap.core.git_repo.is_git_repo', return_value=False)
    with pytest.raises(GitRepositoryError, match="Not a git repository"):
        git_repo.discard_changes()
