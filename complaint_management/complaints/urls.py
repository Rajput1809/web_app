from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('dashboard/', views.dashboard, name='dashboard'),  # Admin or engineer dashboard
    path('raise/', views.raise_complaint, name='raise_complaint'),  # Raise a new complaint
    path('user/complaints/', views.view_user_complaints, name='view_user_complaints'),  # View user complaints
    path('engineer/complaints/', views.engineer_view_complaints, name='engineer_view_complaints'),  # Engineer's complaint list
    path('accept/<int:complaint_id>/', views.accept_complaint, name='accept_complaint'),
    path('engineer/accept/<int:complaint_id>/', views.accept_complaint, name='accept_complaint'),  # Accept a complaint
    path('engineer/notify/', views.notify_user, name='notify_user'),
    path('engineer/update_status/<int:complaint_id>/', views.update_complaint_status, name='update_status'),  # Update status of a complaint

]
 