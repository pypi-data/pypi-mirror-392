



from hashlib import md5
import ctypes
import json
import random
import requests
import time
from urllib.parse import urlparse, urlencode
from binascii        import hexlify
from uuid            import uuid4
from requests        import request



import hashlib
import math


def int_overflow(val):
    maxint = 2147483647
    if not -maxint - 1 <= val <= maxint:
        val = (val + (maxint + 1)) % (2 * (maxint + 1)) - maxint - 1
    return val


def unsigned_right_shitf(n, i):
    if n < 0:
        n = ctypes.c_uint32(n).value
    if i < 0:
        return -int_overflow(n << abs(i))
    return int_overflow(n >> i)


def decode(string):
    _0x50ff23 = {
        48: 0, 49: 1, 50: 2, 51: 3, 52: 4, 53: 5,
        54: 6, 55: 7, 56: 8, 57: 9, 97: 10, 98: 11,
        99: 12, 100: 13, 101: 14, 102: 15
    }
    arr = []
    for i in range(0, 32, 2):
        arr.append(_0x50ff23[ord(string[i])] << 4 | _0x50ff23[ord(string[i + 1])])
    return arr


def md5_arry(arry):
    m = hashlib.md5()
    m.update(bytearray(arry))
    return m.hexdigest()


def md5_string(s):
    m = hashlib.md5()
    m.update(s.encode())
    return m.hexdigest()


def encodeWithKey(key, data):
    result = [None] * 256
    temp = 0
    output = ""
    for i in range(256):
        result[i] = i
    for i in range(256):
        temp = (temp + result[i] + key[i % len(key)]) % 256
        temp1 = result[i]
        result[i] = result[temp]
        result[temp] = temp1
    temp2 = 0
    temp = 0
    for i in range(len(data)):
        temp2 = (temp2 + 1) % 256
        temp = (temp + result[temp2]) % 256
        temp1 = result[temp2]
        result[temp2] = result[temp]
        result[temp] = temp1
        output += chr(ord(data[i]) ^ result[(result[temp2] + result[temp]) % 256])
    return output


def b64_encode(string, key_table="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="):
    last_list = list()
    for i in range(0, len(string), 3):
        try:
            num_1 = ord(string[i])
            num_2 = ord(string[i + 1])
            num_3 = ord(string[i + 2])
            arr_1 = num_1 >> 2
            arr_2 = ((3 & num_1) << 4 | (num_2 >> 4))
            arr_3 = ((15 & num_2) << 2) | (num_3 >> 6)
            arr_4 = 63 & num_3
        except IndexError:
            arr_1 = num_1 >> 2
            arr_2 = ((3 & num_1) << 4) | 0
            arr_3 = 64
            arr_4 = 64
        last_list.append(arr_1)
        last_list.append(arr_2)
        last_list.append(arr_3)
        last_list.append(arr_4)
    return "".join([key_table[value] for value in last_list])


def cal_num_list(_num_list):
    new_num_list = []
    for x in [3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 4, 6, 8, 10, 12, 14, 16, 18, 20]:
        new_num_list.append(_num_list[x - 1])
    return new_num_list


def _0x22a2b6(_0x59d7ab, _0x151cde, _0x1e0c94, _0x54aa83, _0x76d8ab, _0x550bdb, _0xb90041, _0x44b16d, _0x28659f,
              _0x252c2c, _0x365218, _0x48af11, _0x25e3db, _0x34084f, _0x4f0729, _0x46a34c, _0x1f67f1, _0x5cd529,
              _0x53097b):
    _0xa0a6ac = [0] * 19
    _0xa0a6ac[-0x1 * -0x2192 + 0x11b * 0x5 + -0x2719 * 0x1] = _0x59d7ab
    _0xa0a6ac[0x4a * 0x3 + -0x6d * 0xb + -0x1e9 * -0x2] = _0x365218
    _0xa0a6ac[-0x59f * -0x3 + -0x46c * -0x4 + -0x228b] = _0x151cde
    _0xa0a6ac[0x11a1 + 0xf3d * -0x1 + 0x3 * -0xcb] = _0x48af11
    _0xa0a6ac[-0x1 * -0xa37 + 0x13 * 0x173 + -0x25bc] = _0x1e0c94
    _0xa0a6ac[-0x4 * -0x59f + -0x669 * 0x4 + 0x32d] = _0x25e3db
    _0xa0a6ac[-0x1b42 + 0x10 * -0x24 + 0x1d88] = _0x54aa83
    _0xa0a6ac[0x2245 + 0x335 * 0x6 + -0x357c] = _0x34084f
    _0xa0a6ac[0x3fb + 0x18e1 + -0x1cd4] = _0x76d8ab
    _0xa0a6ac[0x3 * 0x7a + 0x1 * 0x53f + 0x154 * -0x5] = _0x4f0729
    _0xa0a6ac[0x25a * -0x9 + 0x11f6 + 0xa6 * 0x5] = _0x550bdb
    _0xa0a6ac[-0x1b * -0x147 + -0x21e9 * -0x1 + 0x445b * -0x1] = _0x46a34c
    _0xa0a6ac[-0x2f * 0xaf + 0x22f0 + -0x2c3] = _0xb90041
    _0xa0a6ac[0x2f * 0x16 + 0x17 * 0x19 + -0x63c] = _0x1f67f1
    _0xa0a6ac[-0x46a * 0x1 + 0xb * -0x97 + 0xaf5] = _0x44b16d
    _0xa0a6ac[0x47 * 0x4f + -0x8cb * -0x4 + -0x3906] = _0x5cd529
    _0xa0a6ac[-0x7 * 0x40e + 0xb8b + 0x10e7] = _0x28659f
    _0xa0a6ac[0x6f9 + 0x196b + 0x5 * -0x677] = _0x53097b
    _0xa0a6ac[-0xa78 + 0x1b89 + 0xe5 * -0x13] = _0x252c2c
    return ''.join([chr(x) for x in _0xa0a6ac])


def _0x263a8b(_0x2a0483):
    return "\u0002" + "ÿ" + _0x2a0483


def get_x_bogus(params, data, user_agent):
    s0 = md5_string(data)
    s1 = md5_string(params)
    s0_1 = md5_arry(decode(s0))
    s1_1 = md5_arry(decode(s1))
    d = encodeWithKey([0, 1, 12], user_agent)
    ua_str = b64_encode(d)
    ua_str_md5 = md5_string(ua_str)
    timestamp = int(time.time())
    canvas = 536919696
    salt_list = [timestamp, canvas, 64, 0, 1, 12, decode(s1_1)[-2], decode(s1_1)[-1], decode(s0_1)[-2],
                 decode(s0_1)[-1], decode(ua_str_md5)[-2], decode(ua_str_md5)[-1]]
    for x in [24, 16, 8, 0]:
        salt_list.append(salt_list[0] >> x & 255)
    for x in [24, 16, 8, 0]:
        salt_list.append(salt_list[1] >> x & 255)
    _tem = 64
    for x in salt_list[3:]:
        _tem = _tem ^ x
    salt_list.append(_tem)
    salt_list.append(255)
    num_list = cal_num_list(salt_list)
    short_str_2 = encodeWithKey([255], _0x22a2b6(*num_list))
    short_str_3 = _0x263a8b(short_str_2)
    x_b = b64_encode(short_str_3, "Dkdpgh4ZKsQB80/Mfvw36XI1R25-WUAlEi7NLboqYTOPuzmFjJnryx9HVGcaStCe")
    return x_b


def random_k(unm):
    y = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    z = []
    for i in range(unm):
        z.append(random.choice(y))

    return ''.join(z)


def random_32():
    reut = 'xxxxxxxxxxxx4xxxyxxxxxxxxxxxxxxx'
    hex_t = '0123456789abcdef'
    reut_li = []
    for i in reut:
        if i == 'x':
            reut_li.append(random.choice(hex_t))
        else:
            reut_li.append(i)
    return ''.join(reut_li)


def int32(i):
    return int(0xFFFFFFFF & i)


def fixk(k):
    if len(k) < 4:
        k = k[:4]
        k.extend([0] * (4 - len(k)))
    return k

def mx(sum, y, z, p, e, k):
    tmp = (((z >> 5) ^ (y << 2)) + ((y >> 3) ^ (z << 4)))
    tmp ^= ((sum ^ y) + (k[p & 3 ^ e] ^ z))
    return tmp


def toBinaryString(v, includeLength):
    length = len(v)
    n = length << 2
    if includeLength:
        m = v[length - 1]
        n -= 4
        if m < n - 3 or m > n:
            return None
        n = m
    for i in range(length):
        v[i] = chr(v[i] & 0xFF) + chr((v[i] >> 8) & 0xFF) + chr((v[i] >> 16) & 0xFF) + chr((v[i] >> 24) & 0xFF)
    result = ''.join(v)
    if includeLength:
        return result[:n]
    return result


def encryptUint32Array(v, k):
    DELTA = 2654435769
    length = len(v)
    n = length - 1
    y, z, sum, e, p, q = 0, 0, 0, 0, 0, 0
    z = v[n]
    sum = 0
    for q in range(int(6 + 52 / length)):
        sum = int32(sum + DELTA)
        e = int(sum >> 2) & 3
        for p in range(n):
            y = v[p + 1]
            z = v[p] = int32(v[p] + mx(sum, y, z, p, e, k))
        y = v[0]
        z = v[n] = int32(v[n] + mx(sum, y, z, n, e, k))
    return v


def decryptUint32Array(v, k):
    DELTA = 2654435769
    length = len(v)
    n = length - 1
    y, z, sum, e, p, q = 0, 0, int32(0), 0, 0, 0
    y = v[0]
    q = math.floor(6 + 52 / length)
    sum = int32(q * DELTA)
    while sum != 0:
        e = int32(sum >> 2 & 3)
        p = n
        while p > 0:
            z = v[p - 1]
            y = v[p] = int32(v[p] - mx(sum, y, z, p, e, k))
            p -= 1
        z = v[n]
        y = v[0] = int32(v[0] - mx(sum, y, z, 0, e, k))
        sum = int32(sum - DELTA)
    return v


def utf8DecodeShortString(bs, n):
    charCodes = []
    i = 0
    off = 0
    len_ = len(bs)
    while i < n and off < len_:
        unit = ord(bs[off])
        off += 1
        if unit < 0x80:
            charCodes.append(unit)
        elif 0xc2 <= unit < 0xe0 and off < len_:
            charCodes.append(((unit & 0x1F) << 6) | (ord(bs[off]) & 0x3F))
            off += 1
        elif 0xe0 <= unit < 0xf0 and off + 1 < len_:
            charCodes.append(((unit & 0x0F) << 12) |
                             ((ord(bs[off]) & 0x3F) << 6) |
                             (ord(bs[off + 1]) & 0x3F))
            off += 2
        elif 0xf0 <= unit < 0xf8 and off + 2 < len_:
            rune = (((unit & 0x07) << 18) |
                    ((ord(bs[off]) & 0x3F) << 12) |
                    ((ord(bs[off + 1]) & 0x3F) << 6) |
                    (ord(bs[off + 2]) & 0x3F)) - 0x10000
            if 0 <= rune <= 0xFFFFF:
                charCodes.append(((rune >> 10) & 0x03FF) | 0xD800)
                charCodes.append((rune & 0x03FF) | 0xDC00)
            else:
                raise ValueError('Character outside valid Unicode range: '
                                 + hex(rune))
            off += 3
        else:
            raise ValueError('Bad UTF-8 encoding 0x' + hex(unit))
        i += 1
    return ''.join(chr(code) for code in charCodes)


def utf8DecodeLongString(bs, n):
    buf = []
    char_codes = [0] * 0x8000
    i = off = 0
    len_bs = len(bs)
    while i < n and off < len_bs:
        unit = ord(bs[off])
        off += 1
        divide = unit >> 4
        if divide < 8:
            char_codes[i] = unit
        elif divide == 12 or divide == 13:
            if off < len_bs:
                char_codes[i] = ((unit & 0x1F) << 6) | (ord(bs[off]) & 0x3F)
                off += 1
            else:
                raise ValueError('Unfinished UTF-8 octet sequence')
        elif divide == 14:
            if off + 1 < len_bs:
                char_codes[i] = ((unit & 0x0F) << 12) | ((ord(bs[off]) & 0x3F) << 6) | (ord(bs[off + 1]) & 0x3F)
                off += 2
            else:
                raise ValueError('Unfinished UTF-8 octet sequence')
        elif divide == 15:
            if off + 2 < len_bs:
                rune = (((unit & 0x07) << 18) | ((ord(bs[off]) & 0x3F) << 12) | ((ord(bs[off + 1]) & 0x3F) << 6) | (
                            ord(bs[off + 2]) & 0x3F)) - 0x10000
                off += 3
                if 0 <= rune <= 0xFFFFF:
                    char_codes[i] = (((rune >> 10) & 0x03FF) | 0xD800)
                    i += 1
                    char_codes[i] = ((rune & 0x03FF) | 0xDC00)
                else:
                    raise ValueError('Character outside valid Unicode range: 0x' + hex(rune))
            else:
                raise ValueError('Unfinished UTF-8 octet sequence')
        else:
            raise ValueError('Bad UTF-8 encoding 0x' + hex(unit))
        if i >= 0x7FFF - 1:
            size = i + 1
            char_codes = char_codes[:size]
            buf.append(''.join([chr(c) for c in char_codes]))
            n -= size
            i = -1
        i += 1
    if i > 0:
        char_codes = char_codes[:i]
        buf.append(''.join([chr(c) for c in char_codes]))
    return ''.join(buf)


def utf8Decode(bs, n=None):
    if n is None or n < 0:
        n = len(bs)
    if n == 0:
        return ''
    if all(0 <= ord(c) <= 127 for c in bs) or not all(0 <= ord(c) <= 255 for c in bs):
        if n == len(bs):
            return bs
        return bs[:n]
    return utf8DecodeShortString(bs, n) if n < 0x7FFF else utf8DecodeLongString(bs, n)


def decrypt(data, key):
    if data is None or len(data) == 0:
        return data

    key = utf8Encode(key)

    return utf8Decode(
        toBinaryString(decryptUint32Array(toUint32Array(data, False), fixk(toUint32Array(key, False))), True))


def encrypt(data, key):
    if (data is None) or (len(data) == 0):
        return data
    data = utf8Encode(data)
    key = utf8Encode(key)
    return toBinaryString(
        encryptUint32Array(
            toUint32Array(data, True),
            fixk(toUint32Array(key, False))
        ),
        False
    )


def strData(x, y):
    b = [i for i in range(256)]
    c = 0
    d = ""
    for i in range(256):
        c = (c + b[i] + ord(x[i % len(x)])) % 256
        a = b[i]
        b[i] = b[c]
        b[c] = a
    e = 0
    c = 0
    for i in range(len(y)):
        e = (e + 1) % 256
        c = (c + b[e]) % 256
        a = b[e]
        b[e] = b[c]
        b[c] = a
        d += chr(ord(y[i]) ^ b[(b[e] + b[c]) % 256])
    return d


def bytes_to_string(a, b=None, c=None):
    d = 'Dkdpgh4ZKsQB80/Mfvw36XI1R25+WUAlEi7NLboqYTOPuzmFjJnryx9HVGcaStCe='
    e = '='
    if c:
        e = ''
    if b:
        d = b
    g = ''
    h = 0
    while len(a) >= h + 3:
        f = 0
        f = f | ord(a[h]) << 16
        f = f | ord(a[h + 1]) << 8
        f = f | ord(a[h + 2]) << 0
        g += d[(16515072 & f) >> 18]
        g += d[(258048 & f) >> 12]
        g += d[(4032 & f) >> 6]
        g += d[63 & f]
        h += 3
    if len(a) - h > 0:
        f = (255 & ord(a[h])) << 16 | (ord(a[h + 1]) << 8 if len(a) > h + 1 else 0)
        g += d[(16515072 & f) >> 18]
        g += d[(258048 & f) >> 12]
        g += d[(4032 & f) >> 6] if len(a) > h + 1 else e
        g += e
    return g


def bool_0_1(x):
    if x is None:
        return ''
    elif isinstance(x, bool):
        return '1' if x else '0'
    else:
        return x


def fromCharCode(value_typ):
    unc = ''
    for c in value_typ:
        unc += chr(c & 0xffff)

    return unc


def utf8Encode(str):
    if all(ord(c) < 128 for c in str):
        return str
    buf = []
    n = len(str)
    i = 0
    while i < n:
        codeUnit = ord(str[i])
        if codeUnit < 0x80:
            buf.append(str[i])
            i += 1
        elif codeUnit < 0x800:
            buf.append(chr(0xC0 | (codeUnit >> 6)))
            buf.append(chr(0x80 | (codeUnit & 0x3F)))
            i += 1
        elif codeUnit < 0xD800 or codeUnit > 0xDFFF:
            buf.append(chr(0xE0 | (codeUnit >> 12)))
            buf.append(chr(0x80 | ((codeUnit >> 6) & 0x3F)))
            buf.append(chr(0x80 | (codeUnit & 0x3F)))
            i += 1
        else:
            if i + 1 < n:
                nextCodeUnit = ord(str[i + 1])
                if codeUnit < 0xDC00 and 0xDC00 <= nextCodeUnit and nextCodeUnit <= 0xDFFF:
                    rune = (((codeUnit & 0x03FF) << 10) | (nextCodeUnit & 0x03FF)) + 0x010000
                    buf.append(chr(0xF0 | ((rune >> 18) & 0x3F)))
                    buf.append(chr(0x80 | ((rune >> 12) & 0x3F)))
                    buf.append(chr(0x80 | ((rune >> 6) & 0x3F)))
                    buf.append(chr(0x80 | (rune & 0x3F)))
                    i += 2
                    continue
            raise ValueError('Malformed string')
    return ''.join(buf)


