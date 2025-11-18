# 📜 ProveChain

**Blockchain Timestamping for Source Code**

> Git tracks your code history. ProveChain proves you wrote it first.

ProveChain creates cryptographic proofs of code authorship using SHA-256 file hashing and timestamped snapshots. Perfect for protecting intellectual property, proving prior art for patents, or maintaining an audit trail of innovation.

---

## 🎯 Use Cases

### 1. **Open Source Attribution**
Prove you wrote code before someone copied it.

### 2. **Patent Protection**
Timestamp your inventions before filing patents (prior art defense).

### 3. **Contractor Proof-of-Work**
Prove code was delivered on specific dates.

### 4. **Academic Research Integrity**
Timestamp research code and data before publication.

### 5. **IP Disputes**
Maintain an audit trail of when code was written.

---

## 🚀 Quick Start

### Installation

```bash
# From source
cd tools/provechain
pip install -e .

# Or directly (future PyPI release)
pip install provechain
```

### Basic Usage

```bash
# Initialize in your project
cd /path/to/your/project
provechain init

# Create your first proof snapshot
provechain snapshot "Initial commit"

# List all proofs
provechain list

# Verify a proof
provechain verify provechain/proofs/proof_2025-11-11.json

# Log an innovation
provechain log "Implemented OAuth2 authentication"
```

---

## 📋 How It Works

### 1. **Snapshot**
ProveChain walks through your project, hashes each file with SHA-256, and creates a timestamped JSON proof file.

```json
{
  "proof_id": "a1b2c3d4-...",
  "timestamp": "2025-11-11T15:30:00Z",
  "description": "Added encryption module",
  "total_files": 127,
  "file_hashes": {
    "src/auth.py": "2a00c67a4ac543ad3b65e611391f28a3...",
    "src/db.py": "5f3d8a1b9c2e4f6a8d0b3c5e7f9a1b3c...",
    ...
  }
}
```

### 2. **Verify**
Re-hash all files and compare to the original proof. See what changed, what's missing, and what stayed the same.

```
[ProveChain] Verification Results:
  ✓ Matches:    120 (94.5%)
  ✗ Mismatches: 5
  ? Missing:    2
```

### 3. **Ledger**
All events (snapshots, innovations) are logged to an append-only NDJSON ledger.

```json
{"event_id": "...", "timestamp": "...", "event_type": "snapshot_created", "proof_id": "..."}
{"event_id": "...", "timestamp": "...", "event_type": "innovation", "description": "Added OAuth"}
```

---

## 🔧 Configuration

Create `provechain.yaml` in your project root:

```yaml
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
```

---

## 📚 CLI Reference

### `provechain init`
Initialize ProveChain in current project. Creates `provechain.yaml` config file.

```bash
provechain init
```

### `provechain snapshot [description]`
Create a proof snapshot of current project state.

```bash
provechain snapshot "v1.0 release"
provechain snapshot "Added authentication module"
provechain snapshot  # No description
```

### `provechain verify <proof_file>`
Verify a proof file against current state.

```bash
provechain verify provechain/proofs/proof_2025-11-11.json
```

**Exit codes:**
- `0` - Verification passed (no changes)
- `1` - Verification failed (changes detected)

### `provechain list`
List all proof files with metadata.

```bash
provechain list
```

### `provechain log <description>`
Log an innovation event to the ledger.

```bash
provechain log "Implemented AES-256-GCM encryption"
provechain log "Fixed critical security vulnerability"
```

---

## 🐍 Python API

```python
from provechain import ProveChain

# Initialize
ledger = ProveChain(project_root=".")

# Create snapshot
proof_file = ledger.snapshot("Added OAuth module")
# Returns: Path to proof JSON file

# Verify proof
result = ledger.verify(proof_file)
# Returns: Dict with matches, mismatches, missing files

# Log innovation
ledger.log_innovation("Implemented ML fraud detection")

# List proofs
proofs = ledger.list_proofs()
# Returns: List of proof metadata dicts
```

---

## 🎯 Workflow Examples

### Protecting a Release

```bash
# Before releasing v1.0
git tag v1.0
provechain snapshot "v1.0 release"

# Now you have cryptographic proof of what v1.0 contained
```

### Daily Innovation Log

```bash
# End of day - log what you built
provechain log "Implemented user authentication"
provechain log "Fixed database connection pooling"
provechain log "Added Prometheus metrics"

# Create weekly snapshot
provechain snapshot "Week ending 2025-11-11"
```

### Pre-Patent Timestamping

```bash
# Before filing patent
provechain snapshot "Patent filing - ML algorithm for fraud detection"

# Proof shows code existed on this date
# Useful for prior art defense
```

### Contractor Deliverables

```bash
# At each milestone
provechain snapshot "Milestone 1: User authentication complete"
provechain snapshot "Milestone 2: Payment processing complete"
provechain snapshot "Final delivery"

# Client can verify what was delivered when
```

