import os
from PIL import Image as PILImage
import numpy as np
from typing import Tuple

class ImageHandler:
    # Tamaño máximo de la matriz que se utilizará para el padding
    target_rows = 128  # Puedes ajustar esto al tamaño deseado
    target_cols = 128  # Puedes ajustar esto al tamaño deseado

    @staticmethod
    def normalize_image(image: PILImage.Image, size: Tuple[int, int] = (128, 128)) -> PILImage.Image:
        return image.resize(size, PILImage.LANCZOS)

    @staticmethod
    def to_binary_matrix(image: PILImage.Image, threshold: float = 0.5) -> np.ndarray:
        """Convierte una imagen en una matriz binaria."""
        grayscale_image = image.convert('L')  # Convertir a escala de grises
        binary_image = np.array(grayscale_image, dtype=np.float32) / 255.0  # Convertir a matriz NumPy
        matriz_binaria = (binary_image > threshold).astype(np.uint8)  # Aplicar umbral
        matriz_binaria_invertida = 1 - matriz_binaria  # Invertir la matriz binaria
        return matriz_binaria_invertida
    
    @staticmethod
    def crop_image(binary_image: np.ndarray) -> np.ndarray:
        """Recorta la imagen binaria para eliminar espacios en blanco."""
        if not np.any(binary_image == 1):
            raise ValueError("La imagen binaria no contiene píxeles negros para recortar.")
        
        rows = np.any(binary_image == 1, axis=1)
        cols = np.any(binary_image == 1, axis=0)
        
        ymin, ymax = np.where(rows)[0][[0, -1]]
        xmin, xmax = np.where(cols)[0][[0, -1]]
        
        cropped_image = binary_image[ymin:ymax + 1, xmin:xmax + 1]
        
        return cropped_image

    @staticmethod
    def pad_image(image: np.ndarray) -> np.ndarray:
        """Ajusta el tamaño de la imagen al tamaño objetivo, añadiendo ceros."""
        padded_image = np.zeros((ImageHandler.target_rows, ImageHandler.target_cols), dtype=np.uint8)
        padded_image[:image.shape[0], :image.shape[1]] = image
        return padded_image

    """@staticmethod
    def save_binary_matrix_to_txt(binary_matrix: np.ndarray, original_image_path: str):
        Guarda la matriz binaria en un archivo de texto en la carpeta media/images.
        output_dir = 'media'
        os.makedirs(output_dir, exist_ok=True)
        
        original_filename = os.path.splitext(os.path.basename(original_image_path))[0]
        output_filename = os.path.join(output_dir, f"{original_filename}binary.txt")
        
        np.savetxt(output_filename, binary_matrix, fmt='%d')  # Usar formato entero
        print(f"Matriz binaria guardada como: {output_filename}")"""

    @staticmethod
    def process_image(image_path: str) -> np.ndarray:
        """Procesa la imagen: normaliza, convierte a binario, recorta y ajusta el tamaño."""
        with PILImage.open(image_path) as image:
            # Normalizar la imagen
            normalized_image = ImageHandler.normalize_image(image)
            
            # Convertir a matriz binaria
            binary_matrix = ImageHandler.to_binary_matrix(normalized_image)

            try:
                cropped_matrix = ImageHandler.crop_image(binary_matrix)
                return cropped_matrix
            except ValueError as e:
                print(f"Error al recortar la imagen: {e}")
                return binary_matrix