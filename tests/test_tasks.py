from datetime import date, timedelta
from fastapi.testclient import TestClient
import faker
from app.main import app

client = TestClient(app)
fake = faker.Faker()
test_roles = ["junior", "middle", "senior", "team lead", "manager"]
task_id = 0

def test_create_task():
    response = client.post("/tasks",
                           json={"description": fake.street_address(),
                                 "deadline": str(fake.date_between(date.today(), timedelta(days=30))),
                                 "priority": fake.random_int(1, 5),
                                 "estimated_time": fake.random_int(1, 10),
                                 "needed_role": test_roles[fake.random_int(0, len(test_roles) - 1)]
                            }
    )
    assert response.status_code == 201
    global task_id
    task_id = response.json()["task_id"]

def test_get_tasks():
    response = client.get("/tasks")
    assert response.status_code == 200

def test_get_task_by_id():
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200

def test_update_task():
    response = client.patch(f"/tasks/{task_id}", json={"description": fake.street_address()})
    assert response.status_code == 200

def test_delete_task():
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 200
