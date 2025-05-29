from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class Category(models.Model):
    name = models.CharField("Название категории", max_length=100, db_index=True)
    slug = models.SlugField("Слаг", max_length=255, unique=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('portfolio:category_detail', kwargs={'cat_slug': self.slug})

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

class Tag(models.Model):
    name = models.CharField("Название тега", max_length=100, db_index=True)
    slug = models.SlugField("Слаг", max_length=255, unique=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('portfolio:tag_detail', kwargs={'tag_slug': self.slug})

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

class Client(models.Model):
    name = models.CharField("Имя клиента", max_length=100)
    contact_email = models.EmailField("Email", blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)

class PortfolioItem(models.Model):
    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание")
    image = models.ImageField("Изображение", upload_to='portfolio_images/', blank=True, null=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    is_published = models.BooleanField("Опубликовано", default=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='portfolio_items',
        verbose_name="Категория",
        null=True,  # Временно, чтобы избежать ошибок
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='portfolio_items',
        verbose_name="Теги"
    )
    client = models.OneToOneField(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='portfolio_item',
        verbose_name="Клиент"
    )
    
    class Meta:
        verbose_name = 'Элемент портфолио'
        verbose_name_plural = 'Элементы портфолио'

    objects = models.Manager()
    published = PublishedManager()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('portfolio:portfolio_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title
    