# tests/component/test_authentication_component.py

import pytest
import pika
import json
import time
import pymongo
import subprocess


class TestAuthenticationComponent:

    @pytest.fixture(scope="module")
    def docker_compose(self):
        """Поднимаем всё через docker-compose"""
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        time.sleep(15)  # Ждём полной инициализации всех сервисов
        yield
        subprocess.run(["docker-compose", "down"], check=True)

    def test_authentication_creates_record_on_user_added_event(self, docker_compose):
        """Тест: публикуем событие, проверяем запись в MongoDB"""

        # 1. Подключаемся к RabbitMQ
        print("\n🐰 Connecting to RabbitMQ...")
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost', port=5672)
        )
        channel = connection.channel()

        # Убеждаемся, что exchange существует
        channel.exchange_declare(exchange='user.added', exchange_type='fanout', durable=True)
        print("✅ Exchange 'user.added' ready")

        # 2. Публикуем событие с реальными данными из e2e теста
        event_data = {
            "emailAddress": "misskisslip@gmail.com",
            "password": "Testing011*",
            "role": "user",
            "firstName": "Test",
            "lastName": "User"
        }

        channel.basic_publish(
            exchange='user.added',
            routing_key='',
            body=json.dumps(event_data)
        )
        print(f"✅ Event published for: {event_data['emailAddress']}")

        # 3. Проверяем MongoDB
        print("\n🍃 Checking MongoDB...")
        client = pymongo.MongoClient("mongodb://localhost:27017")

        # Ищем во всех базах данных
        user = None
        found_in_db = None
        found_in_coll = None

        for db_name in client.list_database_names():
            if db_name in ['admin', 'config', 'local']:
                continue

            db = client[db_name]
            for coll_name in db.list_collection_names():
                # Ищем по реальному email
                result = db[coll_name].find_one({"emailAddress": "misskisslip@gmail.com"})
                if result:
                    user = result
                    found_in_db = db_name
                    found_in_coll = coll_name
                    print(f"✅ Found user in {db_name}.{coll_name}")
                    break
            if user:
                break

        # Если не нашли сразу, ждём с повторными попытками
        if not user:
            print("⏳ Waiting for user to be created...")
            for i in range(30):
                for db_name in client.list_database_names():
                    if db_name in ['admin', 'config', 'local']:
                        continue
                    db = client[db_name]
                    for coll_name in db.list_collection_names():
                        user = db[coll_name].find_one({"emailAddress": "misskisslip@gmail.com"})
                        if user:
                            found_in_db = db_name
                            found_in_coll = coll_name
                            print(f"✅ Found user in {db_name}.{coll_name} (attempt {i + 1})")
                            break
                    if user:
                        break
                if user:
                    break
                print(f"⏳ Waiting... ({i + 1}/30)")
                time.sleep(1)

        # 4. Проверяем результат
        if user:
            print(f"\n📋 User data found:")
            print(f"   Database: {found_in_db}")
            print(f"   Collection: {found_in_coll}")
            print(f"   Email: {user.get('emailAddress')}")
            print(f"   Role: {user.get('role')}")
            print(f"   Password hash: {user.get('password')[:20]}...")

            assert user["password"] != "Testing011*", "Password not hashed!"
            assert user["role"] == "user", "Role mismatch"
            print("✅ Password is properly hashed")
            print("✅ Role is correct")
        else:
            print("\n❌ User not found in any database!")
            print(f"Available databases: {client.list_database_names()}")

            # Показываем содержимое всех баз для диагностики
            for db_name in client.list_database_names():
                if db_name in ['admin', 'config', 'local']:
                    continue
                db = client[db_name]
                print(f"\nDatabase: {db_name}")
                for coll_name in db.list_collection_names():
                    count = db[coll_name].count_documents({})
                    print(f"  {coll_name}: {count} documents")
                    if count > 0:
                        sample = db[coll_name].find_one()
                        print(f"    Sample: {sample}")

        assert user is not None, "User not created in MongoDB"

        connection.close()
        client.close()
        print("\n✅ Test passed!")