from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """自定义异常"""
    def __init__(self, status_code: int, detail: str, code: str):
        self.status_code = status_code
        self.detail = detail
        self.code = code


def register_exception_handlers(app: FastAPI):
    """注册全局异常处理器"""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "code": exc.code},
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"detail": "服务器内部错误", "code": "INTERNAL_ERROR"},
        )
