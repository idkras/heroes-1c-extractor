#!/usr/bin/env python3
"""
Git Conflict Resolver - автоматическое разрешение Git конфликтов
Решает проблему: merge конфликты блокируют синхронизацию с GitHub
"""

import os
import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path

class GitConflictResolver:
    def __init__(self):
        self.project_root = Path.cwd()
        self.backup_dir = self.project_root / "backups" / f"git_conflict_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.log_file = self.project_root / "git_conflict_resolution.log"
        
    def log(self, message):
        """Логирование операций"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')
    
    def run_git_command(self, command, capture_output=True):
        """Выполнение Git команды с логированием"""
        self.log(f"Executing: git {command}")
        try:
            result = subprocess.run(
                f"git {command}",
                shell=True,
                capture_output=capture_output,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode != 0:
                self.log(f"Error: {result.stderr}")
                return None, result.stderr
            
            if capture_output:
                self.log(f"Output: {result.stdout.strip()}")
            
            return result.stdout.strip() if capture_output else "Success", None
        except Exception as e:
            self.log(f"Exception: {str(e)}")
            return None, str(e)
    
    def check_git_status(self):
        """Проверка текущего статуса Git"""
        self.log("Checking Git status...")
        
        status, error = self.run_git_command("status --porcelain")
        if error:
            return False, "Cannot check Git status"
        
        # Проверяем наличие изменений
        if status:
            self.log(f"Found {len(status.splitlines())} changed files")
        
        # Проверяем статус merge
        merge_status, _ = self.run_git_command("status")
        is_merging = "You have unmerged paths" in (merge_status or "")
        
        return True, {
            "changed_files": status.splitlines() if status else [],
            "is_merging": is_merging,
            "clean": not bool(status)
        }
    
    def create_backup(self):
        """Создание бэкапа текущего состояния"""
        self.log("Creating backup of current state...")
        
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Бэкап всех измененных файлов
            status_result, error = self.run_git_command("status --porcelain")
            if status_result:
                for line in status_result.splitlines():
                    if len(line) > 3:
                        file_path = line[3:].strip()
                        source_file = self.project_root / file_path
                        
                        if source_file.exists():
                            backup_file = self.backup_dir / file_path
                            backup_file.parent.mkdir(parents=True, exist_ok=True)
                            
                            import shutil
                            shutil.copy2(source_file, backup_file)
                            self.log(f"Backed up: {file_path}")
            
            self.log(f"Backup created at: {self.backup_dir}")
            return True
        except Exception as e:
            self.log(f"Backup failed: {str(e)}")
            return False
    
    def handle_merge_conflicts(self):
        """Обработка merge конфликтов с выбором стратегии"""
        self.log("Handling merge conflicts with strategy selection...")
        
        # Проверяем состояние merge
        merge_head = self.project_root / ".git" / "MERGE_HEAD"
        if not merge_head.exists():
            self.log("No active merge found")
            return True
        
        # Отменяем текущий merge
        self.log("Aborting current merge...")
        abort_result, abort_error = self.run_git_command("merge --abort")
        if abort_error:
            self.log(f"Merge abort failed: {abort_error}")
        
        # Используем стратегию "ours" для приоритета локальных изменений
        self.log("Attempting merge with 'ours' strategy...")
        merge_result, merge_error = self.run_git_command("merge origin/main -X ours")
        
        if merge_error and "conflict" in merge_error.lower():
            # Если все еще есть конфликты, разрешаем вручную
            return self.resolve_remaining_conflicts()
        
        return merge_error is None
    
    def resolve_remaining_conflicts(self):
        """Разрешение оставшихся конфликтов"""
        self.log("Resolving remaining conflicts manually...")
        
        # Получаем список конфликтующих файлов
        conflicts, error = self.run_git_command("diff --name-only --diff-filter=U")
        if error:
            self.log(f"Cannot get conflict list: {error}")
            return False
        
        if not conflicts:
            self.log("No conflicts found")
            return True
        
        conflict_files = conflicts.splitlines()
        self.log(f"Found {len(conflict_files)} conflicted files")
        
        for file_path in conflict_files:
            self.log(f"Resolving conflicts in: {file_path}")
            
            # Принимаем локальную версию для каждого конфликтующего файла
            checkout_result, checkout_error = self.run_git_command(f"checkout --ours \"{file_path}\"")
            if checkout_error:
                self.log(f"Failed to checkout ours for {file_path}: {checkout_error}")
                continue
            
            # Добавляем файл в staging
            add_result, add_error = self.run_git_command(f"add \"{file_path}\"")
            if add_error:
                self.log(f"Failed to add {file_path}: {add_error}")
                continue
            
            self.log(f"Resolved and staged: {file_path}")
        
        return True
    
    def commit_changes(self):
        """Коммит всех изменений"""
        self.log("Committing all changes...")
        
        # Добавляем все изменения
        add_all_result, add_all_error = self.run_git_command("add .")
        if add_all_error:
            self.log(f"Failed to add all changes: {add_all_error}")
            return False
        
        # Проверяем, есть ли что коммитить
        status, _ = self.run_git_command("status --porcelain")
        if not status:
            self.log("No changes to commit")
            return True
        
        # Создаем коммит
        commit_message = f"resolve: sync with remote and resolve conflicts - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        commit_result, commit_error = self.run_git_command(f"commit -m \"{commit_message}\"")
        if commit_error:
            self.log(f"Commit failed: {commit_error}")
            return False
        
        self.log("Changes committed successfully")
        return True
    
    def force_sync_with_remote(self):
        """Принудительная синхронизация с удаленным репозиторием"""
        self.log("Force syncing with remote repository...")
        
        # Fetch последние изменения
        fetch_result, fetch_error = self.run_git_command("fetch origin")
        if fetch_error:
            self.log(f"Fetch failed: {fetch_error}")
            return False
        
        # Пытаемся push
        push_result, push_error = self.run_git_command("push origin main")
        if push_error:
            if "non-fast-forward" in push_error or "rejected" in push_error:
                self.log("Push rejected, attempting force push with lease...")
                force_push_result, force_push_error = self.run_git_command("push origin main --force-with-lease")
                if force_push_error:
                    self.log(f"Force push failed: {force_push_error}")
                    return False
                self.log("Force push successful")
            else:
                self.log(f"Push failed: {push_error}")
                return False
        else:
            self.log("Push successful")
        
        return True
    
    def resolve_all_conflicts(self):
        """Основной метод для разрешения всех конфликтов"""
        self.log("Starting comprehensive Git conflict resolution...")
        
        # 1. Проверяем статус
        success, status_info = self.check_git_status()
        if not success:
            self.log("Cannot proceed: Git status check failed")
            return False
        
        self.log(f"Git status: {status_info}")
        
        # 2. Создаем бэкап
        if not self.create_backup():
            self.log("Warning: Backup creation failed, continuing anyway...")
        
        # 3. Fetch изменения с remote
        self.log("Fetching remote changes...")
        fetch_result, fetch_error = self.run_git_command("fetch origin")
        if fetch_error:
            self.log(f"Fetch failed: {fetch_error}")
        
        # 4. Обрабатываем merge конфликты
        if not self.handle_merge_conflicts():
            self.log("Failed to handle merge conflicts")
            return False
        
        # 5. Коммитим все изменения
        if not self.commit_changes():
            self.log("Failed to commit changes")
            return False
        
        # 6. Синхронизируемся с remote
        if not self.force_sync_with_remote():
            self.log("Failed to sync with remote")
            return False
        
        self.log("Git conflict resolution completed successfully!")
        return True

def main():
    """Основная функция"""
    resolver = GitConflictResolver()
    
    print("Git Conflict Resolver")
    print("=" * 50)
    print("Resolving conflicts with GitHub repository...")
    
    if resolver.resolve_all_conflicts():
        print("\n✅ All conflicts resolved successfully!")
        print(f"📁 Backup created at: {resolver.backup_dir}")
        print(f"📝 Log file: {resolver.log_file}")
        print("\nRepository is now synced with GitHub.")
    else:
        print("\n❌ Conflict resolution failed!")
        print(f"📝 Check log file: {resolver.log_file}")
        print(f"📁 Backup available at: {resolver.backup_dir}")
        sys.exit(1)

if __name__ == "__main__":
    main()