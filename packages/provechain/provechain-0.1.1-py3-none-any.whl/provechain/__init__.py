"""
ProveChain - Blockchain Timestamping for Source Code
====================================================

Git tracks your code history. ProveChain proves you wrote it first.

Core Components:
    - ProveChain: Main ledger class for creating/verifying proofs
    - CLI: Command-line interface (provechain command)

Quick Start:
    from provechain import ProveChain

    ledger = ProveChain(project_root=".")
    proof_file = ledger.snapshot("Initial commit")
    result = ledger.verify(proof_file)

CLI Usage:
    provechain init
    provechain snapshot "Added authentication"
    provechain verify provechain/proofs/proof_2025-11-11.json
    provechain list

Author: John Doyle
Version: 0.1.0
License: MIT
"""

from .ledger import ProveChain

__version__ = "0.1.1"
__author__ = "John Doyle"
__all__ = ["ProveChain"]
