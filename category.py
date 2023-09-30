import asyncio
import aiohttp
import os
from lxml import etree
from openpyxl import Workbook

# Путь к файлу
output_path = "pars_out/getfast_product_category.xlsx"
output_directory = "pars_out"

# Извлекаем директорию из пути
output_directory = os.path.dirname(output_path)

# Проверяем существование директории и создаем ее, если она не существует
if not os.path.exists(output_directory):
    os.makedirs(output_directory)


# Функция для асинхронного скачивания XML с вашей ссылки
async def download_xml(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()


async def build_category_path(category_id, categories):
    def get_category_path(cat_id):
        category = categories.get(cat_id)
        if category:
            parent_id = category.get("parentID")
            if parent_id:
                parent_path = get_category_path(parent_id)
                return f"{parent_path}/{category.get('name')}"
            else:
                return category.get("name")
        return ""

    return get_category_path(category_id)


async def main():
    # Загрузка XML с вашей ссылки
    url = "https://getfast.ua/products_feed.xml?hash_tag=0e373656e582f62e6ad1aef067cb3e30&sales_notes=&product_ids=&label_ids=6503389%2C6503380%2C6503457%2C7793793%2C6503404%2C6503393%2C6503483&exclude_fields=description&html_description=0&yandex_cpa=&process_presence_sure=&languages=uk%2Cru&group_ids="

    xml_data = await download_xml(url)
    tree = etree.XML(xml_data)

    # Создание нового Excel файла
    workbook = Workbook()
    sheet = workbook.active

    # Заголовки столбцов в Excel
    headers = [
        "Product ID",
        "cataloge",

    ]

    # Запись заголовков в первую строку
    sheet.append(headers)


    # Извлечение данных и запись их в Excel
    for param in tree.xpath(".//shop"):
        if param == tree.xpath(".//offer"):
            for product in tree.xpath(".//offer"):
                product_id = product.get("id")
                product_category = product.get(".//categoryId")
                product_path = build_category_path(category_id, product_category)

        elif param == tree.xpath(".//offer"):
            categories = {}
            categories_elem = tree.find(".//categories")
            for category_elem in categories_elem.findall(".//category"):
                category_id = category_elem.get("id")
                category_name = category_elem.get("name")
                parent_id = category_elem.get("parentID")
                categories[category_id] = {"id": category_id, "name": category_name, "parentID": parent_id}







        # Создайте словарь с данными для записи
        data = {
            "Product ID": product_id,
            "catalog": category_path,
        }

        # Добавьте данные из словаря в строку Excel в правильном порядке
        row_data = [data[header] for header in headers]
        sheet.append(row_data)

    # Сохранение Excel файла
    workbook.save(output_path)


if __name__ == "__main__":
    asyncio.run(main())
