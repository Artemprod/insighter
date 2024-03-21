import asyncio
import re


class PostProcessor:
    @staticmethod
    async def clean_gibberish(text):
        """
        Метод для удаления неоднородных бессмысленных последовательностей символов из текста.
        """
        # Удаляем несмысловые последовательности символов в словах, сохраняя целостность чисел.
        text = re.sub(r"\b(?!\d+\b)\w*[^A-Za-zА-Яа-я0-9\s]{2,}\w*\b", "", text)
        # Удаление длинных последовательностей одинаковых символов, кроме цифр
        text = re.sub(r"([^\d])\1{2,}", r"\1", text)
        return text

    async def remove_redundant_repeats(self,
                                       text):
        """
        Метод для очистки текста от повторяющихся паттернов и символов,
        включая удаление бессмысленных последовательностей символов в словах.
        """
        text = await self.clean_gibberish(text)  # Сначала очистим текст от бессмысленных последовательностей

        # Удаляем повторяющиеся символы, оставляя только один (например, "ааа" -> "а").


        return text

if __name__ == '__main__':
    examples = [
        "80 0000",
        "80000",
        "5678493021",
        "5555555",
        "-----------",
        "...................",
        "dfdfdfdfdfdf"
    ]
    async def main():
        # Тестирование метода
        for example in examples:
            print(f"Original: {example}")
            print(f"Processed: {await PostProcessor().remove_redundant_repeats(text=example)}\n")

    asyncio.run(main())