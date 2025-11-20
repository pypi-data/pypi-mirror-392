import re
from balinese_nlp.textpreprocessor.stemming.Context.Visitor.VisitorProvider import VisitorProvider
from balinese_nlp.textpreprocessor.stemming.Filter import TextNormalizer
from balinese_nlp.textpreprocessor.stemming.Context.Context import Context
from balinese_nlp.textpreprocessor.stemming.Dictionary import ArrayDictionary
from balinese_nlp.textpreprocessor.utils import load_balinese_vocabs_file


class Stemmer(object):

    def __init__(self, dictionary):
        self.word_dictionary = ArrayDictionary(load_balinese_vocabs_file())
        self.visitor_provider = VisitorProvider()

    def get_dictionary(self):
        return self.word_dictionary

    def stem_word(self, word):
        # word = TextNormalizer.normalize_text(word)
        """Stem a word to its common stem form."""
        if self.is_plural(word):
            # print(word)
            return self.stem_plural_word(word)
        else:
            return self.stem_singular_word(word)

    def is_plural(self, word):
        # -ku|-mu|-nya
        # nikmat-Ku, etc
        # print(word)
        matches = re.match(r'^(.*)-(an|in|an|a|n|ing|e|ne)$', word)
        # print(matches)
        if matches:
            # print(matches.group(1).find('-'))
            return matches.group(1).find('-') != -1

        # print(word.find('-'))
        return word.find('-') != -1

    def stem_plural_word(self, plural):
        """Stem a plural word to its common stem form.
        Asian J. (2007) "Effective Techniques for Indonesian Text Retrieval" page 76-77.

        @link   http://researchbank.rmit.edu.au/eserv/rmit:6312/Asian.pdf
        """
        # print(plural)
        matches = re.match(r'^(.*)-(.*)$', plural)
        # print(matches.group())
        # translated from PHP conditional check:
        # if (!isset($words[1]) || !isset($words[2]))
        if not matches:
            return plural
        words = [matches.group(1), matches.group(2)]
        # print(words)

        # malaikat-malaikat-nya -> malaikat malaikat-nya
        suffix = words[1]
        suffixes = ['an', 'in', 'an', 'a', 'n', 'ing', 'e', 'ne']
        matches = re.match(r'^(.*)-(.*)$', words[0])
        if suffix in suffixes and matches:
            words[0] = matches.group(1)
            words[1] = matches.group(2) + '-' + suffix
            # print(words[1])

        # berbalas-balasan -> balas
        rootWord1 = self.stem_singular_word(words[0])
        rootWord2 = self.stem_singular_word(words[1])
        # print(rootWord1)
        # print(rootWord2)

        # meniru-nirukan -> tiru
        # print(words[0])
        # print(words[1])
        if not self.word_dictionary.contains(words[1]) and rootWord2 == words[1]:
            rootWord2 = self.stem_singular_word('me' + words[1])

        if rootWord1 == rootWord2:
            # print('as')
            return rootWord1
        else:
            return plural

    def stem_singular_word(self, word):
        """Stem a singular word to its common stem form."""
        # print(word)
        # print(self.visitor_provider)
        context = Context(word, self.word_dictionary, self.visitor_provider)
        context.execute()

        return context.result
