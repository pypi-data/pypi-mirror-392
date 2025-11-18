import subprocess
from unittest.mock import patch, MagicMock, call
import pytest

from gitsnap.core import git_push
from gitsnap.core.errors import GitRepositoryError

@pytest.fixture
def mock_git_push():
    """Fixture to mock dependencies for git_push functions."""
    with patch('gitsnap.core.git_push.ensure_on_branch') as mock_ensure, \
         patch('gitsnap.core.git_push.load_config', return_value={'username': 'Test User', 'email': 'test@example.com'}) as mock_load, \
         patch('subprocess.run') as mock_run:
        
        # Default success for all subprocess calls
        mock_run.return_value = MagicMock(returncode=0, stdout="snapshot-123", stderr="")
        yield mock_ensure, mock_load, mock_run

# --- Tests for pull_from_remote ---

def test_pull_from_remote_success(mock_git_push):
    mock_ensure, _, mock_run = mock_git_push
    
    status, _ = git_push.pull_from_remote("https://github.com/u/r.git", "token")

    assert status == "success"
    mock_ensure.assert_called_once_with("master")
    pull_command = ['git', 'pull', '--rebase', 'https://token@github.com/u/r.git', 'master']
    mock_run.assert_called_with(pull_command, capture_output=True, text=True)

def test_pull_from_remote_conflict(mock_git_push):
    mock_ensure, _, mock_run = mock_git_push
    mock_run.return_value = MagicMock(returncode=1, stderr="CONFLICT (content):")

    status, message = git_push.pull_from_remote("https://github.com/u/r.git", "token")

    assert status == "conflict"
    assert "Conflito de merge detectado" in message
    # Check that rebase was aborted
    mock_run.assert_called_with(['git', 'rebase', '--abort'], capture_output=True)

# --- Tests for push_snapshot ---

def test_push_snapshot_success(mock_git_push):
    mock_ensure, _, mock_run = mock_git_push
    
    status, _ = git_push.push_snapshot("snapshot-123", "https://github.com/u/r.git", "token")

    assert status == "success"
    mock_ensure.assert_called_once_with("master")
    push_command = ['git', 'push', 'https://token@github.com/u/r.git', 'master', 'refs/tags/snapshot-123']
    # The last call should be the push
    assert mock_run.call_args.args[0] == push_command

def test_push_snapshot_non_fast_forward_force_pushes(mock_git_push):
    mock_ensure, _, mock_run = mock_git_push
    
    # First push fails, second (force) push succeeds
    mock_run.side_effect = [
        MagicMock(returncode=0), # git config user.name
        MagicMock(returncode=0), # git config user.email
        MagicMock(returncode=0, stdout="snapshot-123"), # git tag
        MagicMock(returncode=1, stderr="non-fast-forward"), # First push
        MagicMock(returncode=0, stderr="")  # Force push
    ]

    status, _ = git_push.push_snapshot("snapshot-123", "https://github.com/u/r.git", "token")

    assert status == "success"
    assert mock_run.call_count == 5
    force_push_command = ['git', 'push', '--force', 'https://token@github.com/u/r.git', 'master', 'refs/tags/snapshot-123']
    mock_run.assert_called_with(force_push_command, capture_output=True, text=True)

def test_push_snapshot_with_message_change(mock_git_push):
    mock_ensure, _, mock_run = mock_git_push
    
    # First push fails (rejected), second push (force) succeeds
    mock_run.side_effect = [
        MagicMock(returncode=0), # git config
        MagicMock(returncode=0), # git config
        MagicMock(returncode=0, stdout="snapshot-123"), # git tag
        MagicMock(returncode=0, stdout="abc1234"), # rev-parse commit
        MagicMock(returncode=0), # reset
        MagicMock(returncode=0), # commit --amend
        MagicMock(returncode=0), # tag -d
        MagicMock(returncode=0), # tag -a
        MagicMock(returncode=1, stderr="! [rejected]"), # First push fails
        MagicMock(returncode=0, stderr="")  # Force push succeeds
    ]
    
    status, _ = git_push.push_snapshot("snapshot-123", "https://github.com/u/r.git", "token", push_message="new msg")

    assert status == "success"
    mock_ensure.assert_called_once_with("master")
    # Check that the force push command was the last one called
    force_push_command = ['git', 'push', '--force', 'https://token@github.com/u/r.git', 'master', 'refs/tags/snapshot-123']
    mock_run.assert_called_with(force_push_command, capture_output=True, text=True)

# --- Tests for sync_with_remote ---

@patch('gitsnap.core.git_push.pull_from_remote')
@patch('gitsnap.core.git_push.push_snapshot')
@patch('gitsnap.core.git_push.ensure_on_branch')
def test_sync_with_remote_success(mock_ensure, mock_push, mock_pull):
    mock_pull.return_value = ("success", "Pulled.")
    mock_push.return_value = ("success", "Pushed.")

    status, message = git_push.sync_with_remote("tag", "url", "token", "msg")

    assert status == "success"
    assert "Sincronização completa" in message
    mock_ensure.assert_called_once_with("master")
    mock_pull.assert_called_once_with("url", "token")
    mock_push.assert_called_once_with("tag", "url", "token", "msg")

@patch('gitsnap.core.git_push.pull_from_remote')
@patch('gitsnap.core.git_push.push_snapshot')
@patch('gitsnap.core.git_push.ensure_on_branch')
def test_sync_with_remote_fails_on_pull(mock_ensure, mock_push, mock_pull):
    mock_pull.return_value = ("conflict", "Conflict.")

    status, message = git_push.sync_with_remote("tag", "url", "token", "msg")

    assert status == "conflict"
    assert "falhou na fase de pull" in message
    mock_ensure.assert_called_once_with("master")
    mock_pull.assert_called_once_with("url", "token")
    mock_push.assert_not_called()
