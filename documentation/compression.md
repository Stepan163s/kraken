# Модуль компрессии (Huffman-like)

## Задачи
- Уменьшить объём текстовых данных, хранимых в БД (особенно за большие периоды).
- Ускорить поиск и анализ за счёт кодирования часто используемых слов.
- Сложность: не просто символы, а **слова** (и даже словосочетания).

## Принцип действия
1. **Сбор статистики**: Раз в сутки/неделю/месяц анализируются все слова, которые бот видел.
2. **Присвоение кодов**:
   - Часто встречаемым словам — более короткие коды.
   - Редким словам — коды длиннее.
3. **Упаковка в БД**: Вместо оригинального текста в поле “content_compressed” хранится зашифрованная строка.
4. **Декомпрессия при необходимости**: Если боту нужно уточнить контекст, он может “распаковать” текст (или частично), обращаясь к словарю кодировок.

## Пример
- Слово “привет” встречается 5000 раз — код “1”.
- Слово “пока” встречается 2500 раз — код “2”.
- “концептуализация” — редкое — код “A3B”.

## Потенциальные расширения
- Хранить также частотность словосочетаний (bigram/trigram).
- Использовать не только Huffman, но и иные алгоритмы (LZ, BPE).
- В будущем: матричная компрессия, которая учитывает связи слов (контекстное кодирование).

---