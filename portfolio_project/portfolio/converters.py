from django.urls import register_converter

class FourDigitYearConverter:
    # Регулярное выражение для выделения ровно 4 цифр
    regex = '[0-9]{4}'

    def to_python(self, value):
        # Преобразуем строку в целое число
        return int(value)

    def to_url(self, value):
        # Обратно формируем URL из целого числа
        return f"{value:04d}"

# Регистрируем конвертер под именем 'yyyy'
register_converter(FourDigitYearConverter, 'yyyy')
