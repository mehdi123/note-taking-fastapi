from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from app.core import config, tasks  

from app.api.routes import router as api_router

def bind_event_handlers(app: FastAPI):
    """
        bind start/stop handlers
    """
    app.add_event_handler("startup", tasks.create_start_app_handler(app))
    app.add_event_handler("shutdown", tasks.create_stop_app_handler(app))

def get_application():
    app = FastAPI(title=config.PROJECT_NAME, version=config.VERSION)  

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    bind_event_handlers(app)
    app.include_router(api_router, prefix=config.API_PREFIX)

    add_pagination(app)
    
    return app


app = get_application()
