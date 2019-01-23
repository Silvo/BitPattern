from itertools import groupby

class BitPattern(object):
    class ItemParts(object):
        def __init__(self, mask, shift, bits):
            self.mask  = mask
            self.shift = shift
            self.bits  = bits

    def __init__(self, format_str, legend_dict):
        self.format_str = format_str
        self.legend = legend_dict

        self._parts = self._extract_parts(format_str)

        self.positive_mask = 0
        self.negative_mask = 0
        self._build_masks(self._parts)

    def _extract_parts(self, format_str):
        parts_dict = {}
        combined = format_str.replace(' ', '')
        pattern_len = len(combined)
        chars = {}
        for i, char in enumerate(combined):
            if char not in chars:
                chars[char] = []
            chars[char].append(i)

        for c in chars:
            continuous_parts = []
            for k, g in groupby(enumerate(chars[c]), lambda x: x[0] - x[1]):
                continuous_parts.append([e[1] for e in g])

            parts = []
            for group in continuous_parts:
                bits = len(group)
                shift = pattern_len - 1 - group[-1]
                mask = (2**bits) - 1
                parts.append(self.ItemParts(mask, shift, bits))

            parts_dict[c] = parts

        return parts_dict

    def _build_masks(self, parts):
        ones = parts.get('1', [])
        bits_handled = 0
        for p in sorted(ones, key=lambda x: x.shift):
            self.positive_mask |= (p.mask << p.shift)
            bits_handled += p.bits

        zeros = parts.get('0', [])
        bits_handled = 0
        for p in sorted(zeros, key=lambda x: x.shift):
            self.negative_mask |= (p.mask << p.shift)
            bits_handled += p.bits

    def match(self, value):
        match = (value & self.positive_mask) == self.positive_mask
        if match:
            match = (~value & self.negative_mask) == self.negative_mask

        return match

    def decode(self, value):
        values = {}
        for c, parts in self._parts.items():
            values[c] = 0
            bits_handled = 0
            for p in sorted(parts, key=lambda x: x.shift):
                values[c] |= ((value & (p.mask << p.shift)) >> (p.shift - bits_handled))
                bits_handled += p.bits

        named_values = {}
        for id_, name in self.legend.items():
            if id_ in values:
                named_values[name] = '{} ({})'.format(values[id_], bin(values[id_]))

        return named_values
