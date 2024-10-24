import os
from threading import Thread
import time
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import numpy as np
import openpyxl
from django.core.files.storage import default_storage
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .logic.algorithm import KohonenAlgorithm

from .logic.data_set import DatasetBuilder
from .models import ImageVector, KohonenConfig, Image
from .serializers import KohonenConfigSerializer, ImageSerializer
from .logic.image_handler import ImageHandler
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class KohonenConfigListCreate(generics.ListCreateAPIView):
    queryset = KohonenConfig.objects.all()
    serializer_class = KohonenConfigSerializer

class KohonenConfigDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = KohonenConfig.objects.all()
    serializer_class = KohonenConfigSerializer

class ImageListCreate(generics.ListCreateAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

class ImageDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            image_path = instance.image.path
            if os.path.isfile(image_path):
                os.remove(image_path)
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HealthCheck(APIView):
    def get(self, request):
        try:
            return Response({"status": "OK"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ImageProcess(APIView):
    def post(self, request):
        try:
            ImageVector.objects.all().delete()
            
            images = Image.objects.all()
            image_paths = [image.image.path for image in images]
            dataset = DatasetBuilder(image_paths)
            dataset.process_images()
            
            for image, vector in zip(images, dataset.column_vectors):
                ImageVector.objects.create(
                    image=image,
                    vector=vector.tolist()
                )
            vectors = ImageVector.objects.filter(image__in=images).values('image__name', 'vector')

            return Response({"vectors": list(vectors)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ImageVectors(APIView):
    def get(self, request):
        try:
            vectors = ImageVector.objects.values('image__name', 'vector')

            # Verificar si existen datasets
            if not vectors.exists():  # Si no hay vectores, retornar un mensaje apropiado
                return Response({"message": "No datasets found"}, status=status.HTTP_404_NOT_FOUND)

            # Si existen, retornar los vectores
            return Response({"vectors": list(vectors)}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ImageVectorsToExcel(APIView):
    def get(self, request):
        try:
            vectors = list(ImageVector.objects.values('image__name', 'vector'))

            # Verificar si existen datasets
            if not vectors:  # Si no hay vectores, retornar un mensaje apropiado
                return Response({"message": "No datasets found"}, status=status.HTTP_404_NOT_FOUND)

            # Ordenar los vectores por nombre de imagen
            vectors.sort(key=lambda x: x['image__name'])  # Ordenar alfabéticamente por 'image__name'

            # Crear un libro de trabajo de Excel
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = "Image Vectors"

            # Agregar encabezados
            sheet.append(['Imagen'] + [f'X{i+1}' for i in range(len(vectors[0]['vector']))])

            # Agregar los datos de los vectores
            for vector in vectors:
                image_name = vector['image__name']
                # Suponiendo que 'vector' es una lista; ajusta esto si es un formato diferente
                vector_values = vector['vector']
                sheet.append([image_name] + vector_values)

            # Crear un objeto HttpResponse con el contenido del archivo Excel
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="image_vectors.xlsx"'

            # Guardar el libro de trabajo en el objeto HttpResponse
            workbook.save(response)

            return response

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
"""class ExecuteKohonenTraining(APIView):
    def get(self, request):
        try:
            # 1. Recibir el id de la configuracion a aplicar
            # 2. Obtener la configuracion de la bd
            # 3. Activar el algoritmo
            # 4. Retornar datos para la grafica del dm, tiempo transcurrido, iteracion.
            vectors = ImageVector.objects.values('image__name', 'vector')


        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)"""
        

class ExecuteKohonenTraining(APIView):
    def post(self, request, config_id):
        try:
            config = KohonenConfig.objects.get(id=config_id)
            neurons = config.neurons
            iterations = config.iterations
            
            entries = self.load_entries_from_db()

            kohonen = KohonenAlgorithm(
                entries=entries,
                neurons=neurons,
                iterations=iterations,
                config_id=config_id
            )
            kohonen.train()
            return Response({"message": "Training Finished"}, status=status.HTTP_200_OK)

        except KohonenConfig.DoesNotExist:
            return Response({"error": "Configuración no encontrada"}, status=404)
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=500)
        
    def load_entries_from_db(self):
        try:
            image_vectors = ImageVector.objects.values_list('vector', flat=True)

            entries = np.array([np.fromiter(vector, dtype=float) for vector in image_vectors if isinstance(vector, list)])

            if entries.size == 0:
                print("No se encontraron vectores en la base de datos.")
                return None

            return entries
        except Exception as e:
            print(f"Error al cargar los datos de la base de datos: {str(e)}")
            return None

