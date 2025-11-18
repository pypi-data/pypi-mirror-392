from .bool_hybrid_array import *
import builtins


class IntBitTag(BHA_Bool, metaclass=ResurrectMeta):
    def __str__(self):
        return "'-1'" if (hasattr(self, 'is_sign_bit') and self.is_sign_bit and self) else "'1'" if self else "'0'"
    __repr__ = __str__

class IntHybridArray(BoolHybridArray):
    def __init__(self, int_array: list[int], bit_length: int = 8):
        self.bit_length = bit_length
        bool_data = []
        max_required_bits = 1
        for num in int_array:
            if num == 0:
                required_bits = 1
            else:
                abs_num = abs(num)
                num_bits_needed = abs_num.bit_length()
                required_bits = 1 + num_bits_needed
            if required_bits > max_required_bits:
                max_required_bits = required_bits
        self.bit_length = max_required_bits
        for num in int_array:
            if num >= 0:
                sign_bit = False
                num_bits = [bool((num >> i) & 1) for i in range(self.bit_length - 1)]
            else:
                sign_bit = True
                abs_num = abs(num)
                num_bits = [not bool((abs_num >> i) & 1) for i in range(self.bit_length - 1)]
                carry = 1
                for j in range(len(num_bits)):
                    if carry:
                        num_bits[j] = not num_bits[j]
                        carry = 0 if num_bits[j] else 1
            bool_data.append(sign_bit)
            bool_data.extend(num_bits)
        temp_arr = BoolHybridArr(bool_data, Type=IntBitTag)
        super().__init__(temp_arr.split_index, temp_arr.size, temp_arr.is_sparse, temp_arr.Type, False)
        for idx in range(temp_arr.size):
            self[idx] = temp_arr[idx].value
        for i in range(0, self.size, self.bit_length):
            if i < self.size:
                self[i].is_sign_bit = True

    def to_int(self, bit_chunk):
        sign_bit = bit_chunk[0].value
        num_bits = [bit.value for bit in bit_chunk[1:]]
        if not sign_bit:
            num = 0
            for j in range(len(num_bits)):
                if num_bits[j]:
                    num += (1 << j)
        else:
            num_bits_inv = [not b for b in num_bits]
            carry = 1
            for j in range(len(num_bits_inv)):
                if carry:
                    num_bits_inv[j] = not num_bits_inv[j]
                    carry = 0 if num_bits_inv[j] else 1
            num = 0
            for j in range(len(num_bits_inv)):
                if num_bits_inv[j]:
                    num += (1 << j)
            num = -num
        return num

    def __getitem__(self, key):
        if isinstance(key, slice):
            start, stop, step = key.indices(len(self))
            result = []
            for i in range(start, stop, step):
                block_idx = i // self.bit_length
                bit_idx_in_block = i % self.bit_length
                block_start = block_idx * self.bit_length
                block_end = block_start + self.bit_length
                bit_chunk = [self[j] for j in range(block_start, block_end)]
                num = self.to_int(bit_chunk)
                result.append(num)
            return IntHybridArray(result, self.bit_length)
        key = key if key >= 0 else key + len(self)
        if not (0 <= key < len(self)):
            raise IndexError("索引超出范围")
        block_idx = key // self.bit_length
        block_start = block_idx * self.bit_length
        block_end = block_start + self.bit_length
        bit_chunk = [self[j] for j in range(block_start, block_end)]
        return self.to_int(bit_chunk)

    def __setitem__(self, key, value):
        value = int(value)
        if isinstance(key, slice):
            start, stop, step = key.indices(len(self))
            values = list(value) if isinstance(value, (list, tuple, IntHybridArray)) else [value] * ((stop - start + step - 1) // step)
            idx = 0
            for i in range(start, stop, step):
                self[i] = values[idx % len(values)]
                idx += 1
            return
        key = key if key >= 0 else key + len(self)
        if not (0 <= key < len(self)):
            raise IndexError("索引超出范围")
        block_idx = key // self.bit_length
        block_start = block_idx * self.bit_length
        bool_data = []
        num = value
        if num >= 0:
            sign_bit = False
            num_bits = [bool((num >> i) & 1) for i in range(self.bit_length - 1)]
        else:
            sign_bit = True
            abs_num = abs(num)
            num_bits = [not bool((abs_num >> i) & 1) for i in range(self.bit_length - 1)]
            carry = 1
            for j in range(len(num_bits)):
                if carry:
                    num_bits[j] = not num_bits[j]
                    carry = 0 if num_bits[j] else 1
        bool_data.append(sign_bit)
        bool_data.extend(num_bits)
        for idx in range(self.bit_length):
            self[block_start + idx] = bool_data[idx]

    def __iter__(self):
        for i in range(0, self.size, self.bit_length):
            bit_chunk = [self[j] for j in range(i, i + self.bit_length)]
            yield self.to_int(bit_chunk)

    def __str__(self):
        return f"IntHybridArray([{', '.join(map(str, self))}])"

    def __len__(self):
        return self.size // self.bit_length
builtins.IntHybridArray = IntHybridArray
if __name__ == "__main__":
    test = [0, 10, -5, 31, 32768, -65536]
    arr = IntHybridArray(test)
    print(arr)
    print(arr[2])
    arr[3] = -100
    print(arr)
    print(list(arr))
    print(arr[1:4])