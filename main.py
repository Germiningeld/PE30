import random
import requests
import base64
import os
import time
from dotenv import load_dotenv
from iam_updater import get_actual_iam

load_dotenv()

# Получаем актуальный IAM токен
iam = get_actual_iam()
if not iam:
    print("Не удалось получить IAM токен")
    exit(1)

catalog_id = os.environ["CATALOG_ID"]

model_url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/imageGenerationAsync'

headers = {
    "Authorization": f"Bearer {iam}",
    "Content-Type": "application/json"
}

data = {
    "modelUri": f"art://{catalog_id}/yandex-art/latest",
    "generationOptions": {
        "seed": f"{random.randint(0, 1000000)}",
        "aspectRatio": {
            "widthRatio": "16",
            "heightRatio": "9"
        }
    },
    "messages": [
        {
            "weight": "1",
            "text": "стеклянный единорог с переливающейся радужной гривой, создающий вокруг себя вихрь из звездной пыли и кристаллов, магическое свечение, сюрреалистичный стиль, фэнтезийная иллюстрация"
        }
    ]
}

get_id = requests.post(model_url, headers=headers, json=data)
if get_id.status_code == 200:
    response_id = get_id.json()["id"]
    print(response_id)
    time.sleep(10)

    get_image_url = f"https://llm.api.cloud.yandex.net:443/operations/{response_id}"
    get_image = requests.get(get_image_url, headers=headers)

    # Проверяем успешность запроса
    if get_image.status_code == 200:
        # Получаем base64 строку изображения
        image_base64 = get_image.json()['response']['image']

        # Декодируем base64 в бинарные данные
        image_data = base64.b64decode(image_base64)

        # Сохраняем в файл
        with open('image.jpeg', 'wb') as f:
            f.write(image_data)
    else:
        print(f"Ошибка: {get_image.status_code}")
        print(get_image.text)

else:
    print(get_id.text)
