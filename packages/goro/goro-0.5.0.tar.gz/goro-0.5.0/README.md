# Goro — Git Ops Repo Orchestrator (v0.5.0)

**Goro** (Git Ops Repo Orchestrator) is a blazing-fast **Textual TUI** for managing and syncing **dozens of Git repositories at once** — think *lazygit, but for your entire workspace*.

![Goro screenshot/demo](https://i.ibb.co/CKQYvzCp/goro.png)  
<!-- *TODO: (replace the link above with your own screenshot or short GIF)* -->

### Install

```bash
pip install goro          # or
uv tool install goro
```

### Run

```bash
goro                      # launches the interactive TUI instantly
```

### Core Features

- Auto-discover all Git repositories in a folder
- Bulk sync (`add → commit → pull → push`) for selected or all repos
- Live status grid with branch, ahead/behind, and dirty indicators
- Add, edit, rename, and remove repositories interactively
- Real-time command output with progress bars
- Full CLI fallback (`goro sync-all`, `goro status my-repo`, etc.)
- Cross-platform (Windows • macOS • Linux)

### TUI Quick Keys

| Key       | Action                     |
|-----------|----------------------------|
| `a`       | Add repository             |
| `s` / `S` | Sync selected • all repos  |
| `t`       | Show detailed git status   |
| `F2`      | Edit / rename repository   |
| `c`       | Clear logs                 |
| `q`       | Quit                       |

### Full CLI Reference & Changelog
→ https://gitlab.com/user4302_Projects/coding/python/textual/goro

**License** — MIT  
**Built with** — Textual • Python 3.8+

Star on GitHub if you like it! ★