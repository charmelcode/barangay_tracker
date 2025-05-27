from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('category/<int:category_id>/', views.category_appliances, name='category_appliances'),
    path('register/', views.register, name='register'),

    # User borrow
    path('borrow/<int:appliance_id>/', views.borrow_appliance, name='borrow_appliance'),
    path('borrow/success/', views.borrow_success, name='borrow_success'),
    path('my-borrow-requests/', views.my_borrow_requests, name='my_borrow_requests'),
    path('return-appliance/<int:request_id>/', views.return_appliance, name='return_appliance'),
    
    # appliances/urls.py
    path('dashboard/borrow-requests/', views.borrow_requests_list, name='borrow_requests_list'),
    path('dashboard/borrowers-list/', views.borrowers_list, name='borrowers_list'),
    path('dashboard/borrow-requests/approve/<int:request_id>/', views.approve_borrow_request, name='approve_borrow_request'),
    path('dashboard/borrow-requests/decline/<int:request_id>/', views.decline_borrow_request, name='decline_borrow_request'),
    path('dashboard/add-appliance/', views.add_appliance, name='add_appliance'),
    path('dashboard/edit-appliance/<int:appliance_id>/', views.edit_appliance, name='edit_appliance'),
    path('dashboard/delete-appliance/<int:appliance_id>/', views.delete_appliance, name='delete_appliance'),
]
