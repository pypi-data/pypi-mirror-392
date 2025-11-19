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

- Manually add any repository path (even weird ones like %APPDATA%, client folders, external drives…)- Bulk sync (`add → commit → pull → push`) for selected or all repos
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
→ https://gitlab.com/user4302_Projects/coding/python/textual/goro/-/blob/main/CHANGELOG.md

### Project Homes

| Platform   | Purpose                                  | Link                                                                      |
|------------|-------------------------------------------|---------------------------------------------------------------------------|
| **GitLab** | Source of truth • Issues • MRs • CI/CD    | https://gitlab.com/user4302_Projects/coding/python/textual/goro           |
| **GitHub** | Mirror for discoverability & extra stars  | https://github.com/user4302/goro                              |

> **Please file issues and feature requests on GitLab** — that’s where I actively track and fix everything.  
> GitHub mirror is kept in sync automatically.

**License** — MIT  
**Built with** — Textual • Typer • uv • Hatch • Python 3.8+

⭐ **Star on whichever platform you prefer** — every star helps!  
(If you star both, I won’t complain 😉)