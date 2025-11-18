import os
import subprocess
from datetime import datetime
from typing import List, Optional, Dict, Tuple, Any
import zipfile
import shutil
import tempfile

from .errors import GitRepositoryError, NoChangesError
from .types import Snapshot
from .git_repo import is_git_repo

import json

def save_snapshot(internal_name: str, tag: str, message: str, type: str = "none", description: str = "", path: str = "."):
    """
    Creates a new local snapshot. If there are no changes, an empty snapshot
    will be created to conform to user expectations.
    """
    if not is_git_repo(path):
        raise GitRepositoryError("Not a git repository.")
    if not all([internal_name, tag, message]):
        raise ValueError("Internal name, tag, and message are required.")
    if " " in tag:
        raise ValueError("A tag não pode conter espaços.")

    # Ensure the tag has the 'snapshot-' prefix for easier identification.
    final_tag = tag if tag.startswith("snapshot-") else f"snapshot-{tag}"

    try:
        # Add all files, including untracked ones.
        subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)

        # Commit with --allow-empty to ensure a snapshot is always created.
        commit_process = subprocess.run(
            ["git", "commit", "--allow-empty", "-m", message],
            cwd=path, check=True, capture_output=True, text=True
        )
        commit_hash = subprocess.run(["git", "rev-parse", "HEAD"], cwd=path, check=True, capture_output=True, text=True).stdout.strip()

        subprocess.run(["git", "tag", "-a", final_tag, "-m", message], cwd=path, check=True)
        
        # Add metadata as a git note in JSON format
        metadata = {"internal_name": internal_name, "type": type, "description": description}
        metadata_json = json.dumps(metadata)
        subprocess.run(["git", "notes", "add", "-f", "-m", metadata_json, commit_hash], cwd=path, check=True)

    except subprocess.CalledProcessError as e:
        output = ""
        if e.stdout:
            output += e.stdout if isinstance(e.stdout, str) else e.stdout.decode()
        if e.stderr:
            output += e.stderr if isinstance(e.stderr, str) else e.stderr.decode()
        raise GitRepositoryError(f"Erro ao criar snapshot: {output}") from e

def list_snapshots(path: str = ".") -> List[Snapshot]:
    """Lists all snapshots, identified by annotated tags with a corresponding git note."""
    if not is_git_repo(path):
        return []
    try:
        # List all tags, not just those with a specific prefix
        cmd = [
            "git", "tag",
            "--sort=-creatordate",
            "--format=%(refname:short)%00%(creatordate:iso)%00%(contents)"
        ]
        result = subprocess.run(cmd, cwd=path, check=True, capture_output=True, text=True, encoding='utf-8')
        output = result.stdout.strip()
        if not output:
            return []

        snapshots_list = []
        for entry in output.split('\n'):
            if not entry.strip():
                continue
            
            parts = entry.split('\x00')
            if len(parts) != 3 or not parts[0]:
                continue
            
            tag, date_str, message = parts
            
            if not message:
                continue
            
            message = message.split('\n\n', 1)[0]
            
            try:
                commit_hash = subprocess.run(["git", "rev-list", "-n", "1", tag], cwd=path, check=True, capture_output=True, text=True).stdout.strip()
            except subprocess.CalledProcessError:
                continue

            internal_name_process = subprocess.run(["git", "notes", "show", commit_hash], cwd=path, capture_output=True, text=True)
            if internal_name_process.returncode != 0:
                continue
            
            note_content = internal_name_process.stdout.strip()
            try:
                metadata = json.loads(note_content)
                internal_name = metadata.get("internal_name", tag)
                snapshot_type = metadata.get("type", "none")
                description = metadata.get("description", "")
            except json.JSONDecodeError:
                internal_name = note_content
                snapshot_type = "none"
                description = ""

            snapshots_list.append(Snapshot(
                internal_name=internal_name,
                tag=tag,
                date=datetime.fromisoformat(date_str),
                message=message,
                type=snapshot_type,
                description=description
            ))
        return snapshots_list
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

