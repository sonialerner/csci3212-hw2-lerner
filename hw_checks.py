"""Provided test checks for CSCI 3212 Homework 2.

No third-party packages are required for the checks themselves.

Usage:
    python3 hw_checks.py [optional_directory_to_test] [--perf]

The checks verify behaviour, not implementation details: any correct answer is
accepted, and the string searchers are compared against independent reference
implementations rather than against fixed expected outputs.
"""

import math
import os
import random
import sys
import time
from typing import Dict, List, Optional, Tuple


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_checks(cases: List[Tuple[str, "callable"]]) -> int:
    """Run (name, zero-arg callable) pairs; return process exit status.

    NotImplementedError -> [TODO]; any other exception -> [FAIL].
    """
    failed = 0
    passed = 0

    for name, test in cases:
        try:
            test()
            passed += 1
            print(f"[PASS] {name}")
        except NotImplementedError as error:
            failed += 1
            print(f"[TODO] {name}: {error}")
        except Exception as error:
            failed += 1
            print(f"[FAIL] {name}: {type(error).__name__}: {error}")

    total = len(cases)
    print(f"\n{passed}/{total} checks passed")
    return 1 if failed else 0


# --- Dynamic import helpers with [TODO] reporting ---

def import_hash_module():
    try:
        import hash_table
    except ImportError as error:
        raise NotImplementedError(f"Create hash_table.py: {error}")
    if not hasattr(hash_table, "ChainedHashTable"):
        raise NotImplementedError("Create hash_table.py with class ChainedHashTable")
    return hash_table


def import_search_module():
    try:
        import string_search
    except ImportError as error:
        raise NotImplementedError(f"Create string_search.py: {error}")
    for name in ("naive_search", "prefix_function", "kmp_search", "rabin_karp"):
        if not hasattr(string_search, name):
            raise NotImplementedError(f"Create string_search.py with {name}")
    return string_search


def import_trie_module():
    try:
        import trie_approx
    except ImportError as error:
        raise NotImplementedError(f"Create trie_approx.py: {error}")
    for name in ("Trie", "TrieNode", "hamming", "brute_force_approx", "trie_approx", "rk_approx"):
        if not hasattr(trie_approx, name):
            raise NotImplementedError(f"Create trie_approx.py with {name}")
    return trie_approx


def import_experiment_module():
    try:
        import experiment
    except ImportError as error:
        if "experiment" not in str(error):
            raise NotImplementedError(
                "experiment.py exists, but a package it imports is missing: " + str(error)
            )
        raise NotImplementedError(f"Create experiment.py: {error}")
    for name in ("run_experiment", "plot_results", "random_dictionary", "random_text", "K_VALUES"):
        if not hasattr(experiment, name):
            raise NotImplementedError(f"Create experiment.py with {name}")
    return experiment


# --- Reference implementations used only by the checks ---

def reference_prefix_function(pattern: str) -> List[int]:
    """Straightforward O(m^3) definition: longest border of every prefix."""
    pi = []
    for i in range(1, len(pattern) + 1):
        prefix = pattern[:i]
        best = 0
        for length in range(1, i):
            if prefix[:length] == prefix[i - length :]:
                best = length
        pi.append(best)
    return pi


def reference_naive(text: str, pattern: str) -> List[int]:
    return [s for s in range(len(text) - len(pattern) + 1) if text[s : s + len(pattern)] == pattern]


def reference_hamming(x: str, y: str) -> int:
    return sum(1 for a, b in zip(x, y) if a != b)


def reference_approx(text: str, words: List[str]) -> List[Tuple[int, str]]:
    if not words:
        return []
    m = len(words[0])
    found = []
    for s in range(len(text) - m + 1):
        window = text[s : s + m]
        for word in words:
            if reference_hamming(window, word) <= 1:
                found.append((s, word))
    return sorted(found)


def check_hash_table(module, rng):
    table = module.ChainedHashTable(4)
    require(len(table) == 0, "a new table must be empty")
    require(table.lookup("missing") is None, "lookup of an absent key must return None")

    for index in range(30):
        key = f"key{index}"
        require(table.insert(key, index) is True, "insert of a new key must report True")
        require(table.lookup(key) == index, "lookup must return the value stored under the key")

    require(len(table) == 30, "len(table) must count every stored pair")
    require(table.insert("key0", "updated") is False, "updating an existing key must report False")
    require(table.lookup("key0") == "updated", "insert must replace the value of an existing key")
    require(len(table) == 30, "updating a key must not change the size")

    expected = {f"key{index}" for index in range(30)}
    require(set(table.keys()) == expected, "keys() must return every stored key exactly once")

    require(table.load_factor() <= 0.75 + 1e-9, "the load factor must stay at most 0.75")
    require(table.capacity() > 4, "the table must grow when it becomes too full")

    require(table.delete("key7") is True, "deleting a present key must return True")
    require(table.lookup("key7") is None, "a deleted key must not be found")
    require(table.delete("key7") is False, "deleting an absent key must return False")
    require(len(table) == 29, "deleting must decrement the size")

    # Keys that share a bucket must still be distinguishable.
    tiny = module.ChainedHashTable(2)
    for index in range(12):
        tiny.insert(f"k{index}", index)
    for index in range(12):
        require(tiny.lookup(f"k{index}") == index, "colliding keys must all be retrievable")


