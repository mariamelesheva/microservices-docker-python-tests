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
    subprocess.run(
        ["docker-compose", "up", "-d", "--build"],
        cwd=project_dir,
        check=True
    )

    wait_for_services()

    # Создаём пользователя
    create_test_user()

    print("✅ Все сервисы готовы!")
    yield

    print("\n🧹 Останавливаем контейнеры...")
    subprocess.run(["docker-compose", "down", "-v"], cwd=project_dir, check=True)
    print("✅ Очистка завершена")


def wait_for_services():
    """Ждёт, пока все сервисы будут готовы"""
    print("⏳ Ожидание готовности сервисов...")
    for attempt in range(60):
        try:
            r1 = requests.get("http://localhost:3000/api/articles", timeout=3)
            r2 = requests.get("http://localhost:3002/api/users", timeout=3)
            if r1.status_code < 500 and r2.status_code < 500:
                print("✅ Все сервисы готовы!")
                return
        except:
            pass
        time.sleep(2)
        print(f"⏳ Ждём... попытка {attempt + 1}/60")

    raise Exception("❌ Сервисы не запустились")


def create_test_user():
    """Создаёт тестового пользователя"""

    hashed = "$2b$08$xZmPPa3elCWJRorTqJGAd.gDwjvYgXHVc2jPmn/6BFlW6JzmdIJke"

    # Проверяем существование пользователя
    check = 'docker exec mongodb mongo auth_db --eval "db.users.findOne({emailAddress: \'rithinch@gmail.com\'})"'
    result = subprocess.run(check, shell=True, capture_output=True, text=True)

    if "rithinch" in result.stdout:
        print("ℹ️ Пользователь уже есть")
        return

    # Создаём пользователя
    cmd = f'docker exec mongodb mongo auth_db --eval "db.users.insertOne({{emailAddress: \'rithinch@gmail.com\', password: \'{hashed}\', role: \'admin\'}})"'
    subprocess.run(cmd, shell=True)
    print("✅ Тестовый пользователь создан")


@pytest.fixture(scope="session")
def auth_token(full_app):
    """Получает токен администратора"""

    # Даём время на создание пользователя
    time.sleep(2)

    response = requests.post(
        "http://localhost:3003/api/auth",
        json={"emailAddress": "rithinch@gmail.com", "password": "Testing0*"}
    )

    if response.status_code != 200:
        print(f"❌ Ошибка: {response.status_code} - {response.text}")
        # Показываем, есть ли пользователь в БД
        subprocess.run('docker exec mongodb mongo auth_db --eval "db.users.find().pretty()"', shell=True)

    assert response.status_code == 200, f"Auth failed: {response.text}"
    return response.json()["token"]