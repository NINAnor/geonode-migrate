from django.urls import path

from .views import UpdateUserPassword, UpdateResourceOwner

urlpatterns = [
    path('api/v2/extra/admin-set-user-password/', view=UpdateUserPassword.as_view()),
    path('api/v2/extra/admin-set-resource-owner/', view=UpdateResourceOwner.as_view()),
]
