# Bastidor para PDF

Este projeto implementa um sistema de rastreio círculos em imagens com OpenCV, reescalando-as e recortando-as para que se fiquem com exatos 20cm de diâmetro (tamanho padrão para bastidores de bordado) em um PDF de folha A4.

Sendo assim, é possível alimentar o projeto com imagens contendo bastidores com os desenhos desejados, e o bastidor-para-pdf irá devolver arquivos PDF prontos para impressão.

## Funcionalidades

- Detecção de circulos em imagens.
- Recorte e redimensionamento do circulo principal.
- Conversão para PDF

## Executando o Projeto

Para executar o bastidor-para-pdf, adicione as imagens desejadas na pasta 'imagens' e simplesmente execute o script `main.py` com Python. Colete os PDFs na pasta 'pdfs'

```bash
python main.py
```
# Calibrando a Detecção

É possível que os parametros precisem de ajuste para alguns casos (imagens mais escuras, imagens com muitos detalhes, etc). 

Ajuste os Parametros até que consiga um resultado desejável.

```python
PARAMS = {
    'minDist': 32, # Diminuir para detectar círculos menores, aumentar para detectar círculos maiores
    'param1': 30, # Alterar moderadamente caso a detecção de círculos não esteja funcionando para o seu caso
    'param2': 550, # Quanto maior, menos círculos são detectados (se aproxima do círculo 'principal' da imagem)
}
```

Desenvolvido por: Thor Galli

Quaisquer dúvidas: gallithor@gmail.com
