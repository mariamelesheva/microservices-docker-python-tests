import requests

def register_new_user(auth_token, email= "misskisslip@gmail.com", password= "Testing011*"):
    """email example: "rithinch@gmail.com"
    password example: "Testing0*"""
    # Если регистрация не удалась (например, email уже существует), response.json()['_id'] вызовет ошибку. Нужна проверка статуса
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.post("http://localhost:3002/api/users",
                             json={"emailAddress":email,"password": password}, headers=headers)
    return response.json()['_id']

def delete_user(auth_token, user_id):
    """DELETE | http://localhost:3002/api/users/:id"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.delete(f"http://localhost:3002/api/users/{user_id}", headers=headers)
    print(response.json())

def get_all_users():
    response = requests.get("http://localhost:3002/api/users")
    print(response.json())



def test_e2e_create_article_with_new_user(full_app, auth_token):
    # Напишу свой первый тест, который будет регистрировать нового пользователя.
    # Далее юзер авторизуется, получит токен и по токену создаст новую статью и проверит что она создалась
    # Также проверить что уведомление ушло в Notification
    # Удалить созданные данные (через DELETE API)
    # Негативный сценарий (позже)
    # Между регистрацией и авторизацией есть задержка (Authentication должен обработать событие). В тесте нужен time.sleep(1) или повтор запросов.

    #  Небольшая подсказка (без кода)
    # Порядок операций — сначала регистрация, потом пауза (1-2 секунды), потом авторизация
    #
    # Уникальность email — используйте int(time.time()) в email
    #
    # Проверку статус-кодов — 200/201 после успешных операций
    # POST | http://localhost:3002/api/users
    user_id = register_new_user(auth_token)
    delete_user(auth_token, user_id)
    # json_user_example = {'_id': '69d5d07adb7e810be5202b1a', 'emailAddress': 'misskisslip@gmail.com', 'createdDate': '2026-04-08T03:50:18.012Z', 'updatedDate': '2026-04-08T03:50:18.012Z'}


