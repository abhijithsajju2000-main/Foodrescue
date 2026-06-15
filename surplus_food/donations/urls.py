from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.DonationListView.as_view(), name='donation-list'),
    
    path('donation/add/', views.AddDonationView.as_view(), name='add-donation'),
    
    path('donation/<str:uuid>/', views.DonationDetailView.as_view(), name='donation-detail'),
    
    path('donation/<str:uuid>/claim/', views.ClaimFoodView.as_view(), name='claim-food'),
    
    path('donation/<str:uuid>/edit/', views.EditDonationView.as_view(), name='edit-donation'),
    
    path('donation/<str:uuid>/delete/', views.DeleteDonationView.as_view(), name='delete-donation'),
    
    path('dashboard/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
    
    path('dashboard/users/', views.AdminUsersView.as_view(), name='admin-users'),
    
    path('dashboard/ngo/verify/<int:id>/', views.VerifyNGOView.as_view(), name='verify-ngo'), #The user's database id is a number

    path('my-donations/', views.MyDonationsView.as_view(), name='my-donations'),
    
    path('my-claims/', views.MyClaimsView.as_view(), name='my-claims'),
    
    path('donation/<str:uuid>/payment/', views.PaymentView.as_view(), name='payment'),
    
    path('donation/<str:uuid>/payment/success/', views.PaymentSuccessView.as_view(), name='payment-success'),
    
    
    
]
