from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.home, name='home'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('buy/<int:item_id>/', views.buy_item, name='buy_item'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('buy/order/<int:order_id>/', views.buy_order, name='buy_order'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
]
