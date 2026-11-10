class TrieNode:
    is_end_of_word = False
    children: dict[str, TrieNode]

    def __init__(self):
        pass

class Trie:
    root_node: TrieNode

    def __init__(self):
        pass

    def insert(self, word):
        pass

    def search(self, word):
        pass

    def words_with_prefix(self, prefix):
        pass

    def hamming(self, x, y):
        pass

    def brute_force_approx(self, text, words):
        pass

    def trie_approx(self, text, words):
        pass
    
    def rk_approx(self, text, words, q):
        pass