---

## 🔮 Roadmap

### v0.2 - Git Integration
- [ ] Auto-snapshot on git tags
- [ ] Pre-commit hook integration
- [ ] Git metadata in proofs

### v0.3 - Blockchain Timestamping
- [ ] Ethereum integration
- [ ] Bitcoin OP_RETURN timestamping
- [ ] Stellar ledger integration
- [ ] Verification portal (web UI)

### v0.4 - Team Features
- [ ] Shared ledger (team collaboration)
- [ ] Diff viewer (show changes between proofs)
- [ ] GitHub Actions integration
- [ ] GitLab CI integration

### v1.0 - Enterprise
- [ ] Multi-project management
- [ ] API for CI/CD integration
- [ ] Dashboard for proof management
- [ ] Compliance reports (GDPR, SOC2)

---

## 🤝 Integration with Other Tools

### SignaSeal Integration
ProveChain can integrate with [SignaSeal](../signaseal) for document + code timestamping:

- Use SignaSeal's blockchain infrastructure
- Unified verification portal
- Combined proof: "This agreement was signed AND this code was written on X date"

### Project Freya Integration
ProveChain can integrate with [Project Freya](../project_freya) for automatic snapshots:

- Freya tracks development sessions
- ProveChain auto-snapshots at session end
- Combined: "Here's what I did (Freya) + proof I did it (ProveChain)"

---

## 🔒 Security

### Hashing
- **Algorithm:** SHA-256 (NIST FIPS 180-4)
- **Collision resistance:** Cryptographically secure
- **File chunking:** 64KB chunks for large files

### Timestamps
- **Format:** ISO 8601 UTC
- **Precision:** Second-level
- **Timezone:** Always UTC (Z suffix)

### Future: Blockchain
- **Networks:** Ethereum, Bitcoin, Stellar (planned)
- **Immutability:** Once on blockchain, cannot be altered
- **Verification:** Anyone can verify timestamp on public ledger

---

## 📝 File Formats

### Proof File (JSON)
```json
{
  "proof_id": "uuid",
  "timestamp": "ISO 8601 UTC",
  "description": "string or null",
  "project_root": "absolute path",
  "total_files": "integer",
  "files_processed": "integer",
  "files_skipped": "integer",
  "file_hashes": {
    "relative/path/to/file.py": "sha256 hex digest",
    ...
  }
}
```

### Ledger File (NDJSON)
```json
{"event_id": "uuid", "timestamp": "ISO 8601", "event_type": "snapshot_created", ...}
{"event_id": "uuid", "timestamp": "ISO 8601", "event_type": "innovation", ...}
```

One JSON object per line (newline-delimited JSON).

---

## 🆚 Comparison

| Feature | Git | ProveChain | Blockchain |
|---------|-----|-----------|------------|
| **Tracks history** | ✅ | ✅ | ❌ |
| **Proves authorship** | ⚠️ (can be rewritten) | ✅ | ✅ |
| **Cryptographic proof** | ⚠️ (commits can be changed) | ✅ | ✅ |
| **Immutable** | ❌ (force push) | ⚠️ (local only) | ✅ |
| **Public verification** | ❌ | 🔜 (v0.3) | ✅ |
| **Cost** | Free | Free | $$$ (gas fees) |

**Best practice:** Use all three!
- **Git** for version control and collaboration
- **ProveChain** for local proof-of-work snapshots
- **Blockchain** (via ProveChain v0.3+) for public timestamping

---

## ❓ FAQ

### Q: Can't I just use git commits?
**A:** Git commits can be rewritten (force push, rebase). ProveChain creates immutable proofs. When combined with blockchain (v0.3), proofs are publicly verifiable and cannot be altered.

### Q: How is this different from code signing?
**A:** Code signing proves the publisher (you signed it). ProveChain proves the creation date (you wrote it on X date). Both are useful for different purposes.

### Q: Does this replace version control?
**A:** No! ProveChain complements Git. Use Git for collaboration and version history. Use ProveChain for proof of authorship and IP protection.

### Q: What if someone copies my proof file?
**A:** The proof file only proves that those file hashes existed at that timestamp. Without the actual source code, the proof is useless. In v0.3, blockchain timestamps will provide public verification.

### Q: How do I add this to .gitignore?
```bash
echo "provechain/" >> .gitignore
```

Proofs are local by default. You can optionally commit them if you want proofs in version control.

---

## 📄 License

MIT License - See LICENSE file for details.

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/Aramantos/provechain/issues)
- **Email:** john.doyle.mail@icloud.com

---

## 🙏 Acknowledgments

- Inspired by Git's content-addressable storage
- Hash algorithms from NIST standards
- Blockchain timestamping concept from [OpenTimestamps](https://opentimestamps.org/)

---

**ProveChain** - Because your code is your IP. Prove it. 🔒
