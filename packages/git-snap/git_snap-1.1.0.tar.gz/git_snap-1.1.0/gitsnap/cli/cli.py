import argparse
import sys

from gitsnap.core import git_repo, snapshots
from gitsnap.core.errors import GitSnapError, NoChangesError, RepositoryNotInitializedError

def handle_save(args):
    """Handles the 'save' command."""
    try:
        snapshots.save_snapshot(args.message)
        print(f"Snapshot salvo com a mensagem: '{args.message}'")
    except NoChangesError:
        print("Nenhuma alteração para salvar. O snapshot não foi criado.")
        # Do not exit with an error code, as this is not a failure.
    except GitSnapError as e:
        print(f"Erro ao salvar snapshot: {e}", file=sys.stderr)
        sys.exit(1)

def handle_list(args):
    """Handles the 'list' command."""
    try:
        snap_list = snapshots.list_snapshots()
        if not snap_list:
            print("Nenhum snapshot encontrado.")
            return

        print("Snapshots disponíveis:")
        for snap in snap_list:
            # Support for empty messages from --allow-empty
            message = snap.message or "(sem mensagem)"
            print(f"  - {snap.sha[:7]}: {message}")
            
    except GitSnapError as e:
        print(f"Erro ao listar snapshots: {e}", file=sys.stderr)
        sys.exit(1)

def handle_restore(args):
    """Handles the 'restore' command."""
    if not args.yes:
        confirm = input(f"Tem a certeza que quer restaurar o snapshot '{args.hash}'? (s/n): ")
        if confirm.lower() != 's':
            print("Restauração cancelada.")
            return

    try:
        # We need to find the full tag name from the short hash
        snap_list = snapshots.list_snapshots()
        target_snap = next((s for s in snap_list if s.sha.startswith(args.hash)), None)
        
        if not target_snap:
            print(f"Erro: Snapshot com hash '{args.hash}' não encontrado.", file=sys.stderr)
            sys.exit(1)

        snapshots.restore_snapshot(target_snap.tag)
        print(f"Repositório restaurado para o snapshot '{target_snap.tag}'.")
    except GitSnapError as e:
        print(f"Erro ao restaurar snapshot: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main CLI entry point."""
    try:
        git_repo.check_repo_ready()
    except RepositoryNotInitializedError as e:
        print(f"Aviso: {e}")
        confirm = input("Deseja inicializar um novo repositório Git neste diretório? (s/n): ")
        if confirm.lower() == 's':
            try:
                git_repo.initialize_and_setup_repo()
                print("Repositório Git inicializado com sucesso e pronto para uso.")
            except GitSnapError as init_e:
                print(f"Erro ao inicializar repositório: {init_e}", file=sys.stderr)
                sys.exit(1)
        else:
            print("Operação cancelada. Nenhum repositório Git foi criado.")
            sys.exit(0)
    except GitSnapError as e:
        print(f"Erro inesperado no repositório Git: {e}", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Um utilitário de linha de comando para gitsnap.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Save command
    save_parser = subparsers.add_parser("save", help="Cria um novo snapshot.")
    save_parser.add_argument("message", type=str, help="A mensagem para o snapshot.")
    save_parser.set_defaults(func=handle_save)

    # List command
    list_parser = subparsers.add_parser("list", help="Lista todos os snapshots.")
    list_parser.set_defaults(func=handle_list)

    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restaura para um snapshot específico.")
    restore_parser.add_argument("hash", type=str, help="O hash (curto ou completo) do snapshot a restaurar.")
    restore_parser.add_argument("--yes", "-y", action="store_true", help="Ignora a confirmação.")
    restore_parser.set_defaults(func=handle_restore)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()