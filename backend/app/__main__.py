import uvicorn

from backend.app.main import create_app
from backend.app.settings import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        create_app(settings=settings),
        host=settings.api_host,
        port=settings.api_port,
    )


if __name__ == "__main__":
    main()
