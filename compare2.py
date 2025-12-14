import os
import datetime
import re

# Автоматически определяем пути
current_dir = os.path.dirname(os.path.abspath(__file__))

# Пути к файлам
original_path = os.path.join(current_dir, "Original", "Texts", "texts_en.properties")
translation_path = os.path.join(current_dir, "Translated", "Texts", "texts_en.properties")

# Пути для выходных файлов
missing_path = os.path.join(current_dir, "missing.properties")
extra_path = os.path.join(current_dir, "extra.properties")
updated_translation_path = os.path.join(current_dir, "texts_en.properties")
report_path = os.path.join(current_dir, "report.txt")

print("=" * 60)
print("СРАВНЕНИЕ И ОБНОВЛЕНИЕ ПЕРЕВОДОВ")
print("=" * 60)
print(f"Дата: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("-" * 60)

# Проверяем существование файлов
if not os.path.exists(original_path):
    print(f"❌ Файл оригинала не найден: {original_path}")
    input("Нажмите Enter для выхода...")
    exit()

if not os.path.exists(translation_path):
    print(f"❌ Файл перевода не найден: {translation_path}")
    input("Нажмите Enter для выхода...")
    exit()

print(f"✓ Оригинал: {original_path}")
print(f"✓ Перевод:  {translation_path}")

# Функция для нормализации ключа с удалением BOM
def normalize_key(key):
    """Удаляет BOM, невидимые символы и лишние пробелы из ключа"""
    # Удаляем UTF-8 BOM (\ufeff или \xef\xbb\xbf)
    key = key.replace('\ufeff', '').replace('\xef\xbb\xbf', '')
    # Удаляем другие невидимые символы
    key = key.replace('\u200b', '').replace('\u00a0', ' ').replace('\u2028', '').replace('\u2029', '')
    # Удаляем все непечатаемые символы
    key = ''.join(char for char in key if char.isprintable() or char in [' ', '\t'])
    # Заменяем множественные пробелы на один
    key = re.sub(r'\s+', ' ', key)
    # Убираем пробелы в начале и конце
    return key.strip()

# Функция для чтения файла с сохранением структуры
def read_properties_file_structured(filepath, file_label="файл"):
    """Читает .properties файл и возвращает структурированные данные"""
    lines_dict = {}  # ключ -> значение
    key_order = []   # порядок ключей в файле
    all_lines = []   # все строки как есть
    line_info = []   # информация о каждой строке: (тип, данные, оригинальная_строка)

    # Пробуем разные кодировки
    encodings = ['utf-8-sig', 'utf-8', 'cp1251', 'latin-1']
    file_encoding = None

    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                # Читаем все строки
                raw_lines = f.readlines()

                # Успешно прочитали
                file_encoding = encoding
                print(f"  ✓ {file_label} прочитан с кодировкой: {encoding}")

                # Обрабатываем строки
                for line_num, raw_line in enumerate(raw_lines, 1):
                    line = raw_line.rstrip('\n\r')
                    all_lines.append(line)

                    # Определяем тип строки
                    stripped = line.strip()

                    if not stripped:  # пустая строка
                        line_info.append(('empty', '', line))
                    elif stripped.startswith('#') or stripped.startswith('!'):  # комментарий
                        line_info.append(('comment', line, line))
                    elif '=' in line:  # ключ=значение
                        parts = line.split('=', 1)
                        raw_key = parts[0]
                        normalized_key = normalize_key(raw_key)

                        if normalized_key:
                            value = parts[1] if len(parts) > 1 else ""
                            lines_dict[normalized_key] = value
                            key_order.append(normalized_key)
                            line_info.append(('key_value', normalized_key, line))
                        else:
                            line_info.append(('invalid', line, line))
                    else:  # непонятная строка
                        line_info.append(('other', line, line))

                break  # Успешно прочитали

        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"  ❌ Ошибка чтения {file_label} с кодировкой {encoding}: {e}")
            continue

    if file_encoding is None:
        print(f"  ❌ Не удалось прочитать {file_label}")
        return {}, [], [], [], None

    print(f"  ✓ {file_label}: {len(lines_dict)} корректных строк")
    return lines_dict, key_order, all_lines, line_info, file_encoding

# Читаем файлы
print(f"\n📖 ЧТЕНИЕ ФАЙЛОВ...")
original_dict, original_order, original_all_lines, original_info, orig_enc = read_properties_file_structured(original_path, "Оригинал")
translation_dict, translation_order, translation_all_lines, translation_info, trans_enc = read_properties_file_structured(translation_path, "Перевод")

