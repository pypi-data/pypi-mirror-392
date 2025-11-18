import pytest
import subprocess
from datetime import datetime
from gitsnap.core import snapshots
from gitsnap.core.errors import GitRepositoryError, NoChangesError
from gitsnap.core.types import Snapshot

# Mocked subprocess.CompletedProcess
class MockCompletedProcess:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
    def check_returncode(self):
        if self.returncode != 0:
            raise subprocess.CalledProcessError(self.returncode, "cmd", self.stdout, self.stderr)

def test_list_snapshots_success(mocker):
    """Test listing snapshots successfully."""
    mocker.patch('gitsnap.core.snapshots.is_git_repo', return_value=True)
    
    # tag, date, message separated by null characters
    mock_output = (
        "snapshot-1\x002023-01-01T12:00:00+00:00\x00Message 1\n"
        "snapshot-2\x002023-01-02T12:00:00+00:00\x00Message 2"
    )
    
    def subprocess_side_effect(*args, **kwargs):
        cmd = args[0]
        if cmd[1] == 'tag':
            return MockCompletedProcess(stdout=mock_output)
        if cmd[1] == 'rev-list':
            return MockCompletedProcess(stdout="commit_hash")
        if cmd[1] == 'notes':
            return MockCompletedProcess(stdout="internal_name")
        return MockCompletedProcess()

    mock_run = mocker.patch('subprocess.run', side_effect=subprocess_side_effect)
    
    result = snapshots.list_snapshots()
    
    assert len(result) == 2
    assert result[0].internal_name == "internal_name"
    assert result[0].tag == "snapshot-1"
    assert result[1].message == "Message 2"

def test_list_snapshots_empty(mocker):
    """Test listing snapshots with no tags."""
    mocker.patch('gitsnap.core.snapshots.is_git_repo', return_value=True)
    mocker.patch('subprocess.run', return_value=MockCompletedProcess(stdout=""))
    
    result = snapshots.list_snapshots()
    assert result == []

def test_save_snapshot_success(mocker):
    """Test saving a snapshot successfully when there are changes."""
    mocker.patch('gitsnap.core.snapshots.is_git_repo', return_value=True)
    
    def subprocess_side_effect(*args, **kwargs):
        cmd = args[0]
        if cmd[1] == 'rev-parse':
            return MockCompletedProcess(stdout="commit_hash")
        return MockCompletedProcess()

    mock_run = mocker.patch('subprocess.run', side_effect=subprocess_side_effect)
    
    snapshots.save_snapshot("internal_name", "tag", "message")
    
    assert mock_run.call_count == 5  # add, commit, rev-parse, tag, notes
    mock_run.assert_any_call(['git', 'add', '.'], cwd='.', check=True, capture_output=True)
    mock_run.assert_any_call(
        ['git', 'commit', '--allow-empty', '-m', 'message'],
        cwd='.', check=True, capture_output=True, text=True
    )
    mock_run.assert_any_call(['git', 'rev-parse', 'HEAD'], cwd='.', check=True, capture_output=True, text=True)
    mock_run.assert_any_call(['git', 'tag', '-a', 'tag', '-m', 'message'], cwd='.', check=True)
    mock_run.assert_any_call(['git', 'notes', 'add', '-f', '-m', 'internal_name', 'commit_hash'], cwd='.', check=True)

def test_save_snapshot_succeeds_with_no_changes(mocker):
    """Test that saving a snapshot succeeds even with no file changes."""
    mocker.patch('gitsnap.core.snapshots.is_git_repo', return_value=True)
    
    def subprocess_side_effect(*args, **kwargs):
        cmd = args[0]
        if cmd[1] == 'rev-parse':
            return MockCompletedProcess(stdout="commit_hash")
        return MockCompletedProcess()
        
    mock_run = mocker.patch('subprocess.run', side_effect=subprocess_side_effect)

    # Execute without expecting an error
    snapshots.save_snapshot("internal_name", "tag", "message")

    # Verify that commit is still called with --allow-empty
    mock_run.assert_any_call(
        ['git', 'commit', '--allow-empty', '-m', 'message'],
        cwd='.', check=True, capture_output=True, text=True
    )
    assert mock_run.call_count == 5  # add, commit, rev-parse, tag, notes

def test_save_snapshot_commit_fails(mocker):
    """Test saving a snapshot when the commit command fails for a generic reason."""
    mocker.patch('gitsnap.core.snapshots.is_git_repo', return_value=True)
    
    def mock_run_side_effect(*args, **kwargs):
        cmd = args[0]
        if cmd[1] == 'commit':
            raise subprocess.CalledProcessError(1, cmd, stderr="commit hook failed")
        return MockCompletedProcess()

    mocker.patch('subprocess.run', side_effect=mock_run_side_effect)
    
    with pytest.raises(GitRepositoryError, match="commit hook failed"):
        snapshots.save_snapshot("internal_name", "tag", "message")

