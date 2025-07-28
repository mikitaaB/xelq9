import json
import re
import logging
from datetime import datetime
from django.shortcuts import render
from django.db import transaction, IntegrityError
from .models import Entry

logger = logging.getLogger(__name__)

def upload_json(request):
    if request.method == 'POST':
        json_file = request.FILES.get('file')
        if not json_file:
            return render(request, 'upload.html', {'errors': ['Файл не выбран']})

        try:
            data = json.load(json_file)
        except json.JSONDecodeError:
            return render(request, 'upload.html', {'errors': ['Неверный формат JSON файла']})

        if not isinstance(data, list):
            return render(request, 'upload.html', {'errors': ['JSON должен содержать массив объектов']})

        errors, valid_entries = [], []

        for i, item in enumerate(data):
            if not isinstance(item, dict):
                errors.append(f"Элемент {i+1}: должен быть объектом")
                continue

            name = item.get('name')
            date_str = item.get('date')

            if not name or not date_str:
                errors.append(f"Элемент {i+1}: отсутствуют обязательные поля 'name' или 'date'")
                continue

            if len(name) >= 50:
                errors.append(f"Элемент {i+1}: имя '{name}' слишком длинное (>= 50 символов)")
                continue

            if not re.match(r"\d{4}-\d{2}-\d{2}_\d{2}:\d{2}", date_str):
                errors.append(f"Элемент {i+1}: неверный формат даты '{date_str}'. Ожидается YYYY-MM-DD_HH:mm")
                continue

            try:
                date_fmt = date_str.replace('_', ' ')
                datetime.strptime(date_fmt, '%Y-%m-%d %H:%M')
                valid_entries.append(Entry(name=name, date=date_fmt))
            except ValueError:
                errors.append(f"Элемент {i+1}: некорректная дата '{date_str}'. Проверьте правильность даты")
                continue

        if errors:
            return render(request, 'upload.html', {'errors': errors})

        try:
            with transaction.atomic():
                Entry.objects.bulk_create(valid_entries)
            logger.info(f'Successfully uploaded {len(valid_entries)} entries')
            return render(request, 'upload.html', {'success': f'Успешно загружено {len(valid_entries)} записей!'})
        except IntegrityError as e:
            logger.error(f'Database error during upload: {e}')
            return render(request, 'upload.html', {'errors': ['Ошибка сохранения в базу данных. Попробуйте еще раз.']})

    return render(request, 'upload.html')

def show_table(request):
    entries = Entry.objects.all().order_by('-date')
    return render(request, 'table.html', {'entries': entries})
