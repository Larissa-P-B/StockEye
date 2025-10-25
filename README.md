# 📦 StockEye - A visão artificial a serviço do seu laboratório.

## 🔹 Descrição
**StockEye** é uma aplicação web interativa que utiliza **visão computacional** e **deep learning** para detectar automaticamente itens em estoque, especificamente:

- **Caixas de Máscara N95**  
- **Luvas Cirúrgicas**  
- **Seringas 5ml**

O sistema permite capturar imagens com a câmera do dispositivo e identificar o item em tempo real, exibindo o resultado no navegador.

O projeto foi desenvolvido com:
- Python 3.11  
- Streamlit  
- TensorFlow / Keras 3  
- OpenCV e Pillow  
- Modelo de deep learning em formato **SavedModel (`.pb`)**  

---

## 🔹 Funcionalidades

- Captura de imagens via câmera integrada ou upload de arquivo.  
- Pré-processamento de imagem (redimensionamento, normalização).  
- Predição de itens utilizando modelo treinado (`SavedModel`).  
- Exibição do item detectado e confiança da predição em tempo real.  

---

## 🔹 Estrutura do Projeto

```
stockeye/
├── app.py # Aplicação Streamlit principal
├── detector.py # Classe e funções para detectar itens com modelo SavedModel
├── save_model/ # Modelo treinado (SavedModel .pb)
│ ├── saved_model.pb
│ └── variables/
│ ├── variables.data-00000-of-00001
│ └── variables.index
├── requirements.txt # Dependências do projeto
└── README.md # Este arquivo
```
---

## 🔹 Pré-requisitos

- Python 3.11  
- Navegador web moderno  
- Modelo `SavedModel` presente na pasta `save_model/`

---

## 🔹 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/stockeye.git
cd stockeye
```
2. Crie e ative um ambiente virtual (opcional mas recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
3. Instale as dependências:
```bash
pip install -r requirements.txt
```

---
🔹 Uso Local

Execute a aplicação:
```
streamlit run app.py
```

Abra o navegador no endereço fornecido pelo Streamlit (normalmente http://localhost:8501).

Tire uma foto ou faça upload de um item do estoque (apenas caixas de máscara, luvas ou seringas 5ml).

A aplicação exibirá o item detectado e a confiança da predição.

🔹 Deploy no Streamlit Cloud

Faça push do projeto para o GitHub:
```
git add .
git commit -m "Deploy StockEye"
git push
```

Acesse Streamlit Cloud
 e conecte sua conta GitHub.

Crie um novo app selecionando o repositório stockeye e a branch correta.

Clique em “Deploy”. O Streamlit instalará automaticamente as dependências do requirements.txt.

Se tudo estiver correto, a aplicação estará online com acesso à câmera.

---
🔹 Observações

O modelo identifica apenas caixas de máscara N95, luvas cirúrgicas e seringas 5ml.

O modelo deve estar na pasta save_model/ para que a detecção funcione.

Caso o modelo seja muito grande, você pode usar uma versão hospedada na nuvem (Google Drive, Hugging Face) e baixar dinamicamente na inicialização.

A aplicação foi testada com Python 3.11, TensorFlow 2.17 e Keras 3.4.1.

---
🔹 Estrutura das Classes

SavedModelDetector: classe responsável por carregar o modelo, pré-processar imagens e realizar predições.

detect_item(): função auxiliar que recebe uma imagem PIL e retorna o item detectado.

---

🔹 Tecnologias Utilizadas

| Tecnologia           | Função                       |
| -------------------- | ---------------------------- |
| Python 3.11          | Linguagem principal          |
| Streamlit            | Interface web interativa     |
| TensorFlow / Keras 3 | Deep learning para detecção  |
| OpenCV               | Pré-processamento de imagens |
| Pillow               | Manipulação de imagens PIL   |
| NumPy                | Operações numéricas e arrays |

--- 

🔹 Contato

Projeto desenvolvido por: [StockEye]

