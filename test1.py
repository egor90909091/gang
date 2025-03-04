from locust import HttpUser, task, between, tag
import random
import logging


class EnglishGangUserGETPUT(HttpUser):
    """
    Класс для эмуляции пользователя системы English Gang (только GET и PUT запросы)
    """

    # Время ожидания между запросами (от 1 до 5 секунд)
    wait_time = between(1.0, 5.0)
    
    # Авторизационный токен
    token = None
    user_id = None
    teacher_id = None
    
    def on_start(self):
        """Действия при старте тестирования - авторизуемся как студент"""
        # Для тестов нам нужна авторизация, поэтому мы используем существующего студента
        try:
            # Авторизуемся как студент
            response = self.client.post("/api/token", 
                data={
                    "username": "alice@example.com",
                    "password": "password123",
                }
            )
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                # Получаем информацию о пользователе
                user_response = self.client.get(
                    "/api/me", 
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                if user_response.status_code == 200:
                    self.user_id = user_response.json()["id"]
                    self.teacher_id = user_response.json()["additional_info"]["teacher_id"]
                    logging.info(f"Успешная авторизация. User ID: {self.user_id}, Teacher ID: {self.teacher_id}")
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

    @tag("get")
    @task(3)
    def visit_courses_page(self):
        """Тест GET-запроса для страницы курсов"""
        with self.client.get(
            "/Courses.html", catch_response=True, name="GET courses page"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Ошибка доступа к странице курсов: {response.status_code}"
                )
    
    @tag("get")
    @task(3)
    def visit_tests_page(self):
        """Тест GET-запроса для страницы тестов"""
        with self.client.get(
            "/Tests.html", catch_response=True, name="GET tests page"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Ошибка доступа к странице тестов: {response.status_code}"
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
    
    @tag("get_auth")
    @task(3)
    def get_student_info(self):
        """Тест GET-запроса для получения информации о студенте"""
        if not self.token or not self.user_id:
            return

        with self.client.get(
            f"/api/students/{self.user_id}", 
            headers={"Authorization": f"Bearer {self.token}"},
            catch_response=True, 
            name="GET student info"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Ошибка получения информации о студенте: {response.status_code}"
                )
    
    @tag("get_auth")
    @task(3)
    def get_teacher_info(self):
        """Тест GET-запроса для получения информации о преподавателе"""
        if not self.token or not self.teacher_id:
            return

        with self.client.get(
            f"/api/teachers/{self.teacher_id}", 
            headers={"Authorization": f"Bearer {self.token}"},
            catch_response=True, 
            name="GET teacher info"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Ошибка получения информации о преподавателе: {response.status_code}"
                )
    
    # PUT запросы
    @tag("put")
    @task(2)
    def update_student_info(self):
        """Тест PUT-запроса для обновления информации о студенте"""
        if not self.token or not self.user_id:
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