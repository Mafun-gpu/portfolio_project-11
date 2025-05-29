from django.db import models

class CategoryType(models.TextChoices):
    MUSIC = "Music", 'Музыка'
    SPORT = "Sport", 'Спорт'
    FILM = "Film", 'Фильм'
    OTHER = "Other", 'Другое'
