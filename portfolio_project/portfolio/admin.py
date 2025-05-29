from django.contrib import admin
from django.contrib import messages
from django.utils.safestring import mark_safe
from .models import PortfolioItem, Category, Tag, Client

class HasClientFilter(admin.SimpleListFilter):
    title = 'Наличие клиента'
    parameter_name = 'has_client'

    def lookups(self, request, model_admin):
        return [
            ('yes', 'С клиентом'),
            ('no', 'Без клиента'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(client__isnull=False)
        if self.value() == 'no':
            return queryset.filter(client__isnull=True)



@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at', 'is_published', 'category', 'description_length', 'tags_count', 'image_thumbnail')
    list_display_links = ('id', 'title')
    list_editable = ('is_published',)
    ordering = ['-created_at', 'title']
    list_per_page = 5
    actions = ['set_published', 'set_draft']
    search_fields = ['title__startswith', 'category__name']
    list_filter = ['category__name', 'is_published', HasClientFilter]
    fields = ['title', 'description', 'image', 'image_thumbnail', 'slug', 'category', 'tags', 'client', 'is_published']
    readonly_fields = ['image_thumbnail']
    filter_horizontal = ['tags']

    @admin.display(description='Миниатюра')
    def image_thumbnail(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50">')
        return "Без изображения"
    
    @admin.display(description='Длина описания')
    def description_length(self, obj):
        return f"{len(obj.description)} символов"

    @admin.display(description='Количество тегов')
    def tags_count(self, obj):
        return obj.tags.count()

    @admin.action(description='Опубликовать выбранные элементы')
    def set_published(self, request, queryset):
        count = queryset.update(is_published=True)
        self.message_user(request, f"Опубликовано {count} элемента(ов).")

    @admin.action(description='Снять с публикации выбранные элементы')
    def set_draft(self, request, queryset):
        count = queryset.update(is_published=False)
        self.message_user(request, f"Снято с публикации {count} элемента(ов).", messages.WARNING)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    list_display_links = ('id', 'name')
    list_editable = ('slug',)
    ordering = ['name']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    list_display_links = ('id', 'name')
    list_editable = ('slug',)
    ordering = ['name']

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'contact_email')
    list_display_links = ('id', 'name')
    ordering = ['name']