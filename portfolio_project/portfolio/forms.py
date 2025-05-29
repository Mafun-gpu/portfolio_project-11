from django import forms
from .models import Category, Tag, PortfolioItem

class UploadFileForm(forms.Form):
    file = forms.FileField(label="Файл", widget=forms.FileInput(attrs={'class': 'form-control'}))

class NonModelPortfolioForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        min_length=5,
        label="Название",
        error_messages={
            'required': 'Название обязательно.',
            'min_length': 'Название слишком короткое (минимум 5 символов).'
        }
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),
        label="Описание",
        required=False
    )
    slug = forms.SlugField(
        max_length=255,
        label="Слаг",
        error_messages={'required': 'Слаг обязателен.'}
    )
    is_published = forms.BooleanField(
        label="Опубликовано",
        required=False,
        initial=True
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="Категория",
        empty_label="Выберите категорию"
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        label="Теги",
        required=False
    )
    image = forms.ImageField(
        label="Изображение",
        required=False
    )

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and any(char.isdigit() for char in title):
            raise forms.ValidationError("Название не должно содержать цифры.")
        return title
    

class PortfolioItemForm(forms.ModelForm):
    class Meta:
        model = PortfolioItem
        fields = ['title', 'description', 'image', 'slug', 'is_published', 'category', 'tags', 'client']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'image': 'Изображение',
            'slug': 'Слаг',
            'is_published': 'Опубликовано',
            'category': 'Категория',
            'tags': 'Теги',
            'client': 'Клиент',
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title and len(title) > 50:
            raise forms.ValidationError("Название не должно превышать 50 символов.")
        return title