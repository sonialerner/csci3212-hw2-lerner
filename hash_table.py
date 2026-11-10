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
        self.buckets: list[list[KVPair]] = [[] for _ in range(capacity)]
    
    def __len__(self):
        len = 0
        for bucket in self.buckets:
            for _ in bucket:
                len += 1
        
        return len

    def insert(self, key, value) -> bool:
        # update existing kvpair if found
        for k in self.buckets[hash(key) % self.cap]:
            if k.key == key:
                k.value = value
                return False

        new_kv: KVPair = KVPair(key, value)
        bucket: int = hash(key) % self.cap # recompute bucket
        
        self.buckets[bucket].append(new_kv)
        self.num_keys += 1

        # check load factor and adjust if needed
        if self.load_factor() > 0.75:
            new_cht = ChainedHashTable(self.cap * 2)
            for b in self.buckets:
                for pair in b:
                    new_cht.insert(pair.key, pair.value)

            # update current cht
            self.buckets = new_cht.buckets
            self.cap = new_cht.cap
            self.num_keys = new_cht.num_keys

        return True

    def lookup(self, key) -> str | None:
        bucket = hash(key) % self.cap

        for pair in self.buckets[bucket]:
            if pair.key == key:
                return pair.value
   
        return None

    def delete(self, key) -> bool:
        bucket = hash(key) % self.cap

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
        
