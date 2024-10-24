import numpy as np
from typing import List
from .image_handler import ImageHandler

class DatasetBuilder:
    def __init__(self, image_paths: List[str]):
        self.image_paths = image_paths
        self.data: List[np.ndarray] = []
        self.column_vectors = []

    def process_images(self) -> None:
        """Procesa todas las imágenes y genera los vectores de columnas."""
        for image_path in self.image_paths:
            binary_image = ImageHandler.process_image(image_path)
            self.data.append(binary_image)

        self.stabilize_and_generate_vectors()

    def stabilize_and_generate_vectors(self) -> None:
        if not self.data:
            raise ValueError("No hay imágenes en el dataset para estabilizar.")
        
        max_cols = max(image.shape[1] for image in self.data)

        for idx, image in enumerate(self.data):
            current_cols = image.shape[1]
            if current_cols < max_cols:
                padding_cols = max_cols - current_cols
                image = np.pad(image, pad_width=((0, 0), (0, padding_cols)), mode='constant', constant_values=0)
                self.data[idx] = image  
                
            column_sum = image.sum(axis=0).astype(np.float64)  # Asegurando que sea float64
            self.column_vectors.append(column_sum)

        # Normalizar los vectores
        self.normalize_column_vectors()

    def normalize_column_vectors(self) -> None:
        """Normaliza los vectores de columnas entre 0 y 1, preservando la precisión de los decimales."""
        for idx in range(len(self.column_vectors)):
            max_value = np.max(self.column_vectors[idx])
            if max_value > 0:  # Asegúrate de que el máximo no sea cero para evitar división por cero
                self.column_vectors[idx] = np.round(self.column_vectors[idx] / max_value, 5)  # Redondear a 5 decimales

    def get_column_sums(self) -> List[np.ndarray]:
        return self.column_vectors.copy()

    def get_dataset(self) -> List[np.ndarray]:
        return self.data.copy()
