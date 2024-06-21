from main_rest import settings


def checkout_use_method_crud_url(methods, pk=None):
    methods_url = {
        "products": settings.SERVER_URL + f"products/{pk if pk else ''}",
        "user_lesson_fit": settings.SERVER_URL
        + f"user_lesson_fit/{pk}/get_for_telegram/",
    }

    for key, value in methods_url.items():
        if methods == "user_lesson_fit" and not pk:
            print({"error": f"for method '{methods}' not use pk"})
        elif methods == key:
            print(value)
            return value


checkout_use_method_crud_url(methods="user_lesson_fit")
