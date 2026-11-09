class KVPair:
    def __init__(self, key, value) -> None:
        self.key = key
        self.value = value

class ChainedHashTable:
    buckets: list[list[KVPair]]
    num_keys: int = 0

    def __init__(self, capacity) -> None:
        self.cap: int = capacity
        # initialize correct number of buckets
        self.buckets: list[list[KVPair]] = [] * capacity 

    def insert(self, key, value) -> bool:
        bucket: int = key % self.cap

        # update existing kvpair if found
        if key in self.buckets[bucket]:
            for k in self.buckets[bucket]:
                if k.key == key:
                    k.value = value
                    return False

        new_kv: KVPair = KVPair(key, value)
        
        self.buckets[bucket].append(new_kv)
        self.num_keys += 1

        return True

    def lookup(self, key) -> str | None:
        bucket = key % self.cap

        for pair in self.buckets[bucket]:
            if pair.key == key:
                return pair.value
   
        return None

    def delete(self, key) -> bool:
        bucket = key % self.cap

        for i, pair in enumerate(self.buckets[bucket]):
            if pair.key == key:
                del self.buckets[bucket][i]
                self.num_keys -= 1
                return True
            
        return False

    def keys(self) -> list[str]:
        k = []
        for bucket in self.buckets:
            for pair in bucket:
                k.append(pair.key)

        return k

    def capacity(self):
        return self.cap

    def load_factor(self) -> float:
        return self.num_keys / self.cap

    def len(self):
        len = 0
        for bucket in self.buckets:
            for _ in bucket:
                len += 1
        
        return len
