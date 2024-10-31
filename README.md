# XLF Translator / XLF Çevirici

XLF Translator is a Python tool that helps you translate untranslated segments in XLF files. It uses multiple translation APIs to perform the translations and allows the user to select the desired API.

XLF Çevirici, XLF dosyalarındaki çevrilmemiş segmentleri çevirmenize yardımcı olan bir Python aracıdır. Birden fazla çeviri API'si kullanarak çevirileri gerçekleştirir ve kullanıcının istediği API'yi seçmesine olanak tanır.

## Requirements / Gereksinimler

- Python 3.6 or newer / Python 3.6 veya daha yeni
- Install the required Python libraries: / Gerekli Python kütüphanelerini yükleyin:

```sh
pip install requests
```

## Usage / Kullanım

```sh
python translate_untranslated_xlf.py --input_file <input_xlf_path> --output_file <output_xlf_path> --api <api_choice>
```

### Arguments / Argümanlar

- `--input_file` (required): The path to the input XLF file that you want to translate.
  - `--input_file` (gerekli): Çevirmek istediğiniz XLF dosyasının yolu.
- `--output_file` (required): The path to the output XLF file that will contain the translations.
  - `--output_file` (gerekli): Çevirileri içerecek olan çıktı XLF dosyasının yolu.
- `--api` (required): The translation API to use. Available choices are:
  - `--api` (gerekli): Kullanılacak çeviri API'si. Mevcut seçenekler:
  - `libre` for LibreTranslate / LibreTranslate için `libre`
  - `mymemory` for MyMemory / MyMemory için `mymemory`
  - `azure` for Microsoft Azure Translate / Microsoft Azure Çeviri için `azure`
  - `google` for Google Translate / Google Çeviri için `google`

### Example / Örnek

```sh
python translate_untranslated_xlf.py --input_file example.xlf --output_file translated_example.xlf --api libre
```

## Features / Özellikler

- The program will automatically detect and handle placeholders like `{}` that should not be translated.
  - Program, `{}` gibi çevrilmemesi gereken yer tutucuları otomatik olarak algılar ve yönetir.
- Translation progress is logged, and partial results are saved if the process is interrupted.
  - Çeviri ilerlemesi kaydedilir ve işlem kesintiye uğrarsa kısmi sonuçlar kaydedilir.
- Log files are created under the `logs/` directory, separated by `info.log` and `error.log`.
  - Log dosyaları `logs/` dizininde oluşturulur, `info.log` ve `error.log` olarak ayrılır.
- If translations fail, the program will retry using a different translation API.
  - Çeviriler başarısız olursa, program farklı bir çeviri API'si kullanarak yeniden dener.

## Notes / Notlar

- The program allows you to stop the process by pressing `Enter`. Any progress made up to that point will be saved to a partial output file.
  - Program, `Enter` tuşuna basarak işlemi durdurmanıza olanak tanır. O ana kadar yapılan ilerleme kısmi bir çıktı dosyasına kaydedilecektir.
- To change the API key values for Azure or Google Translate, edit the corresponding key in the source code.
  - Azure veya Google Translate için API anahtarlarını değiştirmek için kaynak koddaki ilgili anahtarı düzenleyin.

## License / Lisans

This project is licensed under the MIT License.

Bu proje MIT Lisansı ile lisanslanmıştır.