def toUint32Array(bs, includeLength):
    length = len(bs)
    n = length >> 2
    if (length & 3) != 0:
        n += 1
    if includeLength:
        v = [0] * (n + 1)
        v[n] = length
    else:
        v = [0] * n
    for i in range(length):
        v[i >> 2] |= ord(bs[i]) << ((i & 3) << 3)
    return v


def bytes2string_1(a, b="", c=False):
    d = 'Dkdpgh4ZKsQB80/Mfvw36XI1R25+WUAlEi7NLboqYTOPuzmFjJnryx9HVGcaStCe'
    e = ''
    if c:
        e = ''
    if b:
        d = b
    g = ''
    h = 0
    while len(a) >= h + 3:
        f = 0
        f |= ord(a[h]) << 16
        f |= ord(a[h + 1]) << 8
        f |= ord(a[h + 2]) << 0
        g += d[(16515072 & f) >> 18]
        g += d[(258048 & f) >> 12]
        g += d[(4032 & f) >> 6]
        g += d[63 & f]
        h += 3
    if len(a) - h > 0:
        f = (255 & ord(a[h])) << 16
        if len(a) > h + 1:
            f |= (255 & ord(a[h + 1])) << 8
        g += d[(16515072 & f) >> 18]
        g += d[(258048 & f) >> 12]
        if len(a) > h + 1:
            g += d[(4032 & f) >> 6]
        else:
            g += e
        g += e
    return g


def douyin_xxbg_q_encrypt(obj, obj_2=None):
    if obj_2:
        j = 0
        for i in range(len(obj)):
            if obj[j]['p']:
                obj[j]['r'] = obj_2[j]
                j += 1
    temp_text = ''
    for arg in obj:
        temp_text += bool_0_1(arg['r']) + '^^'
    temp_text += str(int(time.time() * 1000))
    salt = random_32()
    temp_num = math.floor(ord(salt[3]) / 8) + ord(salt[3]) % 8
    key = salt[4:4 + temp_num]
    entrypt_byte = encrypt(temp_text, key) + salt
    res = bytes2string_1(entrypt_byte, 'Dkdpgh4ZKsQB80/Mfvw36XI1R25+WUAlEi7NLboqYTOPuzmFjJnryx9HVGcaStCe==')
    return res


def tiktok_mssdk_encode(value):
    b64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-."
    k = random_k(4)
    q = encrypt(value, k)
    result = k + bytes2string_1(q, b64)
    return result


def encrypt_strData(text):
    key_num = random.randint(200, 256)
    temp = fromCharCode([65, key_num]) + strData(fromCharCode([key_num]), text)
    return bytes_to_string(temp)




def left_shift(x, y):
    return ctypes.c_int(x << y).value


def get_time():
    return str(int(time.time() * 1000))


