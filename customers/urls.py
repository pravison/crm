from django.urls import path
from . import views

urlpatterns = [
    path('add-interaction/<int:id>/', views.add_interaction, name='add_interaction'),
    path('edit-escalation/<int:id>/', views.edit_escalation, name='edit_escalation'),
]

