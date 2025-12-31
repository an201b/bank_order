import sys
import os
import csv
import xml.etree.ElementTree as ET

def print_help():
    """Выводит справку по использованию скрипта."""
    print("=" * 60)
    print(" RC Patcher - Обновление имен в SEPA XML по базе Registru Centras")
    print("=" * 60)
    print("Использование:")
    print("  rc_patcher.exe <ПАПКА> <ФАЙЛ_XML> [РЕЖИМ_ПЕРЕЗАПИСИ]")
    print("\nПараметры:")
    print("  1. ПАПКА            : Полный путь к папке, где лежат CSV и XML файлы.")
    print("  2. ФАЙЛ_XML         : Имя файла платежки (например, export.xml).")
    print("  3. РЕЖИМ_ПЕРЕЗАПИСИ : (Необязательно) 1 - Перезаписать исходный файл.")
    print("                                      0 - Создать новый файл (suffix _UPDATED).")
    print("                                      По умолчанию: 0 (Создает новый файл).")
    print("\nПримеры:")
    print('  rc_patcher.exe "C:\\Bank" "export.xml" 1      (Перезапишет export.xml)')
    print('  rc_patcher.exe "C:\\Bank" "export.xml" 0      (Создаст export_UPDATED.xml)')
    print("=" * 60)

def load_rc_data(csv_path):
    """Считывает CSV файл JAR_IREGISTRUOTI и создает словарь {код: название}."""
    company_map = {}
    print(f"--- Чтение базы RC: {csv_path}")
    
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter='|', quotechar='"')
            header = next(reader, None)
            for row in reader:
                if len(row) > 1:
                    code = row[0].strip()
                    name = row[1].strip()
                    company_map[code] = name
        print(f"--- Загружено компаний: {len(company_map)}")
        return company_map
    except FileNotFoundError:
        print(f"ОШИБКА: Файл базы данных {csv_path} не найден.")
        sys.exit(1)
    except Exception as e:
        print(f"ОШИБКА при чтении CSV: {e}")
        sys.exit(1)

def update_payment_file(xml_path, company_map, overwrite_mode):
    """Открывает XML, меняет имена и сохраняет результат (С ОТЛАДКОЙ)."""
    print(f"--- Обработка файла: {xml_path}")
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Обработка Namespace
        if '}' in root.tag:
            ns_url = root.tag.split('}')[0].strip('{')
            ns = {'ns': ns_url}
            ET.register_namespace('', ns_url)
        else:
            ns = {}
            
        replaced_count = 0
        # Ищем все транзакции
        transactions = root.findall('.//ns:CdtTrfTxInf', ns) if ns else root.findall('.//CdtTrfTxInf')
        
        print(f"--- Найдено транзакций (платежей): {len(transactions)}")

        for i, tx in enumerate(transactions):
            # Ищем получателя (Creditor)
            cdtr = tx.find('ns:Cdtr', ns) if ns else tx.find('Cdtr')
            if cdtr is None:
                print(f"  [Tx {i+1}] Не найден блок Cdtr (Получатель)")
                continue
                
            # Более надежный поиск ID (прямой путь)
            # Ищем путь: Id -> OrgId -> Othr -> Id
            org_id_tag = cdtr.find('ns:Id/ns:OrgId/ns:Othr/ns:Id', ns) if ns else cdtr.find('Id/OrgId/Othr/Id')
            
            # Если не нашли по прямому пути, пробуем поиск в глубину (на случай вариаций XML)
            if org_id_tag is None:
                 org_id_tag = cdtr.find('.//ns:Id/ns:OrgId/ns:Othr/ns:Id', ns) if ns else cdtr.find('.//Id/OrgId/Othr/Id')

            if org_id_tag is not None and org_id_tag.text:
                code = org_id_tag.text.strip()
                current_xml_name_tag = cdtr.find('ns:Nm', ns) if ns else cdtr.find('Nm')
                current_xml_name = current_xml_name_tag.text if current_xml_name_tag is not None else "(нет имени)"
                
                print(f"  [Tx {i+1}] Код в XML: '{code}' | Имя в XML: '{current_xml_name}'")
                
                if code in company_map:
                    correct_name = company_map[code]
                    print(f"      -> НАЙДЕН в базе RC. Правильное имя: '{correct_name}'")
                    
                    if current_xml_name != correct_name:
                        if current_xml_name_tag is not None:
                            print(f"      -> МЕНЯЕМ: {current_xml_name} -> {correct_name}")
                            current_xml_name_tag.text = correct_name
                            replaced_count += 1
                        else:
                            print("      -> Ошибка: тег Nm отсутствует, некуда писать имя.")
                    else:
                        print("      -> Имена совпадают, замена не нужна.")
                else:
                    print(f"      -> НЕ НАЙДЕН в CSV файле. Пропускаем.")
            else:
                print(f"  [Tx {i+1}] В этой транзакции нет OrgId (возможно, платеж физлицу или ошибка структуры).")
        
        # Сохранение
        if overwrite_mode:
            output_path = xml_path
            mode_str = "ПЕРЕЗАПИСЬ"
        else:
            output_path = xml_path.replace('.xml', '_UPDATED.xml')
            mode_str = "НОВЫЙ ФАЙЛ"
            
        tree.write(output_path, encoding='UTF-8', xml_declaration=True)
        print(f"--- Готово. Обновлено записей: {replaced_count}")
        print(f"--- Режим: {mode_str}. Сохранено в: {output_path}")

    except ET.ParseError:
        print("ОШИБКА: Некорректный формат XML.")
        sys.exit(1)
    except Exception as e:
        print(f"ОШИБКА при обработке XML: {e}")
        sys.exit(1)
def main():
    # Если аргументов нет или их мало - выводим справку
    if len(sys.argv) < 3:
        print_help()
        # Не выходим с ошибкой, просто завершаем работу штатно, показав справку
        return

    folder_path = sys.argv[1]
    payment_filename = sys.argv[2]
    
    # Обработка 3-го параметра (Перезапись)
    overwrite = False # По умолчанию создаем новый файл
    if len(sys.argv) >= 4:
        arg3 = sys.argv[3].lower()
        if arg3 in ['1', 'true', 'y', 'yes', 'overwrite']:
            overwrite = True
    
    csv_file_path = os.path.join(folder_path, "JAR_IREGISTRUOTI.csv")
    payment_file_path = os.path.join(folder_path, payment_filename)
    
    if not os.path.exists(csv_file_path):
        print(f"ОШИБКА: CSV файл не найден: {csv_file_path}")
        sys.exit(1)
        
    rc_map = load_rc_data(csv_file_path)
    
    if not os.path.exists(payment_file_path):
        print(f"ОШИБКА: Файл платежки не найден: {payment_file_path}")
        sys.exit(1)
        
    update_payment_file(payment_file_path, rc_map, overwrite)

if __name__ == "__main__":
    main()