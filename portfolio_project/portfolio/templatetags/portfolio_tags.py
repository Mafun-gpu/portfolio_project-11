from django import template
from portfolio.models import PortfolioItem, Category, Tag
from django.db.models import Count

register = template.Library()

@register.simple_tag
def portfolio_count():
    return PortfolioItem.objects.count()

@register.inclusion_tag('portfolio/partial_categories.html')
def show_categories(selected_cat_slug=None):
    categories = Category.objects.annotate(total=Count('portfolio_items')).filter(total__gt=0)
    return {'categories': categories, 'selected_cat_slug': selected_cat_slug}

@register.inclusion_tag('portfolio/partial_tags.html')
def show_tags():
    tags = Tag.objects.annotate(total=Count('portfolio_items')).filter(total__gt=0)
    return {'tags': tags}