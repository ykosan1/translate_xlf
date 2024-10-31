import requests
import xml.etree.ElementTree as ET
import logging
import time
import os
import re
import argparse
from datetime import datetime

# Loglama yapılandırması
if not os.path.exists("logs"):
    os.makedirs("logs")

info_logger = logging.getLogger("info_logger")
error_logger = logging.getLogger("error_logger")
info_handler = logging.FileHandler("logs/info.log")
error_handler = logging.FileHandler("logs/error.log")
info_handler.setLevel(logging.INFO)
error_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
info_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)
info_logger.addHandler(info_handler)
error_logger.addHandler(error_handler)
info_logger.setLevel(logging.INFO)
error_logger.setLevel(logging.ERROR)

# Loglama başlangıç banner'ı ve program bilgileri
def log_banner():
    banner = """
  _                         _     ,      __        ___,  , _    
 (_|   |                   | |   /|   / /\_\/ ()  /   | /|/ \   
   |   |         ,         | |    |__/ |    | /\ |    |  |   |  
   |   | |   |  / \_|   |  |/     | \  |    |/  \|    |  |   |  
    \_/|/ \_/|_/ \/  \_/|_/|__/   |  \_/\__//(__/ \__/\_/|   |_/ 
      /|                   |\                                   
      \|                   |/                                   
    """
    start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    info_logger.info(f"\n{banner}\nProgram Başlangıç Saati: {start_time}\n{'-' * 120}")
    error_logger.error(f"\n{banner}\nProgram Başlangıç Saati: {start_time}\n{'-' * 120}")

# Çeviri API'leri bilgileri
apis = [
    {"url": "https://libretranslate.com/translate", "type": "libre"},
    {"url": "https://api.mymemory.translated.net/get", "type": "mymemory"},
    {"url": "https://api.cognitive.microsofttranslator.com/translate", "key": "<APIKEY>", "type": "azure", "region": "<REGION>"},
    {"url": "https://translation.googleapis.com/language/translate/v2", "key": "<APIKEY>", "type": "google"}
]

current_api_index = 0

stop_requested = False

translation_summary = {
    "start_time": datetime.now(),
    "total_translations": 0,
    "total_sentences": 0,
    "total_words": 0,
    "total_characters": 0,
    "untranslated_units": []
}

