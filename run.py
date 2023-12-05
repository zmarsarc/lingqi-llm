import uvicorn
from multiprocessing import Process
import time
from pydantic_settings import BaseSettings


class ServerSettings(BaseSettings):
    app_port: int = 8000
    admin_port: int = 8001
    dev_reload: bool = False
    host: str = '127.0.0.1'


server_settings = ServerSettings()


if __name__ == '__main__':
    app_proc = Process(target=uvicorn.run, kwargs={
        'app': 'app.main:app',
        'host': server_settings.host,
        'port': server_settings.app_port,
        'reload': server_settings.dev_reload
    })
    admin_proc = Process(target=uvicorn.run, kwargs={
        'app': 'app.main:admin',
        'host': server_settings.host,
        'port': server_settings.admin_port,
        'reload': server_settings.dev_reload
    })

    app_proc.start()
    admin_proc.start()

    try:
        while True:
            time.sleep(30)
    except KeyboardInterrupt:
        pass

    app_proc.terminate()
    admin_proc.terminate()
