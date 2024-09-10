import os
from django.conf import settings
from django.test import TestCase, RequestFactory
from unittest.mock import patch, Mock
from debugmate.utils import DebugmateAPI
from unittest.mock import MagicMock

class DebugmateAPITest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        os.environ['DJANGO_SETTINGS_MODULE'] = 'test_settings'

    def setUp(self):
        self.factory = RequestFactory()
        settings.DEBUGMATE_API_URL = 'https://example.com'
        settings.DEBUGMATE_API_TOKEN = 'fake-token'

    @patch('requests.post')
    def test_send_exception_to_api(self, mock_post):
        mock_post.return_value = Mock(status_code=200, json=lambda: {"status": "success"})

        request = self.factory.get('/test-url')
        request.user = MagicMock()
        request.user.is_authenticated = True
        request.user.id = 1
        request.user.username = 'testuser'
        request.user.email = 'test@example.com'

        # Adicionando o mock para o atributo `session`
        request.session = MagicMock()

        # Adicionando o mock para o resolver_match
        request.resolver_match = MagicMock()
        request.resolver_match.route = 'test_route'
        request.resolver_match.kwargs = {}
        request.resolver_match.func = Mock(__name__='TestController')
        request.resolver_match.view_name = 'test_view'

        try:
            raise ValueError("Test exception")
        except ValueError as e:
            DebugmateAPI.send_exception_to_api(e, request)

        mock_post.assert_called_once()
        self.assertIn(settings.DEBUGMATE_API_URL + '/api/capture', mock_post.call_args[0])
        headers = mock_post.call_args[1]['headers']
        self.assertEqual(headers['X-DEBUGMATE-TOKEN'], settings.DEBUGMATE_API_TOKEN)
        self.assertEqual(headers['Content-Type'], 'application/json')

        data = mock_post.call_args[1]['json']
        self.assertEqual(data['exception'], 'ValueError')
        self.assertEqual(data['message'], 'Test exception')
        self.assertEqual(data['url'], 'http://testserver/test-url')

    def test_get_app_context(self):
        request = self.factory.get('/test-url')
        request.resolver_match = Mock(route='test_route', kwargs={}, func=Mock(__name__='TestController'), view_name='test_view')

        context = DebugmateAPI.get_app_context(request, None)
        self.assertEqual(context['controller'], 'TestController')
        self.assertEqual(context['route']['name'], 'test_route')
        self.assertEqual(context['view']['name'], 'test_view')

    def test_get_user_context_authenticated(self):
        request = self.factory.get('/test-url')
        request.user = Mock(is_authenticated=True, id=1, username='testuser', email='test@example.com')

        context = DebugmateAPI.get_user_context(request)
        self.assertEqual(context['id'], 1)
        self.assertEqual(context['username'], 'testuser')
        self.assertEqual(context['email'], 'test@example.com')

    def test_get_user_context_unauthenticated(self):
        request = self.factory.get('/test-url')
        request.user = Mock(is_authenticated=False)

        context = DebugmateAPI.get_user_context(request)
        self.assertEqual(context, {})