def translate_text(text, file_path, unit_index, source_lang, target_lang):
    """
    Verilen metni belirtilen hedef dile çevirir.
    """
    global current_api_index

    # HTML etiketleri ve satır başı belirteçlerinin çevrilmemesi için kontrol
    if re.search(r"<.*?>|\\n", text):
        info_logger.info(f"Metin HTML etiketi veya satır başı belirteci içeriyor, çevrilmedi (Sıra No: {unit_index}): {text}")
        return text

    # {} şeklindeki formatlanmış ibarelerin çevrilmemesi için koruma
    placeholders = re.findall(r"\{.*?\}", text)
    if placeholders:
        info_logger.info(f"Metin içinde {{...}} ifadesi bulundu, çevrilmeden bırakılıyor (Sıra No: {unit_index}): {text}")
    temp_text = re.sub(r"\{.*?\}", "PLACEHOLDER", text)

    while current_api_index < len(apis):
        api = apis[current_api_index]
        try:
            if api["type"] == "libre":
                response = requests.post(api["url"], data={
                    'q': temp_text,
                    'source': source_lang.lower(),
                    'target': target_lang.lower(),
                    'format': 'text'
                })
                prefix = "LIBRE"
            elif api["type"] == "mymemory":
                response = requests.get(api["url"], params={
                    'q': temp_text,
                    'langpair': f"{source_lang.lower()}|{target_lang.lower()}"
                })
                prefix = "MEMO"
            elif api["type"] == "azure":
                headers = {
                    'Ocp-Apim-Subscription-Key': api["key"],
                    'Ocp-Apim-Subscription-Region': api["region"],
                    'Content-type': 'application/json'
                }
                body = [{
                    'text': temp_text
                }]
                response = requests.post(api["url"], headers=headers, json=body, params={
                    'api-version': '3.0',
                    'from': source_lang.lower(),
                    'to': target_lang.lower()
                })
                prefix = "AZURE"
            elif api["type"] == "google":
                response = requests.post(api["url"], params={
                    'key': api["key"],
                    'q': temp_text,
                    'source': source_lang.lower(),
                    'target': target_lang.lower()
                })
                prefix = "GTRANS"

            response.raise_for_status()
            if api["type"] == "mymemory":
                translated_text = response.json().get("responseData", {}).get("translatedText")
            elif api["type"] == "azure":
                translated_text = response.json()[0]["translations"][0]["text"]
            elif api["type"] == "google":
                translated_text = response.json().get("data", {}).get("translations", [])[0].get("translatedText")
            else:
                translated_text = response.json().get("translations", [])[0].get("text")

            # Yer tutucuları orijinal konumlarına geri koy
            for placeholder in placeholders:
                translated_text = translated_text.replace("PLACEHOLDER", placeholder, 1)

            info_logger.info(f"{prefix} Çeviri tamamlandı (Sıra No: {unit_index}): {translated_text}")
            
            # Özet bilgileri güncelle
            translation_summary["total_translations"] += 1
            translation_summary["total_sentences"] += 1
            translation_summary["total_words"] += len(translated_text.split())
            translation_summary["total_characters"] += len(translated_text)

            return translated_text
        except requests.exceptions.RequestException as e:
            error_message = f"{api['type']} API isteği sırasında hata oluştu (Sıra No: {unit_index}): {e}"
            error_logger.error(error_message)
            print(f"Hata: {error_message}")
            if 'response' in locals() and response.status_code >= 400 and response.status_code < 500:
                # Mevcut dosyayı kaydet ve sonraki API'ye geç
                output_path = "translated_partial_" + file_path
                tree.write(output_path, encoding="utf-8", xml_declaration=True)
                info_logger.info(f"HTTP {response.status_code} hatası alındı. Güncellenmiş XLF dosyası kısmi olarak kaydedildi: {output_path}")
                current_api_index += 1
                continue
            time.sleep(1)  # Hata sonrası bekleme süresi ekleyerek tekrar denemeleri önleyin

    # Tüm API'ler tükendiğinde dosyayı kaydet
    output_path = "translated_partial_" + file_path
    tree.write(output_path, encoding="utf-8", xml_declaration=True)
    info_logger.info(f"Tüm API'ler tükendi. Güncellenmiş XLF dosyası kısmi olarak kaydedildi: {output_path}")
    
    # Çevrilemeyen metni özet bilgilerinde sakla
    translation_summary["untranslated_units"].append((unit_index, text))
    return text  # Çevrilemeyen metni geri döndür

