import time
import logging

def retry(fn, retries=3, delay=1, stage=None, logger: logging.Logger = None):
    """Ejecuta una función con reintentos exponiendo logs opcionales.

    Args:
        fn: Función a ejecutar.
        retries: Cantidad de reintentos.
        delay: Delay entre intentos en segundos.
        stage: Nombre de etapa para logging.
        logger: Logger opcional.
    Returns:
        Resultado de `fn` si tiene éxito.
    Raises:
        Exception: Última excepción capturada si falla en todos los intentos.
    """
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            return fn()
        except Exception as e:
            last_exc = e
            if logger and stage:
                logger.info(f"[{stage}] intento {attempt} falló: {e}")
            time.sleep(delay)
    if last_exc:
        raise last_exc
