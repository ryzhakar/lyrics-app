from __future__ import annotations

import bcrypt
from sqladmin.authentication import AuthenticationBackend

from .db import get_connection
from .repositories.admin_users import get_admin_by_email


class AdminAuth(AuthenticationBackend):
    """Authenticate admin users with DB-backed credentials."""

    def __init__(self, secret_key: str) -> None:
        """Initialize backend and ensure session middleware is present."""
        super().__init__(secret_key)

    async def login(self, request) -> bool:  # type: ignore[override]
        form = await request.form()
        email = str(form.get('username') or form.get('email') or '')
        password = str(form.get('password') or '')
        if not email or not password:
            return False
        user = None
        async for conn in get_connection():
            user = await get_admin_by_email(conn, email)
            break
        if not user:
            return False
        pw_hash = str(user.get('password_hash') or '')
        if not pw_hash:
            return False
        ok = False
        try:
            ok = bcrypt.checkpw(password.encode(), pw_hash.encode())
        except ValueError:
            return False
        if not ok:
            return False
        request.session['admin_email'] = email
        return True

    async def logout(self, request) -> bool:  # type: ignore[override]
        request.session.clear()
        return True

    async def authenticate(self, request) -> bool:  # type: ignore[override]
        return bool(request.session.get('admin_email'))
