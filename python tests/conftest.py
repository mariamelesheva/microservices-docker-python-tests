import pytest
import subprocess
import time
import requests
import os


@pytest.fixture(scope="session")
def full_app():
    """Поднимает всё приложение через docker-compose"""

    project_dir = os.path.dirname(os.path.dirname(__file__))

    print("\n🐳 Поднимаем контейнеры...")
    # 1. Поднимаем контейнеры
    subprocess.run(
        ["docker-compose", "up", "-d", "--build"],
        cwd=project_dir,
        check=True
    )

    # 2. Ждём, пока все сервисы запустятся (увеличиваем таймаут)
    wait_for_services()

    print("✅ Все сервисы готовы!")

    yield

    # 3. После тестов — останавливаем и чистим
    print("\n🧹 Останавливаем контейнеры...")
    subprocess.run(
        ["docker-compose", "down", "-v"],
        cwd=project_dir,
        check=True
    )
    print("✅ Очистка завершена")


def wait_for_services():
    """Ждёт, пока все сервисы будут готовы принимать запросы"""
    services = {
        "articles": "http://localhost:3000/api/articles",
        "users": "http://localhost:3002/api/users",
        "auth": "http://localhost:3003/api/auth",
        "rabbitmq": "http://localhost:15672"
    }

    # Увеличиваем количество попыток до 60 (2 минуты)
    max_attempts = 60
    for attempt in range(max_attempts):
        all_ready = True
        for name, url in services.items():
            try:
                response = requests.get(url, timeout=5)  # увеличиваем timeout до 5 секунд
                if response.status_code >= 500:
                    all_ready = False
                    print(f"⏳ {name} вернул {response.status_code}, ждём... ({attempt + 1}/{max_attempts})")
                else:
                    print(f"✅ {name} готов (статус {response.status_code})")
            except requests.exceptions.ConnectionError:
                all_ready = False
                print(f"⏳ {name} ещё не отвечает... ({attempt + 1}/{max_attempts})")
            except Exception as e:
                all_ready = False
                print(f"⏳ {name} ошибка: {type(e).__name__} ({attempt + 1}/{max_attempts})")

        if all_ready:
            print("✅ Все сервисы готовы!")
            return

        time.sleep(2)  # ждём 2 секунды между попытками

    # Если не дождались, покажем последние логи для диагностики
    print("\n❌ Таймаут! Последние логи контейнеров:")
    subprocess.run(["docker-compose", "logs", "--tail=20"])

    raise Exception("❌ Сервисы не запустились за отведённое время")


@pytest.fixture(scope="session")
def auth_token(full_app):
    """Получает токен администратора"""
    response = requests.post(
        "http://localhost:3003/api/auth",
        json={"emailAddress": "rithinch@gmail.com", "password": "Testing0*"}
    )
    assert response.status_code == 200, f"Auth failed: {response.text}"
    return response.json()["token"]