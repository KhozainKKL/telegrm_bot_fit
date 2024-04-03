from django import forms

from main_table_admin.models import UserFitLesson


class UserFitInLinesForm(forms.ModelForm):
    class Meta:
        model = UserFitLesson
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        lesson = cleaned_data.get('lesson')

        # Проверяем, что форма редактирует уже существующий объект
        if self.instance.pk:
            return cleaned_data

        if user and lesson:
            # Проверяем, не добавлен ли уже этот пользователь на данное занятие
            if UserFitLesson.objects.filter(user=user, lesson=lesson).exists():
                raise forms.ValidationError('Этот пользователь уже выбран для данного занятия.')
        return cleaned_data