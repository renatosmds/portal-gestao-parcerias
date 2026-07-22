from django.urls import path
from .views import (
    CursoList,
    CursoCreate,
    CursoUpdate,
    CursoDelete
)

urlpatterns = [
    path('list/', CursoList.as_view(), name='list_curso'),
    path('novo/', CursoCreate.as_view(), name='create_curso'),
    # path('novo/<int:funcionario_id>/', CursoCreate.as_view(), name='create_curso'),
    path('update/<int:pk>/', CursoUpdate.as_view(), name='update_curso'),
    path('delete/<int:pk>/', CursoDelete.as_view(), name='delete_curso'),
]
