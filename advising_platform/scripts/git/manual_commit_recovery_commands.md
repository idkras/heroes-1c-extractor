# Manual Commit Recovery Commands

**Цель:** Восстановить 19 утерянных коммитов после force push

## Быстрая диагностика

Выполните эти команды по порядку:

```bash
# 1. Проверка текущего состояния
git status
git log --oneline -10

# 2. Анализ reflog для поиска утерянных коммитов
git reflog show origin/main --oneline -30

# 3. Поиск всех доступных веток
git branch -a
git fetch --all
git branch -r

# 4. Проверка dangling коммитов
git fsck --dangling | grep commit
```

## Стратегия восстановления

### Шаг 1: Создание резервной копии
```bash
git branch backup-current-$(date +%Y%m%d-%H%M%S)
```

### Шаг 2: Исследование reflog
```bash
# Посмотрите на вывод этой команды - ищите коммиты до force push
git reflog show origin/main --oneline -50

# Найдите коммит с хэшем, который был ДО вашего force push
# Создайте восстановительную ветку
git checkout -b recovery-attempt <commit-hash-before-force-push>

# Проверьте что восстановили
git log --oneline -20
git diff main recovery-attempt --name-only
```

### Шаг 3: Анализ веток
```bash
# Проверьте каждую remote ветку на ценный контент
git log origin/main --oneline -30
git log HEAD~73..HEAD --oneline  # Ваши 73 коммита

# Если есть другие ветки, проверьте их тоже
git branch -r | while read branch; do
  echo "=== Checking $branch ==="
  git log $branch --oneline -10
done
```

### Шаг 4: Поиск в dangling коммитах
```bash
# Получите список dangling коммитов
git fsck --dangling --no-reflogs | grep commit | cut -d' ' -f3 > dangling_commits.txt

# Проверьте каждый dangling коммит
cat dangling_commits.txt | head -10 | while read commit; do
  echo "=== Commit $commit ==="
  git show --oneline -s $commit
  git show $commit --stat
done
```

## Восстановление ценного контента

### Если нашли ценные коммиты в recovery-attempt:
```bash
git checkout main
git merge recovery-attempt --no-ff -m "recover: restore lost commits from reflog"
```

### Если нужно восстановить отдельные коммиты:
```bash
git checkout main
git cherry-pick <valuable-commit-hash-1>
git cherry-pick <valuable-commit-hash-2>
```

### Если нужно восстановить отдельные файлы:
```bash
git checkout main
git checkout <commit-with-valuable-file> -- path/to/file.ext
git add path/to/file.ext
git commit -m "recover: restore valuable file from lost commits"
```

## Альтернативные источники

### GitHub Web Interface
1. Зайдите на https://github.com/idkras/heroes-advising-project
2. Проверьте вкладку "Insights" → "Network" 
3. Ищите orphaned commits или ветки
4. Проверьте уведомления о force push

### Локальные копии
Если у вас есть другие клоны репозитория на других машинах:
```bash
# На другой машине
git fetch origin
git log origin/main --oneline -50
git push origin old-main-backup:refs/heads/recovery-from-other-machine
```

## Проверка результата

После восстановления:
```bash
git status
git log --oneline -20
git diff HEAD~10..HEAD --stat  # Посмотрите что восстановлено
```

## Экстренный план

Если ничего не помогает:
1. Проверьте `.git/logs/refs/remotes/origin/main` вручную
2. Обратитесь к GitHub Support 
3. Поищите локальные backup файлы проекта
4. Восстановите из памяти самые критичные изменения

## Практический пример

```bash
# Пример выполнения
git reflog show origin/main --oneline -20
# Найдите что-то вроде:
# abc1234 origin/main@{5}: update by push (before your force push)

git checkout -b recovery abc1234
git log --oneline -15
# Если видите потерянные коммиты:

git checkout main  
git merge recovery --no-ff
git branch -d recovery
```

**Важно:** Ищите коммиты с датами ДО вашего force push и содержательными сообщениями commit'ов.