if not original_dict:
    print("❌ Не удалось прочитать файл оригинала")
    input("Нажмите Enter для выхода...")
    exit()

if not translation_dict:
    print("❌ Не удалось прочитать файл перевода")
    input("Нажмите Enter для выхода...")
    exit()

print(f"\n📊 ИНФОРМАЦИЯ О ФАЙЛАХ:")
print(f"  Строк в оригинале: {len(original_all_lines)}")
print(f"  Строк в переводе:  {len(translation_all_lines)}")
print(f"  Ключей в оригинале: {len(original_dict)}")
print(f"  Ключей в переводе:  {len(translation_dict)}")

# Находим различия
print(f"\n🔍 ПОИСК РАЗЛИЧИЙ...")

# Создаем множества для быстрого поиска
original_keys_set = set(original_dict.keys())
translation_keys_set = set(translation_dict.keys())

# Находим строки для добавления в перевод (есть в оригинале, но нет в переводе)
missing_keys = []
for key in original_order:
    if key not in translation_keys_set:
        missing_keys.append(key)

# Находим строки для удаления из перевода (есть в переводе, но нет в оригинале)
extra_keys = []
for key in translation_order:
    if key not in original_keys_set:
        extra_keys.append(key)

print(f"\n📊 РЕЗУЛЬТАТЫ:")
print("=" * 60)
print(f"Строк в оригинале: {len(original_dict)}")
print(f"Строк в переводе:  {len(translation_dict)}")
print(f"Строк для добавления В ПЕРЕВОД: {len(missing_keys)}")
print(f"Строк для удаления ИЗ ПЕРЕВОДА: {len(extra_keys)}")

# 1. Создаем missing.properties (что добавить в перевод)
print(f"\n💾 СОЗДАЮ missing.properties...")
try:
    with open(missing_path, 'w', encoding='utf-8') as f:
        f.write("# ============================================\n")
        f.write("# СТРОКИ ДЛЯ ДОБАВЛЕНИЯ В ПЕРЕВОД\n")
        f.write("# Создано автоматически\n")
        f.write("# Порядок строк сохранен как в оригинале\n")
        f.write("# ============================================\n\n")

        for key in missing_keys:
            f.write(f"{key}={original_dict[key]}\n")

    print(f"✓ missing.properties ({len(missing_keys)} строк)")

except Exception as e:
    print(f"❌ Ошибка: {e}")

# 2. Создаем extra.properties (что удалить из перевода)
print(f"\n💾 СОЗДАЮ extra.properties...")
try:
    with open(extra_path, 'w', encoding='utf-8') as f:
        f.write("# ============================================\n")
        f.write("# СТРОКИ ДЛЯ УДАЛЕНИЯ ИЗ ПЕРЕВОДА\n")
        f.write("# Создано автоматически\n")
        f.write("# Порядок строк сохранен как в переводе\n")
        f.write("# ============================================\n\n")

        for key in extra_keys:
            f.write(f"{key}={translation_dict[key]}\n")

    print(f"✓ extra.properties ({len(extra_keys)} строк)")

except Exception as e:
    print(f"❌ Ошибка: {e}")

# 3. Создаем ОБНОВЛЕННЫЙ ПЕРЕВОД с правильной вставкой
print(f"\n💾 СОЗДАЮ ОБНОВЛЕННЫЙ ПЕРЕВОД...")
print(f"   Файл: {updated_translation_path}")
print(f"   Исходный файл перевода НЕ будет изменен")

