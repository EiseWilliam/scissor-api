
from fastapi import HTTPException, Request, status


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Unauthorized") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
        
class ForbiddenException(HTTPException):
    def __init__(self, detail: str = "Forbidden") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
        
class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Not Found") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        
class URLNotFoundException(HTTPException):
    def __init__(self, detail: str = "URL Not Found") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        
    @staticmethod
    def handler (request: Request):
        from fastapi.templating import Jinja2Templates
        templates = Jinja2Templates(directory="app/templates")
        return templates.TemplateResponse("404.jinja", {"request": request})


class ConflictException(HTTPException):
    def __init__(self, detail: str = "Conflict") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
    