def test_restore_snapshot_success(mocker):
    """Test restoring a snapshot successfully."""
    mocker.patch('gitsnap.core.snapshots.is_git_repo', return_value=True)
    mock_run = mocker.patch('subprocess.run')

    snapshots.restore_snapshot("snapshot-123")

    assert mock_run.call_count == 2
    # The backup branch name is dynamic, so we check the start of the command
    backup_call = mock_run.call_args_list[0]
    assert backup_call.args[0][0] == 'git' and backup_call.args[0][1] == 'branch'
    
    mock_run.assert_any_call(['git', 'reset', '--hard', 'snapshot-123'], cwd='.', check=True, capture_output=True)

def test_compare_snapshot_with_local_success(mocker):
    """Test comparing a snapshot with the local directory."""
    mocker.patch('gitsnap.core.snapshots.is_git_repo', return_value=True)
    mock_run = mocker.patch('subprocess.run', return_value=MockCompletedProcess(stdout="diff text"))
    
    diff = snapshots.compare_snapshot_with_local("tag-1")
    
    assert diff == "diff text"
    mock_run.assert_called_once_with(['git', 'diff', 'tag-1'], cwd='.', check=True, capture_output=True, text=True)

def test_compare_snapshots_success(mocker):
    """Test comparing two snapshots."""
    mocker.patch('gitsnap.core.snapshots.is_git_repo', return_value=True)
    mock_run = mocker.patch('subprocess.run', return_value=MockCompletedProcess(stdout="diff text"))
    
    diff = snapshots.compare_snapshots("tag-1", "tag-2")
    
    assert diff == "diff text"
    mock_run.assert_called_once_with(['git', 'diff', 'tag-1', 'tag-2'], cwd='.', check=True, capture_output=True, text=True)

def test_rename_snapshot_success(mocker):
    """Test renaming a snapshot successfully."""
    mocker.patch('gitsnap.core.snapshots.is_git_repo', return_value=True)
    mock_run = mocker.patch('subprocess.run')
    
    snapshots.rename_snapshot("tag-1", "new message")
    
    mock_run.assert_called_once_with(
        ['git', 'tag', '-a', 'tag-1', '-f', '-m', 'new message'],
        cwd='.', check=True, capture_output=True
    )

def test_rename_snapshot_internal_name_success(mocker):
    """Test renaming a snapshot's internal name successfully."""
    mocker.patch('gitsnap.core.snapshots.is_git_repo', return_value=True)
    
    def subprocess_side_effect(*args, **kwargs):
        cmd = args[0]
        if cmd[1] == 'rev-list':
            return MockCompletedProcess(stdout="commit_hash")
        return MockCompletedProcess()

    mock_run = mocker.patch('subprocess.run', side_effect=subprocess_side_effect)
    
    snapshots.rename_snapshot_internal_name("tag-1", "new internal name")
    
    mock_run.assert_any_call(['git', 'rev-list', '-n', '1', 'tag-1'], cwd='.', check=True, capture_output=True, text=True)
    mock_run.assert_any_call(['git', 'notes', 'add', '-f', '-m', 'new internal name', 'commit_hash'], cwd='.', check=True)

def test_rename_snapshot_empty_message(mocker):
    """Test that renaming with an empty message raises ValueError."""
    mocker.patch('gitsnap.core.snapshots.is_git_repo', return_value=True)
    with pytest.raises(ValueError):
        snapshots.rename_snapshot("tag-1", "")

def test_delete_snapshot_success(mocker):
    """Test deleting a snapshot successfully."""
    mocker.patch('gitsnap.core.snapshots.is_git_repo', return_value=True)
    mock_run = mocker.patch('subprocess.run')
    
    snapshots.delete_snapshot("tag-1")
    
    mock_run.assert_called_once_with(['git', 'tag', '-d', 'tag-1'], cwd='.', check=True, capture_output=True)

def test_delete_snapshot_fails(mocker):
    """Test that deleting a snapshot raises GitRepositoryError on failure."""
    mocker.patch('gitsnap.core.snapshots.is_git_repo', return_value=True)
    mocker.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, "cmd"))
    
    with pytest.raises(GitRepositoryError):
        snapshots.delete_snapshot("tag-1")

