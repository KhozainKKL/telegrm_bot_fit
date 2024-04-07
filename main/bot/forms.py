from django import forms
from django.core.exceptions import ValidationError

from .models import UserFit


class UserFitModelForm(forms.ModelForm):
    class Meta:
        model = UserFit
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Отключаем поле relative_user при добавлении нового объекта
        if not self.instance.pk:
            self.fields['relative_user'].widget.attrs['disabled'] = True
            self.fields['relative_user'].help_text = 'Поле родственника недоступно при создании нового клиента.'

        if self.instance.pk:
            self.fields['phone'].help_text = 'Формат +7-999-999-99-99 обязательный'

    def clean_relative_user(self):
        relative_user = self.cleaned_data.get('relative_user')
        if relative_user == self.instance:
            raise ValidationError('Нельзя выбирать текущего пользователя в качестве родственника')
        return relative_user
