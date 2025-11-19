import os
import socket
import asyncio
import logging
import uuid
from typing import Optional, Tuple

import aiohttp

logger = logging.getLogger(__name__)


async def consul_register(
    address_mode: Optional[str] = None,
    custom_session: Optional[aiohttp.ClientSession] = None,
) -> Tuple[str, aiohttp.ClientSession]:
    """
    Асинхронно регистрирует сервис в Consul.
    
    Args:
        address_mode: "internal", "external" или None
        custom_session
    Returns:
        (service_id: str, session: aiohttp.ClientSession)
    """
    consul_http_addr = os.getenv("CONSUL_HTTP_ADDR", "http://127.0.0.1:8500").rstrip("/")
    consul_token = os.getenv("CONSUL_HTTP_TOKEN")

    service_name = os.getenv("SERVICE_NAME")
    if not service_name:
        raise ValueError("Переменная окружения SERVICE_NAME не объявленна!")

    service_port = int(os.getenv("SERVICE_PORT", "8000"))
    service_version = os.getenv("SERVICE_VERSION", "unknown")

    health_interval = os.getenv("HEALTH_INTERVAL", "10s")
    health_timeout = os.getenv("HEALTH_TIMEOUT", "1s")
    dereg_after = os.getenv("DEREG_AFTER", "1m")
    explicit_address = os.getenv("SERVICE_ADDRESS")

    mode = (address_mode or os.getenv("ADDRESS_MODE", "internal")).lower()

    if explicit_address:
        address = explicit_address
    elif mode == "internal":
        address = socket.gethostbyname(socket.gethostname())
    elif mode == "external":
        if not explicit_address:
            raise ValueError("Для ADDRESS_MODE=external требуется SERVICE_ADDRESS")
        address = explicit_address
    else:
        address = socket.gethostbyname(socket.gethostname())

    service_id = f"{service_name}-{address.replace('.', '-')}-{service_port}-{uuid.uuid4().hex[:8]}"

    payload = {
        "ID": service_id,
        "Name": service_name,
        "Address": address,
        "Port": service_port,
        "Meta": {"version": service_version},
        "Tags": [f"v{service_version}"],
        "Check": {
            "HTTP": f"http://{address}:{service_port}/health",
            "Interval": health_interval,
            "Timeout": health_timeout,
            "DeregisterCriticalServiceAfter": dereg_after,
        },
    }

    headers = {"Content-Type": "application/json"}
    if consul_token:
        headers["X-Consul-Token"] = consul_token

    if custom_session:
        session = custom_session
        need_close = False
    else:
        session = aiohttp.ClientSession(headers=headers)
        need_close = True

    max_retries = 15
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Регистрация в Consul ({consul_http_addr}), попытка {attempt}")

            async with session.get(f"{consul_http_addr}/v1/agent/self") as resp:
                if resp.status != 200:
                    await asyncio.sleep(5)
                    continue

            async with session.put(
                f"{consul_http_addr}/v1/agent/service/register",
                json=payload,
            ) as resp:
                if resp.status == 200:
                    logger.info(f"Сервис зарегистрирован: {service_id}")
                    return service_id, session
                else:
                    text = await resp.text()
                    logger.error(f"Ошибка регистрации: {resp.status} {text}")
        except Exception as e:
            logger.warning(f"Consul недоступен: {e}")
            await asyncio.sleep(5)

    if need_close:
        await session.close()
    raise RuntimeError("Не удалось зарегистрировать сервис в Consul")


async def consul_deregister(service_id: str, session: aiohttp.ClientSession):
    """Дерегистрация сервиса и закрытие сессии"""
    consul_http_addr = os.getenv("CONSUL_HTTP_ADDR", "http://127.0.0.1:8500").rstrip("/")

    try:
        async with session.put(
            f"{consul_http_addr}/v1/agent/service/deregister/{service_id}"
        ) as resp:
            if resp.status == 200:
                logger.info(f"Сервис снят с регистрации: {service_id}")
            else:
                logger.error(f"Ошибка дерегистрации: {resp.status}")
    finally:
        await session.close()
