from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect, render
from django.contrib import messages
from django.conf import settings
import requests
from django.http import JsonResponse, FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from io import BytesIO

@csrf_exempt
def proxy_view(request, path, service_url):
    url = f"{service_url}/{path}"
    
    # Проксируем заголовки
    headers = {
        key: value 
        for key, value in request.headers.items() 
        if key.lower() not in ['host', 'content-length', 'content-type']
    }
    
    if request.session.get('auth_token'):
        headers['Authorization'] = f'Bearer {request.session.get("auth_token")}'
    
    try:
        # Проксируем запрос
        response = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.body,
            params=request.GET,
            cookies=request.COOKIES,
            allow_redirects=False,
            timeout=30
        )
        
        # Обрабатываем файловые ответы
        if 'image' in response.headers.get('Content-Type', '') or \
           'application/octet-stream' in response.headers.get('Content-Type', ''):
            return HttpResponse(
                BytesIO(response.content),
                content_type=response.headers.get('Content-Type'),
                status=response.status_code
            )
        
        # Возвращаем JSON ответ
        if 'application/json' in response.headers.get('Content-Type', ''):
            return HttpResponse(
                response.content,
                content_type='application/json',
                status=response.status_code
            )
        
        # Для всех остальных типов
        proxy_response = HttpResponse(
            content=response.content,
            status=response.status_code,
            content_type=response.headers.get('Content-Type')
        )
        
        # Проксируем важные заголовки
        for header in ['Cache-Control', 'Expires', 'Location', 'Set-Cookie']:
            if header in response.headers:
                proxy_response[header] = response.headers[header]
                
        return proxy_response
        
    except requests.exceptions.RequestException as e:
        return HttpResponse(
            content=str(e),
            status=502,
            content_type='text/plain'
        )

def get_fdb_service_url(service_name):
    services = getattr(settings, 'FDB_SERVICES', {})
    url = services.get(service_name)
    
    if not url:
        raise ValueError(f"Service URL for {service_name} not configured")
    
    return url.rstrip('/')

def base_fdb_view(request, service_name, template_name):
    service_url = get_fdb_service_url(service_name)
    context = {
        'service_url': service_url,
        'service_name': service_name.replace('_', ' ').title()
    }
    return render(request, f'fdb_integration/{template_name}', context)

def auth_service_view(request):
    # Если пользователь уже авторизован, перенаправляем его
    if request.session.get('auth_token'):
        return redirect('fdb:storage')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            # Отправляем запрос в FastAPI
            response = requests.post(
                f"{settings.FDB_SERVICES['auth_service']}/auth/jwt/login",
                data={
                    'username': email,
                    'password': password
                },
                timeout=5  # Таймаут 5 секунд
            )
            
            if response.status_code == 200:
                token = response.json().get('access_token')
                request.session['auth_token'] = token
                request.session['user_email'] = email
                messages.success(request, 'Вы успешно авторизованы!')
                return redirect('fdb:storage')
            else:
                error_detail = response.json().get('detail', 'Неверные учетные данные')
                messages.error(request, f'Ошибка авторизации: {error_detail}')
                
        except requests.exceptions.RequestException as e:
            messages.error(request, f'Ошибка соединения с сервером авторизации: {str(e)}')
        except Exception as e:
            messages.error(request, f'Произошла ошибка: {str(e)}')
    
    return render(request, 'fdb_integration/auth.html')

def logout_view(request):
    request.session.flush()
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('fdb:auth')

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, 'Пароли не совпадают')
            return render(request, 'fdb_integration/register.html')
            
        try:
            response = requests.post(
                f"{settings.FDB_SERVICES['auth_service']}/auth/register",
                json={
                    'email': email,
                    'password': password
                },
                timeout=5
            )
            
            if response.status_code == 201:
                messages.success(request, 'Регистрация прошла успешно! Теперь вы можете войти.')
                return redirect('fdb:auth')
            else:
                error_detail = response.json().get('detail', 'Ошибка регистрации')
                if isinstance(error_detail, dict):
                    error_detail = ', '.join([f"{k}: {v}" for k, v in error_detail.items()])
                messages.error(request, f'Ошибка регистрации: {error_detail}')
                
        except requests.exceptions.RequestException as e:
            messages.error(request, f'Ошибка соединения с сервером: {str(e)}')
        except Exception as e:
            messages.error(request, f'Произошла ошибка: {str(e)}')
    
    return render(request, 'fdb_integration/register.html')