def restore_snapshot(tag: str, path: str = "."):
    """Restores the repository to a given snapshot tag."""
    if not is_git_repo(path):
        raise GitRepositoryError("Not a git repository.")
    try:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_branch_name = f"backup-before-restore-{timestamp}"
        subprocess.run(["git", "branch", backup_branch_name], cwd=path, check=True)
        subprocess.run(["git", "reset", "--hard", tag], cwd=path, check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise GitRepositoryError(f"Erro ao restaurar snapshot: {e}") from e

def get_current_snapshot_tag(path: str = ".") -> Optional[str]:
    """Gets the tag of the current HEAD, if it's a snapshot."""
    if not is_git_repo(path):
        return None
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--exact-match", "HEAD"],
            cwd=path, check=True, capture_output=True, text=True, stderr=subprocess.DEVNULL
        )
        tag = result.stdout.strip()
        if tag.startswith("snapshot-"):
            return tag
        return None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def compare_snapshot_with_local(tag: str, path: str = ".") -> str:
    """Compares a snapshot with the local working directory."""
    if not is_git_repo(path):
        raise GitRepositoryError("Not a git repository.")
    try:
        result = subprocess.run(["git", "diff", tag], cwd=path, check=True, capture_output=True, text=True)
        return result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise GitRepositoryError(f"Erro ao comparar snapshot: {e}") from e

def compare_snapshots(tag1: str, tag2: str, path: str = ".") -> str:
    """Compares two different snapshots."""
    if not is_git_repo(path):
        raise GitRepositoryError("Not a git repository.")
    try:
        result = subprocess.run(["git", "diff", tag1, tag2], cwd=path, check=True, capture_output=True, text=True)
        return result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise GitRepositoryError(f"Erro ao comparar snapshots: {e}") from e

