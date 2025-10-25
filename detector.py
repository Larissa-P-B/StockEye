# detector

# import os
# import numpy as np
# from PIL import Image
# import tensorflow as tf
#
# # ===================== Classe Detector =====================
# class SavedModelDetector:
#     def __init__(self, model_path=None, class_indices=None, img_size=(224, 224), threshold=0.5):
#         """
#         model_path: caminho da pasta SavedModel (contendo saved_model.pb)
#         class_indices: lista de nomes das classes
#         img_size: tamanho de input esperado pelo modelo
#         threshold: probabilidade mínima para considerar válido
#         """
#         self.img_size = img_size
#         self.threshold = threshold
#
#         # nomes das classes
#         if class_indices is None:
#             self.class_indices = ["Luvas Cirúrgicas", "Máscara N95", "Seringa 5ml"]
#         else:
#             self.class_indices = class_indices
#
#         # define caminho padrão relativo ao projeto
#         if model_path is None:
#             base_dir = os.path.dirname(os.path.abspath(__file__))
#             model_path = os.path.join(base_dir, "save_model")
#
#         # verifica se o modelo existe
#         if not os.path.exists(model_path):
#             raise FileNotFoundError(
#                 f"Modelo não encontrado em: {model_path}\n"
#                 "Certifique-se de que a pasta 'save_model/' existe no diretório do projeto."
#             )
#
#         # carregar modelo SavedModel
#         self.model = tf.keras.models.load_model(model_path)
#
#     def preprocess(self, pil_img):
#         """Redimensiona e normaliza imagem"""
#         img = pil_img.resize(self.img_size)
#         arr = np.array(img) / 255.0
#         arr = np.expand_dims(arr, axis=0)  # (1, h, w, 3)
#         return arr
#
#     def detect(self, pil_img):
#         """Detecta item mais provável"""
#         x = self.preprocess(pil_img)
#         preds = self.model.predict(x, verbose=0)[0]
#
#         best_idx = int(np.argmax(preds))
#         best_prob = float(preds[best_idx])
#
#         if best_prob >= self.threshold:
#             return self.class_indices[best_idx]
#         else:
#             return None
#
#
# # ===================== Instância global =====================
# # Caminho relativo (não absoluto!)
# global_detector = SavedModelDetector(
#     model_path=None,
#     class_indices=["Luvas Cirúrgicas", "Máscara N95", "Seringa 5ml"]
# )
#
#
# # ===================== Função utilitária =====================
# def detect_item(pil_img):
#     """
#     Função para usar no app.py
#     Recebe PIL.Image e retorna o item detectado ou None
#     """
#     return global_detector.detect(pil_img)
#






import numpy as np
import tensorflow as tf
from keras import layers
from PIL import Image
import streamlit as st

# ===================== Classe Detector =====================
class SavedModelDetector:
    def __init__(self, model_path, img_size=(224, 224), threshold=0.5):
        self.img_size = img_size
        self.threshold = threshold
        try:
            # Carrega modelo compatível com Keras 3
            self.model = layers.TFSMLayer(model_path, call_endpoint="serving_default")
            st.success("✅ Modelo carregado com sucesso!")
        except Exception as e:
            st.error(f"❌ Erro ao carregar modelo: {e}")
            self.model = None

    def preprocess_image(self, image):
        """Converte PIL.Image → array normalizado para o modelo"""
        try:
            if isinstance(image, Image.Image):
                image = np.array(image)  # converte PIL para NumPy

            # Redimensiona e normaliza
            img = tf.image.resize(image, self.img_size)
            img = tf.cast(img, tf.float32) / 255.0
            img = tf.expand_dims(img, axis=0)  # (1, h, w, 3)
            return img
        except Exception as e:
            st.error(f"Erro ao pré-processar imagem: {e}")
            return None

    def predict(self, image):
        """Executa predição no frame"""
        if self.model is None:
            st.error("Modelo não carregado.")
            return None

        img = self.preprocess_image(image)
        if img is None:
            return None

        try:
            preds = self.model(img)
            if isinstance(preds, dict):
                preds = list(preds.values())[0].numpy()
            else:
                preds = preds.numpy()
            return preds
        except Exception as e:
            st.error(f"Erro durante a predição: {e}")
            return None


# ===================== Função utilitária =====================
def detect_item(pil_img):
    """Recebe PIL.Image e retorna o nome ou índice do item detectado"""
    preds = global_detector.predict(pil_img)
    if preds is None:
        st.warning("Não foi possível identificar o item.")
        return None

    idx = int(np.argmax(preds))
    prob = float(np.max(preds))

    if prob < 0.5:
        st.warning("Confiança muito baixa.")
        return None

    classes = ["Luvas Cirúrgicas", "Máscara N95", "Seringa 5ml"]
    st.info(f"🧾 Item detectado: {classes[idx]} (confiança: {prob:.2f})")
    return classes[idx]


# ===================== Instância global =====================
MODEL_PATH = "save_model"
global_detector = SavedModelDetector(MODEL_PATH)
