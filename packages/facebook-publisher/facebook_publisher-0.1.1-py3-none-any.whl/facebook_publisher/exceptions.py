class FacebookError(Exception):
    """Error base para el SDK de Facebook."""

class LoginError(FacebookError):
    """Error en el proceso de inicio de sesión."""
    pass

class GroupNotFoundError(FacebookError):
    """No se encontró el grupo o el botón de acceso correspondiente."""
    pass

class PublishError(FacebookError):
    """Fallo al enviar o confirmar una publicación."""
    pass