def process_xlf(file_path, output_path, source_lang, target_lang):
    """
    XLF dosyasını okuyup çevrilmemiş metinleri çevirir ve dosyayı günceller.
    """
    global stop_requested
    try:
        global tree
        tree = ET.parse(file_path)
        root = tree.getroot()

        # XLF dosyasındaki <trans-unit> etiketlerini bul
        namespace = {'ns': 'urn:oasis:names:tc:xliff:document:1.2'}
        trans_units = root.findall('.//ns:trans-unit', namespace)

        total_units = len(trans_units)
        untranslated_count = 0
        for unit in trans_units:
            target = unit.find('ns:target', namespace)
            if target is None or not target.text.strip():
                untranslated_count += 1

        info_logger.info(f"Toplam girdi sayısı: {total_units}")
        info_logger.info(f"Çevrilmemiş girdi sayısı: {untranslated_count}")

        # İlerleme çubuğu benzeri bir çıktı ile çevrilmemiş metinleri çevir
        completed = 0
        for index, unit in enumerate(trans_units, start=1):
            # Programın manuel olarak durdurulması için kontrol
            if stop_requested:
                output_path_partial = "translated_partial_" + output_path
                tree.write(output_path_partial, encoding="utf-8", xml_declaration=True)
                info_logger.info(f"Kullanıcı tarafından durduruldu. Güncellenmiş XLF dosyası kısmi olarak kaydedildi: {output_path_partial}")
                print("\nİşlem kullanıcı tarafından durduruldu. Dosya kaydedildi.")
                return

            target = unit.find('ns:target', namespace)
            source = unit.find('ns:source', namespace)

            # Eğer "target" etiketi yoksa veya boşsa, çeviri yapılmamış demektir
            if target is None or not target.text.strip():
                if source is not None and source.text:
                    translated_text = translate_text(source.text, file_path, index, source_lang, target_lang)
                    if translated_text:
                        if target is None:
                            target = ET.SubElement(unit, 'target')
                        target.text = translated_text
                    else:
                        # Çeviri başarısız olursa orijinal metni target olarak ayarla
                        if target is None:
                            target = ET.SubElement(unit, 'target')
                        target.text = source.text
                    completed += 1
                    print(f"Çeviri işlemi: {completed}/{untranslated_count} tamamlandı", end="\r")
                    time.sleep(0.5)  # Çıktının daha rahat okunabilmesi için kısa bir gecikme

        # Kaynak dosyadaki XML üst bilgisi ve kök elemanı koru
        new_root = ET.Element("xliff", attrib={"xmlns": "urn:oasis:names:tc:xliff:document:1.2", "version": "1.2"})
        new_file = ET.SubElement(new_root, "file", attrib={"target-language": target_lang.lower(), "source-language": source_lang.lower(), "original": "lit-localize-inputs", "datatype": "plaintext"})
        new_body = ET.SubElement(new_file, "body")

        # Güncellenmiş trans-unit elemanlarını yeni ağaca ekle
        for unit in trans_units:
            new_body.append(unit)

        # Güncellenmiş XLF dosyasını kaydet
        tree = ET.ElementTree(new_root)
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
        info_logger.info(f"Güncellenmiş XLF dosyası kaydedildi: {output_path}")

        # Programın çalışma süresi ve özet bilgileri
        end_time = datetime.now()
        duration = end_time - translation_summary["start_time"]
        summary_message = (
            f"\n{'-' * 120}\n"
            f"Program çalışma süresi: {duration}\n"
            f"Toplam çeviri sayısı: {translation_summary['total_translations']}\n"
            f"Toplam cümle sayısı: {translation_summary['total_sentences']}\n"
            f"Toplam kelime sayısı: {translation_summary['total_words']}\n"
            f"Toplam harf sayısı: {translation_summary['total_characters']}\n"
            f"Çevrilemeyen cümleler: {len(translation_summary['untranslated_units'])}\n"
        )
        for unit_index, text in translation_summary['untranslated_units']:
            summary_message += f"Sıra No: {unit_index}, Metin: {text}\n"
        summary_message += f"{'-' * 120}\n"

        print(summary_message)
        info_logger.info(summary_message)

        # Çevrilemeyen cümleleri yeniden dene
        if translation_summary['untranslated_units']:
            info_logger.info("Çevrilemeyen cümleler yeniden çevrilmeye çalışılıyor...")
            current_api_index = 0  # API sıfırlama
            for unit_index, text in translation_summary['untranslated_units']:
                translate_text(text, file_path, unit_index, source_lang, target_lang)

    except ET.ParseError as e:
        error_message = f"XLF dosyası okunurken hata oluştu: {e}"
        error_logger.error(error_message)
        print(f"Hata: {error_message}")
    except Exception as e:
        error_message = f"Beklenmeyen bir hata oluştu: {e}"
        error_logger.error(error_message)
        print(f"Hata: {error_message}")

if __name__ == "__main__":
    import threading

    log_banner()

    parser = argparse.ArgumentParser(description="Translate untranslated XLF segments using various translation APIs.")
    parser.add_argument('--input_file', type=str, required=True, help='Path to the input XLF file to be translated.')
    parser.add_argument('--output_file', type=str, default='out_file.xlf', help='Path to the output XLF file where translations will be saved.')
    parser.add_argument('--api', type=str, choices=['libre', 'mymemory', 'azure', 'google'], help='Translation API to use. If not specified, all APIs will be tried sequentially.')
    parser.add_argument('--source_lang', type=str, default='EN', help='Source language of the translations (e.g., en).')
    parser.add_argument('--target_lang', type=str, default='TR', help='Target language of the translations (e.g., tr).')
    args = parser.parse_args()

    # API seçimini ayarla
    selected_api = next((api for api in apis if api["type"] == args.api), None)
    if selected_api:
        current_api_index = apis.index(selected_api)
    else:
        current_api_index = 0

    def listen_for_stop():
        global stop_requested
        input("Çeviriyi durdurmak için herhangi bir tuşa basın...")
        stop_requested = True

    stop_thread = threading.Thread(target=listen_for_stop)
    stop_thread.daemon = True
    stop_thread.start()

    process_xlf(args.input_file, args.output_file, args.source_lang, args.target_lang)
