#!/usr/bin/env python3
"""
ProveChain CLI - Command-line interface for code authorship proofs

Commands:
    snapshot    Create a new proof snapshot
    verify      Verify a proof file
    list        List all proofs
    log         Log an innovation event
    init        Initialize ProveChain in current project

Usage:
    provechain snapshot "Added OAuth integration"
    provechain verify provechain/proofs/proof_2025-11-11.json
    provechain list
    provechain log "Implemented AES-256-GCM encryption"
"""

import argparse
import sys
import json
from pathlib import Path
from .ledger import ProveChain
from rich.console import Console

console = Console()


def cmd_init(args):
    """Initialize ProveChain in current project."""
    project_root = Path.cwd()
    config_path = project_root / "provechain.yaml"

    if config_path.exists() and not args.force:
        console.print("[red]ERROR:[/red] provechain.yaml already exists")
        console.print("[dim]Use --force to overwrite[/dim]")
        return 1

    # Create default config
    default_config = """# ProveChain Configuration
# https://github.com/aramantos/provechain

# File extensions to include in snapshots
include_extensions:
  - .py
  - .js
  - .ts
  - .java
  - .go
  - .rs
  - .c
  - .cpp
  - .md
  - .yaml
  - .json

# Paths to ignore (relative to project root)
ignore_paths:
  - .git
  - .venv
  - venv
  - node_modules
  - __pycache__
  - dist
  - build
  - provechain

# Blockchain timestamping (future feature)
# blockchain:
#   enabled: false
#   network: ethereum
#   contract_address: 0x...
"""

    try:
        with open(config_path, 'w') as f:
            f.write(default_config)

        console.print()
        console.print(f"[bold green]ProveChain Initialized![/bold green]")
        console.print(f"[dim]Location: {project_root}[/dim]")
        console.print(f"[dim]Config: provechain.yaml[/dim]")
        console.print()
        console.print("[bold cyan]Next steps:[/bold cyan]")
        console.print("  [cyan]1.[/cyan] Edit provechain.yaml to customize settings")
        console.print("  [cyan]2.[/cyan] Run: [green]provechain snapshot \"Initial commit\"[/green]")
        console.print("  [cyan]3.[/cyan] Add [yellow]provechain/[/yellow] to your .gitignore")
        console.print()

        return 0
    except IOError as e:
        console.print(f"[red]ERROR:[/red] Error writing config file: {e}")
        return 1


def cmd_snapshot(args):
    """Create a proof snapshot."""
    try:
        ledger = ProveChain(args.project_root or Path.cwd())
        proof_file = ledger.snapshot(description=args.description)
        return 0
    except FileNotFoundError as e:
        console.print(f"[red]ERROR:[/red] Error: {e}")
        console.print("[dim]Make sure you're in a valid project directory[/dim]")
        return 1
    except PermissionError as e:
        console.print(f"[red]ERROR:[/red] Permission denied: {e}")
        return 1
    except Exception as e:
        console.print(f"[red]ERROR:[/red] Unexpected error creating snapshot: {e}")
        return 1


def cmd_verify(args):
    """Verify a proof file."""
    try:
        ledger = ProveChain(args.project_root or Path.cwd())
        result = ledger.verify(Path(args.proof_file))

        # Exit code based on verification result
        if result['mismatches'] == 0 and result['missing'] == 0:
            return 0
        else:
            return 1
    except FileNotFoundError:
        console.print(f"[red]ERROR:[/red] Error: Proof file not found: {args.proof_file}")
        console.print("[dim]Use 'provechain list' to see available proofs[/dim]")
        return 1
    except json.JSONDecodeError:
        console.print(f"[red]ERROR:[/red] Error: Invalid JSON in proof file")
        console.print("[dim]The proof file may be corrupted[/dim]")
        return 1
    except Exception as e:
        console.print(f"[red]ERROR:[/red] Unexpected error verifying proof: {e}")
        return 1