class AFREncrypt:
    def __init__(self, user_agent):
        self.ua = user_agent
        self.href_hash = ""
        self.ua_hash = ""
        self.params_hash = ""
        self.fix_hash = 65599
        self.fix_bin = 8240
        self.fix_seq = 65521
        self.canvas_hash = 536919696
        # self.ctx = self.load_js()

    # def load_js(self):
    #     # with open("./DouyinRegisterDevice/app/jsFiles/websdk.js", mode="r", encoding="utf-8") as f:
    #     with open("./websdk.js", mode="r", encoding="utf-8") as f:
    #         ctx = execjs.compile(f.read())
    #     # 本地
    #     # with open("./jsFiles/websdk.js", mode="r", encoding="utf-8") as f:
    #     #     ctx = execjs.compile(f.read())
    #
    #     return ctx

    @staticmethod
    def move_char_calc(nor):
        if 0 <= nor < 26:
            char_at = nor + 65
        elif 26 <= nor < 52:
            char_at = nor + 71
        elif nor == 62 or nor == 63:
            char_at = nor - 17
        else:
            char_at = nor - 4
        return chr(char_at)

    @staticmethod
    def unsigned_right_shift(signed, i=0):
        shift = signed % 0x100000000
        return shift >> i

    def sdb_hash(self, string=None, sdb_value=0):
        for index, char in enumerate(string):
            if string.startswith("_02B4Z6wo00"):
                sdb_value = self.unsigned_right_shift((sdb_value * self.fix_hash) + ord(char))
            elif string.startswith("{"):
                if index in [0, 1]:
                    sdb_value = self.unsigned_right_shift((sdb_value * self.fix_hash) ^ ord(char))
                else:
                    sdb_value = self.unsigned_right_shift((sdb_value * self.fix_hash) + ord(char))
            else:
                sdb_value = self.unsigned_right_shift((sdb_value ^ ord(char)) * self.fix_hash)
        return sdb_value

    def char_to_signature(self, sequence_num):
        offsets = [24, 18, 12, 6, 0]
        string = ""
        for offset in offsets:
            nor = sequence_num >> offset & 63
            string += self.move_char_calc(nor)
        return string

    def href_sequence(self, url):
        timestamp = int(time.time())
        timestamp_hash = self.sdb_hash(str(timestamp))
        self.href_hash = self.sdb_hash(url.split("//")[-1], sdb_value=timestamp_hash)
        sequence = timestamp ^ (self.href_hash % self.fix_seq * self.fix_seq)
        sequence = self.unsigned_right_shift(sequence)
        str_bin_sequence = str(bin(sequence)).replace("0b", "")
        fix_zero = "0" * (32 - len(str_bin_sequence))
        binary = f"{bin(self.fix_bin)}{fix_zero}{str_bin_sequence}".replace("0b", "")
        sequence_number = int(binary, 2)
        return sequence_number

    def char_to_signature1(self, sequence):
        sequence_first = sequence >> 2
        signature_one = self.char_to_signature(sequence_first)
        return signature_one

    def char_to_signature2(self, sequence):
        sequence_second = (sequence << 28) ^ (self.fix_bin >> 4)
        signature_two = self.char_to_signature(sequence_second)
        return signature_two

    def char_to_signature3(self, sequence):
        timestamp_sequence = sequence ^ self.canvas_hash
        sequence_three = left_shift(self.fix_bin, 26) ^ self.unsigned_right_shift(timestamp_sequence, i=6)
        signature_three = self.char_to_signature(sequence_three)
        return signature_three

    def char_to_signature4(self, sequence):
        timestamp_sequence = sequence ^ self.canvas_hash
        signature_four = self.move_char_calc(timestamp_sequence & 63)
        return signature_four

    def char_to_signature5(self, sequence, params, body=None):
        if body:
            new_body = dict()
            for key in sorted(body):
                new_body[key] = body[key]
            body_str = json.dumps(new_body, ensure_ascii=False).replace(" ", "")
            body_hash = self.sdb_hash(body_str)
            params = f"body_hash={body_hash}&{params}"
        sdb_sequence = self.sdb_hash(str(sequence))
        self.ua_hash = self.sdb_hash(self.ua, sdb_sequence)
        self.params_hash = self.sdb_hash(params, sdb_sequence)
        sequence_five = (((self.ua_hash % self.fix_seq) << 16) ^ (self.params_hash % self.fix_seq)) >> 2
        signature_five = self.char_to_signature(sequence_five)
        return signature_five

    def char_to_signature6(self, sequence):
        ua_remainder = self.ua_hash % self.fix_seq
        data_remainder = self.params_hash % self.fix_seq
        ua_data_number = ((int(ua_remainder) << 16) ^ int(data_remainder)) << 28
        sequence_six = ua_data_number ^ self.unsigned_right_shift((288 ^ sequence), 4)
        signature_six = self.char_to_signature(sequence_six)
        return signature_six

    def char_to_signature7(self):
        sequence_seven = self.href_hash % self.fix_seq
        signature_seven = self.char_to_signature(int(sequence_seven))
        return signature_seven

    def char_to_signature_hex(self, signature):
        sdb_signature = self.sdb_hash(signature)
        hex_signature = hex(sdb_signature).replace("0x", "")
        return hex_signature[-2:]

    def get_x_bogus(self, params, body=None, content_type=None):
        body_str = ""
        if content_type == "data":
            body_str = urlencode(body)
        elif content_type == "json":
            body_str = json.dumps(body, ensure_ascii=False).replace(" ", "")
        # x_bogus = self.ctx.call("get_xb", params, body_str, self.ua, self.canvas_hash)
        x_bogus = get_x_bogus(params, body_str, self.ua)
        return x_bogus

    def sign_100(self, ttscid):
        # sign = self.ctx.call("tiktok_mssdk_encode", ttscid)
        sign = tiktok_mssdk_encode(ttscid)
        return sign

    def generate_signature(self, href, api, body=None, content_type=None, ttscid="", prefix="_02B4Z6wo00001"):
        params = api.split("?")[1]
        params_str = str()
        if urlparse(api).query.split("&"):
            params_dict = {item.split("=")[0]: item.split("=")[1] for item in urlparse(api).query.split("&")}
            sort_dict = dict(sorted(params_dict.items(), key=lambda item: item[0]))
            for key, value in sort_dict.items():
                params_str += f"{key}={value}&"
        params_str += f"pathname={urlparse(api).path}&tt_webid=&uuid="
        x_bogus = self.get_x_bogus(params, body, content_type)
        params_str = f"X-Bogus={x_bogus}&{params_str}"
        sequence = self.href_sequence(href)
        sign1 = self.char_to_signature1(sequence)
        sign2 = self.char_to_signature2(sequence)
        sign3 = self.char_to_signature3(sequence)
        sign4 = self.char_to_signature4(sequence)
        sign5 = self.char_to_signature5(sequence, params_str, body)
        sign6 = self.char_to_signature6(sequence)
        sign7 = self.char_to_signature7()
        signature = f"{prefix}{sign1}{sign2}{sign3}{sign4}{sign5}{sign6}{sign7}"
        if ttscid:
            signature = f"{signature}{self.sign_100(ttscid)}"
        sign8 = self.char_to_signature_hex(signature)
        _signature = f"{signature}{sign8}"
        return x_bogus, _signature

    def cookie_signature(self, href, ac_nonce, ttscid="", prefix="_02B4Z6wo00f01"):
        sequence = self.href_sequence(href)
        sign1 = self.char_to_signature1(sequence)
        sign2 = self.char_to_signature2(sequence)
        sign3 = self.char_to_signature3(sequence)
        sign4 = self.char_to_signature4(sequence)
        sign5 = self.char_to_signature5(sequence, ac_nonce)
        sign6 = self.char_to_signature6(sequence)
        sign7 = self.char_to_signature7()
        signature = f"{prefix}{sign1}{sign2}{sign3}{sign4}{sign5}{sign6}{sign7}"
        sign8 = self.char_to_signature_hex(signature)
        if ttscid:
            _signature = f"{signature}{self.sign_100(ttscid)}{sign8}"
        else:
            _signature = f"{signature}{sign8}"
        return _signature

    def encrypt_strData(self, canvas_chrome_str):
        # strData = self.ctx.call("encrypt_strData", canvas_chrome_str)
        strData =encrypt_strData(canvas_chrome_str)
        return strData

    def ms_token(self, href):
        url = "https://mssdk.snssdk.com/web/report?msToken="
        canvas_chrome = {
            "tokenList": [],
            "navigator": {
                "appCodeName": self.ua.split("/")[0],
                "appMinorVersion": "undefined",
                "appName": "Netscape",
                "appVersion": self.ua.replace("Mozilla/", ""),
                "buildID": "undefined",
                "doNotTrack": "null",
                "msDoNotTrack": "undefined",
                "oscpu": "undefined",
                "platform": "Win32",
                "product": "Gecko",
                "productSub": "20030107",
                "cpuClass": "undefined",
                "vendor": "Google Inc.",
                "vendorSub": "",
                "deviceMemory": "8",
                "language": "zh-CN",
                "systemLanguage": "undefined",
                "userLanguage": "undefined",
                "webdriver": "false",
                "cookieEnabled": 1,
                "vibrate": 3,
                "credentials": 99,
                "storage": 99,
                "requestMediaKeySystemAccess": 3,
                "bluetooth": 99,
                "hardwareConcurrency": 4,
                "maxTouchPoints": -1,
                "languages": "zh-CN",
                "touchEvent": 2,
                "touchstart": 2,
            },
            "wID": {
                "load": 0,
                "nativeLength": 33,
                "jsFontsList": "17f",
                "syntaxError": "Failed to construct WebSocket: The URL Create WebSocket is invalid.",
                "timestamp": get_time(),
                "timezone": 8,
                "magic": 3,
                "canvas": str(self.canvas_hash),
                "wProps": 374198,
                "dProps": 2,
                "jsv": "1.7",
                "browserType": 16,
                "iframe": 2,
                "aid": 6383,
                "msgType": 1,
                "privacyMode": 0,
                "aidList": [6383, 6383, 6383],
                "index": 1,
            },
            "window": {
                "Image": 3,
                "isSecureContext": 1,
                "ActiveXObject": 4,
                "toolbar": 99,
                "locationbar": 99,
                "external": 99,
                "mozRTCPeerConnection": 4,
                "postMessage": 3,
                "webkitRequestAnimationFrame": 3,
                "BluetoothUUID": 3,
                "netscape": 4,
                "localStorage": 99,
                "sessionStorage": 99,
                "indexDB": 4,
                "devicePixelRatio": 1,
                "location": href,
            },
            "webgl": {
                "antialias": 1,
                "blueBits": 8,
                "depthBits": 24,
                "greenBits": 8,
                "maxAnisotropy": 16,
                "maxCombinedTextureImageUnits": 32,
                "maxCubeMapTextureSize": 16384,
                "maxFragmentUniformVectors": 1024,
                "maxRenderbufferSize": 16384,
                "maxTextureImageUnits": 16,
                "maxTextureSize": 16384,
                "maxVaryingVectors": 30,
                "maxVertexAttribs": 16,
                "maxVertexTextureImageUnits": 16,
                "maxVertexUniformVectors": 4096,
                "shadingLanguageVersion": "WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)",
                "stencilBits": 0,
                "version": "WebGL 1.0 (OpenGL ES 2.0 Chromium)",
                "vendor": "Google Inc. (Intel)",
                "renderer": "ANGLE (Intel, Intel(R) HD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            },
            "document": {
                "characterSet": "UTF-8",
                "compatMode": "CSS1Compat",
                "documentMode": "undefined",
                "layers": 4,
                "all": 12,
                "images": 99,
            },
            "screen": {
                "innerWidth": random.randint(1200, 1600),
                "innerHeight": random.randint(600, 800),
                "outerWidth": random.randint(1200, 1600),
                "outerHeight": random.randint(600, 800),
                "screenX": 0,
                "screenY": 0,
                "pageXOffset": 0,
                "pageYOffset": 0,
                "availWidth": random.randint(1200, 1600),
                "availHeight": random.randint(600, 800),
                "sizeWidth": random.randint(1200, 1600),
                "sizeHeight": random.randint(600, 800),
                "clientWidth": random.randint(1200, 1600),
                "clientHeight": random.randint(600, 800),
                "colorDepth": 24,
                "pixelDepth": 24,
            },
            "plugins": {
                "plugin": [
                    "internal-pdf-viewer|application/pdf|pdf",
                    "internal-pdf-viewer|text/pdf|pdf",
                    "internal-pdf-viewer|application/pdf|pdf",
                    "internal-pdf-viewer|text/pdf|pdf",
                    "internal-pdf-viewer|application/pdf|pdf",
                    "internal-pdf-viewer|text/pdf|pdf",
                    "internal-pdf-viewer|application/pdf|pdf",
                    "internal-pdf-viewer|text/pdf|pdf",
                    "internal-pdf-viewer|application/pdf|pdf",
                    "internal-pdf-viewer|text/pdf|pdf",
                ],
                "pv": "0",
            },
            "custom": {},
        }
        str_data = self.encrypt_strData(json.dumps(canvas_chrome).replace(" ", ""))
        payload = {
            "dataType": 8,
            "magic": 538969122,
            "strData": str_data,
            "tspFromClient": int(get_time()),
            "version": 1,
        }
        x_bogus = self.get_x_bogus(url.split("?")[-1], payload, content_type="json")
        url = url + "&X-Bogus=" + x_bogus
        headers = {"user-agent": self.ua}
        response = requests.post(url, json=payload, headers=headers)
        return response.cookies.get("msToken")

    def get_info(self, url):
        api = "https://xxbg.snssdk.com/websdk/v1/getInfo?"
        startTime = int(time.time() * 1000)
        timestamp1 = startTime + random.randint(1, 3)
        timestamp2 = timestamp1 + random.randint(10, 15)
        timestamp3 = timestamp2 + random.randint(100, 150)
        timestamp4 = timestamp3 + random.randint(1, 10)
        plain_arr_1 = [
            {"n": "aid", "f": 4, "r": 6383},
            {"n": "startTime", "f": 3, "r": startTime},
            {"n": "abilities", "f": 3, "r": "111"},
            {"n": "canvas", "f": 3, "r": self.canvas_hash},
            {"n": "timestamp1", "f": 3, "r": timestamp1},
            {"n": "platform", "f": 0, "r": "Win32"},
            {"n": "hardwareConcurrency", "f": 0, "r": 4},
            {"n": "deviceMemory", "f": 0, "r": 8},
            {"n": "language", "f": 0, "r": "zh-CN"},
            {"n": "languages", "f": 0,
             "r": random.sample(['zh-CN', 'zh-TW', 'zh', 'en-US', 'en', 'zh-HK', 'ja'], random.randint(1, 7))},
            {"n": "resolution", "f": 3, "r": f"{random.randint(1200, 1600)}_{random.randint(600, 800)}_24"},
            {"n": "availResolution", "f": 3, "r": f"{random.randint(1200, 1600)}_{random.randint(600, 800)}"},
            {"n": "screenTop", "f": 1, "r": 0},
            {"n": "screenLeft", "f": 1, "r": 0},
            {"n": "devicePixelRatio", "f": 1, "r": 1.25},
            {"n": "productSub", "f": 0, "r": "20030107"},
            {"n": "battery", "f": 3, "p": 1, "r": "true_0_Infinity_1"},
            {"n": "touchInfo", "f": 3, "r": "0_false_false"},
            {"n": "timezone", "f": 3, "r": 480},
            {"n": "timestamp2", "f": 3, "r": timestamp2},
            {
                "n": "gpuInfo",
                "f": 3,
                "r": "Google Inc. (Intel)/ANGLE (Intel, Intel(R) HD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            },
            {"n": "jsFontsList", "f": 3, "r": "17f"},
            {
                "n": "pluginsList",
                "f": 3,
                "r": "PDF Viewerinternal-pdf-viewerapplication/pdftext/pdf##Chrome PDF Viewerinternal-pdf-viewerapplication/pdftext/pdf##Chromium PDF Viewerinternal-pdf-viewerapplication/pdftext/pdf##Microsoft Edge PDF Viewerinternal-pdf-viewerapplication/pdftext/pdf##WebKit built-in PDFinternal-pdf-viewerapplication/pdftext/pdf",
            },
            {"n": "timestamp3", "f": 3, "r": timestamp3},
            {"n": "userAgent", "f": 0, "r": self.ua},
            {"n": "everCookie", "f": 3, "m": "tt_scid"},
            {
                "n": "syntaxError",
                "f": 3,
                "r": "Failed to construct 'WebSocket': The URL 'Create WebSocket' is invalid.",
            },
            {"n": "nativeLength", "f": 3, "r": 33},
            {"n": "rtcIP", "f": 3, "p": 1, "r": "58.19.72.31"},
            {"n": "location", "f": 1, "r": url},
            {"n": "fpVersion", "f": 4, "r": "2.11.0"},
            # {"n": "clientId", "f": 3, "r": self.ctx.call("random_32")},
            {"n": "clientId", "f": 3, "r": random_32()},
            {"n": "timestamp4", "f": 3, "r": timestamp4},
            {"n": "extendField", "f": 4},
        ]
        plain_arr_2 = ["true_0_Infinity_1", "58.19.72.31"]
        # q = self.ctx.call("douyin_xxbg_q_encrypt", plain_arr_1, plain_arr_2)
        q = douyin_xxbg_q_encrypt(plain_arr_1, plain_arr_2)

        headers = {"user-agent": self.ua}
        params = {"q": q, "callback": f"_7013_{get_time()}"}
        response = requests.get(api, headers=headers, params=params)
        return response.cookies

class Signer:
    shift_array = "Dkdpgh4ZKsQB80/Mfvw36XI1R25-WUAlEi7NLboqYTOPuzmFjJnryx9HVGcaStCe"
    magic = 536919696

    def md5_2x(string):
        return md5(md5(string.encode()).digest()).hexdigest()

    def rc4_encrypt(plaintext: str, key: list[int]) -> str:
        s_box = [_ for _ in range(256)]
        index = 0

        for _ in range(256):
            index = (index + s_box[_] + key[_ % len(key)]) % 256
            s_box[_], s_box[index] = s_box[index], s_box[_]

        _ = 0
        index = 0
        ciphertext = ""

        for char in plaintext:
            _ = (_ + 1) % 256
            index = (index + s_box[_]) % 256

            s_box[_], s_box[index] = s_box[index], s_box[_]
            keystream = s_box[(s_box[_] + s_box[index]) % 256]
            ciphertext += chr(ord(char) ^ keystream)

        return ciphertext

    def b64_encode(
        string,
        key_table="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",
    ):
        last_list = list()
        for i in range(0, len(string), 3):
            try:
                num_1 = ord(string[i])
                num_2 = ord(string[i + 1])
                num_3 = ord(string[i + 2])
                arr_1 = num_1 >> 2
                arr_2 = (3 & num_1) << 4 | (num_2 >> 4)
                arr_3 = ((15 & num_2) << 2) | (num_3 >> 6)
                arr_4 = 63 & num_3

            except IndexError:
                arr_1 = num_1 >> 2
                arr_2 = ((3 & num_1) << 4) | 0
                arr_3 = 64
                arr_4 = 64

            last_list.append(arr_1)
            last_list.append(arr_2)
            last_list.append(arr_3)
            last_list.append(arr_4)

        return "".join([key_table[value] for value in last_list])

    def filter(num_list: list):
        return [
            num_list[x - 1]
            for x in [3,5,7,9,11,13,15,17,19,21,4,6,8,10,12,14,16,18,20,
            ]
        ]

    def scramble(a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s) -> str:
        return "".join(
            [
                chr(_)
                for _ in [a,k,b,l,c,m,d,n,e,o,f,p,g,q,h,r,i,s,j,
                ]
            ]
        )

    def checksum(salt_list: str) -> int:
        checksum = 64
        _ = [checksum := checksum ^ x for x in salt_list[3:]]

        return checksum

    def _x_bogus(params, user_agent, timestamp, data) -> str:

        md5_data = Signer.md5_2x(data)
        md5_params = Signer.md5_2x(params)
        md5_ua = md5(
            Signer.b64_encode(Signer.rc4_encrypt(user_agent, [0, 1, 14])).encode()
        ).hexdigest()

        salt_list = [
            timestamp,
            Signer.magic,
            64,
            0,
            1,
            14,
            bytes.fromhex(md5_params)[-2],
            bytes.fromhex(md5_params)[-1],
            bytes.fromhex(md5_data)[-2],
            bytes.fromhex(md5_data)[-1],
            bytes.fromhex(md5_ua)[-2],
            bytes.fromhex(md5_ua)[-1],
        ]

        salt_list.extend([(timestamp >> i) & 0xFF for i in range(24, -1, -8)])
        salt_list.extend([(salt_list[1] >> i) & 0xFF for i in range(24, -1, -8)])
        salt_list.extend([Signer.checksum(salt_list), 255])

        num_list = Signer.filter(salt_list)
        rc4_num_list = Signer.rc4_encrypt(Signer.scramble(*num_list), [255])

        return Signer.b64_encode(f"\x02ÿ{rc4_num_list}", Signer.shift_array)
    
def tim():
    _rticket = int(time.time() * 1000)
    ts=str(int(time.time() * 1000))[:10]
    ts1=str(int(time.time() * 1000))[:10]
    icket = int(time.time() * 1000)
    return _rticket,ts,ts1,icket

import gzip
import binascii
import random

class AFRITON:
    __content = []
    __content_raw = []
    CF = 0
    begining = [0x74, 0x63, 0x05, 0x10, 0, 0]
    dword_0 = [99, 124, 119, 123, 242, 107, 111, 197, 48, 1, 103, 43, 254, 215, 171, 118, 202, 130, 201, 125, 250, 89, 71, 240, 173, 212, 162, 175, 156, 164, 114, 192, 183, 253, 147, 38, 54, 63, 247, 204, 52, 165, 229, 241, 113, 216, 49, 21, 4, 199, 35, 195, 24, 150, 5, 154, 7, 18, 128, 226, 235, 39, 178, 117, 9, 131, 44, 26, 27, 110, 90, 160, 82, 59, 214, 179, 41, 227, 47, 132, 83, 209, 0, 237, 32, 252, 177, 91, 106, 203, 190, 57, 74, 76, 88, 207, 208, 239, 170, 251, 67, 77, 51, 133, 69, 249, 2, 127, 80, 60, 159, 168, 81, 163, 64, 143, 146, 157, 56, 245, 188, 182, 218, 33, 16, 255, 243, 210, 205, 12, 19, 236, 95, 151, 68, 23, 196, 167, 126, 61, 100, 93, 25, 115, 96, 129, 79, 220, 34, 42, 144, 136, 70, 238, 184, 20, 222, 94, 11, 219, 224, 50, 58, 10, 73, 6, 36, 92, 194, 211, 172, 98, 145, 149, 228, 121, 231, 200, 55, 109, 141, 213, 78, 169, 108, 86, 244, 234, 101, 122, 174, 8, 186, 120, 37, 46, 28, 166, 180, 198, 232, 221, 116, 31, 75, 189, 139, 138, 112, 62, 181, 102, 72, 3, 246, 14, 97, 53, 87, 185, 134, 193, 29, 158, 225, 248, 152, 17, 105, 217, 142, 148, 155, 30, 135, 233, 206, 85, 40, 223, 140, 161, 137, 13, 191, 230, 66, 104, 65, 153, 45, 15, 176, 84, 187, 22]
    dword_1 = [16777216, 33554432, 67108864, 134217728, 268435456, 536870912, 1073741824, 2147483648, 452984832, 905969664]
    dword_2 = [0, 235474187, 470948374, 303765277, 941896748, 908933415, 607530554, 708780849, 1883793496, 2118214995, 1817866830, 1649639237, 1215061108, 1181045119, 1417561698, 1517767529, 3767586992, 4003061179, 4236429990, 4069246893, 3635733660, 3602770327, 3299278474, 3400528769, 2430122216, 2664543715, 2362090238, 2193862645, 2835123396, 2801107407, 3035535058, 3135740889, 3678124923, 3576870512, 3341394285, 3374361702, 3810496343, 3977675356, 4279080257, 4043610186, 2876494627, 2776292904, 3076639029, 3110650942, 2472011535, 2640243204, 2403728665, 2169303058, 1001089995, 899835584, 666464733, 699432150, 59727847, 226906860, 530400753, 294930682, 1273168787, 1172967064, 1475418501, 1509430414, 1942435775, 2110667444, 1876241833, 1641816226, 2910219766, 2743034109, 2976151520, 3211623147, 2505202138, 2606453969, 2302690252, 2269728455, 3711829422, 3543599269, 3240894392, 3475313331, 3843699074, 3943906441, 4178062228, 4144047775, 1306967366, 1139781709, 1374988112, 1610459739, 1975683434, 2076935265, 1775276924, 1742315127, 1034867998, 866637845, 566021896, 800440835, 92987698, 193195065, 429456164, 395441711, 1984812685, 2017778566, 1784663195, 1683407248, 1315562145, 1080094634, 1383856311, 1551037884, 101039829, 135050206, 437757123, 337553864, 1042385657, 807962610, 573804783, 742039012, 2531067453, 2564033334, 2328828971, 2227573024, 2935566865, 2700099354, 3001755655, 3168937228, 3868552805, 3902563182, 4203181171, 4102977912, 3736164937, 3501741890, 3265478751, 3433712980, 1106041591, 1340463100, 1576976609, 1408749034, 2043211483, 2009195472, 1708848333, 1809054150, 832877231, 1068351396, 766945465, 599762354, 159417987, 126454664, 361929877, 463180190, 2709260871, 2943682380, 3178106961, 3009879386, 2572697195, 2538681184, 2236228733, 2336434550, 3509871135, 3745345300, 3441850377, 3274667266, 3910161971, 3877198648, 4110568485, 4211818798, 2597806476, 2497604743, 2261089178, 2295101073, 2733856160, 2902087851, 3202437046, 2968011453, 3936291284, 3835036895, 4136440770, 4169408201, 3535486456, 3702665459, 3467192302, 3231722213, 2051518780, 1951317047, 1716890410, 1750902305, 1113818384, 1282050075, 1584504582, 1350078989, 168810852, 67556463, 371049330, 404016761, 841739592, 1008918595, 775550814, 540080725, 3969562369, 3801332234, 4035489047, 4269907996, 3569255213, 3669462566, 3366754619, 3332740144, 2631065433, 2463879762, 2160117071, 2395588676, 2767645557, 2868897406, 3102011747, 3069049960, 202008497, 33778362, 270040487, 504459436, 875451293, 975658646, 675039627, 641025152, 2084704233, 1917518562, 1615861247, 1851332852, 1147550661, 1248802510, 1484005843, 1451044056, 933301370, 967311729, 733156972, 632953703, 260388950, 25965917, 328671808, 496906059, 1206477858, 1239443753, 1543208500, 1441952575, 2144161806, 1908694277, 1675577880, 1842759443, 3610369226, 3644379585, 3408119516, 3307916247, 4011190502, 3776767469, 4077384432, 4245618683, 2809771154, 2842737049, 3144396420, 3043140495, 2673705150, 2438237621, 2203032232, 2370213795]
    dword_3 = [0, 185469197, 370938394, 487725847, 741876788, 657861945, 975451694, 824852259, 1483753576, 1400783205, 1315723890, 1164071807, 1950903388, 2135319889, 1649704518, 1767536459, 2967507152, 3152976349, 2801566410, 2918353863, 2631447780, 2547432937, 2328143614, 2177544179, 3901806776, 3818836405, 4270639778, 4118987695, 3299409036, 3483825537, 3535072918, 3652904859, 2077965243, 1893020342, 1841768865, 1724457132, 1474502543, 1559041666, 1107234197, 1257309336, 598438867, 681933534, 901210569, 1052338372, 261314535, 77422314, 428819965, 310463728, 3409685355, 3224740454, 3710368113, 3593056380, 3875770207, 3960309330, 4045380933, 4195456072, 2471224067, 2554718734, 2237133081, 2388260884, 3212035895, 3028143674, 2842678573, 2724322336, 4138563181, 4255350624, 3769721975, 3955191162, 3667219033, 3516619604, 3431546947, 3347532110, 2933734917, 2782082824, 3099667487, 3016697106, 2196052529, 2313884476, 2499348523, 2683765030, 1179510461, 1296297904, 1347548327, 1533017514, 1786102409, 1635502980, 2087309459, 2003294622, 507358933, 355706840, 136428751, 53458370, 839224033, 957055980, 605657339, 790073846, 2373340630, 2256028891, 2607439820, 2422494913, 2706270690, 2856345839, 3075636216, 3160175349, 3573941694, 3725069491, 3273267108, 3356761769, 4181598602, 4063242375, 4011996048, 3828103837, 1033297158, 915985419, 730517276, 545572369, 296679730, 446754879, 129166120, 213705253, 1709610350, 1860738147, 1945798516, 2029293177, 1239331162, 1120974935, 1606591296, 1422699085, 4148292826, 4233094615, 3781033664, 3931371469, 3682191598, 3497509347, 3446004468, 3328955385, 2939266226, 2755636671, 3106780840, 2988687269, 2198438022, 2282195339, 2501218972, 2652609425, 1201765386, 1286567175, 1371368976, 1521706781, 1805211710, 1620529459, 2105887268, 1988838185, 533804130, 350174575, 164439672, 46346101, 870912086, 954669403, 636813900, 788204353, 2358957921, 2274680428, 2592523643, 2441661558, 2695033685, 2880240216, 3065962831, 3182487618, 3572145929, 3756299780, 3270937875, 3388507166, 4174560061, 4091327024, 4006521127, 3854606378, 1014646705, 930369212, 711349675, 560487590, 272786309, 457992840, 106852767, 223377554, 1678381017, 1862534868, 1914052035, 2031621326, 1211247597, 1128014560, 1580087799, 1428173050, 32283319, 182621114, 401639597, 486441376, 768917123, 651868046, 1003007129, 818324884, 1503449823, 1385356242, 1333838021, 1150208456, 1973745387, 2125135846, 1673061617, 1756818940, 2970356327, 3120694122, 2802849917, 2887651696, 2637442643, 2520393566, 2334669897, 2149987652, 3917234703, 3799141122, 4284502037, 4100872472, 3309594171, 3460984630, 3545789473, 3629546796, 2050466060, 1899603969, 1814803222, 1730525723, 1443857720, 1560382517, 1075025698, 1260232239, 575138148, 692707433, 878443390, 1062597235, 243256656, 91341917, 409198410, 325965383, 3403100636, 3252238545, 3704300486, 3620022987, 3874428392, 3990953189, 4042459122, 4227665663, 2460449204, 2578018489, 2226875310, 2411029155, 3198115200, 3046200461, 2827177882, 2743944855]
    dword_4 = [0, 218828297, 437656594, 387781147, 875313188, 958871085, 775562294, 590424639, 1750626376, 1699970625, 1917742170, 2135253587, 1551124588, 1367295589, 1180849278, 1265195639, 3501252752, 3720081049, 3399941250, 3350065803, 3835484340, 3919042237, 4270507174, 4085369519, 3102249176, 3051593425, 2734591178, 2952102595, 2361698556, 2177869557, 2530391278, 2614737639, 3145456443, 3060847922, 2708326185, 2892417312, 2404901663, 2187128086, 2504130317, 2555048196, 3542330227, 3727205754, 3375740769, 3292445032, 3876557655, 3926170974, 4246310725, 4027744588, 1808481195, 1723872674, 1910319033, 2094410160, 1608975247, 1391201670, 1173430173, 1224348052, 59984867, 244860394, 428169201, 344873464, 935293895, 984907214, 766078933, 547512796, 1844882806, 1627235199, 2011214180, 2062270317, 1507497298, 1423022939, 1137477952, 1321699145, 95345982, 145085239, 532201772, 313773861, 830661914, 1015671571, 731183368, 648017665, 3175501286, 2957853679, 2807058932, 2858115069, 2305455554, 2220981195, 2474404304, 2658625497, 3575528878, 3625268135, 3473416636, 3254988725, 3778151818, 3963161475, 4213447064, 4130281361, 3599595085, 3683022916, 3432737375, 3247465558, 3802222185, 4020912224, 4172763771, 4122762354, 3201631749, 3017672716, 2764249623, 2848461854, 2331590177, 2280796200, 2431590963, 2648976442, 104699613, 188127444, 472615631, 287343814, 840019705, 1058709744, 671593195, 621591778, 1852171925, 1668212892, 1953757831, 2037970062, 1514790577, 1463996600, 1080017571, 1297403050, 3673637356, 3623636965, 3235995134, 3454686199, 4007360968, 3822090177, 4107101658, 4190530515, 2997825956, 3215212461, 2830708150, 2779915199, 2256734592, 2340947849, 2627016082, 2443058075, 172466556, 122466165, 273792366, 492483431, 1047239000, 861968209, 612205898, 695634755, 1646252340, 1863638845, 2013908262, 1963115311, 1446242576, 1530455833, 1277555970, 1093597963, 1636604631, 1820824798, 2073724613, 1989249228, 1436590835, 1487645946, 1337376481, 1119727848, 164948639, 81781910, 331544205, 516552836, 1039717051, 821288114, 669961897, 719700128, 2973530695, 3157750862, 2871682645, 2787207260, 2232435299, 2283490410, 2667994737, 2450346104, 3647212047, 3564045318, 3279033885, 3464042516, 3980931627, 3762502690, 4150144569, 4199882800, 3070356634, 3121275539, 2904027272, 2686254721, 2200818878, 2384911031, 2570832044, 2486224549, 3747192018, 3528626907, 3310321856, 3359936201, 3950355702, 3867060991, 4049844452, 4234721005, 1739656202, 1790575107, 2108100632, 1890328081, 1402811438, 1586903591, 1233856572, 1149249077, 266959938, 48394827, 369057872, 418672217, 1002783846, 919489135, 567498868, 752375421, 209336225, 24197544, 376187827, 459744698, 945164165, 895287692, 574624663, 793451934, 1679968233, 1764313568, 2117360635, 1933530610, 1343127501, 1560637892, 1243112415, 1192455638, 3704280881, 3519142200, 3336358691, 3419915562, 3907448597, 3857572124, 4075877127, 4294704398, 3029510009, 3113855344, 2927934315, 2744104290, 2159976285, 2377486676, 2594734927, 2544078150]
    dword_5 = [0, 151849742, 303699484, 454499602, 607398968, 758720310, 908999204, 1059270954, 1214797936, 1097159550, 1517440620, 1400849762, 1817998408, 1699839814, 2118541908, 2001430874, 2429595872, 2581445614, 2194319100, 2345119218, 3034881240, 3186202582, 2801699524, 2951971274, 3635996816, 3518358430, 3399679628, 3283088770, 4237083816, 4118925222, 4002861748, 3885750714, 1002142683, 850817237, 698445255, 548169417, 529487843, 377642221, 227885567, 77089521, 1943217067, 2061379749, 1640576439, 1757691577, 1474760595, 1592394909, 1174215055, 1290801793, 2875968315, 2724642869, 3111247143, 2960971305, 2405426947, 2253581325, 2638606623, 2487810577, 3808662347, 3926825029, 4044981591, 4162096729, 3342319475, 3459953789, 3576539503, 3693126241, 1986918061, 2137062819, 1685577905, 1836772287, 1381620373, 1532285339, 1078185097, 1229899655, 1040559837, 923313619, 740276417, 621982671, 439452389, 322734571, 137073913, 19308535, 3871163981, 4021308739, 4104605777, 4255800159, 3263785589, 3414450555, 3499326569, 3651041127, 2933202493, 2815956275, 3167684641, 3049390895, 2330014213, 2213296395, 2566595609, 2448830231, 1305906550, 1155237496, 1607244650, 1455525988, 1776460110, 1626319424, 2079897426, 1928707164, 96392454, 213114376, 396673818, 514443284, 562755902, 679998000, 865136418, 983426092, 3708173718, 3557504664, 3474729866, 3323011204, 4180808110, 4030667424, 3945269170, 3794078908, 2507040230, 2623762152, 2272556026, 2390325492, 2975484382, 3092726480, 2738905026, 2857194700, 3973773121, 3856137295, 4274053469, 4157467219, 3371096953, 3252932727, 3673476453, 3556361835, 2763173681, 2915017791, 3064510765, 3215307299, 2156299017, 2307622919, 2459735317, 2610011675, 2081048481, 1963412655, 1846563261, 1729977011, 1480485785, 1362321559, 1243905413, 1126790795, 878845905, 1030690015, 645401037, 796197571, 274084841, 425408743, 38544885, 188821243, 3613494426, 3731654548, 3313212038, 3430322568, 4082475170, 4200115116, 3780097726, 3896688048, 2668221674, 2516901860, 2366882550, 2216610296, 3141400786, 2989552604, 2837966542, 2687165888, 1202797690, 1320957812, 1437280870, 1554391400, 1669664834, 1787304780, 1906247262, 2022837584, 265905162, 114585348, 499347990, 349075736, 736970802, 585122620, 972512814, 821712160, 2595684844, 2478443234, 2293045232, 2174754046, 3196267988, 3079546586, 2895723464, 2777952454, 3537852828, 3687994002, 3234156416, 3385345166, 4142626212, 4293295786, 3841024952, 3992742070, 174567692, 57326082, 410887952, 292596766, 777231668, 660510266, 1011452712, 893681702, 1108339068, 1258480242, 1343618912, 1494807662, 1715193156, 1865862730, 1948373848, 2100090966, 2701949495, 2818666809, 3004591147, 3122358053, 2235061775, 2352307457, 2535604243, 2653899549, 3915653703, 3764988233, 4219352155, 4067639125, 3444575871, 3294430577, 3746175075, 3594982253, 836553431, 953270745, 600235211, 718002117, 367585007, 484830689, 133361907, 251657213, 2041877159, 1891211689, 1806599355, 1654886325, 1568718495, 1418573201, 1335535747, 1184342925]
    dword_6 = [3328402341, 4168907908, 4000806809, 4135287693, 4294111757, 3597364157, 3731845041, 2445657428, 1613770832, 33620227, 3462883241, 1445669757, 3892248089, 3050821474, 1303096294, 3967186586, 2412431941, 528646813, 2311702848, 4202528135, 4026202645, 2992200171, 2387036105, 4226871307, 1101901292, 3017069671, 1604494077, 1169141738, 597466303, 1403299063, 3832705686, 2613100635, 1974974402, 3791519004, 1033081774, 1277568618, 1815492186, 2118074177, 4126668546, 2211236943, 1748251740, 1369810420, 3521504564, 4193382664, 3799085459, 2883115123, 1647391059, 706024767, 134480908, 2512897874, 1176707941, 2646852446, 806885416, 932615841, 168101135, 798661301, 235341577, 605164086, 461406363, 3756188221, 3454790438, 1311188841, 2142417613, 3933566367, 302582043, 495158174, 1479289972, 874125870, 907746093, 3698224818, 3025820398, 1537253627, 2756858614, 1983593293, 3084310113, 2108928974, 1378429307, 3722699582, 1580150641, 327451799, 2790478837, 3117535592, 0, 3253595436, 1075847264, 3825007647, 2041688520, 3059440621, 3563743934, 2378943302, 1740553945, 1916352843, 2487896798, 2555137236, 2958579944, 2244988746, 3151024235, 3320835882, 1336584933, 3992714006, 2252555205, 2588757463, 1714631509, 293963156, 2319795663, 3925473552, 67240454, 4269768577, 2689618160, 2017213508, 631218106, 1269344483, 2723238387, 1571005438, 2151694528, 93294474, 1066570413, 563977660, 1882732616, 4059428100, 1673313503, 2008463041, 2950355573, 1109467491, 537923632, 3858759450, 4260623118, 3218264685, 2177748300, 403442708, 638784309, 3287084079, 3193921505, 899127202, 2286175436, 773265209, 2479146071, 1437050866, 4236148354, 2050833735, 3362022572, 3126681063, 840505643, 3866325909, 3227541664, 427917720, 2655997905, 2749160575, 1143087718, 1412049534, 999329963, 193497219, 2353415882, 3354324521, 1807268051, 672404540, 2816401017, 3160301282, 369822493, 2916866934, 3688947771, 1681011286, 1949973070, 336202270, 2454276571, 201721354, 1210328172, 3093060836, 2680341085, 3184776046, 1135389935, 3294782118, 965841320, 831886756, 3554993207, 4068047243, 3588745010, 2345191491, 1849112409, 3664604599, 26054028, 2983581028, 2622377682, 1235855840, 3630984372, 2891339514, 4092916743, 3488279077, 3395642799, 4101667470, 1202630377, 268961816, 1874508501, 4034427016, 1243948399, 1546530418, 941366308, 1470539505, 1941222599, 2546386513, 3421038627, 2715671932, 3899946140, 1042226977, 2521517021, 1639824860, 227249030, 260737669, 3765465232, 2084453954, 1907733956, 3429263018, 2420656344, 100860677, 4160157185, 470683154, 3261161891, 1781871967, 2924959737, 1773779408, 394692241, 2579611992, 974986535, 664706745, 3655459128, 3958962195, 731420851, 571543859, 3530123707, 2849626480, 126783113, 865375399, 765172662, 1008606754, 361203602, 3387549984, 2278477385, 2857719295, 1344809080, 2782912378, 59542671, 1503764984, 160008576, 437062935, 1707065306, 3622233649, 2218934982, 3496503480, 2185314755, 697932208, 1512910199, 504303377, 2075177163, 2824099068, 1841019862, 739644986]
    dword_7 = [2781242211, 2230877308, 2582542199, 2381740923, 234877682, 3184946027, 2984144751, 1418839493, 1348481072, 50462977, 2848876391, 2102799147, 434634494, 1656084439, 3863849899, 2599188086, 1167051466, 2636087938, 1082771913, 2281340285, 368048890, 3954334041, 3381544775, 201060592, 3963727277, 1739838676, 4250903202, 3930435503, 3206782108, 4149453988, 2531553906, 1536934080, 3262494647, 484572669, 2923271059, 1783375398, 1517041206, 1098792767, 49674231, 1334037708, 1550332980, 4098991525, 886171109, 150598129, 2481090929, 1940642008, 1398944049, 1059722517, 201851908, 1385547719, 1699095331, 1587397571, 674240536, 2704774806, 252314885, 3039795866, 151914247, 908333586, 2602270848, 1038082786, 651029483, 1766729511, 3447698098, 2682942837, 454166793, 2652734339, 1951935532, 775166490, 758520603, 3000790638, 4004797018, 4217086112, 4137964114, 1299594043, 1639438038, 3464344499, 2068982057, 1054729187, 1901997871, 2534638724, 4121318227, 1757008337, 0, 750906861, 1614815264, 535035132, 3363418545, 3988151131, 3201591914, 1183697867, 3647454910, 1265776953, 3734260298, 3566750796, 3903871064, 1250283471, 1807470800, 717615087, 3847203498, 384695291, 3313910595, 3617213773, 1432761139, 2484176261, 3481945413, 283769337, 100925954, 2180939647, 4037038160, 1148730428, 3123027871, 3813386408, 4087501137, 4267549603, 3229630528, 2315620239, 2906624658, 3156319645, 1215313976, 82966005, 3747855548, 3245848246, 1974459098, 1665278241, 807407632, 451280895, 251524083, 1841287890, 1283575245, 337120268, 891687699, 801369324, 3787349855, 2721421207, 3431482436, 959321879, 1469301956, 4065699751, 2197585534, 1199193405, 2898814052, 3887750493, 724703513, 2514908019, 2696962144, 2551808385, 3516813135, 2141445340, 1715741218, 2119445034, 2872807568, 2198571144, 3398190662, 700968686, 3547052216, 1009259540, 2041044702, 3803995742, 487983883, 1991105499, 1004265696, 1449407026, 1316239930, 504629770, 3683797321, 168560134, 1816667172, 3837287516, 1570751170, 1857934291, 4014189740, 2797888098, 2822345105, 2754712981, 936633572, 2347923833, 852879335, 1133234376, 1500395319, 3084545389, 2348912013, 1689376213, 3533459022, 3762923945, 3034082412, 4205598294, 133428468, 634383082, 2949277029, 2398386810, 3913789102, 403703816, 3580869306, 2297460856, 1867130149, 1918643758, 607656988, 4049053350, 3346248884, 1368901318, 600565992, 2090982877, 2632479860, 557719327, 3717614411, 3697393085, 2249034635, 2232388234, 2430627952, 1115438654, 3295786421, 2865522278, 3633334344, 84280067, 33027830, 303828494, 2747425121, 1600795957, 4188952407, 3496589753, 2434238086, 1486471617, 658119965, 3106381470, 953803233, 334231800, 3005978776, 857870609, 3151128937, 1890179545, 2298973838, 2805175444, 3056442267, 574365214, 2450884487, 550103529, 1233637070, 4289353045, 2018519080, 2057691103, 2399374476, 4166623649, 2148108681, 387583245, 3664101311, 836232934, 3330556482, 3100665960, 3280093505, 2955516313, 2002398509, 287182607, 3413881008, 4238890068, 3597515707, 975967766]
    dword_8 = [1671808611, 2089089148, 2006576759, 2072901243, 4061003762, 1807603307, 1873927791, 3310653893, 810573872, 16974337, 1739181671, 729634347, 4263110654, 3613570519, 2883997099, 1989864566, 3393556426, 2191335298, 3376449993, 2106063485, 4195741690, 1508618841, 1204391495, 4027317232, 2917941677, 3563566036, 2734514082, 2951366063, 2629772188, 2767672228, 1922491506, 3227229120, 3082974647, 4246528509, 2477669779, 644500518, 911895606, 1061256767, 4144166391, 3427763148, 878471220, 2784252325, 3845444069, 4043897329, 1905517169, 3631459288, 827548209, 356461077, 67897348, 3344078279, 593839651, 3277757891, 405286936, 2527147926, 84871685, 2595565466, 118033927, 305538066, 2157648768, 3795705826, 3945188843, 661212711, 2999812018, 1973414517, 152769033, 2208177539, 745822252, 439235610, 455947803, 1857215598, 1525593178, 2700827552, 1391895634, 994932283, 3596728278, 3016654259, 695947817, 3812548067, 795958831, 2224493444, 1408607827, 3513301457, 0, 3979133421, 543178784, 4229948412, 2982705585, 1542305371, 1790891114, 3410398667, 3201918910, 961245753, 1256100938, 1289001036, 1491644504, 3477767631, 3496721360, 4012557807, 2867154858, 4212583931, 1137018435, 1305975373, 861234739, 2241073541, 1171229253, 4178635257, 33948674, 2139225727, 1357946960, 1011120188, 2679776671, 2833468328, 1374921297, 2751356323, 1086357568, 2408187279, 2460827538, 2646352285, 944271416, 4110742005, 3168756668, 3066132406, 3665145818, 560153121, 271589392, 4279952895, 4077846003, 3530407890, 3444343245, 202643468, 322250259, 3962553324, 1608629855, 2543990167, 1154254916, 389623319, 3294073796, 2817676711, 2122513534, 1028094525, 1689045092, 1575467613, 422261273, 1939203699, 1621147744, 2174228865, 1339137615, 3699352540, 577127458, 712922154, 2427141008, 2290289544, 1187679302, 3995715566, 3100863416, 339486740, 3732514782, 1591917662, 186455563, 3681988059, 3762019296, 844522546, 978220090, 169743370, 1239126601, 101321734, 611076132, 1558493276, 3260915650, 3547250131, 2901361580, 1655096418, 2443721105, 2510565781, 3828863972, 2039214713, 3878868455, 3359869896, 928607799, 1840765549, 2374762893, 3580146133, 1322425422, 2850048425, 1823791212, 1459268694, 4094161908, 3928346602, 1706019429, 2056189050, 2934523822, 135794696, 3134549946, 2022240376, 628050469, 779246638, 472135708, 2800834470, 3032970164, 3327236038, 3894660072, 3715932637, 1956440180, 522272287, 1272813131, 3185336765, 2340818315, 2323976074, 1888542832, 1044544574, 3049550261, 1722469478, 1222152264, 50660867, 4127324150, 236067854, 1638122081, 895445557, 1475980887, 3117443513, 2257655686, 3243809217, 489110045, 2662934430, 3778599393, 4162055160, 2561878936, 288563729, 1773916777, 3648039385, 2391345038, 2493985684, 2612407707, 505560094, 2274497927, 3911240169, 3460925390, 1442818645, 678973480, 3749357023, 2358182796, 2717407649, 2306869641, 219617805, 3218761151, 3862026214, 1120306242, 1756942440, 1103331905, 2578459033, 762796589, 252780047, 2966125488, 1425844308, 3151392187, 372911126]
    dword_9 = [1667474886, 2088535288, 2004326894, 2071694838, 4075949567, 1802223062, 1869591006, 3318043793, 808472672, 16843522, 1734846926, 724270422, 4278065639, 3621216949, 2880169549, 1987484396, 3402253711, 2189597983, 3385409673, 2105378810, 4210693615, 1499065266, 1195886990, 4042263547, 2913856577, 3570689971, 2728590687, 2947541573, 2627518243, 2762274643, 1920112356, 3233831835, 3082273397, 4261223649, 2475929149, 640051788, 909531756, 1061110142, 4160160501, 3435941763, 875846760, 2779116625, 3857003729, 4059105529, 1903268834, 3638064043, 825316194, 353713962, 67374088, 3351728789, 589522246, 3284360861, 404236336, 2526454071, 84217610, 2593830191, 117901582, 303183396, 2155911963, 3806477791, 3958056653, 656894286, 2998062463, 1970642922, 151591698, 2206440989, 741110872, 437923380, 454765878, 1852748508, 1515908788, 2694904667, 1381168804, 993742198, 3604373943, 3014905469, 690584402, 3823320797, 791638366, 2223281939, 1398011302, 3520161977, 0, 3991743681, 538992704, 4244381667, 2981218425, 1532751286, 1785380564, 3419096717, 3200178535, 960056178, 1246420628, 1280103576, 1482221744, 3486468741, 3503319995, 4025428677, 2863326543, 4227536621, 1128514950, 1296947098, 859002214, 2240123921, 1162203018, 4193849577, 33687044, 2139062782, 1347481760, 1010582648, 2678045221, 2829640523, 1364325282, 2745433693, 1077985408, 2408548869, 2459086143, 2644360225, 943212656, 4126475505, 3166494563, 3065430391, 3671750063, 555836226, 269496352, 4294908645, 4092792573, 3537006015, 3452783745, 202118168, 320025894, 3974901699, 1600119230, 2543297077, 1145359496, 387397934, 3301201811, 2812801621, 2122220284, 1027426170, 1684319432, 1566435258, 421079858, 1936954854, 1616945344, 2172753945, 1330631070, 3705438115, 572679748, 707427924, 2425400123, 2290647819, 1179044492, 4008585671, 3099120491, 336870440, 3739122087, 1583276732, 185277718, 3688593069, 3772791771, 842159716, 976899700, 168435220, 1229577106, 101059084, 606366792, 1549591736, 3267517855, 3553849021, 2897014595, 1650632388, 2442242105, 2509612081, 3840161747, 2038008818, 3890688725, 3368567691, 926374254, 1835907034, 2374863873, 3587531953, 1313788572, 2846482505, 1819063512, 1448540844, 4109633523, 3941213647, 1701162954, 2054852340, 2930698567, 134748176, 3132806511, 2021165296, 623210314, 774795868, 471606328, 2795958615, 3031746419, 3334885783, 3907527627, 3722280097, 1953799400, 522133822, 1263263126, 3183336545, 2341176845, 2324333839, 1886425312, 1044267644, 3048588401, 1718004428, 1212733584, 50529542, 4143317495, 235803164, 1633788866, 892690282, 1465383342, 3115962473, 2256965911, 3250673817, 488449850, 2661202215, 3789633753, 4177007595, 2560144171, 286339874, 1768537042, 3654906025, 2391705863, 2492770099, 2610673197, 505291324, 2273808917, 3924369609, 3469625735, 1431699370, 673740880, 3755965093, 2358021891, 2711746649, 2307489801, 218961690, 3217021541, 3873845719, 1111672452, 1751693520, 1094828930, 2576986153, 757954394, 252645662, 2964376443, 1414855848, 3149649517, 370555436]
    LIST_6B0 = [4089235720, 1779033703, 2227873595, 3144134277, 4271175723, 1013904242, 1595750129, 2773480762, 2917565137, 1359893119, 725511199, 2600822924, 4215389547, 528734635, 327033209, 1541459225]
    ord_list = [77, 212, 194, 230, 184, 49, 98, 9, 14, 82, 179, 199, 166, 115, 59, 164, 28, 178, 70, 43, 130, 154, 181, 138, 25, 107, 57, 219, 87, 23, 117, 36, 244, 155, 175, 127, 8, 232, 214, 141, 38, 167, 46, 55, 193, 169, 90, 47, 31, 5, 165, 24, 146, 174, 242, 148, 151, 50, 182, 42, 56, 170, 221, 88]
    rodata = [3609767458, 1116352408, 602891725, 1899447441, 3964484399, 3049323471, 2173295548, 3921009573, 4081628472, 961987163, 3053834265, 1508970993, 2937671579, 2453635748, 3664609560, 2870763221, 2734883394, 3624381080, 1164996542, 310598401, 1323610764, 607225278, 3590304994, 1426881987, 4068182383, 1925078388, 991336113, 2162078206, 633803317, 2614888103, 3479774868, 3248222580, 2666613458, 3835390401, 944711139, 4022224774, 2341262773, 264347078, 2007800933, 604807628, 1495990901, 770255983, 1856431235, 1249150122, 3175218132, 1555081692, 2198950837, 1996064986, 3999719339, 2554220882, 766784016, 2821834349, 2566594879, 2952996808, 3203337956, 3210313671, 1034457026, 3336571891, 2466948901, 3584528711, 3758326383, 113926993, 168717936, 338241895, 1188179964, 666307205, 1546045734, 773529912, 1522805485, 1294757372, 2643833823, 1396182291, 2343527390, 1695183700, 1014477480, 1986661051, 1206759142, 2177026350, 344077627, 2456956037, 1290863460, 2730485921, 3158454273, 2820302411, 3505952657, 3259730800, 106217008, 3345764771, 3606008344, 3516065817, 1432725776, 3600352804, 1467031594, 4094571909, 851169720, 275423344, 3100823752, 430227734, 1363258195, 506948616, 3750685593, 659060556, 3785050280, 883997877, 3318307427, 958139571, 3812723403, 1322822218, 2003034995, 1537002063, 3602036899, 1747873779, 1575990012, 1955562222, 1125592928, 2024104815, 2716904306, 2227730452, 442776044, 2361852424, 593698344, 2428436474, 3733110249, 2756734187, 2999351573, 3204031479, 3815920427, 3329325298, 3928383900, 3391569614, 566280711, 3515267271, 3454069534, 3940187606, 4000239992, 4118630271, 1914138554, 116418474, 2731055270, 174292421, 3203993006, 289380356, 320620315, 460393269, 587496836, 685471733, 1086792851, 852142971, 365543100, 1017036298, 2618297676, 1126000580, 3409855158, 1288033470, 4234509866, 1501505948, 987167468, 1607167915, 1246189591, 1816402316]
    list_9C8 = []

    def encrypt(self, data):
        headers = [31, 139, 8, 0, 0, 0, 0, 0, 0, 0]
        data = gzip.compress(bytes(data.encode("latin-1")), compresslevel=9, mtime=0)
        data = list(data)
        self.setData(data)
        for i in range(len(headers)):
            self.__content[i] = headers[i]
        list_0B0 = self.calculate(self.list_9C8) + self.ord_list
        list_5D8 = self.calculate(list_0B0)
        list_378 = []
        list_740 = []
        for i in range(0x10):
            list_378.append(list_5D8[i])
        list_378Array = self.dump_list(list_378)
        for i in range(0x10, 0x20):
            list_740.append(list_5D8[i])
        list_8D8 = self.calculate(self.__content)
        list_AB0 = list_8D8 + self.__content
        list_AB0List = self.convertLongList(list_AB0)
        differ = 0x10 - len(list_AB0) % 0x10
        for i in range(differ):
            list_AB0List.append(differ)
        list_AB0 = list_AB0List
        list_55C = self.hex_CF8(list_378Array)
        final_list = self.hex_0A2(list_AB0, list_740, list_55C)
        final_list = (self.begining + self.list_9C8) + final_list
        final_list = self.changeLongArrayTobytes(final_list)
        return bytes(i % 256 for i in final_list).hex()

    def decrypt(self, data):
        data = bytearray.fromhex(data)
        data = list(data)
        self.setData(data)
        self.__content = self.__content_raw[38:]
        self.list_9C8 = self.__content_raw[6:38]
        self.__content = self.changeByteArrayToLong(self.__content)
        list_0B0 = self.calculate(self.list_9C8) + self.ord_list
        list_5D8 = self.calculate(list_0B0)
        list_378 = []
        list_740 = []
        for i in range(0x10):
            list_378.append(list_5D8[i])
        list_378Array = self.dump_list(list_378)
        for i in range(0x10, 0x20):
            list_740.append(list_5D8[i])
        key_longs = self.hex_list(list_378Array)
        decrypted = self.aes_decrypt(bytes(key_longs), bytes(self.__content))
        decryptedByteArray = ([0] * 16) + list(decrypted)
        toDecompress = decryptedByteArray[64:]
        result = gzip.decompress(bytes(toDecompress))
        return result.decode()

   

    def bytearray_decode(self, arrays):
        out = []
        for d in arrays:
            out.append(chr(d))
        return "".join(out)

    def changeLongArrayTobytes(self, array):
        result = []
        for i in range(len(array)):
            if array[i] > 127:
                result.append(array[i] - 256)
            else:
                result.append(array[i])
        return result

    def hex_0A2(self, content, list_740, list_55C):
        result = []
        l55cl = len(list_55C)
        lens = len(content)
        end = lens // 16
        for i in range(end):
            for j in range(16):
                list_740[j] = list_740[j] ^ content[16 * i + j]
            tmp_list = self.dump_list(list_740)
            R6 = tmp_list[3]
            LR = tmp_list[0]
            R8 = tmp_list[1]
            R12 = tmp_list[2]
            R5 = list_55C[0]
            R4 = list_55C[1]
            R1 = list_55C[2]
            R2 = list_55C[3]
            R11 = 0
            v_334 = 0
            R2 = R2 ^ R6
            v_33C = R2
            R1 = R1 ^ R12
            v_338 = R1
            R4 = R4 ^ R8
            R12 = R5 ^ LR
            for j in range(5):
                R3 = v_33C
                R9 = R4
                R0 = int(self.UBFX(R12, 0x10, 8))
                R1 = R3 >> 0x18
                R1 = self.dword_6[R1]
                R0 = self.dword_7[R0]
                R0 = R0 ^ R1
                R1 = int(self.UBFX(R4, 8, 8))
                R8 = v_338
                R1 = self.dword_8[R1]
                LR = list_55C[8 * j + 6]
                R0 = R0 ^ R1
                R1 = int(self.UTFX(R8))
                R1 = self.dword_9[R1]
                R0 = R0 ^ R1
                R1 = list_55C[8 * j + 4]
                v_334 = R1
                R1 = list_55C[8 * j + 5]
                v_330 = R1
                R1 = list_55C[8 * j + 7]
                R11 = R0 ^ R1
                R1 = int(self.UBFX(R3, 0x10, 8))
                R0 = R8 >> 24
                R0 = self.dword_6[R0]
                R1 = self.dword_7[R1]
                R0 = R0 ^ R1
                R1 = int(self.UBFX(R12, 8, 8))
                R1 = self.dword_8[R1]
                R0 = R0 ^ R1
                R1 = int(self.UTFX(R9))
                R1 = self.dword_9[R1]
                R0 = R0 ^ R1
                R1 = int(self.UBFX(R8, 0x10, 8))
                R6 = R0 ^ LR
                R0 = R9 >> 24
                R0 = self.dword_6[R0]
                R1 = self.dword_7[R1]
                R0 = R0 ^ R1
                R1 = int(self.UBFX(R3, 8, 8))
                R1 = self.dword_8[R1]
                R0 = R0 ^ R1
                R1 = int(self.UTFX(R12))
                R1 = self.dword_9[R1]
                R0 = R0 ^ R1
                R1 = v_330
                LR = R0 ^ R1
                R0 = int(self.UTFX(R3))
                R0 = self.dword_9[R0]
                R4 = R12 >> 24
                R1 = int(self.UBFX(R8, 8, 8))
                R4 = self.dword_6[R4]
                R5 = int(self.UBFX(R9, 16, 8))
                R1 = self.dword_8[R1]
                R5 = self.dword_7[R5]
                R5 = R5 ^ R4
                R1 = R1 ^ R5
                R0 = R0 ^ R1
                R1 = v_334
                R1 = R1 ^ R0
                R0 = R1 >> 0x18
                v_334 = R0
                if j == 4:
                    break
                else:
                    R4 = int(self.UBFX(R1, 16, 8))
                    R5 = R11 >> 24
                    R10 = R6
                    R5 = self.dword_6[R5]
                    R4 = self.dword_7[R4]
                    R5 = R5 ^ R4
                    R4 = int(self.UBFX(LR, 8, 8))
                    R4 = self.dword_8[R4]
                    R5 = R5 ^ R4
                    R4 = int(self.UTFX(R10))
                    R4 = self.dword_9[R4]
                    R5 = R5 ^ R4
                    R4 = list_55C[8 * j + 11]
                    R0 = R5 ^ R4
                    v_33C = R0
                    R4 = int(self.UBFX(R11, 16, 8))
                    R5 = R10 >> 24
                    R5 = self.dword_6[R5]
                    R4 = self.dword_7[R4]
                    R5 = R5 ^ R4
                    R4 = int(self.UBFX(R1, 8, 8))
                    R0 = list_55C[8 * j + 9]
                    R9 = list_55C[8 * j + 8]
                    R1 = int(self.UTFX(R1))
                    R4 = self.dword_8[R4]
                    R1 = self.dword_9[R1]
                    R5 = R5 ^ R4
                    R4 = int(self.UTFX(LR))
                    R4 = self.dword_9[R4]
                    R5 = R5 ^ R4
                    R4 = list_55C[8 * j + 10]
                    R4 = R4 ^ R5
                    v_338 = R4
                    R5 = int(self.UBFX(R10, 16, 8))
                    R4 = LR >> 24
                    R4 = self.dword_6[R4]
                    R5 = self.dword_7[R5]
                    R4 = R4 ^ R5
                    R5 = int(self.UBFX(R11, 8, 8))
                    R5 = self.dword_8[R5]
                    R4 = R4 ^ R5
                    R1 = R1 ^ R4
                    R4 = R1 ^ R0
                    R0 = v_334
                    R1 = int(self.UBFX(LR, 16, 8))
                    R5 = int(self.UBFX(R10, 8, 8))
                    R0 = self.dword_6[R0]
                    R1 = self.dword_7[R1]
                    R5 = self.dword_8[R5]
                    R0 = R0 ^ R1
                    R1 = int(self.UTFX(R11))
                    R1 = self.dword_9[R1]
                    R0 = R0 ^ R5
                    R0 = R0 ^ R1
                    R12 = R0 ^ R9
            R2 = R11 >> 24
            R3 = int(self.UBFX(R1, 16, 8))
            R10 = R6
            R0 = R10 >> 24
            R2 = self.dword_0[R2]
            R2 = int(self.parseLong(self.toHex(R2) + "000000", 10, 16))
            R9 = R10
            R3 = self.dword_0[R3]
            R3 = int(self.parseLong(self.toHex(R3) + "0000", 10, 16))
            R0 = self.dword_0[R0]
            R0 = int(self.parseLong(self.toHex(R0) + "000000", 10, 16))
            R2 = R2 ^ R3
            v_350 = R2
            R2 = int(self.UBFX(R11, 0x10, 8))
            R2 = self.dword_0[R2]
            R2 = int(self.parseLong(self.toHex(R2) + "0000", 10, 16))
            R0 = R0 ^ R2
            R2 = int(self.UBFX(R1, 8, 8))
            R1 = int(self.UTFX(R1))
            R2 = self.dword_0[R2]
            R2 = int(self.parseLong(self.toHex(R2) + "00", 10, 16))
            R1 = self.dword_0[R1]
            R0 = R0 ^ R2
            R2 = int(self.UTFX(LR))
            R2 = self.dword_0[R2]
            R12 = R0 ^ R2
            R0 = list_55C[l55cl - 2]
            R10 = list_55C[l55cl - 3]
            R12 = R12 ^ R0
            R2 = list_55C[l55cl - 1]
            R0 = LR >> 24
            v_34C = R2
            R2 = int(self.UBFX(R9, 0x10, 8))
            R0 = self.dword_0[R0]
            R0 = int(self.parseLong(self.toHex(R0) + "000000", 10, 16))
            R2 = self.dword_0[R2]
            R2 = int(self.parseLong(self.toHex(R2) + "0000", 10, 16))
            R0 = R0 ^ R2
            R2 = int(self.UBFX(R11, 8, 8))
            R2 = self.dword_0[R2]
            R2 = int(self.parseLong(self.toHex(R2) + "00", 10, 16))
            R0 = R0 ^ R2
            R0 = R0 ^ R1
            R1 = R0 ^ R10
            R0 = v_334
            R2 = int(self.UBFX(LR, 0x10, 8))
            R0 = self.dword_0[R0]
            R0 = int(self.parseLong(self.toHex(R0) + "000000", 10, 16))
            R2 = self.dword_0[R2]
            R2 = int(self.parseLong(self.toHex(R2) + "0000", 10, 16))
            R0 = R0 ^ R2
            R2 = int(self.UBFX(R9, 8, 8))
            R2 = self.dword_0[R2]
            R2 = int(self.parseLong(self.toHex(R2) + "00", 10, 16))
            R0 = R0 ^ R2
            R2 = int(self.UTFX(R11))
            R2 = self.dword_0[R2]
            R0 = R0 ^ R2
            R2 = int(self.UTFX(R9))
            R2 = self.dword_0[R2]
            R3 = int(self.UBFX(LR, 8, 8))
            R3 = self.dword_0[R3]
            R3 = int(self.parseLong(self.toHex(R3) + "00", 10, 16))
            R5 = v_350
            R6 = list_55C[l55cl - 4]
            R3 = R3 ^ R5
            R2 = R2 ^ R3
            R3 = v_34C
            R0 = R0 ^ R6
            R2 = R2 ^ R3
            list_740 = self.hex_list([R0, R1, R12, R2])
            result = result + list_740
        return result

    def calculate(self, content):
        hex_6A8 = 0
        tmp_list = []
        length = len(content)
        list_6B0 = self.LIST_6B0.copy()
        for item in content:
            tmp_list.append(item)

        divisible = length % 0x80
        tmp = 0x80 - divisible
        if tmp > 0x11:
            tmp_list.append(0x80)
            for i in range(tmp - 0x11):
                tmp_list.append(0)
            for j in range(16):
                tmp_list.append(0)
        else:
            tmp_list.append(128)
            for i in range(128 - 16 + tmp + 1):
                tmp_list.append(0)
            for j in range(16):
                tmp_list.append(0)
        tmp_list_size = len(tmp_list)
        d = tmp_list_size // 0x80
        for i in range(tmp_list_size // 0x80):
            if (tmp_list_size // 128 - 1) == i:
                ending = self.handle_ending(hex_6A8, divisible)
                for j in range(8):
                    index = tmp_list_size - j - 1
                    tmp_list[index] = ending[7 - j]
            param_list = []
            for j in range(32):
                tmpss = ""
                for k in range(4):
                    tmp_string = self.toHex(tmp_list[0x80 * i + 4 * j + k])
                    if len(tmp_string) < 2:
                        tmp_string = "0" + tmp_string
                    tmpss = tmpss + tmp_string
                param_list.append(int(self.parseLong(tmpss, 10, 16)))
            list_3B8 = self.hex_27E(param_list)
            list_6B0 = self.hex_30A(list_6B0, list_3B8)
            hex_6A8 += 0x400
        list_8D8 = self.hex_C52(list_6B0)
        return list_8D8

    def convertLongList(self, content):
        if len(content) == 0:
            return []
        result = []
        for i in content:
            result.append(i)
        return result

    def dump_list(self, content):
        size = len(content)
        ssize = size // 4
        result = []
        for index in range(ssize):
            tmp_string = ""
            for j in range(4):
                tmp = self.toHex(content[4 * index + j])
                if len(tmp) < 2:
                    tmp = "0" + tmp

                tmp_string = tmp_string + tmp
            i = int(self.parseLong(tmp_string, 10, 16))
            result.append(int(i))
        return result

    def hex_CF8(self, param_list):
        list_388 = []
        list_378 = param_list
        for i in range(0xA):
            R3 = list_378[0]
            R8 = list_378[1]
            R9 = list_378[2]
            R5 = list_378[3]
            R6 = int(self.UBFX(R5, 8, 8))
            R6 = self.dword_0[R6]
            R6 = int(self.parseLong(self.toHex(R6) + "0000", 10, 16))
            R4 = int(self.UBFX(R5, 0x10, 8))
            R11 = self.dword_1[i]
            R4 = self.dword_0[R4]
            R4 = int(self.parseLong(self.toHex(R4) + "000000", 10, 16))
            R3 = R3 ^ R4
            R4 = int(self.UTFX(R5))
            R3 = R3 ^ R6
            R4 = self.dword_0[R4]
            R4 = int(self.parseLong(self.toHex(R4) + "00", 10, 16))
            R3 = R3 ^ R4
            R4 = R5 >> 24
            R4 = self.dword_0[R4]
            R3 = R3 ^ R4
            R3 = R3 ^ R11
            R2 = R8 ^ R3
            R4 = R9 ^ R2
            R5 = R5 ^ R4
            list_378 = [R3, R2, R4, R5]
            list_388 = list_388 + list_378
        l388l = len(list_388)
        list_478 = []
        for i in range(0x9):
            R5 = list_388[l388l - 8 - 4 * i]
            R4 = int(self.UBFX(R5, 0x10, 8))
            R6 = R5 >> 0x18
            R6 = self.dword_2[R6]
            R4 = self.dword_3[R4]
            R6 = R6 ^ R4
            R4 = int(self.UBFX(R5, 8, 8))
            R5 = int(self.UTFX(R5))
            R4 = self.dword_4[R4]
            R5 = self.dword_5[R5]
            R6 = R6 ^ R4
            R6 = R6 ^ R5
            list_478.append(R6)
            R6 = list_388[l388l - 7 - 4 * i]
            R1 = int(self.UBFX(R6, 0x10, 8))
            R4 = R6 >> 0x18
            R4 = self.dword_2[R4]
            R1 = self.dword_3[R1]
            R1 = R1 ^ R4
            R4 = int(self.UBFX(R6, 8, 8))
            R4 = self.dword_4[R4]
            R1 = R1 ^ R4
            R4 = int(self.UTFX(R6))
            R4 = self.dword_5[R4]
            R1 = R1 ^ R4
            list_478.append(R1)
            R1 = list_388[l388l - 6 - 4 * i]
            R6 = int(self.UBFX(R1, 0x10, 8))
            R4 = R1 >> 0x18
            R4 = self.dword_2[R4]
            R6 = self.dword_3[R6]
            R4 = R4 ^ R6
            R6 = int(self.UBFX(R1, 8, 8))
            R1 = int(self.UTFX(R1))
            R6 = self.dword_4[R6]
            R1 = self.dword_5[R1]
            R4 = R4 ^ R6
            R1 = R1 ^ R4
            list_478.append(R1)
            R0 = list_388[l388l - 5 - 4 * i]
            R1 = int(self.UTFX(R0))
            R4 = int(self.UBFX(R0, 8, 8))
            R6 = R0 >> 0x18
            R0 = int(self.UBFX(R0, 0x10, 8))
            R6 = self.dword_2[R6]
            R0 = self.dword_3[R0]
            R4 = self.dword_4[R4]
            R1 = self.dword_5[R1]
            R0 = R0 ^ R6
            R0 = R0 ^ R4
            R0 = R0 ^ R1
            list_478.append(R0)
        list_468 = param_list + list_388
        return list_468

    def handle_ending(self, num, r0):
        s = self.toHex(num)
        r1 = None
        r2 = None
        if len(s) <= 8:
            r1 = num
            r2 = 0
        else:
            num_str = self.toHex(num)
            length = len(num)
            r1 = self.parseLong(num_str[: length - 8], 10, 16)
            r2 = self.parseLong(num_str[2 : length - 8], 10, 16)
        r1 = self.ADDS(r1, r0 << 3)
        r2 = self.ADC(r2, r0 >> 29)
        a = self.hex_list([r2, r1])
        return self.hex_list([r2, r1])

    def UTFX(self, num):
        tmp_string = self.toBinaryString(num)
        start = len(tmp_string) - 8
        return self.parseLong(tmp_string[start:], 10, 2)

    def hex_27E(self, param_list):
        r6 = param_list[0]
        r8 = param_list[1]
        for i in range(0x40):
            r0 = param_list[2 * i + 0x1C]
            r5 = param_list[2 * i + 0x1D]
            r4 = self.LSRS(r0, 0x13)
            r3 = self.LSRS(r0, 0x1D)
            lr = r4 | self.check(r5) << 13
            r4 = self.LSLS(r0, 3)
            r4 = r4 | self.check(r5) >> 29
            r3 = r3 | self.check(r5) << 3
            r4 = r4 ^ self.check(r0) >> 6
            lr = lr ^ r4
            r4 = self.LSRS(r5, 6)
            r4 = r4 | self.check(r0) << 26
            r9 = r3 ^ r4
            r4 = self.LSRS(r5, 0x13)
            r0 = r4 | self.check(r0) << 13
            r10 = param_list[2 * i + 0x12]
            r3 = param_list[2 * i + 0x13]
            r5 = param_list[2 * i + 0x2]
            r4 = param_list[2 * i + 0x3]
            r0 = r0 ^ r9
            r3 = self.ADDS(r3, r8)
            r6 = self.ADC(r6, r10)
            r8 = self.ADDS(r3, r0)
            lr = self.ADC(lr, r6)
            r6 = self.LSRS(r4, 7)
            r3 = self.LSRS(r4, 8)
            r6 = r6 | self.check(r5) << 25
            r3 = r3 | self.check(r5) << 24
            r3 = int(self.EORS(r3, r6))
            r6 = self.LSRS(r5, 1)
            r0 = int(self.RRX(r4))
            r0 = int(self.EORS(r0, r3))
            r3 = r6 | self.check(r4) << 31
            r6 = self.LSRS(r5, 8)
            r0 = int(self.ADDS(r0, r8))
            r6 = r6 | self.check(r4) << 24
            r8 = r4
            r6 = r6 ^ self.check(r5) >> 7
            r3 = r3 ^ r6
            r6 = r5
            r3 = self.ADC(r3, lr)
            param_list = param_list + [r3, r0]
        return param_list

    def hex_30A(self, param_list, list_3B8):
        v_3A0 = param_list[7]
        v_3A4 = param_list[6]
        v_374 = param_list[5]
        v_378 = param_list[4]
        LR = param_list[0]
        R12 = param_list[1]
        v_39C = param_list[2]
        v_398 = param_list[3]
        v_3AC = param_list[11]
        v_3A8 = param_list[10]
        R9 = param_list[12]
        R10 = param_list[13]
        R5 = param_list[9]
        R8 = param_list[8]
        R4 = param_list[15]
        R6 = param_list[14]
        for index in range(10):
            v_384 = R5
            R3 = self.rodata[0x10 * index]
            R1 = self.rodata[0x10 * index + 2]
            R2 = self.rodata[0x10 * index + 1]
            R3 = self.ADDS(R3, R6)
            R6 = self.check(R8) >> 14
            v_390 = R1
            R6 = R6 | self.check(R5) << 18
            R1 = self.rodata[0x10 * index + 3]
            R0 = self.rodata[0x10 * index + 4]
            v_36C = R0
            R0 = self.ADC(R2, R4)
            R2 = self.LSRS(R5, 0x12)
            R4 = self.LSRS(R5, 0xE)
            R2 = R2 | self.check(R8) << 14
            R4 = R4 | self.check(R8) << 18
            R2 = self.EORS(R2, R4)
            R4 = self.LSLS(R5, 0x17)
            R4 = R4 | self.check(R8) >> 9
            v_38C = R1
            R2 = self.EORS(R2, R4)
            R4 = self.check(R8) >> 18
            R4 = R4 | self.check(R5) << 14
            R6 = self.EORS(R6, R4)
            R4 = self.LSRS(R5, 9)
            R4 = R4 | self.check(R8) << 23
            v_354 = R8
            R6 = self.EORS(R6, R4)
            R3 = self.ADDS(R3, R6)
            R0 = self.ADCS(R0, R2)
            R2 = list_3B8[0x10 * index + 1]
            R2 = self.ADDS(R2, R3)
            R3 = list_3B8[0x10 * index + 3]
            R6 = list_3B8[0x10 * index]
            v_358 = R10
            R6 = self.ADCS(R6, R0)
            R0 = v_3AC
            v_360 = R3
            R0 = R0 ^ R10
            R3 = list_3B8[0x10 * index + 2]
            R0 = self.ANDS(R0, R5)
            R1 = list_3B8[0x10 * index + 5]
            R4 = R0 ^ R10
            R0 = v_3A8
            v_364 = R1
            R0 = R0 ^ R9
            R1 = v_374
            R0 = R0 & R8
            R8 = v_39C
            R0 = R0 ^ R9
            v_35C = R3
            R10 = self.ADDS(R2, R0)
            R0 = v_398
            R11 = self.ADC(R6, R4)
            R3 = v_378
            R2 = R0 | R12
            R6 = R0 & R12
            R2 = self.ANDS(R2, R1)
            R1 = R0
            R2 = self.ORRS(R2, R6)
            R6 = R8 | LR
            R6 = self.ANDS(R6, R3)
            R3 = R8 & LR
            R3 = self.ORRS(R3, R6)
            R6 = self.check(R12) << 30
            R0 = self.check(R12) >> 28
            R6 = R6 | self.check(LR) >> 2
            R0 = R0 | self.check(LR) << 4
            R4 = self.check(LR) >> 28
            R0 = self.EORS(R0, R6)
            R6 = self.check(R12) << 25
            R6 = R6 | self.check(LR) >> 7
            R4 = R4 | self.check(R12) << 4
            R0 = self.EORS(R0, R6)
            R6 = self.check(R12) >> 2
            R6 = R6 | self.check(LR) << 30
            R3 = self.ADDS(R3, R10)
            R6 = R6 ^ R4
            R4 = self.check(R12) >> 7
            R4 = R4 | self.check(LR) << 25
            R2 = self.ADC(R2, R11)
            R6 = self.EORS(R6, R4)
            v_37C = R12
            R5 = self.ADDS(R3, R6)
            R6 = self.ADC(R2, R0)
            R0 = R6 | R12
            R2 = R6 & R12
            R0 = self.ANDS(R0, R1)
            R3 = self.LSRS(R6, 0x1C)
            R0 = self.ORRS(R0, R2)
            R2 = self.LSLS(R6, 0x1E)
            R2 = R2 | self.check(R5) >> 2
            R3 = R3 | self.check(R5) << 4
            R2 = self.EORS(R2, R3)
            R3 = self.LSLS(R6, 0x19)
            R3 = R3 | self.check(R5) >> 7
            R4 = self.LSRS(R5, 0x1C)
            R3 = self.EORS(R3, R2)
            R2 = self.LSRS(R6, 2)
            R2 = R2 | self.check(R5) << 30
            R4 = R4 | self.check(R6) << 4
            R2 = self.EORS(R2, R4)
            R4 = self.LSRS(R6, 7)
            R4 = R4 | self.check(R5) << 25
            R12 = R6
            R2 = self.EORS(R2, R4)
            R4 = R5 | LR
            R4 = R4 & R8
            R6 = R5 & LR
            R4 = self.ORRS(R4, R6)
            v_388 = R5
            R5 = self.ADDS(R2, R4)
            R0 = self.ADCS(R0, R3)
            v_398 = R1
            R4 = R9
            v_350 = R0
            R0 = v_3A4
            R1 = v_3A0
            v_380 = LR
            LR = self.ADDS(R0, R10)
            R9 = self.ADC(R1, R11)
            R0 = v_3AC
            R6 = self.check(LR) >> 14
            R1 = v_384
            R3 = self.check(R9) >> 18
            R2 = self.check(R9) >> 14
            R3 = R3 | self.check(LR) << 14
            R2 = R2 | self.check(LR) << 18
            R2 = self.EORS(R2, R3)
            R3 = self.check(R9) << 23
            R3 = R3 | self.check(LR) >> 9
            R6 = R6 | self.check(R9) << 18
            R2 = self.EORS(R2, R3)
            R3 = self.check(LR) >> 18
            R3 = R3 | self.check(R9) << 14
            v_39C = R8
            R3 = self.EORS(R3, R6)
            R6 = self.check(R9) >> 9
            R6 = R6 | self.check(LR) << 23
            R8 = v_354
            R3 = self.EORS(R3, R6)
            R6 = R0 ^ R1
            R6 = R6 & R9
            v_370 = R12
            R6 = self.EORS(R6, R0)
            R0 = v_3A8
            R1 = R0 ^ R8
            R1 = R1 & LR
            R1 = self.EORS(R1, R0)
            R0 = v_358
            R1 = self.ADDS(R1, R4)
            R6 = self.ADCS(R6, R0)
            R0 = v_390
            R1 = self.ADDS(R1, R0)
            R0 = v_38C
            R6 = self.ADCS(R6, R0)
            R0 = v_360
            R1 = self.ADDS(R1, R0)
            R0 = v_35C
            R6 = self.ADCS(R6, R0)
            R1 = self.ADDS(R1, R3)
            R3 = self.ADC(R6, R2)
            R2 = v_350
            R0 = self.ADDS(R5, R1)
            R5 = v_37C
            R4 = self.ADC(R2, R3)
            v_390 = R4
            R2 = R4 | R12
            R6 = R4 & R12
            R2 = self.ANDS(R2, R5)
            R5 = self.LSRS(R4, 0x1C)
            R10 = R2 | R6
            R2 = self.LSLS(R4, 0x1E)
            R2 = R2 | self.check(R0) >> 2
            R5 = R5 | self.check(R0) << 4
            R2 = self.EORS(R2, R5)
            R5 = self.LSLS(R4, 0x19)
            R5 = R5 | self.check(R0) >> 7
            R6 = self.LSRS(R0, 0x1C)
            R12 = R2 ^ R5
            R2 = self.LSRS(R4, 2)
            R2 = R2 | self.check(R0) << 30
            R6 = R6 | self.check(R4) << 4
            R2 = self.EORS(R2, R6)
            R6 = self.LSRS(R4, 7)
            R4 = v_388
            R6 = R6 | self.check(R0) << 25
            R5 = v_380
            R2 = self.EORS(R2, R6)
            R6 = R0 | R4
            R4 = self.ANDS(R4, R0)
            R6 = self.ANDS(R6, R5)
            v_38C = R0
            R4 = self.ORRS(R4, R6)
            R6 = LR ^ R8
            R0 = self.ADDS(R2, R4)
            v_3A4 = R0
            R0 = self.ADC(R12, R10)
            v_3A0 = R0
            R0 = v_378
            R10 = self.ADDS(R1, R0)
            R0 = v_374
            R6 = R6 & R10
            R1 = self.ADC(R3, R0)
            R5 = self.check(R10) >> 14
            R0 = v_384
            R6 = R6 ^ R8
            R3 = self.LSRS(R1, 0x12)
            R4 = self.LSRS(R1, 0xE)
            R3 = R3 | self.check(R10) << 14
            R4 = R4 | self.check(R10) << 18
            R3 = self.EORS(R3, R4)
            R4 = self.LSLS(R1, 0x17)
            R4 = R4 | self.check(R10) >> 9
            R5 = R5 | self.check(R1) << 18
            R11 = R3 ^ R4
            R3 = self.check(R10) >> 18
            R3 = R3 | self.check(R1) << 14
            v_378 = R1
            R3 = self.EORS(R3, R5)
            R5 = self.LSRS(R1, 9)
            R5 = R5 | self.check(R10) << 23
            R3 = self.EORS(R3, R5)
            R5 = R9 ^ R0
            R5 = self.ANDS(R5, R1)
            R1 = v_3A8
            R5 = self.EORS(R5, R0)
            R0 = v_36C
            R4 = self.ADDS(R0, R1)
            R2 = self.rodata[0x10 * index + 5]
            R0 = v_3AC
            R2 = self.ADCS(R2, R0)
            R0 = v_364
            R4 = self.ADDS(R4, R0)
            R12 = list_3B8[0x10 * index + 4]
            R0 = v_3A4
            R2 = self.ADC(R2, R12)
            R6 = self.ADDS(R6, R4)
            R2 = self.ADCS(R2, R5)
            R3 = self.ADDS(R3, R6)
            R11 = self.ADC(R11, R2)
            R1 = self.ADDS(R0, R3)
            R0 = v_3A0
            R6 = v_390
            R4 = self.check(R1) >> 28
            R0 = self.ADC(R0, R11)
            R5 = v_370
            R2 = R0 | R6
            R6 = self.ANDS(R6, R0)
            R2 = self.ANDS(R2, R5)
            R5 = self.LSRS(R0, 0x1C)
            R12 = R2 | R6
            R6 = self.LSLS(R0, 0x1E)
            R6 = R6 | self.check(R1) >> 2
            R5 = R5 | self.check(R1) << 4
            R6 = self.EORS(R6, R5)
            R5 = self.LSLS(R0, 0x19)
            R5 = R5 | self.check(R1) >> 7
            R4 = R4 | self.check(R0) << 4
            R6 = self.EORS(R6, R5)
            R5 = self.LSRS(R0, 2)
            R5 = R5 | self.check(R1) << 30
            v_3AC = R0
            R5 = self.EORS(R5, R4)
            R4 = self.LSRS(R0, 7)
            R0 = v_38C
            R4 = R4 | self.check(R1) << 25
            R2 = v_388
            R5 = self.EORS(R5, R4)
            R4 = R1 | R0
            v_3A8 = R1
            R4 = self.ANDS(R4, R2)
            R2 = R1 & R0
            R2 = self.ORRS(R2, R4)
            R0 = self.ADDS(R5, R2)
            v_3A4 = R0
            R0 = self.ADC(R6, R12)
            v_3A0 = R0
            R0 = v_39C
            R2 = v_398
            R0 = self.ADDS(R0, R3)
            v_39C = R0
            R11 = self.ADC(R11, R2)
            R4 = self.LSRS(R0, 0xE)
            R3 = self.check(R11) >> 18
            R6 = self.check(R11) >> 14
            R3 = R3 | self.check(R0) << 14
            R6 = R6 | self.check(R0) << 18
            R3 = self.EORS(R3, R6)
            R6 = self.check(R11) << 23
            R6 = R6 | self.check(R0) >> 9
            R4 = R4 | self.check(R11) << 18
            R1 = self.EORS(R3, R6)
            R6 = self.LSRS(R0, 0x12)
            R6 = R6 | self.check(R11) << 14
            R3 = R10 ^ LR
            R6 = self.EORS(R6, R4)
            R4 = self.check(R11) >> 9
            R3 = self.ANDS(R3, R0)
            R4 = R4 | self.check(R0) << 23
            R5 = R6 ^ R4
            v_398 = R1
            R3 = R3 ^ LR
            R1 = v_378
            R6 = self.rodata[0x10 * index + 6]
            R12 = self.rodata[0x10 * index + 7]
            R4 = R1 ^ R9
            R0 = v_384
            R6 = self.ADDS(R6, R8)
            R4 = R4 & R11
            R12 = self.ADC(R12, R0)
            R4 = R4 ^ R9
            R8 = list_3B8[0x10 * index + 7]
            R2 = list_3B8[0x10 * index + 6]
            R6 = self.ADDS(R6, R8)
            R0 = v_398
            R2 = self.ADC(R2, R12)
            R3 = self.ADDS(R3, R6)
            R2 = self.ADCS(R2, R4)
            R6 = self.ADDS(R3, R5)
            R12 = self.ADC(R2, R0)
            R0 = v_3A4
            R4 = v_390
            R1 = self.ADDS(R0, R6)
            R0 = v_3A0
            v_384 = R1
            R5 = self.ADC(R0, R12)
            R0 = v_3AC
            R8 = self.check(R1) >> 28
            R2 = R5 | R0
            R3 = R8 | self.check(R5) << 4
            R2 = self.ANDS(R2, R4)
            R4 = R5 & R0
            R0 = R2 | R4
            R4 = self.LSLS(R5, 0x1E)
            R2 = self.LSRS(R5, 0x1C)
            R4 = R4 | self.check(R1) >> 2
            R2 = R2 | self.check(R1) << 4
            v_3A0 = R0
            R2 = self.EORS(R2, R4)
            R4 = self.LSLS(R5, 0x19)
            R4 = R4 | self.check(R1) >> 7
            R0 = v_3A8
            R2 = self.EORS(R2, R4)
            R4 = self.LSRS(R5, 2)
            R4 = R4 | self.check(R1) << 30
            R8 = R5
            R3 = self.EORS(R3, R4)
            R4 = self.LSRS(R5, 7)
            R4 = R4 | self.check(R1) << 25
            R5 = v_38C
            R3 = self.EORS(R3, R4)
            R4 = R1 | R0
            R4 = self.ANDS(R4, R5)
            R5 = R1 & R0
            R4 = self.ORRS(R4, R5)
            v_36C = R8
            R0 = self.ADDS(R3, R4)
            v_3A4 = R0
            R0 = v_3A0
            R0 = self.ADCS(R0, R2)
            v_3A0 = R0
            R0 = v_380
            R2 = v_37C
            R0 = self.ADDS(R0, R6)
            R5 = self.ADC(R12, R2)
            v_37C = R5
            R4 = self.LSRS(R0, 0xE)
            v_380 = R0
            R2 = self.LSRS(R5, 0x12)
            R3 = self.LSRS(R5, 0xE)
            R2 = R2 | self.check(R0) << 14
            R3 = R3 | self.check(R0) << 18
            R2 = self.EORS(R2, R3)
            R3 = self.LSLS(R5, 0x17)
            R3 = R3 | self.check(R0) >> 9
            R4 = R4 | self.check(R5) << 18
            R1 = R2 ^ R3
            R3 = self.LSRS(R0, 0x12)
            R3 = R3 | self.check(R5) << 14
            v_398 = R1
            R3 = self.EORS(R3, R4)
            R4 = self.LSRS(R5, 9)
            R1 = v_378
            R4 = R4 | self.check(R0) << 23
            R12 = R3 ^ R4
            R3 = list_3B8[0x10 * index + 9]
            R4 = R11 ^ R1
            R4 = self.ANDS(R4, R5)
            R4 = self.EORS(R4, R1)
            R1 = v_39C
            R5 = R1 ^ R10
            R5 = self.ANDS(R5, R0)
            R5 = R5 ^ R10
            R2 = self.rodata[0x10 * index + 8]
            R0 = self.ADDS(R2, LR)
            R2 = self.rodata[0x10 * index + 9]
            R2 = self.ADC(R2, R9)
            R0 = self.ADDS(R0, R3)
            R3 = list_3B8[0x10 * index + 8]
            R2 = self.ADCS(R2, R3)
            R0 = self.ADDS(R0, R5)
            R2 = self.ADCS(R2, R4)
            R1 = self.ADDS(R0, R12)
            R0 = v_398
            R3 = v_3AC
            R4 = self.ADC(R2, R0)
            R0 = v_3A4
            R6 = self.ADDS(R0, R1)
            R0 = v_3A0
            v_3A4 = R6
            R0 = self.ADCS(R0, R4)
            v_3A0 = R0
            R2 = R0 | R8
            R2 = self.ANDS(R2, R3)
            R3 = R0 & R8
            LR = R2 | R3
            R8 = R6
            R3 = self.LSLS(R0, 0x1E)
            R5 = self.LSRS(R0, 0x1C)
            R3 = R3 | self.check(R8) >> 2
            R5 = R5 | self.check(R8) << 4
            R3 = self.EORS(R3, R5)
            R5 = self.LSLS(R0, 0x19)
            R5 = R5 | self.check(R8) >> 7
            R2 = self.check(R8) >> 28
            R12 = R3 ^ R5
            R5 = self.LSRS(R0, 2)
            R5 = R5 | self.check(R8) << 30
            R2 = R2 | self.check(R0) << 4
            R2 = self.EORS(R2, R5)
            R5 = self.LSRS(R0, 7)
            R3 = v_384
            R5 = R5 | self.check(R8) << 25
            R6 = v_3A8
            R2 = self.EORS(R2, R5)
            R5 = R8 | R3
            R5 = self.ANDS(R5, R6)
            R6 = R8 & R3
            R5 = self.ORRS(R5, R6)
            R0 = self.ADDS(R2, R5)
            v_398 = R0
            R2 = v_388
            R12 = self.ADC(R12, LR)
            R0 = v_370
            R3 = self.ADDS(R1, R2)
            R1 = v_380
            R8 = self.ADC(R4, R0)
            R0 = R3
            R2 = self.check(R8) >> 18
            R3 = self.check(R8) >> 14
            R2 = R2 | self.check(R0) << 14
            R3 = R3 | self.check(R0) << 18
            R2 = self.EORS(R2, R3)
            R3 = self.check(R8) << 23
            R3 = R3 | self.check(R0) >> 9
            R4 = self.LSRS(R0, 0xE)
            LR = R2 ^ R3
            R3 = self.LSRS(R0, 0x12)
            R3 = R3 | self.check(R8) << 14
            R4 = R4 | self.check(R8) << 18
            R3 = self.EORS(R3, R4)
            R4 = self.check(R8) >> 9
            R4 = R4 | self.check(R0) << 23
            R2 = R0
            R0 = v_37C
            R3 = self.EORS(R3, R4)
            v_388 = R2
            R4 = R0 ^ R11
            R0 = v_39C
            R4 = R4 & R8
            R5 = R1 ^ R0
            R4 = R4 ^ R11
            R5 = self.ANDS(R5, R2)
            R5 = self.EORS(R5, R0)
            R6 = self.rodata[0x10 * index + 10]
            R1 = self.ADDS(R6, R10)
            R6 = self.rodata[0x10 * index + 11]
            R0 = v_378
            R6 = self.ADCS(R6, R0)
            R2 = list_3B8[0x10 * index + 11]
            R1 = self.ADDS(R1, R2)
            R2 = list_3B8[0x10 * index + 10]
            R0 = v_398
            R2 = self.ADCS(R2, R6)
            R1 = self.ADDS(R1, R5)
            R2 = self.ADCS(R2, R4)
            R1 = self.ADDS(R1, R3)
            R4 = self.ADC(R2, LR)
            R6 = v_3A0
            R0 = self.ADDS(R0, R1)
            R9 = self.ADC(R12, R4)
            R3 = v_36C
            R2 = R9 | R6
            R5 = self.check(R9) >> 28
            v_374 = R9
            R2 = self.ANDS(R2, R3)
            R3 = R9 & R6
            R10 = R2 | R3
            R3 = self.check(R9) << 30
            R3 = R3 | self.check(R0) >> 2
            R5 = R5 | self.check(R0) << 4
            R3 = self.EORS(R3, R5)
            R5 = self.check(R9) << 25
            R5 = R5 | self.check(R0) >> 7
            R6 = self.LSRS(R0, 0x1C)
            R12 = R3 ^ R5
            R5 = self.check(R9) >> 2
            R5 = R5 | self.check(R0) << 30
            R6 = R6 | self.check(R9) << 4
            R5 = self.EORS(R5, R6)
            R6 = self.check(R9) >> 7
            R3 = v_3A4
            R6 = R6 | self.check(R0) << 25
            R2 = v_384
            R5 = self.EORS(R5, R6)
            R6 = R0 | R3
            R6 = self.ANDS(R6, R2)
            R2 = R0 & R3
            R2 = R2 | R6
            R2 = self.ADDS(R2, R5)
            v_398 = R2
            R2 = self.ADC(R12, R10)
            v_378 = R2
            R2 = v_38C
            R12 = self.ADDS(R1, R2)
            R1 = v_390
            LR = self.ADC(R4, R1)
            R4 = self.check(R12) >> 14
            R1 = self.check(LR) >> 18
            R2 = self.check(LR) >> 14
            R1 = R1 | self.check(R12) << 14
            R2 = R2 | self.check(R12) << 18
            R1 = self.EORS(R1, R2)
            R2 = self.check(LR) << 23
            R2 = R2 | self.check(R12) >> 9
            R4 = R4 | self.check(LR) << 18
            R1 = self.EORS(R1, R2)
            R2 = self.check(R12) >> 18
            R2 = R2 | self.check(LR) << 14
            v_390 = R1
            R2 = self.EORS(R2, R4)
            R4 = self.check(LR) >> 9
            R1 = v_37C
            R4 = R4 | self.check(R12) << 23
            R10 = R2 ^ R4
            R2 = v_388
            R4 = R8 ^ R1
            R4 = R4 & LR
            R4 = self.EORS(R4, R1)
            R1 = v_380
            R5 = R2 ^ R1
            R2 = v_39C
            R5 = R5 & R12
            R5 = self.EORS(R5, R1)
            R6 = self.rodata[0x10 * index + 12]
            R3 = self.rodata[0x10 * index + 13]
            R6 = self.ADDS(R6, R2)
            R3 = self.ADC(R3, R11)
            R1 = list_3B8[0x10 * index + 13]
            R1 = self.ADDS(R1, R6)
            R6 = list_3B8[0x10 * index + 12]
            R3 = self.ADCS(R3, R6)
            R1 = self.ADDS(R1, R5)
            R3 = self.ADCS(R3, R4)
            R5 = self.ADDS(R1, R10)
            R1 = v_390
            R2 = self.ADC(R3, R1)
            R1 = v_398
            R3 = v_3A0
            R10 = self.ADDS(R1, R5)
            R1 = v_378
            v_378 = R0
            R11 = self.ADC(R1, R2)
            R6 = self.check(R10) >> 28
            R1 = R11 | R9
            v_398 = R11
            R1 = self.ANDS(R1, R3)
            R3 = R11 & R9
            R9 = R1 | R3
            R3 = self.check(R11) << 30
            R4 = self.check(R11) >> 28
            R3 = R3 | self.check(R10) >> 2
            R4 = R4 | self.check(R10) << 4
            R6 = R6 | self.check(R11) << 4
            R3 = self.EORS(R3, R4)
            R4 = self.check(R11) << 25
            R4 = R4 | self.check(R10) >> 7
            R1 = v_3A4
            R3 = self.EORS(R3, R4)
            R4 = self.check(R11) >> 2
            R4 = R4 | self.check(R10) << 30
            v_39C = R10
            R4 = self.EORS(R4, R6)
            R6 = self.check(R11) >> 7
            R6 = R6 | self.check(R10) << 25
            R4 = self.EORS(R4, R6)
            R6 = R10 | R0
            R6 = self.ANDS(R6, R1)
            R1 = R10 & R0
            R1 = self.ORRS(R1, R6)
            R10 = LR
            R0 = self.ADDS(R4, R1)
            v_390 = R0
            R0 = self.ADC(R3, R9)
            v_38C = R0
            R0 = v_3A8
            R9 = R12
            R4 = self.ADDS(R5, R0)
            R0 = v_3AC
            v_3A8 = R4
            R0 = self.ADCS(R0, R2)
            R3 = self.LSRS(R4, 0xE)
            v_3AC = R0
            R1 = self.LSRS(R0, 0x12)
            R2 = self.LSRS(R0, 0xE)
            R1 = R1 | self.check(R4) << 14
            R2 = R2 | self.check(R4) << 18
            R1 = self.EORS(R1, R2)
            R2 = self.LSLS(R0, 0x17)
            R2 = R2 | self.check(R4) >> 9
            R3 = R3 | self.check(R0) << 18
            R11 = R1 ^ R2
            R2 = self.LSRS(R4, 0x12)
            R2 = R2 | self.check(R0) << 14
            R2 = self.EORS(R2, R3)
            R3 = self.LSRS(R0, 9)
            R3 = R3 | self.check(R4) << 23
            R2 = self.EORS(R2, R3)
            R3 = LR ^ R8
            R3 = self.ANDS(R3, R0)
            R0 = v_388
            LR = R3 ^ R8
            R5 = R12 ^ R0
            R5 = self.ANDS(R5, R4)
            R3 = R0
            R5 = self.EORS(R5, R0)
            R4 = self.rodata[0x10 * index + 14]
            R6 = self.rodata[0x10 * index + 15]
            R0 = v_380
            R4 = self.ADDS(R4, R0)
            R0 = v_37C
            R6 = self.ADCS(R6, R0)
            R0 = list_3B8[0x10 * index + 14]
            R1 = list_3B8[0x10 * index + 15]
            R1 = self.ADDS(R1, R4)
            R0 = self.ADCS(R0, R6)
            R1 = self.ADDS(R1, R5)
            R0 = self.ADC(R0, LR)
            R1 = self.ADDS(R1, R2)
            R2 = v_390
            R0 = self.ADC(R0, R11)
            R4 = R8
            LR = self.ADDS(R2, R1)
            R2 = v_38C
            R6 = R3
            R12 = self.ADC(R2, R0)
            R2 = v_384
            R8 = self.ADDS(R1, R2)
            R2 = v_36C
            R5 = self.ADC(R0, R2)
        list_638 = [
            self.check(LR),
            self.check(R12),
            self.check(v_39C),
            self.check(v_398),
            self.check(v_378),
            self.check(v_374),
            self.check(v_3A4),
            self.check(v_3A0),
            self.check(R8),
            self.check(R5),
            self.check(v_3A8),
            self.check(v_3AC),
            self.check(R9),
            self.check(R10),
            self.check(R6),
            self.check(R4),
        ]
        for i in range(8):
            R0 = param_list[2 * i]
            R1 = param_list[2 * i + 1]
            R0 = self.ADDS(R0, list_638[2 * i])
            R1 = self.ADCS(R1, list_638[2 * i + 1])
            param_list[2 * i] = R0
            param_list[2 * i + 1] = R1
        return param_list

    def hex_C52(self, list_6B0):
        list_8D8 = []
        for i in range(8):
            tmp = self.hex_list([list_6B0[2 * i + 1], list_6B0[2 * i]])
            list_8D8 = list_8D8 + tmp
        return list_8D8

    def toHex(self, num):
        return format(int(num), "x")

    def check(self, tmp):
        ss = ""
        if tmp < 0:
            ss = self.toHex(4294967296 + int(tmp))
        else:
            ss = self.toHex(tmp)
        if len(ss) > 8:
            size = len(ss)
            start = size - 8
            ss = ss[start:]
            tmp = int(self.parseLong(ss, 10, 16))
        return tmp

    def ADDS(self, a, b):
        c = self.check(a) + self.check(b)
        if len(self.toHex(c)) > 8:
            self.CF = 1
        else:
            self.CF = 0
        result = self.check(c)
        return result

    def ANDS(self, a, b):
        return self.check(a & b)

    def EORS(self, a, b):
        return self.check(a ^ b)

    def ADC(self, a, b):
        c = self.check(a) + self.check(b)
        d = self.check(c + self.CF)
        return d

    def ADCS(self, a, b):
        c = self.check(a) + self.check(b)
        d = self.check(c + self.CF)
        if len(self.toHex(c)) > 8:
            self.CF = 1
        else:
            self.CF = 0
        return d

    def LSLS(self, num, k):
        result = self.bin_type(num)
        self.CF = result[k - 1]
        return self.check(self.check(num) << k)

    def LSRS(self, num, k):
        result = self.bin_type(num)
        self.CF = result[len(result) - k]
        return self.check(self.check(num) >> k)

    def ORRS(self, a, b):
        return self.check(a | b)

    def RRX(self, num):
        result = self.bin_type(num)
        lenght = len(result)
        s = str(self.CF) + result[: lenght - 1 - 0]
        return self.parseLong(s, 10, 2)

    def bin_type(self, num):
        result = ""
        num = self.check(num)
        lst = self.toBinaryString(num)
        for i in range(32):
            if i < len(lst):
                result += str(lst[i])
            else:
                result = "0" + result
        return result

    def UBFX(self, num, lsb, width):
        tmp_string = self.toBinaryString(num)
        while len(tmp_string) < 32:
            tmp_string = "0" + tmp_string
        lens = len(tmp_string)
        start = lens - lsb - width
        end = start - lsb
        a = int(self.parseLong(tmp_string[start : end - start], 10, 2))

        return int(self.parseLong(tmp_string[start : end - start], 10, 2))

    def UFTX(self, num):
        tmp_string = self.toBinaryString(num)
        start = len(tmp_string) - 8
        return self.parseLong(tmp_string[start:], 10, 2)

    def toBinaryString(self, num):
        return "{0:b}".format(num)

    def setData(self, data):
        self.__content_raw = data
        self.__content = data
        self.list_9C8 = self.hex_9C8()

    def hex_9C8(self):
        result = []
        for i in range(32):
            result.append(self.chooice(0, 0x100))
        return result

    def chooice(self, start, end):
        return int(random.uniform(0, 1) * (end + 1 - start) + start)

    def s2b(self, data):
        arr = []
        for i in range(len(data)):
            arr.append(data[i])
        return arr

    def hex_list(self, content):
        result = []
        for value in content:
            tmp = self.toHex(value)
            while len(tmp) < 8:
                tmp = "0" + tmp
            for i in range(4):
                start = 2 * i
                end = 2 * i + 2
                ss = tmp[start:end]
                result.append(int(self.parseLong(ss, 10, 16)))
        return result

    def parseLong(self, num, to_base=10, from_base=10):
        if isinstance(num, str):
            n = int(num, from_base)
        else:
            n = int(num)
        alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if n < to_base:
            return alphabet[n]
        else:
            return self.parseLong(n // to_base, to_base) + alphabet[n % to_base]

    def byteArray2str(self, b):
        return binascii.hexlify(bytes(b)).decode()

    def changeByteArrayToLong(self, bytes):
        result = []
        for byte in bytes:
            if byte < 0:
                result.append(byte + 256)
            else:
                result.append(byte)
        return result
    


http=["7421185094760040198:7421184511113283078:c3df63f5fd02a9ac:786100e9-614d-49ec-a222-f3b8a172f7d0:1727879356",
"7421185246433249030:7421184490586916358:df9927f682881622:72d4de88-de4e-49c8-9488-5edab7baeb0c:1727879386",
"7421185447612729094:7421184864579339781:acdc20f90d571ef7:5a7127ab-52cd-4e31-8f93-d862dd5b2ac8:1727879429",
"7421185585094772486:7421185030787073541:7645f439e35a2fcc:26398c55-60f1-435a-b052-1fb07b103cc7:1727879467",
"7421220394336782086:7421219778851079685:775a547275d8b50e:6d5d76a4-00c4-4176-9bc1-52990d4ee70e:1727887576",
"7421221929799927558:7421221200468985349:2e32c6cc7f608e33:0026cb8d-9e37-4227-b3ec-f1b5505bb71a:1727887932",
"7421222595683616517:7421222413256443398:c6222b8abc4facf8:fd98317c-6a1c-4a6d-9264-f778f0f0ba42:1727887969",
"7421222154584508166:7421221501062202886:b838a367df56ef64:e5bf517a-e811-4ded-8b80-40f69cb15cff:1727887982",
"7421222280589575941:7421221460021151238:1daaa99c79906d91:8824b20e-f1e0-46a1-a8ba-68169f396dc9:1727888008",
"7421228740006692614:7421228270014727685:1bb106048070f753:038d808a-1c24-4180-98f4-a23058f51050:1727889513",
"7421233187554166534:7421232395834557957:d7ec8b037a373001:0cc517b6-be77-4e02-8307-60edfce4d961:1727890550",
"7421233501587179270:7421232995996190214:ae4d2aea45af4bcf:e4104809-e6cb-42f3-8b37-bb515d802c50:1727890634",
"7421233746747066117:7421232949918893574:10351a0a0e7c68dd:d5e23f94-22dd-4587-b74d-68d664ec10ac:1727890681",
"7421234253407897350:7421233744084354565:d335dfde581fe089:bb477b21-76da-43fd-8d84-e370f47095a1:1727890809",
"7421234293274101510:7421233668583130629:d7189a98af5b21fd:fe8161d4-5bf6-4afa-a696-47bc8945717b:1727890813",
"7421234361310660357:7421233797612766726:0b613623aac63d47:8df737f6-07f6-427f-8719-50040cc9f9a9:1727890834",
"7421234386950096646:7421233782525150726:e94b652538f08246:f9d21955-3d92-4cbf-849c-f2c6426dfdb2:1727890837",
"7421234448572188422:7421233887927944710:473b0e2fa04ff0c7:244a0dcc-bcb5-4406-a877-6d87b9385d9e:1727890845",
"7421234442222700294:7421233943531423238:003bc4ee00bcf315:f3f15e8d-a49c-4b13-b172-b2729de03675:1727890849",
"7421234467979757317:7421233879107339782:ba588ed0bb056851:a053f33b-e486-47ea-9430-6a71fb1c48b9:1727890853",
"7421234491375175429:7421233993800140294:20d16ea59ae3ddb1:5a8c54d3-296a-4df1-9c73-8762a1c799db:1727890857",
"7421234499104753414:7421233943531816454:0ac3c8786ae27008:0ed6225b-8785-4a9a-92b9-bfda2b712d1b:1727890861",
"7421234561805190917:7421233866088318470:f6ef5e8e473f1693:43d162be-dfb8-4488-bc2a-5879c4d1658e:1727890865",
"7421234667402479365:7421234100533331462:9069a8545a892ead:4b0c8a5e-221d-44f9-8317-4e43689d5ff0:1727890903",
]


def tt_encrypt(data) -> str:
  return AFRITON().encrypt(json.dumps(data).replace(" ", ""))
def device_register() -> dict:
      _rticket,ts,ts1,icket=tim()
      openudid = hexlify(random.randbytes(8)).decode()
      cdid = str(uuid4())
      google_aid = str(uuid4())
      clientudid = str(uuid4())
      req_id = str(uuid4())
      url = f"https://log-va.tiktokv.com/service/2/device_register/?ac=wifi&channel=googleplay&aid=1233&app_name=musical_ly&version_code=170404&version_name=17.4.4&device_platform=android&ab_version=17.4.4&ssmix=a&device_type=SM-G611M&device_brand=samsung&language=en&os_api=28&os_version=9&openudid={openudid}&manifest_version_code=2021704040&resolution=720*1280&dpi=320&update_version_code=2021704040&_rticket={icket}&_rticket={_rticket}&storage_type=2&app_type=normal&sys_region=US&appTheme=light&pass-route=1&pass-region=1&timezone_name=Europe%252FBerlin&cpu_support64=false&host_abi=armeabi-v7a&app_language=en&ac2=wifi&uoo=1&op_region=US&timezone_offset=3600&build_number=17.4.4&locale=en&region=US&ts={ts}&cdid={cdid}"
      
      payload = {"magic_tag":"ss_app_log","header":{"display_name":"TikTok","update_version_code":2021704040,"manifest_version_code":2021704040,"app_version_minor":"","aid":1233,"channel":"googleplay","package":"com.zhiliaoapp.musically","app_version":"17.4.4","version_code":170404,"sdk_version":"2.12.1-rc.5","sdk_target_version":29,"git_hash":"050d489d","os":"Android","os_version":"9","os_api":28,"device_model":"SM-G611M","device_brand":"samsung","device_manufacturer":"samsung","cpu_abi":"armeabi-v7a","release_build":"e1611c6_20200824","density_dpi":320,"display_density":"xhdpi","resolution":"1280x720","language":"en","timezone":1,"access":"wifi","not_request_sender":0,"mcc_mnc":"26203","rom":"G611MUBS6CTD1","rom_version":"PPR1.180610.011","cdid":cdid,"sig_hash":"e89b158e4bcf988ebd09eb83f5378e87","gaid_limited":0,"google_aid":google_aid,"openudid":openudid,"clientudid":clientudid,"region":"US","tz_name":"Europe\\/Berlin","tz_offset":7200,"oaid_may_support":False,"req_id":req_id,"apk_first_install_time":1653436407842,"is_system_app":0,"sdk_flavor":"global"},"_gen_time":1653464286461}
      
      headers = {
        "Host": "log-va.tiktokv.com",
        "accept-encoding": "gzip",
        "sdk-version": "2",
        "passport-sdk-version": "17",
        "content-type": "application/octet-stream",
        "user-agent": "okhttp/3.10.0.1"
      }
      response = request("POST", url, headers=headers, data=bytes.fromhex(tt_encrypt(payload))).json()

      try:
       install_id = response["install_id_str"]
       device_id = response["device_id_str"]
       ti=response['server_time']
       return install_id,device_id,openudid,cdid,ti
      except:
        rfr=random.choice(http)
        install_id=rfr.split(':')[0]
        device_id=rfr.split(':')[1].split(':')[0]
        openudid=rfr.split(':')[2].split(':')[0]
        cdid=rfr.split(':')[3].split(':')[0]
        ti=rfr.split(':')[4]
      
        return install_id,device_id,openudid,cdid,ti


class Xgorgon:
    def __init__(self, params: str, data: str) -> None:

        self.params = params
        self.data = data
        self.cookies = None

    def hash(self, data: str) -> str:
        _hash = str(hashlib.md5(data.encode()).hexdigest())

        return _hash

    def get_base_string(self) -> str:
        base_str = self.hash(self.params)
        base_str = (
            base_str + self.hash(self.data) if self.data else base_str + str("0" * 32)
        )
        base_str = (
            base_str + self.hash(self.cookies)
            if self.cookies
            else base_str + str("0" * 32)
        )

        return base_str

    def get_value(self) -> json:
        base_str = self.get_base_string()

        return self.encrypt(base_str)

    def encrypt(self, data: str) -> json:
        unix = int(time.time())
        len = 0x14
        key = [
            0xDF,
            0x77,
            0xB9,
            0x40,
            0xB9,
            0x9B,
            0x84,
            0x83,
            0xD1,
            0xB9,
            0xCB,
            0xD1,
            0xF7,
            0xC2,
            0xB9,
            0x85,
            0xC3,
            0xD0,
            0xFB,
            0xC3,
        ]
        param_list = []
        for i in range(0, 12, 4):
            temp = data[8 * i : 8 * (i + 1)]
            for j in range(4):
                H = int(temp[j * 2 : (j + 1) * 2], 16)
                param_list.append(H)

        param_list.extend([0x0, 0x6, 0xB, 0x1C])

        H = int(hex(unix), 16)

        param_list.append((H & 0xFF000000) >> 24)
        param_list.append((H & 0x00FF0000) >> 16)
        param_list.append((H & 0x0000FF00) >> 8)
        param_list.append((H & 0x000000FF) >> 0)

        eor_result_list = []

        for A, B in zip(param_list, key):
            eor_result_list.append(A ^ B)

        for i in range(len):

            C = self.reverse(eor_result_list[i])
            D = eor_result_list[(i + 1) % len]
            E = C ^ D

            F = self.rbit_algorithm(E)
            H = ((F ^ 0xFFFFFFFF) ^ len) & 0xFF
            eor_result_list[i] = H

        result = ""
        for param in eor_result_list:
            result += self.hex_string(param)

        return {"X-Gorgon": ("0404b0d30000" + result), "X-Khronos": str(unix)}
    def rbit_algorithm(self, num):
        result = ""
        tmp_string = bin(num)[2:]

        while len(tmp_string) < 8:
            tmp_string = "0" + tmp_string

        for i in range(0, 8):
            result = result + tmp_string[7 - i]

        return int(result, 2)

    def hex_string(self, num):
        tmp_string = hex(num)[2:]

        if len(tmp_string) < 2:
            tmp_string = "0" + tmp_string

        return tmp_string

    def reverse(self, num):
        tmp_string = self.hex_string(num)

        return int(tmp_string[1:] + tmp_string[:1], 16)