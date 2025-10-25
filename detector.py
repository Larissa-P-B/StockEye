# detector

import os
import numpy as np
from PIL import Image
import tensorflow as tf

# ===================== Classe Detector =====================
class SavedModelDetector:
    def __init__(self, model_path=None, class_indices=None, img_size=(224, 224), threshold=0.5):
        """
        model_path: caminho da pasta SavedModel (contendo saved_model.pb)
        class_indices: lista de nomes das classes
        img_size: tamanho de input esperado pelo modelo
        threshold: probabilidade mínima para considerar válido
        """
        self.img_size = img_size
        self.threshold = threshold

        # nomes das classes
        if class_indices is None:
            self.class_indices = ["Luvas Cirúrgicas", "Máscara N95", "Seringa 5ml"]
        else:
            self.class_indices = class_indices

        # define caminho padrão relativo ao projeto
        if model_path is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base_dir, "save_model")

        # verifica se o modelo existe
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Modelo não encontrado em: {model_path}\n"
                "Certifique-se de que a pasta 'save_model/' existe no diretório do projeto."
            )

        # carregar modelo SavedModel
        self.model = tf.keras.models.load_model(model_path)

    def preprocess(self, pil_img):
        """Redimensiona e normaliza imagem"""
        img = pil_img.resize(self.img_size)
        arr = np.array(img) / 255.0
        arr = np.expand_dims(arr, axis=0)  # (1, h, w, 3)
        return arr

    def detect(self, pil_img):
        """Detecta item mais provável"""
        x = self.preprocess(pil_img)
        preds = self.model.predict(x, verbose=0)[0]

        best_idx = int(np.argmax(preds))
        best_prob = float(preds[best_idx])

        if best_prob >= self.threshold:
            return self.class_indices[best_idx]
        else:
            return None


# ===================== Instância global =====================
# Caminho relativo (não absoluto!)
global_detector = SavedModelDetector(
    model_path=None,
    class_indices=["Luvas Cirúrgicas", "Máscara N95", "Seringa 5ml"]
)


# ===================== Função utilitária =====================
def detect_item(pil_img):
    """
    Função para usar no app.py
    Recebe PIL.Image e retorna o item detectado ou None
    """
    return global_detector.detect(pil_img)

