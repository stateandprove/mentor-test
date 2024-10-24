class MyDict:
    LOAD_FACTOR_THRESHOLD = 0.7

    def __init__(self, initial_size=8):
        self._buckets = [[] for _ in range(initial_size)]
        self._size = 0

    def _hash(self, key):
        return hash(key) % len(self._buckets)

    def _resize_and_rehash(self):
        new_buckets = [[] for _ in range(len(self._buckets) * 2)]

        for bucket in self._buckets:
            for key, value in bucket:
                new_bucket_index = hash(key) % len(new_buckets)
                new_buckets[new_bucket_index].append((key, value))

        self._buckets = new_buckets

    def _get_load_factor(self):
        return self._size / len(self._buckets)

    def _check_load_factor(self):
        load_factor = self._get_load_factor()

        if load_factor > self.LOAD_FACTOR_THRESHOLD:
            self._resize_and_rehash()

    def _get_bucket(self, key):
        bucket_index = self._hash(key)
        bucket = self._buckets[bucket_index]
        return bucket

    def __setitem__(self, key, value):
        bucket = self._get_bucket(key)

        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return None

        bucket.append((key, value))
        self._size += 1
        self._check_load_factor()

    def __getitem__(self, key):
        bucket = self._get_bucket(key)

        for k, v in bucket:
            if k == key:
                return v

        return None

    def __delitem__(self, key):
        bucket = self._get_bucket(key)

        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self._size -= 1
                return None

    def __contains__(self, key):
        bucket_index = self._hash(key)
        bucket = self._buckets[bucket_index]

        for k, v in bucket:
            if k == key:
                return True

        return False

    def keys(self):
        return [k for bucket in self._buckets for k, v in bucket]

    def values(self):
        return [v for bucket in self._buckets for k, v in bucket]

    def items(self):
        return [(k, v) for bucket in self._buckets for k, v in bucket]

    def __str__(self):
        items = ", ".join(f"{repr(k)}: {repr(v)}" for bucket in self._buckets for k, v in bucket)
        return f"{{{items}}}"


my_dict = MyDict()
my_dict['name'] = 'Alice'
my_dict['age'] = 30

assert my_dict['name'] == 'Alice'
assert ('city' in my_dict) is False
assert my_dict['non_existing_field'] is None
del my_dict['age']
assert my_dict.keys() == ['name']
assert my_dict.values() == ['Alice']
