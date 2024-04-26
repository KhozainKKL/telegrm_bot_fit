from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserFit


@csrf_exempt
def check_user(request):
    if request.method == 'POST':
        card = request.POST.get('card')
        phone = request.POST.get('phone')

        if len(card) < 1:
            return JsonResponse({'error': 'ID Карты не введен.'})
        elif len(phone) < 11:
            return JsonResponse({'error': 'Введенный номер телефона не корректный.'})
        else:
            # Проверяем наличие пользователя в базе данных
            user_exists = UserFit.objects.filter(card=card, phone=phone).exists()
            if user_exists:
                # Возвращаем JSON ответ
                return JsonResponse({'valid': True})
            else:
                return JsonResponse({'error': 'Пользователь не найден в системе.'})
    else:
        return JsonResponse({'error': 'Метод запроса должен быть POST'})
