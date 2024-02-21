from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET


from reqsoft.settings import BASE_DIR


def index(request):
    if request.user.is_authenticated:
        return redirect('blog_app:article_list')
    return render(request, 'main_app/main.html')


def tr_handler404(request, exception):
    """
    Обработка ошибки 404
    """
    return render(request=request, template_name='main_app/error_page.html', status=404, context={
        'title': 'Страница не найдена: 404',
        'error_message': 'К сожалению такая страница была не найдена, или перемещена',
    })


def tr_handler500(request):
    """
    Обработка ошибки 500
    """
    return render(request=request, template_name='main_app/error_page.html', status=500, context={
        'title': 'Ошибка сервера: 500',
        'error_message': 'Внутренняя ошибка сайта, вернитесь на главную страницу, отчет об ошибке мы направим администрации сайта',
    })


def tr_handler403(request, exception):
    """
    Обработка ошибки 403
    """
    return render(request=request, template_name='main_app/error_page.html', status=403, context={
        'title': 'Ошибка доступа: 403',
        'error_message': 'Доступ к этой странице ограничен',
    })

@require_GET
def get_challenge(request, file_name=None):
    lines = []
    if file_name:
        path = f'{BASE_DIR}/static/.well-known/acme-challenge/{file_name}'
    try:
        with open(path) as f:
            lines = f.readlines()
            f.close()
    except:
        return HttpResponse("File not found!")

    return HttpResponse("".join(lines), content_type="text/plain")
