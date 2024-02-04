from typing import Any

from fastapi import Response


class CookieHandler:
    def __init__(
        self,
        cookie_name: str,
        cookie_max_age: int,
        cookie_path: str,
        cookie_domain: str | None,
        cookie_secure: bool,
        cookie_httponly: bool,
        cookie_samesite: Any,
    ) -> None:
        self.cookie_name = cookie_name
        self.cookie_max_age = cookie_max_age
        self.cookie_path = cookie_path
        self.cookie_domain = cookie_domain
        self.cookie_secure = cookie_secure
        self.cookie_httponly = cookie_httponly
        self.cookie_samesite = cookie_samesite

    def login(self, response: Response, token: str) -> Response:
        response.set_cookie(
            self.cookie_name,
            token,
            max_age=self.cookie_max_age,
            path=self.cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
        )
        return response

    def logout(self, response: Response) -> Response:
        response.set_cookie(
            self.cookie_name,
            "",
            max_age=0,
            path=self.cookie_path,
            domain=self.cookie_domain,
            secure=self.cookie_secure,
            httponly=self.cookie_httponly,
            samesite=self.cookie_samesite,
        )
        return response


auth_cookie_handler = CookieHandler(
    cookie_name="token",
    cookie_max_age=1800,
    cookie_path="/",
    cookie_domain=None,
    cookie_secure=False,
    cookie_httponly=True,
    cookie_samesite="lax",
)
