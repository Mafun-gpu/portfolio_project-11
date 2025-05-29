from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from .models import PortfolioItem, Category, Tag
from .forms import NonModelPortfolioForm, PortfolioItemForm, UploadFileForm
from .utils import DataMixin
import os
import uuid
from datetime import datetime


def page_not_found(request, exception):
    return render(request, 'portfolio/404.html', status=404)

def server_error(request):
    return render(request, 'portfolio/500.html', status=500)

def permission_denied(request, exception):
    return render(request, 'portfolio/403.html', status=403)

def bad_request(request, exception):
    return render(request, 'portfolio/400.html', status=400)

# Функция для обработки загрузки файлов
def handle_uploaded_file(f):
    name, ext = os.path.splitext(f.name)
    unique_name = f"{name}_{uuid.uuid4()}{ext}"
    upload_path = os.path.join('uploads', unique_name)
    with open(os.path.join('media', upload_path), 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return upload_path

# Главная страница
class PortfolioListView(DataMixin, ListView):
    model = PortfolioItem
    template_name = 'portfolio/index.html'
    context_object_name = 'items'
    title_page = 'Портфолио'

    def get_queryset(self):
        return PortfolioItem.published.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item_count'] = self.get_queryset().count()
        context['has_items'] = context['item_count'] > 0
        context['first_item'] = self.get_queryset().first()
        context['last_item'] = self.get_queryset().last()
        return self.get_mixin_context(context)

# Детальная страница портфолио
class PortfolioDetailView(DataMixin, DetailView):
    model = PortfolioItem
    template_name = 'portfolio/portfolio_detail.html'
    context_object_name = 'item'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        return get_object_or_404(PortfolioItem.published, slug=self.kwargs[self.slug_url_kwarg])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, title=self.object.title)

# Архив по годам
class ArchiveByYearView(DataMixin, ListView):
    model = PortfolioItem
    template_name = 'portfolio/archive.html'
    context_object_name = 'items'
    allow_empty = True

    def get_queryset(self):
        year = self.kwargs['year']
        if year > datetime.now().year:
            return PortfolioItem.objects.none()
        return PortfolioItem.objects.filter(created_at__year=year).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = self.kwargs['year']
        return self.get_mixin_context(context, title=f'Архив за {year} год', year=year)

# Категории
class CategoryDetailView(DataMixin, ListView):
    model = PortfolioItem
    template_name = 'portfolio/category_detail.html'
    context_object_name = 'items'
    allow_empty = False

    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs['cat_slug'])
        return PortfolioItem.published.filter(category=category).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(Category, slug=self.kwargs['cat_slug'])
        return self.get_mixin_context(context, title=f'Категория: {category.name}', category=category)

# Теги
class TagDetailView(DataMixin, ListView):
    model = PortfolioItem
    template_name = 'portfolio/tag_detail.html'
    context_object_name = 'items'
    allow_empty = False

    def get_queryset(self):
        tag = get_object_or_404(Tag, slug=self.kwargs['tag_slug'])
        return PortfolioItem.published.filter(tags=tag).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = get_object_or_404(Tag, slug=self.kwargs['tag_slug'])
        return self.get_mixin_context(context, title=f'Тег: {tag.name}', tag=tag)

# Создание портфолио
class PortfolioCreateNonModelView(DataMixin, CreateView):
    form_class = NonModelPortfolioForm
    template_name = 'portfolio/portfolio_create_non_model.html'
    success_url = reverse_lazy('portfolio:portfolio_list')
    title_page = 'Добавление портфолио'

    def form_valid(self, form):
        portfolio_item = PortfolioItem.objects.create(
            title=form.cleaned_data['title'],
            description=form.cleaned_data['description'],
            slug=form.cleaned_data['slug'],
            is_published=form.cleaned_data['is_published'],
            category=form.cleaned_data['category'],
            image=form.cleaned_data['image']
        )
        portfolio_item.tags.set(form.cleaned_data['tags'])
        return super().form_valid(form)

# Вспомогательная функция для проверки AJAX-запросов
def is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'

# Создание портфолио с AJAX
class PortfolioCreateView(DataMixin, CreateView):
    form_class = PortfolioItemForm
    template_name = 'portfolio/partial_portfolio_create.html'
    success_url = reverse_lazy('portfolio:portfolio_list')
    title_page = 'Добавление портфолио'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        if is_ajax(request):
            html_form = render_to_string(
                self.template_name,
                {'form': form},
                request=self.request
            )
            return JsonResponse({'html_form': html_form})
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        if is_ajax(self.request):
            data = {
                'form_is_valid': True,
                'html_portfolio_list': render_to_string(
                    'portfolio/partial_portfolio_list.html',
                    {'items': PortfolioItem.objects.all().order_by('-created_at')},
                    request=self.request
                )
            }
            return JsonResponse(data)
        return super().form_valid(form)

    def form_invalid(self, form):
        if is_ajax(self.request):
            data = {
                'form_is_valid': False,
                'html_form': render_to_string(
                    self.template_name,
                    {'form': form},
                    request=self.request
                )
            }
            return JsonResponse(data)
        return super().form_invalid(form)

class PortfolioUpdateView(DataMixin, UpdateView):
    model = PortfolioItem
    form_class = PortfolioItemForm
    template_name = 'portfolio/partial_portfolio_update.html'
    success_url = reverse_lazy('portfolio:portfolio_list')
    title_page = 'Редактирование портфолио'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(instance=self.object)
        if is_ajax(request):
            html_form = render_to_string(
                self.template_name,
                {'form': form, 'object': self.object},
                request=self.request
            )
            return JsonResponse({'html_form': html_form})
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        if is_ajax(self.request):
            data = {
                'form_is_valid': True,
                'html_portfolio_list': render_to_string(
                    'portfolio/partial_portfolio_list.html',
                    {'items': PortfolioItem.objects.all().order_by('-created_at')},
                    request=self.request
                )
            }
            return JsonResponse(data)
        return super().form_valid(form)

    def form_invalid(self, form):
        if is_ajax(self.request):
            data = {
                'form_is_valid': False,
                'html_form': render_to_string(
                    self.template_name,
                    {'form': form, 'object': self.object},
                    request=self.request
                )
            }
            return JsonResponse(data)
        return super().form_invalid(form)

class PortfolioDeleteView(DataMixin, DeleteView):
    model = PortfolioItem
    template_name = 'portfolio/partial_portfolio_delete.html'
    success_url = reverse_lazy('portfolio:portfolio_list')
    title_page = 'Удаление портфолио'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if is_ajax(request):
            html_form = render_to_string(
                self.template_name,
                {'object': self.object},
                request=self.request
            )
            return JsonResponse({'html_form': html_form})
        return super().get(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if is_ajax(request):
            data = {
                'form_is_valid': True,
                'html_portfolio_list': render_to_string(
                    'portfolio/partial_portfolio_list.html',
                    {'items': PortfolioItem.objects.all().order_by('-created_at')},
                    request=self.request
                )
            }
            return JsonResponse(data)
        return super().delete(request, *args, **kwargs)

# Загрузка файла
class UploadFileView(DataMixin, FormView):
    form_class = UploadFileForm
    template_name = 'portfolio/upload_file.html'
    success_url = reverse_lazy('portfolio:upload_success')
    title_page = 'Загрузка файла'

    def form_valid(self, form):
        file_path = handle_uploaded_file(form.cleaned_data['file'])
        return render(self.request, 'portfolio/upload_success.html', {'file_path': file_path})