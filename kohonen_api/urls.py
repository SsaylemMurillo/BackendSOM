from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.HealthCheck.as_view(), name='health_check'),
    path('configurations/', views.KohonenConfigListCreate.as_view(), name='configurations_list_create'),
    path('configurations/<int:pk>/', views.KohonenConfigDetail.as_view(), name='configurations_detail'),
    path('images/', views.ImageListCreate.as_view(), name='images_list_create'),
    path('images/<int:pk>/', views.ImageDetail.as_view(), name='images_detail'),  # Nueva ruta para el detalle
    path('process-image/', views.ImageProcess.as_view(), name='process_image'),  # Nueva ruta para procesar imágenes
    path('image-vectors/', views.ImageVectors.as_view(), name='image_vectors'),  # Ruta para obtener los vectores
    path('image-vectors-to-excel/', views.ImageVectorsToExcel.as_view(), name='image_vectors_to_excel'),
    path('execute-configuration/<int:config_id>', views.ExecuteKohonenTraining.as_view(), name='execute_configuration'),
]