def reset_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            response = requests.post(
                f"{settings.FDB_SERVICES['auth_service']}/auth/forgot-password",
                json={'email': email},
                timeout=5
            )
            
            if response.status_code == 202:
                messages.success(request, 'Инструкции по сбросу пароля отправлены на ваш email')
            else:
                error_detail = response.json().get('detail', 'Ошибка сброса пароля')
                messages.error(request, f'Ошибка: {error_detail}')
                
        except requests.exceptions.RequestException as e:
            messages.error(request, f'Ошибка соединения с сервером: {str(e)}')
        except Exception as e:
            messages.error(request, f'Произошла ошибка: {str(e)}')
    
    return render(request, 'fdb_integration/reset_password.html')

def storage_service_view(request):
    context = {
        'service_url': get_fdb_service_url('storage_service')
    }
    return render(request, 'fdb_integration/storage.html', context)

def data_service_view(request):
    context = {
        'service_url': get_fdb_service_url('data_service'),
        'storage_service_url': settings.FDB_SERVICES['storage_service']
    }
    return render(request, 'fdb_integration/data.html', context)

def visualization_service_view(request):
    context = {
        'service_url': get_fdb_service_url('visualization_service'),
        'storage_service_url': settings.FDB_SERVICES['storage_service'],
        'data_service_url': settings.FDB_SERVICES['data_service']
    }
    return render(request, 'fdb_integration/visualization.html', context)

def missing_data_service_view(request):
    context = {
        'service_url': get_fdb_service_url('missing_data_service'),
        'storage_service_url': settings.FDB_SERVICES['storage_service'],
        'data_service_url': settings.FDB_SERVICES['data_service']
    }
    return render(request, 'fdb_integration/missing_data.html', context)

def statistics_service_view(request):
    context = {
        'service_url': get_fdb_service_url('data_service'),
        'storage_service_url': settings.FDB_SERVICES['storage_service']
    }
    return render(request, 'fdb_integration/descriptive_statistics.html', context)

@csrf_exempt
def missing_data_api_upload(request):
    if request.method == 'POST':
        try:
            auth_token = request.session.get('auth_token')
            if not auth_token:
                return JsonResponse({'error': 'Not authenticated'}, status=401)
            
            if 'file' not in request.FILES:
                return JsonResponse({'error': 'No file uploaded'}, status=400)
            
            file = request.FILES['file']
            threshold = request.POST.get('threshold', '0.3')
            method = request.POST.get('method', 'mean')
            
            files = {'file': (file.name, file.file, file.content_type)}
            params = {
                'threshold': threshold,
                'method': method
            }
            
            response = requests.post(
                f"{settings.FDB_SERVICES['missing_data_service']}/missing/upload",
                files=files,
                params=params,  
                headers={'Authorization': f'Bearer {auth_token}'}
            )
            
            if response.status_code == 200:
                return JsonResponse(response.json())
            else:
                error_detail = response.json().get('detail', response.text)
                return JsonResponse({'error': error_detail}, status=response.status_code)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
@csrf_exempt
def missing_data_api_visualize(request):
    if request.method == 'POST':
        try:
            auth_token = request.session.get('auth_token')
            if not auth_token:
                return JsonResponse({'error': 'Not authenticated'}, status=401)
                
            data = json.loads(request.body)
            response = requests.post(
                f"{get_fdb_service_url('missing_data_service')}/missing/visualize",
                json={'format': data.get('format', 'png')},
                headers={
                    'Authorization': f'Bearer {auth_token}'
                }
            )
            
            if response.status_code != 200:
                return JsonResponse(response.json(), status=response.status_code)
                
            return FileResponse(
                BytesIO(response.content),
                content_type=response.headers.get('Content-Type', 'image/png'),
                status=response.status_code
            )
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def missing_data_api_download(request):
    if request.method == 'POST':
        try:
            auth_token = request.session.get('auth_token')
            if not auth_token:
                return JsonResponse({'error': 'Not authenticated'}, status=401)
                
            response = requests.post(
                f"{get_fdb_service_url('missing_data_service')}/missing/download",
                headers={
                    'Authorization': f'Bearer {auth_token}'
                }
            )
            
            if response.status_code != 200:
                return JsonResponse(response.json(), status=response.status_code)
                
            return FileResponse(
                BytesIO(response.content),
                content_type=response.headers.get('Content-Type', 'text/csv'),
                status=response.status_code,
                as_attachment=True,
                filename='imputed_data.csv'
            )
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)