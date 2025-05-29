from django.urls import path
from . import views
from .converters import FourDigitYearConverter

app_name = 'portfolio'
urlpatterns = [
    path('', views.PortfolioListView.as_view(), name='portfolio_list'),
    path('detail/<slug:slug>/', views.PortfolioDetailView.as_view(), name='portfolio_detail'),
    path('archive/<yyyy:year>/', views.ArchiveByYearView.as_view(), name='archive_by_year'),
    path('category/<slug:cat_slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('tag/<slug:tag_slug>/', views.TagDetailView.as_view(), name='tag_detail'),
    path('create-non-model/', views.PortfolioCreateNonModelView.as_view(), name='portfolio_create_non_model'),
    path('create/', views.PortfolioCreateView.as_view(), name='portfolio_create'),
    path('edit/<slug:slug>/', views.PortfolioUpdateView.as_view(), name='portfolio_update'),
    path('delete/<slug:slug>/', views.PortfolioDeleteView.as_view(), name='portfolio_delete'),
    path('upload/', views.UploadFileView.as_view(), name='upload_file'),
]