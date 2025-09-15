#!/usr/bin/env python3
"""
Quick Commit Recovery - быстрое восстановление утерянных коммитов
"""

import subprocess
from pathlib import Path
from datetime import datetime

def run_git_command(command):
    """Выполнение Git команды"""
    try:
        result = subprocess.run(
            f"git {command}",
            shell=True, capture_output=True, text=True, cwd=Path.cwd()
        )
        return result.stdout.strip(), result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def analyze_reflog():
    """Анализ reflog для поиска утерянных коммитов"""
    print("Checking reflog for lost commits...")
    
    # Получаем расширенный reflog
    stdout, stderr, code = run_git_command("reflog show origin/main --oneline -50")
    
    if code != 0:
        print(f"Cannot access reflog: {stderr}")
        return []
    
    commits = []
    for line in stdout.splitlines():
        if line.strip():
            parts = line.split(' ', 1)
            if len(parts) >= 2:
                hash_part = parts[0]
                message = parts[1] if len(parts) > 1 else "No message"
                commits.append({"hash": hash_part, "message": message})
    
    return commits

def check_dangling_commits():
    """Проверка dangling коммитов"""
    print("Checking for dangling commits...")
    
    stdout, stderr, code = run_git_command("fsck --dangling --no-reflogs")
    
    dangling = []
    if stdout:
        for line in stdout.splitlines():
            if "dangling commit" in line:
                commit_hash = line.split()[-1]
                
                # Получаем информацию о коммите
                commit_stdout, _, commit_code = run_git_command(f"show --oneline -s {commit_hash}")
                if commit_code == 0:
                    dangling.append({"hash": commit_hash, "info": commit_stdout})
    
    return dangling

def get_all_branches():
    """Получение всех веток"""
    print("Fetching all branches...")
    
    # Fetch all
    run_git_command("fetch --all")
    
    # Получаем список remote веток
    stdout, stderr, code = run_git_command("branch -r")
    
    branches = []
    if code == 0:
        for line in stdout.splitlines():
            branch = line.strip()
            if branch and not "->" in branch:
                branches.append(branch)
    
    return branches

def create_recovery_guide():
    """Создание руководства по восстановлению"""
    print("Creating recovery guide...")
    
    # Анализируем источники восстановления
    reflog_commits = analyze_reflog()
    dangling_commits = check_dangling_commits()
    branches = get_all_branches()
    
    guide = f"""# Quick Commit Recovery Guide

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Analysis Results

### Reflog Commits Found: {len(reflog_commits)}
"""
    
    if reflog_commits:
        guide += "\nRecent commits in reflog:\n"
        for i, commit in enumerate(reflog_commits[:15]):
            guide += f"{i+1:2d}. `{commit['hash'][:12]}` {commit['message']}\n"
    else:
        guide += "No commits found in reflog.\n"
    
    guide += f"\n### Dangling Commits Found: {len(dangling_commits)}\n"
    
    if dangling_commits:
        guide += "\nDangling commits:\n"
        for commit in dangling_commits:
            guide += f"- `{commit['hash'][:12]}` {commit['info']}\n"
    else:
        guide += "No dangling commits found.\n"
    
    guide += f"\n### Remote Branches Found: {len(branches)}\n"
    
    if branches:
        for branch in branches[:10]:
            guide += f"- {branch}\n"
    
    guide += """

## Recovery Strategies

### Strategy 1: Reflog Recovery (Recommended)
Execute these commands:

```bash
# View detailed reflog
git reflog show origin/main --oneline -50

# Create recovery branch from promising commit
git checkout -b recovery-branch <commit-hash>

# Check what's in the recovery branch
git log --oneline -20
git diff main recovery-branch --stat

# If valuable, merge to main
git checkout main
git merge recovery-branch --no-ff -m "recover: valuable commits from reflog"
```

### Strategy 2: Examine All Remote Branches
```bash
# Check each remote branch for valuable commits
"""
    
    for branch in branches[:5]:
        guide += f"""
# Check {branch}
git log {branch} --oneline -20
git diff main {branch} --stat
"""
    
    guide += """
# Cherry-pick valuable commits
git cherry-pick <valuable-commit-hash>
```

### Strategy 3: Dangling Commits
```bash
# Examine each dangling commit
"""
    
    for commit in dangling_commits[:3]:
        guide += f"""
git show {commit['hash'][:12]} --stat
"""
    
    guide += """
# Create branch from valuable dangling commit
git checkout -b recovery-dangling <dangling-commit-hash>
```

## Quick Recovery Commands

Based on the analysis, try these commands in order:

```bash
# 1. Backup current state
git branch backup-before-recovery

# 2. Look for the most recent valuable commits in reflog
git reflog show origin/main --oneline -20

# 3. Create recovery branch from suspicious commit
# (Look for commits from before the force push)
git checkout -b recovery-attempt <commit-hash-from-reflog>

# 4. Check what you recovered
git log --oneline -30
git diff main recovery-attempt --name-only

# 5. If valuable content found, merge it
git checkout main
git merge recovery-attempt --no-ff

# 6. Clean up
git branch -d recovery-attempt
```

## What to Look For

When examining recovered commits, prioritize:
- Recent feature additions
- Configuration changes
- New files or major modifications
- Commits with meaningful commit messages
- Commits from the timeframe when you lost data

## Success Indicators

You've successfully recovered if you find:
- Files that don't exist in current main
- Different versions of existing files with valuable changes
- Commit messages that reference lost work
- Recent timestamps matching your memory of lost work
"""
    
    # Сохраняем руководство
    guide_file = Path("quick_recovery_guide.md")
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    return {
        "guide_file": guide_file,
        "reflog_count": len(reflog_commits),
        "dangling_count": len(dangling_commits),
        "branches_count": len(branches),
        "first_reflog_hash": reflog_commits[0]["hash"] if reflog_commits else None
    }

def main():
    print("Quick Commit Recovery Tool")
    print("=" * 30)
    
    result = create_recovery_guide()
    
    print(f"\nRecovery analysis complete!")
    print(f"Guide saved to: {result['guide_file']}")
    print(f"Found: {result['reflog_count']} reflog commits, {result['dangling_count']} dangling commits")
    
    if result['first_reflog_hash']:
        print(f"\nQuick start command:")
        print(f"git checkout -b recovery-check {result['first_reflog_hash']}")
        print(f"git log --oneline -10")
    
    return 0

if __name__ == "__main__":
    exit(main())