import json
from collections import defaultdict
import pdfplumber
from datetime import datetime


def extract_courses_from_pdf(pdf_path, program_name):
    """Извлекает данные о курсах из PDF файла"""
    data = {
        "courses": defaultdict(list),
        "semesters": defaultdict(list),
        "categories": defaultdict(list),
        "total_credits": 0,
        "total_hours": 0
    }

    current_semester = None
    current_category = "Основные дисциплины"

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if len(row) < 4 or not str(row[0]).strip():
                        continue

                    if str(row[0]).strip().isdigit():
                        current_semester = int(row[0])

                    try:
                        name = str(row[1]).strip()
                        credits = int(float(str(row[2]).strip())) if str(row[2]).strip().replace('.','').isdigit() else 0
                        hours = int(float(str(row[3]).strip())) if str(row[3]).strip().replace('.','').isdigit() else 0

                        if name and (credits or hours):
                            course = {
                                "name": name,
                                "semester": current_semester,
                                "credits": credits,
                                "hours": hours,
                                "category": current_category
                            }
                            data["courses"][name] = course
                            data["semesters"][current_semester].append(course)
                            data["categories"][current_category].append(course)
                            data["total_credits"] += credits
                            data["total_hours"] += hours
                    except (ValueError, IndexError) as e:
                        print(f"Ошибка обработки строки: {row}. Ошибка: {e}")

    return data

def create_program_data_json():
    """Создает структурированный JSON файл с информацией о программах"""
    programs_data = {
        "programs": [
            {
                "program_name": "Искусственный интеллект",
                "program_name_en": "Artificial Intelligence",
                "description": "Магистерская программа по подготовке специалистов в области ИИ",
                "website_url": "https://abit.itmo.ru/program/master/ai",
                "program_file_path": "src/ai/AI.pdf",
                "degree_level": "master",
                "duration_years": 2,
                "language": "ru",
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "courses_data": extract_courses_from_pdf("src/ai/AI.pdf", "Искусственный интеллект")
            },
            {
                "program_name": "Управление ИИ-продуктами",
                "program_name_en": "AI Product Management",
                "description": "Программа подготовки менеджеров ИИ-продуктов",
                "website_url": "https://abit.itmo.ru/program/master/ai_product",
                "program_file_path": "src/ai/AI_Product.pdf",
                "degree_level": "master",
                "duration_years": 2,
                "language": "ru",
                "last_updated": datetime.now().strftime("%Y-%m-%d"),
                "courses_data": extract_courses_from_pdf("src/ai/AI_Product.pdf", "Управление ИИ-продуктами")
            }
        ],
        "metadata": {
            "version": "1.1",
            "generated_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "Официальные учебные планы университета",
            "total_programs": 2
        }
    }

    # Сохраняем в JSON
    with open("program_data.json", "w", encoding="utf-8") as f:
        json.dump(programs_data, f, ensure_ascii=False, indent=2)

    print(f"Данные успешно сохранены в program_data.json. Всего программ: {len(programs_data['programs'])}")


if __name__ == "__main__":
    create_program_data_json()