def check_prefix_function(module, rng):
    known = {
        "ababaca": [0, 0, 1, 2, 3, 0, 1],
        "aabaab": [0, 1, 0, 1, 2, 3],
        "aaaa": [0, 1, 2, 3],
        "abcabc": [0, 0, 0, 1, 2, 3],
        "a": [0],
        "abcde": [0, 0, 0, 0, 0],
    }
    for pattern, expected in known.items():
        require(
            module.prefix_function(pattern) == expected,
            "The prefix function is wrong for a known pattern",
        )
    for _ in range(5):
        pattern = "".join(rng.choice("ab") for _ in range(rng.randint(1, 10)))
        require(
            module.prefix_function(pattern) == reference_prefix_function(pattern),
            "The prefix function disagrees with its definition on a random pattern",
        )


def check_naive_and_kmp(module, rng):
    require(module.naive_search("abcabc", "abc") == [0, 3], "naive_search returned wrong shifts")
    require(module.kmp_search("abcabc", "abc") == [0, 3], "kmp_search returned wrong shifts")
    for _ in range(20):
        n = rng.randint(1, 30)
        text = "".join(rng.choice("ab") for _ in range(n))
        m = rng.randint(1, min(4, n))
        pattern = "".join(rng.choice("ab") for _ in range(m))
        expected = reference_naive(text, pattern)
        require(module.naive_search(text, pattern) == expected, "naive_search is wrong on a random case")
        require(module.kmp_search(text, pattern) == expected, "kmp_search is wrong on a random case")


def check_rabin_karp(module, rng):
    text = "ababacab"
    pattern = "aba"
    for q in (13, 101, 1_000_000_007):
        require(
            module.rabin_karp(text, pattern, q) == [0, 2],
            "rabin_karp is wrong on the running example",
        )
    for _ in range(20):
        n = rng.randint(1, 40)
        text = "".join(rng.choice("abcd") for _ in range(n))
        m = rng.randint(1, min(5, n))
        pattern = "".join(rng.choice("abcd") for _ in range(m))
        expected = reference_naive(text, pattern)
        for q in (13, 1_000_000_007):
            require(
                module.rabin_karp(text, pattern, q) == expected,
                "rabin_karp is wrong on a random case (collisions must be verified)",
            )


def check_trie(module):
    trie = module.Trie()
    for word in ["cat", "car", "do", "dog", "dot"]:
        trie.insert(word)
    require(trie.search("do") is True, "search must find a stored word")
    require(trie.search("ca") is False, "search must reject a prefix that is not a word")
    require(trie.search("can") is False, "search must reject a word that is not stored")
    require(trie.words_with_prefix("do") == ["do", "dog", "dot"], "words_with_prefix is wrong")
    require(
        trie.words_with_prefix("") == ["car", "cat", "do", "dog", "dot"],
        "the empty prefix must return every word in order",
    )
    require(trie.words_with_prefix("z") == [], "a missing prefix must return an empty list")

    trie.insert("do")
    require(trie.words_with_prefix("do") == ["do", "dog", "dot"], "re-inserting a word must not duplicate it")

    node = module.TrieNode()
    require(isinstance(node.children, dict) and node.is_end_of_word is False, "TrieNode must start empty")


def check_hamming(module):
    require(module.hamming("abd", "abc") == 1, "hamming distance is wrong")
    require(module.hamming("abd", "abd") == 0, "identical strings must be at distance 0")
    require(module.hamming("cab", "abc") == 3, "hamming distance is wrong")
    raised = False
    try:
        module.hamming("ab", "abc")
    except ValueError:
        raised = True
    require(raised, "hamming must raise ValueError for strings of different lengths")


def check_brute_force_approx(module, rng):
    words = ["abc", "abd", "acd", "bad", "cab"]
    text = "abdcabb"
    expected = [
        (0, "abc"), (0, "abd"), (0, "acd"), (3, "cab"), (4, "abc"), (4, "abd")
    ]
    require(module.brute_force_approx(text, words) == expected, "brute_force_approx is wrong on the example")
    for _ in range(6):
        m = rng.randint(2, 3)
        text = "".join(rng.choice("abc") for _ in range(rng.randint(3, 12)))
        pool = {"".join(rng.choice("abc") for _ in range(m)) for _ in range(rng.randint(1, 8))}
        words = sorted(pool)
        require(
            module.brute_force_approx(text, words) == reference_approx(text, words),
            "brute_force_approx disagrees with a direct reference",
        )


