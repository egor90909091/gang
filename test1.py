from locust import HttpUser, task, between

class TestUser(HttpUser):
    wait_time = between(1, 5)  # Время ожидания между задачами в секундах

    def on_start(self):
        # Получаем токен при старте пользователя
        self.token = self.get_token()

    def get_token(self):
        # Данные для аутентификации менеджера
        response = self.client.post(
            "/api/token",
            data={"username": "admin@example.com", "password": "admin123"},
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Не удалось получить токен: {response.status_code}")
            return None

    @task
    def get_public_teachers(self):
        # GET /api/teachers/public (публичный)
        self.client.get("/api/teachers/public")

    @task
    def get_teachers(self):
        # GET /api/teachers/ (с аутентификацией)
        if self.token:
            self.client.get(
                "/api/teachers/", headers={"Authorization": f"Bearer {self.token}"}
            )

    @task
    def put_teacher(self):
        # PUT /api/teachers/1 (с аутентификацией и ролью менеджера)
        if self.token:
            # Данные для обновления учителя
            update_data = {
                "first_name": "Updated",
                "last_name": "Teacher",
                "age": 40,
                "sex": "M",
                "qualification": "C2",
                "email": "updated.teacher@example.com",
            }
            self.client.put(
                "/api/teachers/1",
                json=update_data,
                headers={"Authorization": f"Bearer {self.token}"},
            )