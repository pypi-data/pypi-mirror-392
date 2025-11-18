"""SDK para automatizar publicaciones en Facebook para tu SaaS.

Provee `FacebookClient` para login, gestión de grupos y publicación, con sesiones persistentes.
"""
from .client import FacebookClient
from .exceptions import FacebookError, LoginError, GroupNotFoundError, PublishError

__all__ = ["FacebookClient", "FacebookError", "LoginError", "GroupNotFoundError", "PublishError"]
