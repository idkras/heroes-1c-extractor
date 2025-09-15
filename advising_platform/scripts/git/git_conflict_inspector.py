#!/usr/bin/env python3
"""
Git Conflict Inspector - анализ и подготовка команд для разрешения конфликтов
Безопасная альтернатива автоматического разрешения конфликтов
"""

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

class GitConflictInspector:
    def __init__(self):
        self.project_root = Path.cwd()
        self.report_file = self.project_root / "git_conflict_report.md"
        
    def check_git_status_safe(self):
        """Безопасная проверка Git статуса через файловую систему"""
        git_dir = self.project_root / ".git"
        
        if not git_dir.exists():
            return {"error": "Not a git repository"}
        
        # Проверяем наличие merge состояния
        merge_head = git_dir / "MERGE_HEAD"
        merge_mode = git_dir / "MERGE_MODE"
        
        # Проверяем индекс
        index_file = git_dir / "index"
        
        # Проверяем HEAD
        head_file = git_dir / "HEAD"
        current_branch = "unknown"
        if head_file.exists():
            with open(head_file, 'r') as f:
                head_content = f.read().strip()
                if head_content.startswith("ref: refs/heads/"):
                    current_branch = head_content.replace("ref: refs/heads/", "")
        
        return {
            "is_git_repo": True,
            "current_branch": current_branch,
            "has_merge_head": merge_head.exists(),
            "has_merge_mode": merge_mode.exists(),
            "has_index": index_file.exists(),
            "merge_in_progress": merge_head.exists() and merge_mode.exists()
        }
    
    def analyze_recent_commits(self):
        """Анализ последних коммитов через лог файлы"""
        logs_dir = self.project_root / ".git" / "logs"
        analysis = {
            "head_log": [],
            "refs_log": [],
            "last_activity": None
        }
        
        # Анализируем HEAD log
        head_log = logs_dir / "HEAD"
        if head_log.exists():
            try:
                with open(head_log, 'r') as f:
                    lines = f.readlines()[-10:]  # Последние 10 записей
                    for line in lines:
                        parts = line.strip().split('\t')
                        if len(parts) >= 2:
                            analysis["head_log"].append({
                                "hash_from": parts[0].split()[0],
                                "hash_to": parts[0].split()[1],
                                "message": parts[1] if len(parts) > 1 else ""
                            })
            except Exception as e:
                analysis["head_log_error"] = str(e)
        
        return analysis
    
    def scan_for_conflict_files(self):
        """Сканирование файлов на наличие маркеров конфликтов"""
        conflict_markers = ["<<<<<<<", "=======", ">>>>>>>"]
        conflict_files = []
        
        # Сканируем основные директории проекта
        scan_dirs = [
            self.project_root,
            self.project_root / "advising_platform",
            self.project_root / "docs",
            self.project_root / "[standards .md]",
            self.project_root / "[todo · incidents]"
        ]
        
        for scan_dir in scan_dirs:
            if not scan_dir.exists():
                continue
                
            for file_path in scan_dir.rglob("*.md"):
                if ".git" in str(file_path):
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    has_conflicts = any(marker in content for marker in conflict_markers)
                    if has_conflicts:
                        # Подсчитываем количество маркеров
                        marker_counts = {}
                        for marker in conflict_markers:
                            marker_counts[marker] = content.count(marker)
                        
                        conflict_files.append({
                            "file": str(file_path.relative_to(self.project_root)),
                            "markers": marker_counts,
                            "size": len(content),
                            "lines": len(content.splitlines())
                        })
                        
                except Exception as e:
                    continue
        
        return conflict_files
    
    def analyze_remote_diff(self):
        """Анализ различий с remote через конфигурацию"""
        git_config = self.project_root / ".git" / "config"
        remote_info = {"remotes": [], "branches": []}
        
        if git_config.exists():
            try:
                with open(git_config, 'r') as f:
                    config_content = f.read()
                
                # Парсим remote URLs
                lines = config_content.splitlines()
                current_section = None
                current_remote = None
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('[remote '):
                        current_remote = line.replace('[remote "', '').replace('"]', '')
                        remote_info["remotes"].append({"name": current_remote, "url": None, "fetch": None})
                    elif line.startswith('url = ') and current_remote:
                        for remote in remote_info["remotes"]:
                            if remote["name"] == current_remote:
                                remote["url"] = line.replace("url = ", "")
                    elif line.startswith('fetch = ') and current_remote:
                        for remote in remote_info["remotes"]:
                            if remote["name"] == current_remote:
                                remote["fetch"] = line.replace("fetch = ", "")
                                
            except Exception as e:
                remote_info["error"] = str(e)
        
        return remote_info
    
    def generate_resolution_commands(self, git_status, conflict_files):
        """Генерация команд для разрешения конфликтов"""
        commands = []
        
        # Базовые команды проверки
        commands.append("# Проверка текущего состояния")
        commands.append("git status")
        commands.append("git log --oneline -10")
        commands.append("git remote -v")
        commands.append("")
        
        # Если есть merge в процессе
        if git_status.get("merge_in_progress"):
            commands.append("# Отмена текущего merge (если нужно)")
            commands.append("git merge --abort")
            commands.append("")
        
        # Команды для резолюции конфликтов
        if conflict_files:
            commands.append("# Разрешение конфликтов в файлах")
            for conflict_file in conflict_files:
                file_path = conflict_file["file"]
                commands.append(f"# Конфликт в файле: {file_path}")
                commands.append(f"git checkout --ours \"{file_path}\"  # Принять локальную версию")
                commands.append(f"# ИЛИ")
                commands.append(f"git checkout --theirs \"{file_path}\"  # Принять remote версию")
                commands.append(f"git add \"{file_path}\"")
                commands.append("")
        
        # Стандартная последовательность синхронизации
        commands.extend([
            "# Стандартная последовательность синхронизации",
            "git fetch origin",
            "git add .",
            "git commit -m \"resolve: sync conflicts with remote\"",
            "git pull origin main --rebase",
            "git push origin main",
            "",
            "# Если push отклонен:",
            "git push origin main --force-with-lease"
        ])
        
        return commands
    
    def create_detailed_report(self):
        """Создание детального отчета о состоянии Git"""
        print("Analyzing Git repository state...")
        
        # Собираем данные
        git_status = self.check_git_status_safe()
        commit_analysis = self.analyze_recent_commits()
        conflict_files = self.scan_for_conflict_files()
        remote_info = self.analyze_remote_diff()
        resolution_commands = self.generate_resolution_commands(git_status, conflict_files)
        
        # Генерируем отчет
        report = f"""# Git Conflict Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Repository Status

- **Is Git Repository:** {git_status.get('is_git_repo', False)}
- **Current Branch:** {git_status.get('current_branch', 'unknown')}
- **Merge in Progress:** {git_status.get('merge_in_progress', False)}
- **Has Index:** {git_status.get('has_index', False)}

## Conflict Analysis

### Files with Conflict Markers: {len(conflict_files)}

"""
        
        if conflict_files:
            report += "| File | <<<<<<< | ======= | >>>>>>> | Size |\n"
            report += "|------|---------|---------|---------|------|\n"
            for cf in conflict_files:
                markers = cf["markers"]
                report += f"| {cf['file']} | {markers.get('<<<<<<<', 0)} | {markers.get('=======', 0)} | {markers.get('>>>>>>>', 0)} | {cf['size']} |\n"
            report += "\n"
        else:
            report += "*No conflict markers found in scanned files.*\n\n"
        
        # Remote information
        report += "## Remote Configuration\n\n"
        if remote_info.get("remotes"):
            for remote in remote_info["remotes"]:
                report += f"- **{remote['name']}:** {remote.get('url', 'N/A')}\n"
        else:
            report += "*No remote repositories configured.*\n"
        
        report += f"\n## Recent Activity\n\n"
        if commit_analysis.get("head_log"):
            report += "### Last 5 HEAD Log Entries\n\n"
            for i, log_entry in enumerate(commit_analysis["head_log"][-5:]):
                report += f"{i+1}. `{log_entry['hash_to'][:8]}` - {log_entry.get('message', 'No message')}\n"
        
        # Resolution commands
        report += f"\n## Recommended Resolution Commands\n\n```bash\n"
        report += "\n".join(resolution_commands)
        report += "\n```\n"
        
        # Warnings and recommendations
        report += f"\n## Recommendations\n\n"
        
        if git_status.get("merge_in_progress"):
            report += "⚠️ **Active merge detected** - Complete or abort current merge before proceeding\n\n"
        
        if conflict_files:
            report += f"⚠️ **{len(conflict_files)} files have conflict markers** - Manual resolution required\n\n"
        
        if not remote_info.get("remotes"):
            report += "⚠️ **No remote repositories found** - Configure remote before syncing\n\n"
        
        report += """### Safe Resolution Steps:

1. **Backup current work:** Create backup of important files
2. **Abort current merge:** `git merge --abort` (if needed)
3. **Fetch latest:** `git fetch origin`
4. **Choose strategy:** Use `--ours` for local priority or `--theirs` for remote priority
5. **Resolve conflicts:** Edit files manually or use `git checkout --ours/--theirs`
6. **Commit resolution:** `git add .` then `git commit`
7. **Sync with remote:** `git push origin main`

### Force Push (Use with caution):
If normal push fails: `git push origin main --force-with-lease`
"""
        
        # Сохраняем отчет
        with open(self.report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return {
            "report_file": self.report_file,
            "git_status": git_status,
            "conflict_files": conflict_files,
            "remote_info": remote_info,
            "resolution_commands": resolution_commands
        }

def main():
    """Главная функция"""
    inspector = GitConflictInspector()
    
    print("Git Conflict Inspector")
    print("=" * 50)
    
    try:
        result = inspector.create_detailed_report()
        
        print(f"\n✅ Analysis complete!")
        print(f"📝 Report saved to: {result['report_file']}")
        print(f"🔍 Found {len(result['conflict_files'])} files with conflicts")
        
        if result['git_status'].get('merge_in_progress'):
            print("⚠️  Active merge detected - resolution required")
        
        print(f"\nNext steps:")
        print(f"1. Review the report: {result['report_file']}")
        print(f"2. Execute recommended commands manually")
        print(f"3. Test the resolution")
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())