def cmd_list(args):
    """List all proof files."""
    try:
        ledger = ProveChain(args.project_root or Path.cwd())
        proofs = ledger.list_proofs()

        if not proofs:
            console.print()
            console.print("[yellow]No proofs found[/yellow]")
            console.print("[dim]Run 'provechain snapshot' to create your first proof[/dim]")
            console.print()
            return 0

        # Interactive proof selection
        if not args.no_interactive:
            console.print("[cyan]Would you like to verify a proof?[/cyan]")
            console.print("[dim]Enter proof number [1-{}], or 'q' to quit:[/dim] ".format(len(proofs)), end="")

            try:
                choice = input().strip().lower()

                if choice == 'q' or choice == '':
                    console.print("[dim]Exiting...[/dim]")
                    return 0

                # Try to parse as number
                try:
                    index = int(choice) - 1  # Convert to 0-based index

                    if 0 <= index < len(proofs):
                        selected_proof = proofs[index]
                        proof_path = ledger.proofs_dir / selected_proof['file']

                        console.print()
                        console.print(f"[cyan]Verifying:[/cyan] {selected_proof['description'] or selected_proof['file']}")
                        console.print()

                        # Create a mock args object for cmd_verify
                        class VerifyArgs:
                            def __init__(self, proof_file, project_root):
                                self.proof_file = proof_file
                                self.project_root = project_root

                        verify_args = VerifyArgs(str(proof_path), args.project_root)
                        return cmd_verify(verify_args)
                    else:
                        console.print(f"[red]ERROR:[/red] Invalid selection. Please choose 1-{len(proofs)}")
                        return 1

                except ValueError:
                    console.print(f"[red]ERROR:[/red] Invalid input. Please enter a number or 'q'")
                    return 1

            except KeyboardInterrupt:
                console.print("\n[dim]Cancelled[/dim]")
                return 0

        return 0
    except FileNotFoundError as e:
        console.print(f"[red]ERROR:[/red] Error: {e}")
        console.print("[dim]Make sure you're in a valid project directory[/dim]")
        return 1
    except Exception as e:
        console.print(f"[red]ERROR:[/red] Unexpected error listing proofs: {e}")
        return 1


def cmd_log(args):
    """Log an innovation event."""
    try:
        ledger = ProveChain(args.project_root or Path.cwd())
        ledger.log_innovation(args.description)
        return 0
    except PermissionError as e:
        console.print(f"[red]ERROR:[/red] Permission denied: {e}")
        return 1
    except Exception as e:
        console.print(f"[red]ERROR:[/red] Unexpected error logging innovation: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        prog='provechain',
        description='🔒 ProveChain - Cryptographic Proof of Code Authorship',
        epilog='For more info: https://provechain.io | https://github.com/aramantos/provechain',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--project-root',
        type=str,
        help='Project root directory (default: current directory)'
    )

    subparsers = parser.add_subparsers(dest='command', required=True)

    # init command
    parser_init = subparsers.add_parser(
        'init',
        help='Initialize ProveChain in current project'
    )
    parser_init.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing provechain.yaml'
    )
    parser_init.set_defaults(func=cmd_init)

    # snapshot command
    parser_snapshot = subparsers.add_parser(
        'snapshot',
        help='Create a new proof snapshot'
    )
    parser_snapshot.add_argument(
        'description',
        nargs='?',
        type=str,
        help='Description of this snapshot (e.g., "v1.0 release")'
    )
    parser_snapshot.set_defaults(func=cmd_snapshot)

    # verify command
    parser_verify = subparsers.add_parser(
        'verify',
        help='Verify a proof file against current state'
    )
    parser_verify.add_argument(
        'proof_file',
        type=str,
        help='Path to proof JSON file'
    )
    parser_verify.set_defaults(func=cmd_verify)

    # list command
    parser_list = subparsers.add_parser(
        'list',
        help='List all proof files'
    )
    parser_list.add_argument(
        '--no-interactive',
        action='store_true',
        help='Disable interactive proof selection'
    )
    parser_list.set_defaults(func=cmd_list)

    # log command
    parser_log = subparsers.add_parser(
        'log',
        help='Log an innovation event'
    )
    parser_log.add_argument(
        'description',
        type=str,
        help='Description of the innovation'
    )
    parser_log.set_defaults(func=cmd_log)

    # Parse and execute
    args = parser.parse_args()

    if hasattr(args, 'func'):
        try:
            exit_code = args.func(args)
            sys.exit(exit_code)
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted by user[/yellow]")
            sys.exit(130)
        except Exception as e:
            console.print(f"\n[red]FATAL ERROR:[/red] {e}")
            if '--debug' in sys.argv:
                raise
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
