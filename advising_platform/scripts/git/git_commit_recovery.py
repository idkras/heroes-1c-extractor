#!/usr/bin/env python3
"""
Git Commit Recovery Tool - восстановление утерянных коммитов
Анализирует reflog, GitHub API и локальные ссылки для поиска потерянных коммитов
"""

import subprocess
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

class GitCommitRecovery:
    def __init__(self):
        self.project_root = Path.cwd()
        self.recovery_file = self.project_root / "git_recovery_analysis.md"
        self.github_api_base = "https://api.github.com/repos/idkras/heroes-advising-project"
        
    def analyze_reflog_history(self):
        """Анализ полной истории reflog для поиска утерянных коммитов"""
        try:
            # Получаем полный reflog
            result = subprocess.run(
                "git reflog show origin/main --all --date=iso",
                shell=True, capture_output=True, text=True, cwd=self.project_root
            )
            
            if result.returncode != 0:
                return {"error": "Cannot access reflog", "stderr": result.stderr}
            
            reflog_lines = result.stdout.strip().splitlines()
            
            # Парсим записи reflog
            commits = []
            for line in reflog_lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        commit_hash = parts[0]
                        # Извлекаем сообщение после символа ':'
                        if ':' in line:
                            message = line.split(':', 1)[1].strip()
                        else:
                            message = ' '.join(parts[1:])
                        
                        commits.append({
                            "hash": commit_hash,
                            "message": message,
                            "raw_line": line
                        })
            
            return {"commits": commits[:50], "total_found": len(commits)}
            
        except Exception as e:
            return {"error": str(e)}
    
    def check_github_events(self):
        """Проверка событий GitHub для поиска force push операций"""
        try:
            # GitHub Events API
            events_url = f"{self.github_api_base}/events"
            response = requests.get(events_url, timeout=10)
            
            if response.status_code != 200:
                return {"error": f"GitHub API error: {response.status_code}"}
            
            events = response.json()
            
            # Ищем push события за последние дни
            relevant_events = []
            cutoff_date = datetime.now() - timedelta(days=7)
            
            for event in events:
                if event.get("type") == "PushEvent":
                    event_date = datetime.strptime(
                        event["created_at"], "%Y-%m-%dT%H:%M:%SZ"
                    )
                    
                    if event_date >= cutoff_date:
                        push_data = event.get("payload", {})
                        relevant_events.append({
                            "date": event["created_at"],
                            "actor": event.get("actor", {}).get("login", "unknown"),
                            "commits": push_data.get("commits", []),
                            "ref": push_data.get("ref", ""),
                            "before": push_data.get("before", ""),
                            "after": push_data.get("after", "")
                        })
            
            return {"events": relevant_events}
            
        except Exception as e:
            return {"error": str(e)}
    
    def search_dangling_commits(self):
        """Поиск dangling (потерянных) коммитов в локальном репозитории"""
        try:
            # Ищем dangling commits
            result = subprocess.run(
                "git fsck --dangling",
                shell=True, capture_output=True, text=True, cwd=self.project_root
            )
            
            dangling_commits = []
            if result.stdout:
                lines = result.stdout.splitlines()
                for line in lines:
                    if "dangling commit" in line:
                        commit_hash = line.split()[-1]
                        
                        # Получаем информацию о commit
                        commit_info = subprocess.run(
                            f"git show --oneline -s {commit_hash}",
                            shell=True, capture_output=True, text=True, cwd=self.project_root
                        )
                        
                        if commit_info.returncode == 0:
                            dangling_commits.append({
                                "hash": commit_hash,
                                "info": commit_info.stdout.strip()
                            })
            
            return {"dangling_commits": dangling_commits}
            
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_github_branches(self):
        """Анализ всех веток GitHub для поиска коммитов"""
        try:
            branches_url = f"{self.github_api_base}/branches"
            response = requests.get(branches_url, timeout=10)
            
            if response.status_code != 200:
                return {"error": f"Cannot get branches: {response.status_code}"}
            
            branches = response.json()
            branch_info = []
            
            for branch in branches:
                branch_info.append({
                    "name": branch["name"],
                    "commit_sha": branch["commit"]["sha"],
                    "commit_url": branch["commit"]["url"]
                })
            
            return {"branches": branch_info}
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_commit_details(self, commit_hash):
        """Получение детальной информации о коммите"""
        try:
            result = subprocess.run(
                f"git show {commit_hash} --stat --oneline",
                shell=True, capture_output=True, text=True, cwd=self.project_root
            )
            
            if result.returncode == 0:
                return {"details": result.stdout, "exists": True}
            else:
                return {"exists": False, "error": result.stderr}
                
        except Exception as e:
            return {"error": str(e)}
    
    def generate_recovery_strategies(self, analysis_data):
        """Генерация стратегий восстановления на основе анализа"""
        strategies = []
        
        # Стратегия 1: Восстановление из reflog
        if analysis_data.get("reflog", {}).get("commits"):
            strategies.append({
                "name": "Reflog Recovery",
                "description": "Восстановление из локального reflog",
                "commands": [
                    "# Просмотр доступных коммитов в reflog",
                    "git reflog show origin/main --oneline -50",
                    "",
                    "# Создание восстановительной ветки из нужного коммита",
                    "git checkout -b recovery-branch <commit-hash>",
                    "",
                    "# Просмотр содержимого восстановленной ветки",
                    "git log --oneline -20",
                    "",
                    "# Объединение ценных изменений с main",
                    "git checkout main",
                    "git merge recovery-branch --no-ff"
                ],
                "risk": "low"
            })
        
        # Стратегия 2: GitHub Events восстановление
        if analysis_data.get("github_events", {}).get("events"):
            strategies.append({
                "name": "GitHub Events Recovery", 
                "description": "Восстановление через GitHub Events API",
                "commands": [
                    "# Получение информации о push событиях",
                    "# (выполнить через браузер или API клиент)",
                    f"curl -H 'Accept: application/vnd.github.v3+json' {self.github_api_base}/events",
                    "",
                    "# Поиск 'before' hash из force push события",
                    "# Попытка fetch этого коммита",
                    "git fetch origin <before-hash>",
                    "git checkout -b recovery-from-events <before-hash>"
                ],
                "risk": "medium"
            })
        
        # Стратегия 3: Dangling commits
        if analysis_data.get("dangling", {}).get("dangling_commits"):
            strategies.append({
                "name": "Dangling Commits Recovery",
                "description": "Восстановление из потерянных коммитов",
                "commands": [
                    "# Просмотр dangling коммитов",
                    "git fsck --dangling",
                    "",
                    "# Исследование каждого dangling коммита",
                    "git show <dangling-commit-hash>",
                    "",
                    "# Создание ветки из ценного dangling коммита",
                    "git checkout -b recovery-dangling <dangling-commit-hash>"
                ],
                "risk": "high"
            })
        
        # Стратегия 4: Branch анализ
        strategies.append({
            "name": "Branch Analysis Recovery",
            "description": "Анализ всех веток для поиска ценных коммитов",
            "commands": [
                "# Получение всех веток с remote",
                "git fetch --all",
                "git branch -r",
                "",
                "# Проверка каждой ветки на наличие ценных коммитов",
                "git log origin/<branch-name> --oneline -20",
                "",
                "# Cherry-pick ценных коммитов",
                "git checkout main",
                "git cherry-pick <valuable-commit-hash>"
            ],
            "risk": "low"
        })
        
        return strategies
    
    def create_recovery_report(self):
        """Создание полного отчета по восстановлению"""
        print("Analyzing recovery options...")
        
        # Собираем данные
        reflog_data = self.analyze_reflog_history()
        github_events = self.check_github_events()
        dangling_data = self.search_dangling_commits()
        branch_data = self.analyze_github_branches()
        
        analysis_data = {
            "reflog": reflog_data,
            "github_events": github_events,
            "dangling": dangling_data,
            "branches": branch_data
        }
        
        # Генерируем стратегии
        strategies = self.generate_recovery_strategies(analysis_data)
        
        # Создаем отчет
        report = f"""# Git Commit Recovery Analysis

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Target:** Recover 19 lost commits from force push operation

## Analysis Results

### Reflog Analysis
"""
        
        if reflog_data.get("commits"):
            report += f"✅ Found {len(reflog_data['commits'])} commits in reflog\n\n"
            report += "**Recent commits:**\n"
            for i, commit in enumerate(reflog_data["commits"][:10]):
                report += f"{i+1}. `{commit['hash'][:8]}` - {commit['message']}\n"
        else:
            report += "❌ No commits found in reflog\n"
        
        report += f"\n### GitHub Events Analysis\n"
        
        if github_events.get("events"):
            report += f"✅ Found {len(github_events['events'])} recent push events\n\n"
            for event in github_events["events"][:5]:
                report += f"- **{event['date']}** by {event['actor']}\n"
                report += f"  - Before: `{event['before'][:8]}`\n"
                report += f"  - After: `{event['after'][:8]}`\n"
                report += f"  - Commits: {len(event['commits'])}\n\n"
        else:
            report += "❌ No recent push events found\n"
        
        report += f"\n### Dangling Commits Analysis\n"
        
        if dangling_data.get("dangling_commits"):
            report += f"✅ Found {len(dangling_data['dangling_commits'])} dangling commits\n\n"
            for commit in dangling_data["dangling_commits"][:5]:
                report += f"- `{commit['hash'][:8]}` - {commit['info']}\n"
        else:
            report += "❌ No dangling commits found\n"
        
        report += f"\n### Branch Analysis\n"
        
        if branch_data.get("branches"):
            report += f"✅ Found {len(branch_data['branches'])} branches\n\n"
            for branch in branch_data["branches"]:
                report += f"- **{branch['name']}**: `{branch['commit_sha'][:8]}`\n"
        else:
            report += "❌ Cannot access branch information\n"
        
        report += f"\n## Recovery Strategies\n\n"
        
        for i, strategy in enumerate(strategies, 1):
            report += f"### Strategy {i}: {strategy['name']}\n"
            report += f"**Risk Level:** {strategy['risk'].upper()}\n"
            report += f"**Description:** {strategy['description']}\n\n"
            report += f"**Commands:**\n```bash\n"
            report += "\n".join(strategy['commands'])
            report += "\n```\n\n"
        
        report += f"""## Recommended Approach

1. **Start with Strategy 1 (Reflog)** - lowest risk, highest success rate
2. **Check GitHub Web Interface** - look for force push notifications
3. **Try Strategy 4 (Branch Analysis)** - examine all remote branches
4. **Last resort: Strategy 3 (Dangling)** - if local commits exist

## Manual Steps

### Immediate Actions:
1. Create backup of current state: `git branch backup-current-state`
2. Explore reflog thoroughly: `git reflog show origin/main --all --oneline -100`
3. Check GitHub notifications for force push alerts

### Value Extraction:
1. Focus on commits with substantial changes (>10 files)
2. Look for feature commits, not just fixes
3. Prioritize recent commits (last 7 days)
4. Extract unique content, not duplicate work

## Emergency Contact

If automated recovery fails:
- Check GitHub Support for repository recovery options
- Contact repository collaborators for local copies
- Review local `.git/logs/` directory manually

---
**Next Steps:** Execute Strategy 1 commands to begin recovery process.
"""
        
        # Сохраняем отчет
        with open(self.recovery_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return {
            "report_file": self.recovery_file,
            "analysis_data": analysis_data,
            "strategies": strategies,
            "summary": {
                "reflog_commits": len(reflog_data.get("commits", [])),
                "github_events": len(github_events.get("events", [])),
                "dangling_commits": len(dangling_data.get("dangling_commits", [])),
                "branches": len(branch_data.get("branches", []))
            }
        }

def main():
    recovery = GitCommitRecovery()
    
    print("Git Commit Recovery Tool")
    print("=" * 40)
    print("Analyzing recovery options for lost commits...")
    
    try:
        result = recovery.create_recovery_report()
        
        print(f"\n✅ Recovery analysis complete!")
        print(f"📝 Report: {result['report_file']}")
        print(f"\nFound recovery options:")
        print(f"- Reflog commits: {result['summary']['reflog_commits']}")
        print(f"- GitHub events: {result['summary']['github_events']}")
        print(f"- Dangling commits: {result['summary']['dangling_commits']}")
        print(f"- Remote branches: {result['summary']['branches']}")
        
        if result['summary']['reflog_commits'] > 0:
            print(f"\n🎯 Recommended: Start with reflog recovery (Strategy 1)")
        
        print(f"\nNext: Review {result['report_file']} and execute recovery commands")
        
    except Exception as e:
        print(f"❌ Recovery analysis failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())