


import time,ctypes,hashlib
import random
import base64
from gmssl import sm3
from functools import reduce
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


box1 = [0, 218, 17, 20, 25, 23, 95, 116, 236, 14, 146, 5, 3, 151, 128, 186, 32, 114, 244, 80, 4, 46, 36, 85, 213, 108,
      174, 201, 63, 129, 47, 99, 38, 81, 150, 242, 69, 60, 72, 55, 192, 52, 10, 77, 96, 141, 59, 62, 165, 204, 67, 120,
      90, 240, 200, 94, 164, 221, 229, 98, 37, 145, 57, 230, 8, 232, 169, 212, 132, 115, 209, 54, 110, 170, 39, 91, 167,
      225, 207, 31, 210, 182, 152, 83, 144, 195, 211, 161, 65, 29, 147, 183, 42, 97, 153, 50, 223, 43, 188, 79, 158,
      187, 166, 179, 68, 121, 44, 155, 75, 173, 252, 249, 11, 159, 27, 133, 58, 124, 243, 198, 239, 45, 241, 217, 1, 74,
      162, 103, 136, 226, 112, 199, 191, 21, 180, 163, 196, 157, 71, 56, 143, 234, 33, 205, 233, 34, 181, 139, 119, 64,
      193, 102, 76, 61, 15, 109, 160, 222, 111, 247, 202, 104, 70, 84, 178, 171, 86, 140, 53, 238, 88, 255, 228, 175,
      22, 118, 177, 197, 105, 82, 7, 154, 92, 190, 248, 246, 214, 203, 135, 126, 123, 78, 18, 30, 35, 245, 12, 168, 51,
      100, 227, 251, 235, 93, 49, 122, 208, 206, 219, 142, 101, 176, 215, 130, 66, 117, 40, 134, 2, 253, 216, 189, 156,
      125, 24, 16, 26, 41, 220, 137, 106, 250, 172, 138, 237, 127, 19, 107, 148, 194, 89, 48, 254, 113, 231, 185, 28,
      224, 87, 73, 184, 9, 6, 13, 131, 149]

box2 = [0, 7, 140, 235, 54, 24, 170, 17, 222, 123, 210, 20, 206, 127, 179, 162, 78, 199, 21, 227, 37, 77, 171, 5, 224, 26,
      3, 114, 176, 89, 151, 57, 220, 100, 69, 70, 28, 254, 60, 58, 113, 92, 73, 18, 186, 98, 228, 152, 75, 255, 64, 23,
      232, 244, 109, 81, 84, 79, 65, 49, 190, 126, 63, 148, 195, 88, 14, 96, 10, 30, 99, 201, 245, 193, 39, 108, 51, 4,
      103, 132, 239, 182, 139, 97, 226, 229, 212, 102, 48, 144, 125, 216, 107, 15, 207, 1, 74, 247, 130, 143, 184, 61,
      217, 189, 149, 225, 211, 204, 253, 145, 241, 194, 214, 202, 236, 47, 121, 164, 157, 93, 8, 196, 67, 34, 118, 25,
      59, 72, 44, 158, 146, 166, 243, 208, 87, 111, 155, 90, 46, 32, 105, 147, 173, 11, 246, 153, 141, 163, 104, 234,
      124, 122, 35, 150, 110, 238, 38, 160, 167, 174, 115, 112, 66, 169, 95, 117, 36, 221, 252, 68, 53, 131, 156, 133,
      213, 198, 161, 101, 83, 159, 76, 116, 142, 91, 9, 12, 178, 205, 55, 209, 137, 183, 120, 197, 19, 180, 172, 71,
      181, 135, 22, 231, 233, 86, 27, 154, 80, 192, 175, 56, 31, 177, 2, 242, 203, 251, 106, 168, 119, 42, 248, 165,
      185, 187, 33, 129, 237, 138, 230, 191, 250, 29, 40, 41, 45, 240, 52, 136, 6, 94, 43, 134, 16, 200, 215, 82, 13,
      249, 85, 188, 0, 50, 219, 128, 218, 223]


def xor_encrypt(message, box):
    encrypt_list = bytearray()
    for i in range(len(message)):
        box[0] = box[0] + box[i + 1]
        if box[0] > 255:
            box[0] ^= 256
        box[i + 1], box[box[0]] = box[box[0]], box[i + 1]
        encrypt_list.append(message[i] ^ (box[(box[i + 1] + box[box[0]]) & 255]))
    return encrypt_list


def base64encode(message, base64table):
    str_trans = str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=", base64table)
    return base64.b64encode(message).decode().translate(str_trans).encode()


def a_bogus(url, data, ua):
    ua_arr = bytes.fromhex(sm3.sm3_hash(list(base64encode(xor_encrypt(ua.encode(), box1[:]), "ckdp1h4ZKsUB80/Mfvw36XIgR25+WQAlEi7NLboqYTOPuzmFjJnryx9HVGDaStCe="))))
    url_arr = bytes.fromhex(sm3.sm3_hash(list(bytes.fromhex(sm3.sm3_hash(list((url + 'bds').encode()))))))
    if data:
        data_arr = bytes.fromhex(sm3.sm3_hash(list(bytes.fromhex(sm3.sm3_hash(list((data + 'bds').encode()))))))
    else:
        data_arr = [83, 69, 109, 82, 24, 153, 247, 200, 198, 128, 168, 162, 244, 70, 5, 146, 100, 77, 138, 136, 44, 218, 117, 115, 118, 120, 152, 238, 238, 224, 239, 43]

    t0 = int(time.time() * 1000)
    t1 = t0 + int(random.random() * (800 - 450 + 1))
    t2 = t1 + int(random.random() * (800 - 450 + 1))

    m29 = list()
    m29 += [
        65, (t0 >> 24) & 255, 0, 0, 0, url_arr[21], data_arr[21], ua_arr[23], (t0 >> 16) & 255, 0, 1, 0, url_arr[22], data_arr[22], ua_arr[24],
        (t1 >> 8) & 255, 0, 0, 0, (t1 >> 0) & 255, 0, 0, 14, (t0 >> 24) & 255, (t0 >> 16) & 255, (t0 >> 8) & 255, (t0 >> 0) & 255, 3
    ]
    m29.append(reduce(lambda x, y: x ^ y, [0] + m29))
    m1 = bytes([(((t2 >> 0) & 255) & 170) | 1, (((t2 >> 0) & 255) & 85) | 2, (((t2 >> 8) & 255) & 170) | 64, (((t2 >> 8) & 255) & 85) | 2]) + xor_encrypt(bytes(m29), box2[:])
    ab = base64encode(m1, "Dkdpgh2ZmsQB80/MfvV36XI1R45-WUAlEixNLwoqYTOPuzKFjJnry79HbGcaStCe=").decode()
    return ab