def test_compare_snapshot_with_local_side_by_side(mocker):
    """Test the side-by-side comparison function."""
    mocker.patch('gitsnap.core.snapshots.is_git_repo', return_value=True)

    # Mock the snapshot's file tree
    ls_tree_output = (
        "100644 blob abc\tfile1.txt\n"
        "100644 blob def\tfile2.txt\n"
        "100644 blob ghi\tfile3.txt"
    )
    
    # Mock the local file system walk
    walk_output = [
        ('.', [], ['file1.txt', 'file2.txt', 'file4.txt'])
    ]
    mocker.patch('os.walk', return_value=walk_output)
    # Let the test use the real os.path.relpath to ensure normalization

    # Mock the subprocess calls for ls-tree and hash-object
    def subprocess_side_effect(*args, **kwargs):
        cmd = args[0]
        if cmd[1] == 'ls-tree':
            return MockCompletedProcess(stdout=ls_tree_output)
        if cmd[1] == 'hash-object':
            file_path = cmd[2]
            if file_path.endswith('file1.txt'):
                return MockCompletedProcess(stdout='abc') # Same hash
            if file_path.endswith('file2.txt'):
                return MockCompletedProcess(stdout='xyz') # Different hash
            if file_path.endswith('file4.txt'):
                return MockCompletedProcess(stdout='jkl') # New file
        return MockCompletedProcess()

    mocker.patch('subprocess.run', side_effect=subprocess_side_effect)

    # --- Execute ---
    snap_results, local_results = snapshots.compare_snapshot_with_local_side_by_side('test-tag')

    # --- Assert ---
    # Convert to dicts for easier lookup
    snap_dict = {item['name']: item for item in snap_results}
    local_dict = {item['name']: item for item in local_results}

    # file1.txt is identical
    assert snap_dict['file1.txt']['status'] == 'igual'
    assert local_dict['file1.txt']['status'] == 'igual'

    # file2.txt is modified
    assert snap_dict['file2.txt']['status'] == 'modificado'
    assert local_dict['file2.txt']['status'] == 'modificado'

    # file3.txt is missing from local
    assert snap_dict['file3.txt']['status'] == 'igual'
    assert local_dict['file3.txt']['status'] == 'missing'

    # file4.txt is new in local
    assert snap_dict['file4.txt']['status'] == 'missing'
    assert local_dict['file4.txt']['status'] == 'igual'
    
def test_compare_snapshots_side_by_side(mocker):
    """Test the side-by-side comparison between two snapshots."""
    mocker.patch('gitsnap.core.snapshots.is_git_repo', return_value=True)

    # Mock the first snapshot's file tree
    ls_tree_output1 = (
        "100644 blob abc\tfile1.txt\n"  # Same
        "100644 blob def\tfile2.txt\n"  # Modified
        "100644 blob ghi\tfile3.txt"   # Deleted in tag2
    )
    
    # Mock the second snapshot's file tree
    ls_tree_output2 = (
        "100644 blob abc\tfile1.txt\n"  # Same
        "100644 blob xyz\tfile2.txt\n"  # Modified
        "100644 blob jkl\tfile4.txt"   # Added in tag2
    )

    def subprocess_side_effect(*args, **kwargs):
        cmd = args[0]
        if cmd[1] == 'ls-tree':
            tag = cmd[-1]
            if tag == 'tag1':
                return MockCompletedProcess(stdout=ls_tree_output1)
            if tag == 'tag2':
                return MockCompletedProcess(stdout=ls_tree_output2)
        return MockCompletedProcess()

    mocker.patch('subprocess.run', side_effect=subprocess_side_effect)

    # --- Execute ---
    results1, results2 = snapshots.compare_snapshots_side_by_side('tag1', 'tag2')

    # --- Assert ---
    dict1 = {item['name']: item for item in results1}
    dict2 = {item['name']: item for item in results2}

    # file1.txt is identical
    assert dict1['file1.txt']['status'] == 'igual'
    assert dict2['file1.txt']['status'] == 'igual'

    # file2.txt is modified
    assert dict1['file2.txt']['status'] == 'modificado'
    assert dict2['file2.txt']['status'] == 'modificado'

    # file3.txt is missing from tag2
    assert dict1['file3.txt']['status'] == 'igual'
    assert dict2['file3.txt']['status'] == 'missing'

    # file4.txt is missing from tag1
    assert dict1['file4.txt']['status'] == 'missing'
    assert dict2['file4.txt']['status'] == 'igual'

def test_get_file_content_from_snapshot(mocker):
    """Test retrieving file content from a snapshot."""
    mocker.patch('gitsnap.core.snapshots.is_git_repo', return_value=True)
    mock_run = mocker.patch('subprocess.run', return_value=MockCompletedProcess(stdout="file content"))
    
    content = snapshots.get_file_content_from_snapshot("tag1", "file.txt")
    
    assert content == "file content"
    mock_run.assert_called_once_with(
        ['git', 'show', 'tag1:file.txt'],
        cwd='.', check=True, capture_output=True, text=True, encoding='utf-8'
    )

def test_get_snapshot_tree(mocker):
    """Test retrieving the file tree of a single snapshot."""
    mocker.patch('gitsnap.core.snapshots.is_git_repo', return_value=True)
    ls_tree_output = (
        "100644 blob abc\tfile1.txt\n"
        "040000 tree def\tdir1"
    )
    mock_run = mocker.patch('subprocess.run', return_value=MockCompletedProcess(stdout=ls_tree_output))
    
    tree = snapshots.get_snapshot_tree("tag-1")
    
    assert len(tree) == 2
    assert tree[0] == {'name': 'file1.txt', 'type': 'file'}
    assert tree[1] == {'name': 'dir1', 'type': 'dir'}
    mock_run.assert_called_once_with(
        ['git', 'ls-tree', '-r', '-t', 'tag-1'],
        cwd='.', check=True, capture_output=True, text=True, encoding='utf-8'
    )

def test_get_file_content_not_found(mocker):
    """Test that getting content for a non-existent file returns an empty string."""
    mocker.patch('gitsnap.core.snapshots.is_git_repo', return_value=True)
    mocker.patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, "cmd"))
    
    content = snapshots.get_file_content_from_snapshot("tag1", "nonexistent.txt")
    
    assert content == ""