def rename_snapshot(tag: str, new_message: str, path: str = "."):
    """Renames a snapshot's message by force-updating the tag."""
    if not is_git_repo(path):
        raise GitRepositoryError("Not a git repository.")
    if not new_message:
        raise ValueError("A nova mensagem não pode estar vazia.")
    try:
        subprocess.run(["git", "tag", "-a", tag, "-f", "-m", new_message], cwd=path, check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise GitRepositoryError(f"Erro ao renomear o snapshot '{tag}': {e}") from e

def delete_snapshot(tag: str, path: str = "."):
    """Deletes a snapshot tag."""
    if not is_git_repo(path):
        raise GitRepositoryError("Not a git repository.")
    try:
        subprocess.run(["git", "tag", "-d", tag], cwd=path, check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise GitRepositoryError(f"Erro ao eliminar o snapshot '{tag}': {e}") from e

def compare_snapshot_with_local_side_by_side(tag: str, path: str = ".") -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Compares a snapshot with the local working directory, returning structured data.
    """
    if not is_git_repo(path):
        raise GitRepositoryError("O diretório não é um repositório Git.")

    snapshot_items: Dict[str, Dict[str, str]] = {}
    local_items: Dict[str, Dict[str, str]] = {}

    try:
        cmd = ["git", "ls-tree", "-r", "-t", tag]
        result = subprocess.run(cmd, cwd=path, check=True, capture_output=True, text=True, encoding='utf-8')
        for line in result.stdout.strip().split('\n'):
            if not line: continue
            meta, name = line.split('\t', 1)
            _, type, sha = meta.split()
            item_type = 'dir' if type == 'tree' else 'file'
            snapshot_items[name] = {'sha': sha, 'type': item_type}
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise GitRepositoryError(f"Erro ao ler o snapshot '{tag}': {e}") from e

    for root, dirs, files in os.walk(path, topdown=True):
        # Filter out dot-directories recursively
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for item_name in dirs + files:
            full_path = os.path.join(root, item_name)
            relative_path = os.path.relpath(full_path, path)

            # Ignore the root '.' path
            if relative_path == '.':
                continue

            if os.path.isdir(full_path):
                local_items[relative_path] = {'sha': '', 'type': 'dir'}
            else:
                try:
                    # Use relative path for hash-object
                    file_sha = subprocess.run(
                        ["git", "hash-object", relative_path],
                        cwd=path, check=True, capture_output=True, text=True
                    ).stdout.strip()
                    local_items[relative_path] = {'sha': file_sha, 'type': 'file'}
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue

    snapshot_results: List[Dict[str, Any]] = []
    local_results: List[Dict[str, Any]] = []
    all_paths = sorted(list(set(snapshot_items.keys()) | set(local_items.keys())))

    for item_path in all_paths:
        s_item = snapshot_items.get(item_path)
        l_item = local_items.get(item_path)

        if s_item and l_item:
            status = 'modificado'
            if s_item['type'] == l_item['type']:
                if s_item['type'] == 'dir' or s_item['sha'] == l_item['sha']:
                    status = 'igual'
            snapshot_results.append({'name': item_path, 'type': s_item['type'], 'status': status})
            local_results.append({'name': item_path, 'type': l_item['type'], 'status': status})
        elif s_item:
            snapshot_results.append({'name': item_path, 'type': s_item['type'], 'status': 'igual'})
            local_results.append({'name': item_path, 'type': s_item['type'], 'status': 'missing'})
        elif l_item:
            snapshot_results.append({'name': item_path, 'type': l_item['type'], 'status': 'missing'})
            local_results.append({'name': item_path, 'type': l_item['type'], 'status': 'igual'})

    return snapshot_results, local_results

def rename_snapshot_tag(old_tag: str, new_tag: str, path: str = "."):
    """Renames a snapshot tag by creating a new one and deleting the old one, preserving the annotation."""
    if not is_git_repo(path):
        raise GitRepositoryError("Not a git repository.")
    if not old_tag or not new_tag:
        raise ValueError("Tags não podem estar vazias.")
    if " " in new_tag:
        raise ValueError("O nome da tag não pode conter espaços.")

    try:
        # Get the commit hash the old tag points to
        commit_hash = subprocess.run(["git", "rev-list", "-n", "1", old_tag], cwd=path, check=True, capture_output=True, text=True).stdout.strip()
        if not commit_hash:
            raise GitRepositoryError(f"Could not find commit for tag '{old_tag}'.")

        # Get the message from the old annotated tag
        tag_message_process = subprocess.run(
            ["git", "for-each-ref", f"refs/tags/{old_tag}", "--format=%(contents)"],
            cwd=path, check=True, capture_output=True, text=True, encoding='utf-8'
        )
        tag_message = tag_message_process.stdout

        # Create the new annotated tag pointing to the same commit with the same message
        subprocess.run(["git", "tag", "-a", new_tag, "-m", tag_message, commit_hash], cwd=path, check=True, capture_output=True)
        
        # Delete the old tag
        subprocess.run(["git", "tag", "-d", old_tag], cwd=path, check=True, capture_output=True)

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        # Attempt to clean up if the new tag was created but the old one failed to delete
        try:
            subprocess.run(["git", "tag", "-d", new_tag], cwd=path, check=False, capture_output=True)
        except:
            pass
        
        output = e.stderr if hasattr(e, 'stderr') and e.stderr else ''
        output = output if isinstance(output, str) else output.decode()
        raise GitRepositoryError(f"Erro ao renomear a tag '{old_tag}': {output}") from e

def compare_snapshots_side_by_side(tag1: str, tag2: str, path: str = ".") -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Compares two snapshots side-by-side, returning structured data for a tree view.
    """
    if not is_git_repo(path):
        raise GitRepositoryError("O diretório não é um repositório Git.")

    def get_snapshot_items(tag: str) -> Dict[str, Dict[str, str]]:
        items: Dict[str, Dict[str, str]] = {}
        try:
            cmd = ["git", "ls-tree", "-r", "-t", tag]
            result = subprocess.run(cmd, cwd=path, check=True, capture_output=True, text=True, encoding='utf-8')
            for line in result.stdout.strip().split('\n'):
                if not line: continue
                meta, name = line.split('\t', 1)
                _, type, sha = meta.split()
                item_type = 'dir' if type == 'tree' else 'file'
                items[name] = {'sha': sha, 'type': item_type}
            return items
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise GitRepositoryError(f"Erro ao ler o snapshot '{tag}': {e}") from e

    tag1_items = get_snapshot_items(tag1)
    tag2_items = get_snapshot_items(tag2)

    results1: List[Dict[str, Any]] = []
    results2: List[Dict[str, Any]] = []
    all_paths = sorted(list(set(tag1_items.keys()) | set(tag2_items.keys())))

    for item_path in all_paths:
        item1 = tag1_items.get(item_path)
        item2 = tag2_items.get(item_path)

        if item1 and item2:
            status = 'modificado'
            if item1['type'] == item2['type'] and item1['sha'] == item2['sha']:
                status = 'igual'
            results1.append({'name': item_path, 'type': item1['type'], 'status': status})
            results2.append({'name': item_path, 'type': item2['type'], 'status': status})
        elif item1:
            results1.append({'name': item_path, 'type': item1['type'], 'status': 'igual'})
            results2.append({'name': item_path, 'type': item1['type'], 'status': 'missing'})
        elif item2:
            results1.append({'name': item_path, 'type': item2['type'], 'status': 'missing'})
            results2.append({'name': item_path, 'type': item2['type'], 'status': 'igual'})

    return results1, results2

def update_snapshot_metadata(tag: str, new_internal_name: Optional[str] = None, new_type: Optional[str] = None, new_description: Optional[str] = None, path: str = "."):
    """Updates the metadata (internal name, type, description) of a snapshot."""
    if not is_git_repo(path):
        raise GitRepositoryError("Not a git repository.")
    
    try:
        commit_hash = subprocess.run(["git", "rev-list", "-n", "1", tag], cwd=path, check=True, capture_output=True, text=True).stdout.strip()
        
        # Get current note
        note_process = subprocess.run(["git", "notes", "show", commit_hash], cwd=path, capture_output=True, text=True)
        note_content = note_process.stdout.strip()
        
        metadata = {}
        if note_process.returncode == 0 and note_content:
            try:
                metadata = json.loads(note_content)
            except json.JSONDecodeError:
                # It's an old snapshot with a plain text note
                metadata = {"internal_name": note_content, "type": "none", "description": ""}

        if new_internal_name is not None:
            metadata["internal_name"] = new_internal_name
        if new_type is not None:
            metadata["type"] = new_type
        if new_description is not None:
            metadata["description"] = new_description
            
        metadata_json = json.dumps(metadata)
        subprocess.run(["git", "notes", "add", "-f", "-m", metadata_json, commit_hash], cwd=path, check=True)

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise GitRepositoryError(f"Erro ao atualizar os metadados do snapshot '{tag}': {e}") from e

def get_snapshot_tree(tag: str, path: str = ".") -> List[Dict[str, str]]:
    """Retrieves the file tree of a single snapshot."""
    if not is_git_repo(path):
        raise GitRepositoryError("O diretório não é um repositório Git.")

    items: List[Dict[str, str]] = []
    try:
        cmd = ["git", "ls-tree", "-r", "-t", tag]
        result = subprocess.run(cmd, cwd=path, check=True, capture_output=True, text=True, encoding='utf-8')
        for line in result.stdout.strip().split('\n'):
            if not line: continue
            meta, name = line.split('\t', 1)
            
            if name == '.gitignore' or name.startswith('.venv/'):
                continue
            
            _, type, _ = meta.split()
            item_type = 'dir' if type == 'tree' else 'file'
            items.append({'name': name, 'type': item_type})
        return items
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise GitRepositoryError(f"Erro ao ler o snapshot '{tag}': {e}") from e

def get_file_content_from_snapshot(tag: str, file_path: str, path: str = ".") -> str:
    """Retrieves the content of a specific file from a given snapshot."""
    if not is_git_repo(path):
        raise GitRepositoryError("Not a git repository.")
    try:
        # Format is <tag>:<path_from_root>
        ref = f"{tag}:{file_path}"
        result = subprocess.run(["git", "show", ref], cwd=path, check=True, capture_output=True, text=True, encoding='utf-8')
        return result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        # Return empty string if file doesn't exist in that snapshot
        return ""
    except Exception as e:
        raise GitRepositoryError(f"Erro ao obter conteúdo do ficheiro '{file_path}' do snapshot '{tag}': {e}") from e

def export_snapshot(tag: str, export_path: str, path: str = "."):
    """Exports a snapshot to a ZIP file, including all its files and metadata, ignoring dotfiles."""
    if not is_git_repo(path):
        raise GitRepositoryError("Not a git repository.")

    # 1. Get snapshot metadata
    try:
        all_snapshots = list_snapshots(path)
        snapshot_to_export = next((s for s in all_snapshots if s.tag == tag), None)
        if not snapshot_to_export:
            raise GitRepositoryError(f"Snapshot com a tag '{tag}' não encontrado.")
        
        metadata = {
            "internal_name": snapshot_to_export.internal_name,
            "tag": snapshot_to_export.tag,
            "message": snapshot_to_export.message,
            "type": snapshot_to_export.type,
            "description": snapshot_to_export.description,
            "date": snapshot_to_export.date.isoformat()
        }
    except GitRepositoryError as e:
        raise GitRepositoryError(f"Erro ao obter metadados do snapshot: {e}")

    try:
        # 2. Get list of files from the snapshot's tree
        ls_tree_process = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", tag],
            cwd=path, check=True, capture_output=True, text=True, encoding='utf-8'
        )
        all_files = ls_tree_process.stdout.strip().split('\n')

        # 3. Filter out dotfiles and dot-directories
        files_to_include = [
            f for f in all_files if not any(part.startswith('.') for part in f.split('/'))
        ]

        # 4. Create the ZIP file and write file contents
        with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add metadata
            zipf.writestr("metadata.json", json.dumps(metadata, indent=4))
            
            # Add files
            for file_path in files_to_include:
                if not file_path: continue
                try:
                    # Get file content from git
                    file_content = get_file_content_from_snapshot(tag, file_path, path)
                    # Write content to zip
                    zipf.writestr(file_path, file_content)
                except GitRepositoryError:
                    # Ignore files that can't be read, though this should be rare
                    continue

    except (subprocess.CalledProcessError, FileNotFoundError, IOError) as e:
        error_message = f"Erro ao exportar o snapshot: {e}"
        if hasattr(e, 'stderr') and e.stderr:
            error_message += f"\nDetalhes: {e.stderr.decode()}"
        raise GitRepositoryError(error_message)


def import_snapshot(zip_path: str, path: str = "."):
    """Imports a snapshot from a ZIP file."""
    if not is_git_repo(path):
        raise GitRepositoryError("Not a git repository.")

    temp_dir = None
    try:
        # 1. Create a temporary directory and extract the ZIP
        temp_dir = tempfile.mkdtemp(prefix="gitsnap_import_")
        
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(temp_dir)

        # 2. Read metadata.json
        metadata_path = os.path.join(temp_dir, "metadata.json")
        if not os.path.exists(metadata_path):
            raise GitRepositoryError("Ficheiro 'metadata.json' não encontrado no arquivo ZIP.")
        
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        # Remove metadata file before committing
        os.remove(metadata_path)

        # 3. Create a new snapshot from the imported files
        # This is a complex operation. We'll create an "orphan" commit
        # that doesn't have a parent, representing the imported state.
        
        # Store current branch name to return to it later
        original_branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=path, check=True, capture_output=True, text=True
        ).stdout.strip()

        # Create a temporary orphan branch
        temp_branch = f"import-temp-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        subprocess.run(
            ["git", "checkout", "--orphan", temp_branch],
            cwd=path, check=True, capture_output=True
        )
        
        # Clean the working directory (it's a new branch, so it's safe)
        subprocess.run(
            ["git", "rm", "-rf", "."],
            cwd=path, check=True, capture_output=True
        )

        # Copy extracted files to the repo root
        for item in os.listdir(temp_dir):
            s = os.path.join(temp_dir, item)
            d = os.path.join(path, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)

        # Add and commit the files
        subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
        
        # Use the date from metadata for the commit
        commit_date = metadata.get("date")
        env = os.environ.copy()
        if commit_date:
            env["GIT_COMMITTER_DATE"] = commit_date
            env["GIT_AUTHOR_DATE"] = commit_date

        commit_process = subprocess.run(
            ["git", "commit", "-m", metadata["message"]],
            cwd=path, check=True, capture_output=True, text=True, env=env
        )
        commit_hash = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=path, check=True, capture_output=True, text=True
        ).stdout.strip()

        # 4. Apply tag and metadata note
        tag = metadata["tag"]
        # Ensure tag is unique if it already exists
        existing_tags = {s.tag for s in list_snapshots(path)}
        if tag in existing_tags:
            tag = f"{tag}-imported-{datetime.now().strftime('%Y%m%d%H%M')}"

        subprocess.run(["git", "tag", "-a", tag, "-m", metadata["message"]], cwd=path, check=True)
        
        note_metadata = {
            "internal_name": metadata["internal_name"],
            "type": metadata["type"],
            "description": metadata["description"]
        }
        metadata_json = json.dumps(note_metadata)
        subprocess.run(["git", "notes", "add", "-f", "-m", metadata_json, commit_hash], cwd=path, check=True)

        # 5. Return to the original branch and clean up
        subprocess.run(["git", "checkout", original_branch], cwd=path, check=True, capture_output=True)
        subprocess.run(["git", "branch", "-D", temp_branch], cwd=path, check=True, capture_output=True)

    except (subprocess.CalledProcessError, FileNotFoundError, IOError, json.JSONDecodeError) as e:
        error_message = f"Erro ao importar o snapshot: {e}"
        if hasattr(e, 'stderr') and e.stderr:
            error_message += f"\nDetalhes: {e.stderr.decode()}"
        raise GitRepositoryError(error_message)
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
