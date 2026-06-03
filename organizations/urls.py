from django.urls import path
from . import views

urlpatterns = [
    # Organization
    path('', views.OrganizationListCreateView.as_view(), name='org-list'),
    path('<int:pk>/', views.OrganizationDetailView.as_view(), name='org-detail'),

    # Public — бот учун (токен лозим нест)
    path('public/', views.PublicOrgsView.as_view(), name='org-public'),
    path('<int:pk>/branches/public/', views.PublicBranchesView.as_view(), name='branch-public'),

    # Branch
    path('<int:org_id>/branches/', views.BranchListCreateView.as_view(), name='branch-list'),
    path('<int:org_id>/branches/<int:pk>/', views.BranchDetailView.as_view(), name='branch-detail'),

    # Window
    path('<int:org_id>/branches/<int:branch_id>/windows/', views.WindowListCreateView.as_view(), name='window-list'),
    path('<int:org_id>/branches/<int:branch_id>/windows/<int:pk>/', views.WindowDetailView.as_view(), name='window-detail'),
]