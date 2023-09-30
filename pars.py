import requests
from bs4 import BeautifulSoup

# Отправляем GET-запрос на указанный URL
url = "https://getfast.ua/ua/product_list"
response = requests.get(url)

# Проверяем успешность запроса
if response.status_code == 200:
    # Инициализируем BeautifulSoup для анализа HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Теперь вы можете использовать BeautifulSoup для извлечения данных из страницы
    # Например, найдем все заголовки h1 на странице
    headings = soup.find_all('h1')
    for heading in headings:
        print(heading.text)

else:
    print("Ошибка при отправке запроса")