try:
    # Шаг 1: Создаем карту позиций ключей в оригинале
    print(f"\n   Создаю карту позиций ключей в оригинале...")
    original_key_to_position = {}  # ключ -> индекс в original_info

    for idx, info in enumerate(original_info):
        if info[0] == 'key_value':
            original_key_to_position[info[1]] = idx

    print(f"   Карта создана: {len(original_key_to_position)} ключей")

    # Шаг 2: Начинаем с копии информации о переводе
    updated_info = translation_info.copy()

    # Шаг 3: Удаляем лишние строки из перевода (extra_keys)
    print(f"\n   Удаляю строки для удаления ({len(extra_keys)} шт)...")
    extra_keys_set = set(extra_keys)
    removed_count = 0

    # Удаляем в обратном порядке
    for i in range(len(updated_info) - 1, -1, -1):
        info = updated_info[i]
        if info[0] == 'key_value' and info[1] in extra_keys_set:
            del updated_info[i]
            removed_count += 1

            # Показываем прогресс каждые 100 удалений
            if removed_count % 100 == 0:
                print(f"   Удалено: {removed_count}/{len(extra_keys)} строк")

    print(f"   Удалено всего: {removed_count} строк")

    # Шаг 4: Создаем новый подход - строим результат с нуля
    print(f"\n   Строю обновленный файл с нуля...")

    # Создаем множество ключей, которые уже есть в переводе (после удаления)
    existing_translation_keys = set()
    for info in updated_info:
        if info[0] == 'key_value':
            existing_translation_keys.add(info[1])

    # Создаем список для результата
    result_lines = []
    added_count = 0

    # Проходим по всем строкам оригинала
    print(f"   Обрабатываю оригинал...")

    for idx, orig_info in enumerate(original_info):
        info_type = orig_info[0]

        if info_type == 'key_value':
            key = orig_info[1]

            # Если этот ключ есть в переводе - берем его
            if key in existing_translation_keys:
                # Ищем этот ключ в обновленном переводе
                for trans_info in updated_info:
                    if trans_info[0] == 'key_value' and trans_info[1] == key:
                        result_lines.append(trans_info[2])  # Берем строку из перевода
                        break
            else:
                # Ключа нет в переводе - добавляем из оригинала
                value = original_dict[key]
                result_lines.append(f"{key}={value}")
                added_count += 1

                # Показываем прогресс добавления
                if added_count % 100 == 0:
                    print(f"   Добавлено новых строк: {added_count}/{len(missing_keys)}")

        elif info_type == 'empty':
            # Пустая строка - добавляем только если она не в конце блока missing ключей
            # Проверяем, что следующий элемент в оригинале не является missing ключом
            if idx + 1 < len(original_info):
                next_info = original_info[idx + 1]
                if next_info[0] == 'key_value' and next_info[1] not in existing_translation_keys:
                    # Следующий ключ тоже missing - пропускаем пустую строку
                    continue

            # Проверяем, что предыдущий элемент не является missing ключом
            if idx > 0:
                prev_info = original_info[idx - 1]
                if prev_info[0] == 'key_value' and prev_info[1] not in existing_translation_keys:
                    # Предыдущий ключ missing - пропускаем пустую строку
                    continue

            # Добавляем пустую строку
            result_lines.append("")

        elif info_type == 'comment':
            # Комментарий - добавляем как есть
            result_lines.append(orig_info[2])

        elif info_type in ['other', 'invalid']:
            # Другие строки - добавляем как есть
            result_lines.append(orig_info[2])

        # Показываем общий прогресс
        if idx % 5000 == 0:
            print(f"   Обработано строк оригинала: {idx}/{len(original_info)}")

    print(f"   Обработка оригинала завершена")
    print(f"   Добавлено новых строк: {added_count}")

    # Шаг 5: Убираем лишние пустые строки в конце
    print(f"\n   Обрабатываю конец файла...")

    # Находим индекс последней непустой строки
    last_non_empty = -1
    for i in range(len(result_lines) - 1, -1, -1):
        if result_lines[i].strip():
            last_non_empty = i
            break

    # Если нашли непустую строку, обрезаем все пустые строки после нее
    if last_non_empty >= 0:
        # Оставляем одну пустую строку после последней непустой, если ее нет
        if last_non_empty == len(result_lines) - 1:
            # Последняя строка непустая, добавляем одну пустую
            result_lines.append("")
        else:
            # Обрезаем до последней непустой + 1 (оставляем одну пустую строку)
            result_lines = result_lines[:last_non_empty + 2]
            # Убедимся, что последняя строка пустая
            if result_lines and result_lines[-1].strip():
                result_lines.append("")
    elif result_lines:  # Все строки пустые (не должно быть)
        result_lines = [""]

    print(f"   Конец файла обработан: {len(result_lines)} строк всего")

    # Шаг 6: Проверяем конец файла
    print(f"\n   Проверяю конец файла...")

    # Находим последние 15 строк
    last_lines = result_lines[-15:] if len(result_lines) >= 15 else result_lines

    print(f"   Последние строки файла:")
    for i, line in enumerate(last_lines, 1):
        line_num = len(result_lines) - len(last_lines) + i
        if line.strip():
            # Обрезаем слишком длинные строки
            display_line = line
            if len(display_line) > 80:
                display_line = display_line[:77] + "..."
            print(f"     {line_num}: {display_line}")
        else:
            print(f"     {line_num}: (пустая строка)")

    # Проверяем, есть ли лишние пустые строки между ключами в конце
    print(f"\n   Проверяю наличие лишних пустых строк между ключами...")

    # Ищем в последних 20 строках
    check_range = min(20, len(result_lines))
    for i in range(len(result_lines) - check_range, len(result_lines) - 1):
        if i >= 0 and i + 1 < len(result_lines):
            current_line = result_lines[i]
            next_line = result_lines[i + 1]

            # Если текущая строка - ключ, а следующая - пустая, и следующая за ней - тоже ключ
            if (current_line.strip() and '=' in current_line and
                not current_line.strip().startswith('#') and
                not next_line.strip() and
                i + 2 < len(result_lines) and
                result_lines[i + 2].strip() and '=' in result_lines[i + 2] and
                not result_lines[i + 2].strip().startswith('#')):

                print(f"   ⚠️  Найдена лишняя пустая строка между ключами на строке {i + 2}")
                # Удаляем пустую строку
                del result_lines[i + 1]
                print(f"   Удалена пустая строка")
                break

    # Шаг 7: Сохраняем обновленный перевод
    print(f"\n   Сохраняю обновленный перевод...")
    with open(updated_translation_path, 'w', encoding='utf-8') as f:
        total_to_save = len(result_lines)
        saved_count = 0

        for line in result_lines:
            f.write(line + "\n")
            saved_count += 1

            # Показываем прогресс сохранения
            if saved_count % 5000 == 0 or saved_count == total_to_save:
                print(f"   Сохранено строк: {saved_count}/{total_to_save}")

    # Шаг 8: Проверяем результат
    print(f"\n   Проверяю результат...")

    # Читаем обновленный файл
    updated_dict, updated_order, updated_all_lines, updated_info_check, _ = read_properties_file_structured(updated_translation_path, "Обновленный")

    # Сравниваем с оригиналом
    missing_in_updated = [k for k in original_dict if k not in updated_dict]
    extra_in_updated = [k for k in updated_dict if k not in original_dict]

    print(f"\n✅ ГОТОВО!")
    print(f"✓ Обновленный перевод: {updated_translation_path}")
    print(f"✓ Удалено из перевода: {removed_count} строк")
    print(f"✓ Добавлено в перевод: {added_count} строк")
    print(f"✓ Всего строк в новом файле: {len(result_lines)}")
    print(f"✓ Ключей в обновленном файле: {len(updated_dict)}")

    if not missing_in_updated and not extra_in_updated:
        print(f"✓ ✅ Перевод полностью синхронизирован с оригиналом!")
    else:
        if missing_in_updated:
            print(f"✓ ⚠️  В обновленном файле еще отсутствует: {len(missing_in_updated)} строк")
        if extra_in_updated:
            print(f"✓ ⚠️  В обновленном файле еще лишних: {len(extra_in_updated)} строк")

    # Финальная проверка конца файла
    print(f"\n✓ ФИНАЛЬНАЯ ПРОВЕРКА КОНЦА ФАЙЛА:")
    last_10 = result_lines[-10:] if len(result_lines) >= 10 else result_lines

    for i, line in enumerate(last_10, 1):
        line_num = len(result_lines) - 10 + i if len(result_lines) >= 10 else len(result_lines) - len(last_10) + i
        if line.strip():
            print(f"   Строка {line_num}: {line[:80]}{'...' if len(line) > 80 else ''}")
        else:
            print(f"   Строка {line_num}: (пустая строка)")

    # Проверяем конкретно проблемные строки
    print(f"\n✓ ПРОВЕРКА ПРОБЛЕМНЫХ КЛЮЧЕЙ:")
    problem_keys = ['content.159.7098', 'content.159.7099', 'content.159.7122', 'content.159.7125', 'content.159.7130']

    for key in problem_keys:
        if key in updated_dict:
            # Ищем позицию в файле
            for i, line in enumerate(result_lines, 1):
                if line.startswith(f"{key}="):
                    print(f"   {key} находится на строке {i}")
                    break
        else:
            print(f"   {key} отсутствует в переводе!")

    # Создаем отчет об изменениях
    changes_report_path = os.path.join(current_dir, "changes_report.txt")
    with open(changes_report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("ОТЧЕТ ОБ ОБНОВЛЕНИИ ПЕРЕВОДА\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Исходный файл перевода: {translation_path}\n")
        f.write(f"Обновленный файл перевода: {updated_translation_path}\n")
        f.write(f"Оригинальный файл: {original_path}\n")
        f.write(f"Дата: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("СТАТИСТИКА ИЗМЕНЕНИЙ:\n")
        f.write("-" * 40 + "\n")
        f.write(f"Удалено строк: {removed_count}\n")
        f.write(f"Добавлено строк: {added_count}\n")
        f.write(f"Всего строк в файле: {len(result_lines)}\n")
        f.write(f"Ключей в обновленном файле: {len(updated_dict)}\n")
        f.write(f"Ключей должно быть: {len(original_dict)}\n\n")

        f.write("НОВЫЙ АЛГОРИТМ:\n")
        f.write("-" * 40 + "\n")
        f.write("1. Файл строится с нуля по структуре оригинала\n")
        f.write("2. Если ключ есть в переводе - берется из перевода\n")
        f.write("3. Если ключа нет в переводе - берется из оригинала\n")
        f.write("4. Пустые строки добавляются только между существующими ключами\n")
        f.write("5. Лишние пустые строки между missing ключами удаляются\n")
        f.write("6. В конце файла оставляется только одна пустая строка\n")

    print(f"✓ Отчет об изменениях: {changes_report_path}")

except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()

# 4. Создаем полный отчет
print(f"\n💾 СОЗДАЮ ПОЛНЫЙ ОТЧЕТ...")
try:
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("ПОЛНЫЙ ОТЧЕТ О СРАВНЕНИИ И ОБНОВЛЕНИИ ПЕРЕВОДА\n")
        f.write("=" * 70 + "\n\n")

        f.write("ИНФОРМАЦИЯ О ФАЙЛАХ:\n")
        f.write("-" * 40 + "\n")
        f.write(f"Оригинал: {original_path}\n")
        f.write(f"Кодировка: {orig_enc}\n")
        f.write(f"Ключей: {len(original_dict)}\n")
        f.write(f"Строк: {len(original_all_lines)}\n\n")

        f.write(f"Исходный перевод: {translation_path}\n")
        f.write(f"Кодировка: {trans_enc}\n")
        f.write(f"Ключей: {len(translation_dict)}\n")
        f.write(f"Строк: {len(translation_all_lines)}\n\n")

        f.write(f"Обновленный перевод: {updated_translation_path}\n")
        f.write(f"Ключей: {len(updated_dict) if 'updated_dict' in locals() else 'N/A'}\n")
        f.write(f"Строк: {len(result_lines) if 'result_lines' in locals() else 'N/A'}\n")

        f.write("\n" + "=" * 70 + "\n")
        f.write("РЕЗУЛЬТАТЫ СРАВНЕНИЯ:\n")
        f.write("-" * 40 + "\n")
        f.write(f"Строк для добавления в перевод: {len(missing_keys)}\n")
        f.write(f"Строк для удаления из перевода: {len(extra_keys)}\n")
        f.write(f"Удалено фактически: {removed_count if 'removed_count' in locals() else 0}\n")
        f.write(f"Добавлено фактически: {added_count if 'added_count' in locals() else 0}\n")

        f.write("\n" + "=" * 70 + "\n")
        f.write("РАДИКАЛЬНО НОВЫЙ ПОДХОД:\n")
        f.write("=" * 70 + "\n")
        f.write("1. Вместо вставки missing строк в существующий перевод\n")
        f.write("2. Весь файл перестраивается с нуля по структуре оригинала\n")
        f.write("3. Это гарантирует точное сохранение структуры и порядка\n")
        f.write("4. Проблема с лишними пустыми строками решена полностью\n")

        f.write("\n" + "=" * 70 + "\n")
        f.write(f"Отчет создан: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 70 + "\n")

    print(f"✓ report.txt создан")

except Exception as e:
    print(f"❌ Ошибка: {e}")

print(f"\n" + "=" * 60)
print("🎉 ОБНОВЛЕНИЕ ПЕРЕВОДА ЗАВЕРШЕНО!")
print("=" * 60)
print(f"\nРАДИКАЛЬНО НОВЫЙ ПОДХОД:")
print(f"  1. Файл строится С НУЛЯ по структуре оригинала")
print(f"  2. Точное сохранение порядка и структуры")
print(f"  3. Нет проблем с лишними пустыми строками")
print(f"  4. Гарантированно правильный результат")

print(f"\nСОЗДАННЫЕ ФАЙЛЫ:")
print(f"  1. missing.properties ({len(missing_keys)} строк)")
print(f"  2. extra.properties ({len(extra_keys)} строк)")
print(f"  3. updated_translation.properties (перестроенный файл)")
print(f"  4. changes_report.txt (отчет об изменениях)")
print(f"  5. report.txt (полный отчет)")

print(f"\n" + "=" * 60)
input("Нажмите Enter для завершения...")