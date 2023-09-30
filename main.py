import asyncio
import aiohttp
import os
from lxml import etree
from openpyxl import Workbook

# Путь к файлу
output_path = "pars_out/getfast.xlsx"
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


# async def build_category_path(product_category_id,tree):
#     for category in tree.xpath(".//category"):
#         category_id = category.get("id")
#         parent_id = category.get("parentId")
#         if product_category_id == category_id:
#             product_path = "Детейлінг" + "/" + parent_id + product_category_id.text
#         return product_path


async def build_category_path(product_category_id, tree):
    category_path = ""
    for category in tree.xpath(".//category[@id='" + product_category_id + "']"):
        category_name = category.text.strip()
        parent_id = category.get("parentId")
        if parent_id:
            parent_category_path = await build_category_path(parent_id, tree)
            if parent_category_path:
                category_path = parent_category_path + "/" + category_name
            else:
                category_path = category_name
        else:
            category_path = category_name
    return category_path




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
        "NameUA",
        "NameRU",
        "Price",
        "old_price",
        "currency",
        "cataloge",
        "picture",
        "description_ua",
        "description_ru",
        "brand",
        "manufacture_code",
        "weight",
        "volume",
        "type",
        "material",
        "diameter",
        "state",
    ]

    # Запись заголовков в первую строку
    sheet.append(headers)

    # Извлечение данных и запись их в Excel
    for product in tree.xpath(".//offer"):
        product_id = product.get("id")
        price = product.find(".//price").text
        currency_id = product.find(".//currencyId").text
        picture = product.find(".//picture").text
        name_ru = product.find(".//name").text
        name_ua = product.find(".//name_ua").text

        product_category_id = product.find(".//categoryId").text
        category_path = await build_category_path(product_category_id, tree)
        category_path = "Детейлінг" + "/" + category_path
        if not category_path:
            category_path = "Детейлінг"

        vendor_element = product.find(".//vendor")
        vendor = vendor_element.text if vendor_element is not None else ""

        vendorCode = product.find(".//vendorCode").text

        description_ua = product.find(".//description_ua")
        description_ua_text = description_ua.text if description_ua is not None else ""
        description_ru = description_ua_text

        volume_param = product.find(".//param[@name='Объем']")
        volume = volume_param.text if volume_param is not None else ""

        type_param = product.find(".//param[@name='Тип']")
        type = type_param.text if type_param is not None else ""

        material_para = product.find(".//param[@name='Материал']")
        material = material_para.text if material_para is not None else ""

        diameter_type = product.find("./param[@name='Диаметр']")
        diameter = diameter_type.text if diameter_type is not None else ""

        state_type = product.find("./param[@name='Состояние']")
        state = state_type.text if state_type is not None else ""

        weight_type = product.find("./param[@name='Вес']")
        weight = weight_type.text if weight_type is not None else ""

        # Создайте словарь с данными для записи
        data = {
            "Product ID": product_id,
            "NameUA": name_ua,
            "NameRU": name_ru,
            "Price": price,
            "old_price": "",
            "currency": currency_id,
            "cataloge": category_path,
            "picture": picture,
            "description_ua": description_ua_text,
            "description_ru": description_ru,
            "brand": vendor,
            "manufacture_code": vendorCode,
            "weight": weight,
            "volume": volume,
            "type": type,
            "material": material,
            "diameter": diameter,
            "state": state,
        }

        # Добавьте данные из словаря в строку Excel в правильном порядке
        row_data = [data[header] for header in headers]
        sheet.append(row_data)

    # Сохранение Excel файла
    workbook.save(output_path)


if __name__ == "__main__":
    asyncio.run(main())
