class AuthTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Добавляем токен в заголовки для API запросов
        if request.path.startswith('/fdb/'):
            auth_token = request.session.get('auth_token')
            if auth_token and 'Authorization' not in request.META:
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {auth_token}'
        
        response = self.get_response(request)
        return response
    
class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Страницы, которые не требуют авторизации
        self.exempt_urls = [
            '/fdb/auth/',
            '/fdb/register/',
            '/fdb/reset-password/',
        ]

    def __call__(self, request):
        # Проверяем, требуется ли авторизация для этого URL
        if not any(request.path.startswith(url) for url in self.exempt_urls):
            if not request.session.get('auth_token'):
                return redirect(f'/fdb/auth/?next={request.path}')
        
        response = self.get_response(request)
        return response