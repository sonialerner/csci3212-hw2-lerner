def hamming(x, y):
    if len(x) != len(y):
        raise ValueError("Strings must have equal lengths")

    distance = 0

    for i in range(len(x)):
        if x[i] != y[i]:
            distance += 1

    return distance


def brute_force_approx(text, words):
    if not words:
        return []

    m = len(words[0])
    results = []

    for s in range(len(text) - m + 1):
        window = text[s:s + m]

        for word in words:
            if hamming(window, word) <= 1:
                results.append((s, word))

    return sorted(set(results))


def trie_approx(text, words):
    if not words:
        return []

    trie = Trie()

    for word in words:
        trie.insert(word)

    m = len(words[0])
    results = set()

    def approx_search(node, window, index, budget, current_word):
        # reached end of window
        if index == m:
            if node.is_end_of_word:
                results.add((shift, current_word))
            return

        # look at each possible kid
        for char, child in node.children.items():

            # see if this character uses a mismatch
            if char == window[index]:
                approx_search(
                    child, window, index + 1,
                    budget, current_word + char
                )

            elif budget > 0:
                approx_search(
                    child, window, index + 1,
                    budget - 1, current_word + char
                )

    # search every text window
    for shift in range(len(text) - m + 1):
        window = text[shift:shift + m]

        approx_search(trie.root, window, 0, 1, "")

    return sorted(results)


def fingerprint(word, q):
    result = 0

    for char in word:
        result = (result * 26 + ord(char) - ord('a')) % q

    return result


def rk_approx(text, words, q):
    if not words:
        return []

    m = len(words[0])
    base = 26
    results = set()

    # calculate fingerprint
    def fingerprint(word):
        result = 0
        for char in word:
            result = (result * base + ord(char) - ord('a')) % q
        return result

    # build dictionary of fingerprints
    word_map = {}

    for word in words:
        fp = fingerprint(word)

        if fp not in word_map:
            word_map[fp] = []

        word_map[fp].append(word)

    # calculate initial text window fingerprint
    window = text[:m]
    window_fp = fingerprint(window)

    # calculate highest positional power
    highest_power = pow(base, m - 1, q)

    # process each text window
    for s in range(len(text) - m + 1):

        # generate fps for window and variants
        candidate_fps = {window_fp}

        for i in range(m):
            old_value = ord(text[s + i]) - ord('a')
            power = pow(base, m - 1 - i, q)

            for new_value in range(26):
                if new_value != old_value:
                    new_fp = (
                        window_fp
                        + (new_value - old_value) * power
                    ) % q

                    candidate_fps.add(new_fp)

        # check potential matches
        for fp in candidate_fps:
            if fp in word_map:
                for word in word_map[fp]:
                    if hamming(text[s:s + m], word) <= 1:
                        results.add((s, word))

        # calculate fp of next window
        if s < len(text) - m:
            old_value = ord(text[s]) - ord('a')
            new_value = ord(text[s + m]) - ord('a')

            window_fp = (
                (window_fp - old_value * highest_power) * base
                + new_value
            ) % q

    return sorted(results)

class TrieNode:
    def __init__(self):
        self.is_end_of_word = False
        self.children: dict[str, TrieNode] = {}

    # helper for words_with_prefix()
    def collect_words(self, current_word):
        results = []

        if self.is_end_of_word:
            results.append(current_word)

        for char, child in self.children.items():
            results.extend(child.collect_words(current_word + char))

        return results


class Trie:

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        curr = self.root

        for char in word:
            if char not in curr.children:
                curr.children[char] = TrieNode()

            curr = curr.children[char]

        curr.is_end_of_word = True


    def search(self, word):
        curr = self.root
        
        for char in word:
            if char not in curr.children:
                return False
            curr = curr.children[char]

        return curr.is_end_of_word
    

    def words_with_prefix(self, prefix):
        curr = self.root

        # find node corresponding to prefix
        for char in prefix:
            if char not in curr.children:
                return []

            curr = curr.children[char]

        # collect all words below this node
        results = curr.collect_words(prefix)

        return sorted(results)