def check_trie_approx(module, rng):
    words = ["abc", "abd", "acd", "bad", "cab"]
    text = "abdcabb"
    expected = [
        (0, "abc"), (0, "abd"), (0, "acd"), (3, "cab"), (4, "abc"), (4, "abd")
    ]
    require(module.trie_approx(text, words) == expected, "trie_approx is wrong on the example")
    require(module.trie_approx(text, []) == [], "an empty dictionary must give no pairs")
    for _ in range(6):
        m = rng.randint(2, 3)
        text = "".join(rng.choice("abc") for _ in range(rng.randint(3, 12)))
        pool = {"".join(rng.choice("abc") for _ in range(m)) for _ in range(rng.randint(1, 8))}
        dictionary = sorted(pool)
        require(
            module.trie_approx(text, dictionary) == reference_approx(text, dictionary),
            "trie_approx disagrees with a direct reference",
        )


def check_rk_approx(module, rng):
    words = ["abc", "abd", "acd", "bad", "cab"]
    text = "abdcabb"
    expected = [
        (0, "abc"), (0, "abd"), (0, "acd"), (3, "cab"), (4, "abc"), (4, "abd")
    ]
    for q in (13, 1_000_000_007):
        require(module.rk_approx(text, words, q) == expected, "rk_approx is wrong on the example")
    for _ in range(6):
        m = rng.randint(2, 3)
        text = "".join(rng.choice("abc") for _ in range(rng.randint(3, 12)))
        pool = {"".join(rng.choice("abc") for _ in range(m)) for _ in range(rng.randint(1, 8))}
        dictionary = sorted(pool)
        for q in (11, 1_000_000_007):
            require(
                module.rk_approx(text, dictionary, q) == reference_approx(text, dictionary),
                "rk_approx is wrong on a random case (fingerprint hits must be verified)",
            )


def check_experiment(module):
    rng = random.Random(3212)
    words = module.random_dictionary(20, rng)
    require(len(words) == 20 and len(set(words)) == 20, "random_dictionary must return k distinct words")
    require(all(len(word) == len(words[0]) for word in words), "the dictionary words must have equal length")
    text = module.random_text(200, rng)
    require(len(text) == 200, "random_text must return n characters")

    elapsed = module.time_method(lambda: None)
    require(isinstance(elapsed, (int, float)) and elapsed >= 0, "time_method must return a non-negative duration")

    results = module.run_experiment()
    require(
        set(results) == {"brute_force", "trie", "rk"},
        "run_experiment must return the three series",
    )
    for name, values in results.items():
        require(
            len(values) == len(module.K_VALUES),
            f"run_experiment must report one timing per k for {name}",
        )
        require(all(value >= 0 for value in values), "timings must be non-negative")


def run_perf_benchmark():
    """Optional timing table: the three exact searchers on one text."""
    search = import_search_module()
    rng = random.Random(3212)
    text = "".join(rng.choice("ab") for _ in range(20_000))
    pattern = "".join(rng.choice("ab") for _ in range(8))
    print("\n--- Quick timing check (n = 20,000, m = 8) ---")
    print(f"{'method':>12} | {'time (ms)':>10}")
    print("-" * 26)
    for name, call in (
        ("naive", lambda: search.naive_search(text, pattern)),
        ("KMP", lambda: search.kmp_search(text, pattern)),
        ("Rabin-Karp", lambda: search.rabin_karp(text, pattern, 1_000_000_007)),
    ):
        start = time.perf_counter()
        call()
        print(f"{name:>12} | {(time.perf_counter() - start) * 1000:>10.2f}")


def main():
    target_dir = os.path.dirname(os.path.abspath(__file__))
    perf_mode = False

    args = sys.argv[1:]
    if "--perf" in args:
        perf_mode = True
        args.remove("--perf")

    if args:
        target_dir = os.path.abspath(args[0])

    sys.path.insert(0, target_dir)

    def hash_case():
        check_hash_table(import_hash_module(), random.Random(3212))

    def prefix_case():
        check_prefix_function(import_search_module(), random.Random(3212))

    def search_case():
        check_naive_and_kmp(import_search_module(), random.Random(3212))

    def rabin_case():
        check_rabin_karp(import_search_module(), random.Random(3212))

    def trie_case():
        check_trie(import_trie_module())

    def hamming_case():
        check_hamming(import_trie_module())

    def brute_case():
        check_brute_force_approx(import_trie_module(), random.Random(3212))

    def trie_approx_case():
        check_trie_approx(import_trie_module(), random.Random(3212))

    def rk_case():
        check_rk_approx(import_trie_module(), random.Random(3212))

    def experiment_case():
        check_experiment(import_experiment_module())

    cases = [
        ("ChainedHashTable: insert, update, lookup, delete, growth", hash_case),
        ("prefix_function: known patterns and random patterns", prefix_case),
        ("naive_search and kmp_search: random texts", search_case),
        ("rabin_karp: small and large moduli", rabin_case),
        ("Trie: search and prefix listing", trie_case),
        ("hamming: distances and length mismatch", hamming_case),
        ("brute_force_approx: running example and random texts", brute_case),
        ("trie_approx: running example and random texts", trie_approx_case),
        ("rk_approx: running example and random texts", rk_case),
        ("experiment: generators, timing, and run_experiment", experiment_case),
    ]

    print(f"Running Homework 2 checks against: {target_dir}\n")
    status = run_checks(cases)

    if perf_mode and status == 0:
        run_perf_benchmark()

    sys.exit(status)


if __name__ == "__main__":
    main()
