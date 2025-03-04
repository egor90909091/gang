from locust import HttpUser, task, between, tag
import random
import logging
import uuid


class EnglishGangUserAllRequests(HttpUser):
    """
    Класс для эмуляции пользователя системы English Gang (GET, PUT и POST запросы)
    """

    # Время ожидания между запросами (от 1 до 5 секунд)
    wait_time = between(1.0, 5.0)
    
    # Авторизационный токен
    token = None
    user_id = None
    teacher_id = None
    is_manager = False
    
    def on_start(self):
        """Действия при старте тестирования - авторизуемся"""
        try:
            # С вероятностью 20% авторизуемся как менеджер, в остальных случаях как студент
            if random.random() < 0.2:
                # Авторизуемся как менеджер
                response = self.client.post("/api/token", 
                    data={
                        "username": "admin@example.com",
                        "password": "admin123",
                    }
                )
                self.is_manager = True
            else:
                # Авторизуемся как студент
                response = self.client.post("/api/token", 
                    data={
                        "username": "alice@example.com",
                        "password": "password123",
                    }
                )
                self.is_manager = False
                
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                # Получаем информацию о пользователе
                user_response = self.client.get(
                    "/api/me", 
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                if user_response.status_code == 200:
                    self.user_id = user_response.json()["id"]
                    if not self.is_manager:
                        self.teacher_id = user_response.json()["additional_info"]["teacher_id"]
                    logging.info(f"Успешная авторизация как {'менеджер' if self.is_manager else 'студент'}. User ID: {self.user_id}")
                else:
                    logging.error(f"Не удалось получить информацию о пользователе: {user_response.status_code}")
            else:
                logging.error(f"Ошибка авторизации: {response.status_code}")
        except Exception as e:
            logging.error(f"Ошибка при авторизации: {str(e)}")

    # GET запросы (публичные)
    @tag("get")
    @task(10)
    def get_public_teachers(self):
        """Тест GET-запроса для получения публичного списка преподавателей"""
        with self.client.get(
            "/api/teachers/public", catch_response=True, name="GET public teachers"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Ошибка получения списка преподавателей: {response.status_code}"
                )

    @tag("get")
    @task(8)
    def visit_homepage(self):
        """Тест GET-запроса для главной страницы"""
        with self.client.get("/", catch_response=True, name="GET homepage") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Ошибка доступа к главной странице: {response.status_code}"
                )

    @tag("get")
    @task(5)
    def visit_team_page(self):
        """Тест GET-запроса для страницы команды"""
        with self.client.get(
            "/team.html", catch_response=True, name="GET team page"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Ошибка доступа к странице команды: {response.status_code}"
                )

    @tag("get")
    @task(5)
    def visit_projects_page(self):
        """Тест GET-запроса для страницы проектов"""
        with self.client.get(
            "/projects.html", catch_response=True, name="GET projects page"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Ошибка доступа к странице проектов: {response.status_code}"
                )

    @tag("get")
    @task(5)
    def visit_technical_page(self):
        """Тест GET-запроса для технической страницы"""
        with self.client.get(
            "/technical.html", catch_response=True, name="GET technical page"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Ошибка доступа к технической странице: {response.status_code}"
                )

    # Авторизованные GET-запросы
    @tag("get_auth")
    @task(5)
    def get_profile_info(self):
        """Тест GET-запроса для получения информации о профиле пользователя"""
        if not self.token:
            return

        with self.client.get(
            "/api/me", 
            headers={"Authorization": f"Bearer {self.token}"},
            catch_response=True, 
            name="GET profile info"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Ошибка получения информации о профиле: {response.status_code}"
                )
    
    # PUT запросы
    @tag("put")
    @task(2)
    def update_student_info(self):
        """Тест PUT-запроса для обновления информации о студенте"""
        if not self.token or not self.user_id or self.is_manager:
            return
            
        # Получаем текущую информацию о студенте
        current_info = None
        try:
            response = self.client.get(
                f"/api/students/{self.user_id}", 
                headers={"Authorization": f"Bearer {self.token}"}
            )
            if response.status_code == 200:
                current_info = response.json()
            else:
                logging.error(f"Не удалось получить информацию о студенте: {response.status_code}")
                return
        except Exception as e:
            logging.error(f"Ошибка при получении информации о студенте: {str(e)}")
            return
            
        # Обновляем данные
        update_data = {
            "first_name": current_info["first_name"],
            "last_name": current_info["last_name"],
            "age": current_info["age"],
            "sex": current_info["sex"],
            "email": current_info["email"],
            "level": current_info["level"],
            "vocabulary": current_info["vocabulary"] + random.randint(-10, 10),  # Небольшое изменение словарного запаса
            "teacher_id": current_info["teacher_id"],
            "password": "password123"  # Оставляем тот же пароль
        }
        
        with self.client.put(
            f"/api/students/{self.user_id}", 
            json=update_data,
            headers={"Authorization": f"Bearer {self.token}"},
            catch_response=True, 
            name="PUT update student"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Ошибка обновления информации о студенте: {response.status_code}, {response.text}"
                )
    
    # POST запросы
    @tag("post")
    @task(10)  # Основной POST-запрос с высоким приоритетом
    def login_attempt(self):
        """Тест POST-запроса для попытки входа в систему"""
        credentials = [
            {"username": "alice@example.com", "password": "password123"},
            {"username": "bob@example.com", "password": "password456"},
            {"username": "admin@example.com", "password": "admin123"},
            {"username": "john.doe@example.com", "password": "teacher123"},
            {"username": "jane.smith@example.com", "password": "teacher456"}
        ]
        
        # Выбираем случайные учетные данные
        cred = random.choice(credentials)
        
        with self.client.post(
            "/api/token", 
            data=cred,
            catch_response=True, 
            name="POST login"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Ошибка авторизации: {response.status_code}, {response.text}"
                )

    @tag("post")
    @task(1)
    def register_student(self):
        """Тест POST-запроса для регистрации нового студента"""
        if self.is_manager and self.token:
            # Генерируем случайные данные для нового студента
            unique_id = uuid.uuid4().hex[:8]
            student_data = {
                "first_name": f"Test{unique_id}",
                "last_name": f"Student{unique_id}",
                "age": random.randint(18, 45),
                "sex": random.choice(["M", "F"]),
                "email": f"test.student{unique_id}@example.com",
                "level": random.choice(["A1", "A2", "B1", "B2", "C1", "C2"]),
                "vocabulary": random.randint(500, 3000),
                "teacher_id": 1,  # Предполагаем, что ID 1 существует
                "password": "testpassword123"
            }
            
            with self.client.post(
                "/api/students/", 
                json=student_data,
                headers={"Authorization": f"Bearer {self.token}"},
                catch_response=True, 
                name="POST register student"
            ) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(
                        f"Ошибка регистрации студента: {response.status_code}, {response.text}"
                    )
                    
    @tag("post")
    @task(1)
    def create_teacher(self):
        """Тест POST-запроса для создания нового преподавателя"""
        if self.is_manager and self.token:
            # Генерируем случайные данные для нового преподавателя
            unique_id = uuid.uuid4().hex[:8]
            teacher_data = {
                "first_name": f"Teacher{unique_id}",
                "last_name": f"Last{unique_id}",
                "age": random.randint(25, 60),
                "sex": random.choice(["M", "F"]),
                "qualification": random.choice(["B2", "C1", "C2"]),
                "email": f"teacher{unique_id}@example.com",
                "password": "teacherpass123"
            }
            
            with self.client.post(
                "/api/teachers/", 
                json=teacher_data,
                headers={"Authorization": f"Bearer {self.token}"},
                catch_response=True, 
                name="POST create teacher"
            ) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(
                        f"Ошибка создания преподавателя: {response.status_code}, {response.text}"
                    )