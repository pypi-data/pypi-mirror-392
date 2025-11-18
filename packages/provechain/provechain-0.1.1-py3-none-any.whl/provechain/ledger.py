"""
ProveChain - Blockchain Timestamping for Source Code
----------------------------------------------------

Core ledger functionality for creating cryptographic proofs of code authorship.

Features:
    - SHA-256 file hashing with configurable filters
    - Timestamped proof snapshots (JSON format)
    - Innovation event ledger (NDJSON)
    - Optional AES-GCM encryption
    - Git integration (planned)
    - Blockchain timestamping (planned)

Author: John Doyle
License: MIT
"""

import os
import uuid
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel

# Initialize rich console
console = Console()


class ProveChain:
    """
    Core ledger for creating and managing code authorship proofs.

    A "proof" is a timestamped snapshot of file hashes in a project.
    The ledger tracks when proofs were created and optionally logs innovation events.
    """

    def __init__(
        self,
        project_root: str,
        output_dir: Optional[str] = None,
        config_path: Optional[str] = None
    ):
        """
        Initialize ProveChain.

        Args:
            project_root: Root directory of the project to snapshot
            output_dir: Where to store proofs and ledger (default: ./provechain/)
            config_path: Path to config YAML (default: ./provechain.yaml)
        """
        self.project_root = Path(project_root).resolve()

        # Default output to ./provechain/ in project root
        if output_dir is None:
            output_dir = self.project_root / "provechain"
        self.output_dir = Path(output_dir)

        # Create subdirectories
        self.proofs_dir = self.output_dir / "proofs"
        self.proofs_dir.mkdir(parents=True, exist_ok=True)

        # Ledger file (NDJSON format - one JSON object per line)
        self.ledger_file = self.output_dir / "innovation_ledger.ndjson"

        # Load configuration
        if config_path is None:
            config_path = self.project_root / "provechain.yaml"
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: Path) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            # Use defaults if no config file
            return {
                'include_extensions': ['.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp', '.md', '.yaml', '.json'],
                'ignore_paths': ['.git', '.venv', 'venv', 'node_modules', '__pycache__', 'dist', 'build', 'provechain']
            }
        except yaml.YAMLError as e:
            print(f"Warning: Error parsing config file: {e}")
            return {}

    def _get_filter_rules(self) -> Tuple[tuple, tuple]:
        """
        Get file filtering rules from config.

        Returns:
            (included_extensions, ignored_paths)
        """
        config = self.config

        # Extensions to include
        included_exts = tuple(config.get('include_extensions', [
            '.py', '.js', '.ts', '.java', '.go', '.rs', '.c', '.cpp',
            '.md', '.yaml', '.json'
        ]))

        # Paths to ignore (relative to project root)
        ignore_list = config.get('ignore_paths', [
            '.git', '.venv', 'venv', 'node_modules', '__pycache__',
            'dist', 'build', 'provechain'
        ])
        ignored_paths = tuple(self.project_root / p for p in ignore_list)

        return included_exts, ignored_paths

    def hash_file(self, file_path: Path) -> str:
        """
        Compute SHA-256 hash of a file.

        Args:
            file_path: Path to file to hash

        Returns:
            Hex-encoded SHA-256 hash
        """
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            # Read in chunks for large files
            for chunk in iter(lambda: f.read(65536), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def snapshot(self, description: Optional[str] = None) -> Path:
        """
        Create a proof snapshot of current project state.

        This walks through the project directory, hashes all included files,
        and saves the results to a timestamped JSON proof file.

        Args:
            description: Optional description of this snapshot

        Returns:
            Path to the created proof file
        """
        included_exts, ignored_paths = self._get_filter_rules()
        file_hashes = {}
        files_processed = 0
        files_skipped = 0

        console.print(f"\n[bold cyan]Creating ProveChain Snapshot[/bold cyan]")
        console.print(f"[dim]Project: {self.project_root}[/dim]")
        console.print(f"[dim]Extensions: {', '.join(included_exts)}[/dim]\n")

        # First, collect all files to process
        files_to_process = []
        for root, dirs, files in os.walk(self.project_root):
            root_path = Path(root)

            # Skip ignored directories
            if any(root_path == ignored or root_path.is_relative_to(ignored)
                   for ignored in ignored_paths):
                files_skipped += len(files)
                continue

            # Collect files
            for file in files:
                if file.endswith(included_exts):
                    file_path = root_path / file
                    files_to_process.append(file_path)
                else:
                    files_skipped += 1

        # Now hash files with progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Hashing files...", total=len(files_to_process))

            for file_path in files_to_process:
                try:
                    file_hash = self.hash_file(file_path)
                    relative_path = file_path.relative_to(self.project_root)
                    # Use forward slashes for cross-platform compatibility
                    file_hashes[str(relative_path).replace('\\', '/')] = file_hash
                    files_processed += 1
                except (IOError, OSError) as e:
                    console.print(f"[yellow]Warning: Could not read {file_path}: {e}[/yellow]")
                    files_skipped += 1
                finally:
                    progress.advance(task)

        # Create proof metadata
        proof_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

        proof_data = {
            "proof_id": proof_id,
            "timestamp": timestamp,
            "description": description,
            "project_root": str(self.project_root),
            "total_files": len(file_hashes),
            "files_processed": files_processed,
            "files_skipped": files_skipped,
            "file_hashes": file_hashes
        }

        # Save proof file
        proof_filename = f"proof_{timestamp.replace(':', '-').replace('.', '-')}.json"
        proof_filepath = self.proofs_dir / proof_filename

        with open(proof_filepath, 'w') as f:
            json.dump(proof_data, f, indent=2)

        # Display success message in a panel
        console.print()
        console.print(Panel.fit(
            f"[bold green]Snapshot Created Successfully![/bold green]\n\n"
            f"[cyan]Proof ID:[/cyan] {proof_id}\n"
            f"[cyan]Files Hashed:[/cyan] {files_processed}\n"
            f"[cyan]Files Skipped:[/cyan] {files_skipped}\n"
            f"[cyan]Saved to:[/cyan] {proof_filepath.name}",
            title="[bold]ProveChain Snapshot[/bold]",
            border_style="green"
        ))

        # Log to ledger
        self._log_to_ledger("snapshot_created", {
            "proof_id": proof_id,
            "proof_file": str(proof_filepath),
            "description": description,
            "files_hashed": files_processed
        })

        return proof_filepath

    def verify(self, proof_file: Path) -> Dict:
        """
        Verify a proof file against current project state.

        Re-hashes all files mentioned in the proof and compares hashes.

        Args:
            proof_file: Path to proof JSON file

        Returns:
            Verification result dict with matches, mismatches, missing files
        """
        with open(proof_file, 'r') as f:
            proof_data = json.load(f)

        original_hashes = proof_data.get('file_hashes', {})
        matches = []
        mismatches = []
        missing = []

        console.print(f"\n[bold cyan]Verifying ProveChain Proof[/bold cyan]")
        console.print(f"[dim]Proof ID: {proof_data.get('proof_id')}[/dim]")
        console.print(f"[dim]Original Timestamp: {proof_data.get('timestamp')}[/dim]")
        console.print(f"[dim]Files to Verify: {len(original_hashes)}[/dim]\n")

        # Verify with progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Verifying hashes...", total=len(original_hashes))

            for relative_path, original_hash in original_hashes.items():
                file_path = self.project_root / relative_path

                if not file_path.exists():
                    missing.append(relative_path)
                    progress.advance(task)
                    continue

                try:
                    current_hash = self.hash_file(file_path)
                    if current_hash == original_hash:
                        matches.append(relative_path)
                    else:
                        mismatches.append({
                            'file': relative_path,
                            'original_hash': original_hash,
                            'current_hash': current_hash
                        })
                except (IOError, OSError) as e:
                    console.print(f"[yellow]Warning: Could not read {file_path}: {e}[/yellow]")
                    missing.append(relative_path)
                finally:
                    progress.advance(task)

        result = {
            "proof_id": proof_data.get('proof_id'),
            "timestamp": proof_data.get('timestamp'),
            "total_files": len(original_hashes),
            "matches": len(matches),
            "mismatches": len(mismatches),
            "missing": len(missing),
            "match_percentage": (len(matches) / len(original_hashes) * 100) if original_hashes else 0,
            "mismatch_details": mismatches,
            "missing_files": missing
        }

        # Display results in a table
        table = Table(title="Verification Results", show_header=True, header_style="bold magenta")
        table.add_column("Status", style="cyan", justify="center")
        table.add_column("Count", justify="right")
        table.add_column("Percentage", justify="right")

        table.add_row("Matches", str(len(matches)), f"{result['match_percentage']:.1f}%")
        table.add_row("Mismatches", str(len(mismatches)), f"{len(mismatches) / len(original_hashes) * 100 if original_hashes else 0:.1f}%")
        table.add_row("Missing", str(len(missing)), f"{len(missing) / len(original_hashes) * 100 if original_hashes else 0:.1f}%")

        console.print()
        console.print(table)

        # Show mismatch details if any
        if mismatches:
            console.print(f"\n[yellow]Files that changed:[/yellow]")
            for mm in mismatches[:5]:  # Show first 5
                console.print(f"  [red]-[/red] {mm['file']}")
            if len(mismatches) > 5:
                console.print(f"  [dim]... and {len(mismatches) - 5} more[/dim]")

        if missing:
            console.print(f"\n[yellow]Files missing:[/yellow]")
            for mf in missing[:5]:  # Show first 5
                console.print(f"  [red]?[/red] {mf}")
            if len(missing) > 5:
                console.print(f"  [dim]... and {len(missing) - 5} more[/dim]")

        # Final verdict
        console.print()
        if result['mismatches'] == 0 and result['missing'] == 0:
            console.print(Panel.fit(
                "[bold green]Verification PASSED[/bold green]\n\n"
                "All files match the original proof.",
                border_style="green"
            ))
        else:
            console.print(Panel.fit(
                "[bold red]Verification FAILED[/bold red]\n\n"
                f"{len(mismatches)} file(s) changed, {len(missing)} file(s) missing.",
                border_style="red"
            ))

        return result

    def log_innovation(self, description: str, metadata: Optional[Dict] = None):
        """
        Log an innovation event to the ledger.

        Args:
            description: Description of the innovation
            metadata: Optional additional metadata
        """
        self._log_to_ledger("innovation", {
            "description": description,
            **(metadata or {})
        })
        console.print(f"[green]Innovation logged:[/green] [cyan]{description}[/cyan]")

    def _log_to_ledger(self, event_type: str, payload: Dict):
        """
        Internal method to append an event to the ledger.

        Args:
            event_type: Type of event (snapshot_created, innovation, etc.)
            payload: Event data
        """
        event_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

        log_entry = {
            "event_id": event_id,
            "timestamp": timestamp,
            "event_type": event_type,
            **payload
        }

        with open(self.ledger_file, 'a') as f:
            json.dump(log_entry, f)
            f.write('\n')

    def list_proofs(self, show_table: bool = True) -> List[Dict]:
        """
        List all proof files in the proofs directory.

        Args:
            show_table: Whether to display results in a table (default: True)

        Returns:
            List of proof metadata dicts
        """
        proofs = []

        for proof_file in sorted(self.proofs_dir.glob("proof_*.json")):
            try:
                with open(proof_file, 'r') as f:
                    proof_data = json.load(f)
                    proofs.append({
                        "file": proof_file.name,
                        "proof_id": proof_data.get('proof_id'),
                        "timestamp": proof_data.get('timestamp'),
                        "description": proof_data.get('description'),
                        "total_files": proof_data.get('total_files')
                    })
            except (IOError, json.JSONDecodeError) as e:
                console.print(f"[yellow]Warning: Could not read {proof_file}: {e}[/yellow]")

        if show_table and proofs:
            table = Table(title=f"ProveChain Proofs ({len(proofs)} total)", show_header=True, header_style="bold cyan")
            table.add_column("#", style="bold magenta", width=3)
            table.add_column("Timestamp", style="dim")
            table.add_column("Description", style="cyan")
            table.add_column("Files", justify="right", style="green")
            table.add_column("Proof ID", style="dim", no_wrap=True)

            for i, proof in enumerate(proofs, start=1):
                timestamp = proof['timestamp'][:19].replace('T', ' ') if proof['timestamp'] else 'N/A'
                description = proof['description'] or '[dim italic]No description[/dim italic]'
                files = str(proof['total_files']) if proof['total_files'] else '0'
                proof_id = proof['proof_id'][:8] + '...' if proof['proof_id'] else 'N/A'

                table.add_row(str(i), timestamp, description, files, proof_id)

            console.print()
            console.print(table)
            console.print()

        return proofs
