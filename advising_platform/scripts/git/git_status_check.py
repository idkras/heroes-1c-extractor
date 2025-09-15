#!/usr/bin/env python3
"""
Quick Git Status Checker - быстрая проверка состояния Git репозитория
"""

import os
from pathlib import Path
from datetime import datetime

def check_git_files():
    """Проверка Git файлов и состояния"""
    project_root = Path.cwd()
    git_dir = project_root / ".git"
    
    if not git_dir.exists():
        return {"status": "Not a git repository"}
    
    status = {
        "git_dir_exists": True,
        "files": {},
        "merge_status": "clean"
    }
    
    # Проверяем ключевые Git файлы
    git_files = [
        "HEAD", "index", "MERGE_HEAD", "MERGE_MODE", 
        "ORIG_HEAD", "FETCH_HEAD", "config"
    ]
    
    for file_name in git_files:
        file_path = git_dir / file_name
        if file_path.exists():
            try:
                if file_name == "HEAD":
                    with open(file_path, 'r') as f:
                        status["files"][file_name] = f.read().strip()
                elif file_name == "config":
                    with open(file_path, 'r') as f:
                        config_content = f.read()
                        # Извлекаем remote URL
                        for line in config_content.splitlines():
                            if "url = " in line and "github" in line:
                                status["remote_url"] = line.strip().replace("url = ", "")
                                break
                else:
                    status["files"][file_name] = "exists"
            except:
                status["files"][file_name] = "exists (unreadable)"
        else:
            status["files"][file_name] = "missing"
    
    # Определяем статус merge
    if status["files"].get("MERGE_HEAD") == "exists":
        status["merge_status"] = "merge_in_progress"
    elif status["files"].get("ORIG_HEAD") == "exists":
        status["merge_status"] = "recent_merge"
    
    return status

def generate_manual_commands():
    """Генерация команд для ручного выполнения"""
    commands = [
        "# Проверка текущего состояния Git",
        "git status",
        "git log --oneline -5",
        "git remote -v",
        "",
        "# Если есть активный merge - отменить его",
        "git merge --abort",
        "",
        "# Базовая синхронизация",
        "git fetch origin",
        "git add .",
        "git commit -m \"sync: resolve conflicts $(date)\"",
        "",
        "# Попытка push",
        "git push origin main",
        "",
        "# Если push отклонен - принудительный с защитой",
        "git push origin main --force-with-lease",
        "",
        "# Альтернативная стратегия - reset к remote",
        "git fetch origin",
        "git reset --hard origin/main",
        "git push origin main"
    ]
    return commands

def create_resolution_guide():
    """Создание руководства по разрешению конфликтов"""
    git_status = check_git_files()
    commands = generate_manual_commands()
    
    guide = f"""# Git Conflict Resolution Guide

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Current Repository Status

- **Git Directory:** {'✅ Present' if git_status.get('git_dir_exists') else '❌ Missing'}
- **Merge Status:** {git_status.get('merge_status', 'unknown')}
- **Remote URL:** {git_status.get('remote_url', 'Not found')}

### Git Files Status:
"""
    
    for file_name, status in git_status.get("files", {}).items():
        if status == "exists":
            guide += f"- **{file_name}:** ✅ Present\n"
        elif status == "missing":
            guide += f"- **{file_name}:** ❌ Missing\n"
        else:
            guide += f"- **{file_name}:** {status}\n"
    
    guide += f"""

## Problem Analysis

Based on your screenshot, you have:
- **19 commits to pull** from remote
- **72 commits to push** to remote
- **Warning:** "pulling will start a merge with conflicts"
- **Error:** "Can't push: unpulled changes must be merged first"

This indicates a diverged branch where both local and remote have unique commits.

## Recommended Solution Steps

Execute these commands in your terminal:

```bash
{chr(10).join(commands)}
```

## Strategy Explanation

### Option 1: Merge Strategy (Safer)
1. Fetch remote changes
2. Commit local changes
3. Pull with merge (resolve conflicts manually)
4. Push merged result

### Option 2: Rebase Strategy (Cleaner history)
```bash
git fetch origin
git rebase origin/main
# Resolve conflicts if any
git push origin main
```

### Option 3: Force Strategy (Use with caution)
```bash
git fetch origin
git reset --hard origin/main  # LOSES LOCAL CHANGES
git push origin main
```

## Conflict Resolution Tips

1. **Before starting:** Create backup of important files
2. **If merge conflicts occur:** 
   - Edit files to remove conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
   - Use `git add <file>` after resolving each file
   - Continue with `git commit`
3. **For binary conflicts:** Choose one version with `git checkout --ours` or `git checkout --theirs`

## Emergency Backup Commands

```bash
# Create backup branch
git checkout -b backup-$(date +%Y%m%d-%H%M%S)
git checkout main

# Stash changes
git stash push -m "backup before conflict resolution"
```

## Verification Steps

After resolution:
```bash
git status  # Should show "nothing to commit, working tree clean"
git log --oneline -10  # Verify commit history
git remote show origin  # Check remote connection
```

---
**Next Steps:** Execute the recommended commands manually in your terminal.
"""
    
    return guide

def main():
    print("Git Conflict Analysis")
    print("=" * 40)
    
    guide = create_resolution_guide()
    
    # Сохраняем руководство
    guide_file = Path("git_resolution_guide.md")
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print(f"Resolution guide created: {guide_file}")
    print("\nQuick status check completed.")
    print("Review the guide file for detailed instructions.")

if __name__ == "__main__":
    main()