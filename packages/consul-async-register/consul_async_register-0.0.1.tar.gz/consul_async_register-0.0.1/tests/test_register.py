import os
import unittest
from unittest.mock import patch, AsyncMock

from consul_async_register import consul_register, consul_deregister


class TestConsulAsyncRegister(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.env_patch = patch.dict(os.environ, {
            "SERVICE_NAME": "test-service",
            "SERVICE_PORT": "8000",
            "CONSUL_HTTP_ADDR": "http://localhost:8500",
        }, clear=True)
        self.env_patch.start()

    def tearDown(self):
        self.env_patch.stop()

    async def test_missing_service_name_raises(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                await consul_register()

    async def test_successful_registration_with_mock(self):
        mock_resp = AsyncMock(status=200)

        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_resp
        mock_context.__aexit__.return_value = None

        mock_session = AsyncMock()
        mock_session.get.return_value = mock_context
        mock_session.put.return_value = mock_context

        service_id, session = await consul_register(custom_session=mock_session)

        mock_session.put.assert_awaited_once()
        self.assertIn("test-service-", service_id)
        self.assertIs(session, mock_session)

    async def test_deregister_called_correctly(self):
        mock_resp = AsyncMock(status=200)

        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = mock_resp
        mock_context.__aexit__.return_value = None

        mock_session = AsyncMock()
        mock_session.put.return_value = mock_context
        mock_session.close = AsyncMock()

        await consul_deregister("fake-id-123", mock_session)

        mock_session.put.assert_awaited_once_with(
            "http://localhost:8500/v1/agent/service/deregister/fake-id-123"
        )
        mock_session.close.assert_awaited_once()

    async def test_external_mode_without_address_raises(self):
        os.environ["ADDRESS_MODE"] = "external"
        with self.assertRaises(ValueError):
            await consul_register()
        del os.environ["ADDRESS_MODE"]
