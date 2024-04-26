import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserFit


@csrf_exempt
def check_user(request):
    if request.method == 'POST':
        # Проверяем, есть ли данные в теле запроса
        if request.body:
            try:
                data = json.loads(request.body)
                card = data.get('card')
                phone = data.get('phone')

                if not card:
                    return JsonResponse({'error': 'ID Карты не введен.'}, status=400)
                elif len(phone) < 11:
                    return JsonResponse({'error': 'Введенный номер телефона некорректный.'}, status=400)
                else:
                    # Проверяем наличие пользователя в базе данных
                    user_exists = UserFit.objects.filter(card=card, phone=phone).exists()
                    if user_exists:
                        # Возвращаем JSON ответ
                        return JsonResponse({'valid': True})
                    else:
                        return JsonResponse({'error': 'Пользователь не найден в системе.'}, status=404)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Невалидный JSON в теле запроса.'}, status=400)
        else:
            return JsonResponse({'error': 'Тело запроса пустое.'}, status=400)
    else:
        return JsonResponse({'error': 'Метод запроса должен быть POST'}, status=405)