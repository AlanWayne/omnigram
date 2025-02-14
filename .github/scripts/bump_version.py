import os
import tomllib
import tomli_w

# Заголовок PR передаётся через переменную окружения
pr_title = os.getenv("PR_TITLE", "").lower()

# Читаем pyproject.toml
with open("pyproject.toml", "rb") as f:
    config = tomllib.load(f)

# Получаем текущую версию
version = config["project"]["version"]
major, minor, patch = map(int, version.split("."))

# Определяем, какую часть версии обновлять
if pr_title.startswith("feat/"):
    minor += 1
    patch = 0  # Сбрасываем patch при увеличении minor
elif pr_title.startswith("fix/"):
    patch += 1
elif pr_title.startswith("release/"):
    major += 1
    minor = 0  # Сбрасываем minor и patch при major
    patch = 0
else:
    print(
        f"❌ PR '{pr_title}' не содержит feat/, fix/, major/ - версия не "
        f"изменена."
    )
    exit(0)  # Прерываем выполнение, если PR не требует изменения версии

# Формируем новую версию
new_version = f"{major}.{minor}.{patch}"
config["project"]["version"] = new_version

# Записываем новую версию обратно в pyproject.toml
with open("pyproject.toml", "wb") as f:
    tomli_w.dump(config, f)

print(f"✅ Версия обновлена: {version} → {new_version}")
