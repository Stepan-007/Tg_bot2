class Word:
    def __init__(self, right_variant):
        self.right_variant = right_variant

    def get_right_variant(self):
        return self.right_variant

    def get_all_variants(self):
        VOWELS = 'А, О, У, Э, Ы, Я, Ё, Ю, Е, И'.lower().split(', ')
        word = self.right_variant.lower()
        all_variants = []
        for let in range(len(word)):
            if word[let] in VOWELS:
                letters = list(word)
                letters[let] = letters[let].upper()
                all_variants.append(''.join(letters))
        return all_variants
