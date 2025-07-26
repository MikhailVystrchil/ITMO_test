import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Настройки
url = "https://abit.itmo.ru/program/master/ai"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
download_folder = "downloaded_pdfs"
os.makedirs(download_folder, exist_ok=True)  # Создаем папку для PDF

# Получаем HTML страницы
response = requests.get(url, headers=headers)
response.raise_for_status()

# Парсим HTML
soup = BeautifulSoup(response.text, 'html.parser')

# Ищем все ссылки, содержащие PDF
pdf_links = set()  # Используем set, чтобы избежать дубликатов

# Вариант 1: Ищем по расширению .pdf
for a in soup.find_all('a', href=True):
    href = a['href']
    if re.search(r'\.pdf$', href, re.IGNORECASE):  # Ищем ссылки, оканчивающиеся на .pdf
        full_url = urljoin(url, href)  # Преобразуем относительную ссылку в абсолютную
        pdf_links.add(full_url)

# Вариант 2: Ищем по тексту кнопки (например, "учебный план", "скачать PDF")
for a in soup.find_all('a'):
    text = a.get_text(strip=True).lower()
    if any(keyword in text for keyword in ["pdf", "учебный план", "скачать"]):
        href = a.get('href', '')
        if href:
            full_url = urljoin(url, href)
            pdf_links.add(full_url)

# Вариант 3: Ищем в JavaScript-данных (если PDF подгружаются динамически)
for script in soup.find_all('script'):
    if script.string:
        js_links = re.findall(r'"(https?://.*?\.pdf)"', script.string)
        pdf_links.update(js_links)

# Скачиваем все найденные PDF
if not pdf_links:
    print("Не найдено ни одного PDF-файла.")
else:
    print(f"Найдено {len(pdf_links)} PDF-файлов. Начинаю загрузку...")

    for i, pdf_url in enumerate(pdf_links, 1):
        try:
            print(f"Скачиваю ({i}/{len(pdf_links)}): {pdf_url}")
            pdf_response = requests.get(pdf_url, headers=headers, stream=True)
            pdf_response.raise_for_status()

            # Извлекаем имя файла из URL
            filename = os.path.join(download_folder, f"document_{i}.pdf")

            # Сохраняем PDF
            with open(filename, 'wb') as f:
                for chunk in pdf_response.iter_content(1024):
                    f.write(chunk)
            print(f"✅ Успешно сохранен: {filename}")

        except Exception as e:
            print(f"❌ Ошибка при загрузке {pdf_url}: {e}")

print("Завершено.")