from fastapi import FastAPI

app = FastAPI(
    title="Система управления задачами",
    description="Простейшая система управления задачами, основанная на "
                "фреймворке FastAPI.",
    version="0.0.1",
    contact={
        "name": "Андрей Вязовцев",
        "url": "https://github.com/AndreyVV-100"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
)
