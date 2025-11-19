
import hashlib
import time
import struct

aa = [
    4294967295, 138, 1498001188, 211147047, 253,
    r"\s*\(\)\s*{\s*\[\s*native\s+code\s*]\s*}\s*$",
    203, 288, 9, 1196819126, 3212677781, 135, 263, 193, 58, 18, 244,
    2931180889, 240, 173, 268, 2157053261, 261, 175, 14, 5, 171, 270,
    156, 258, 13, 15, 3732962506, 185, 169, 2, 6, 132, 162, 200, 3,
    160, 217618912, 62, 2517678443, 44, 164, 4, 96, 183, 2903579748,
    3863347763, 119, 181, 10, 190, 8, 2654435769, 259, 104, 230, 128,
    2633865432, 225, 1, 257, 143, 179, 16, 600974999, 185100057, 32,
    188, 53, 2718276124, 177, 196, 4294967296, 147, 117, 17, 49, 7,
    28, 12, 266, 216, 11, 0, 45, 166, 247, 1451689750
]

kt = [
    aa[44], aa[74], aa[10], aa[62], aa[42], aa[17], aa[2], aa[21],
    aa[3], aa[70], aa[50], aa[32],
    aa[0] & int(time.time()*1000),
    int(aa[77] * time.time()), int(aa[77] * time.time()), int(aa[77] * time.time())
]

St = aa[88]
Ot = [aa[9], aa[69], aa[51], aa[92]]

# -------------------------------
# دوال مساعدة
# -------------------------------
def numToUint8Array(value):
    if value < 255 * 255:
        return list(struct.pack(">H", value))
    else:
        return list(struct.pack(">I", value))

def Ab12(e):
    if isinstance(e, list):
        return Ab39(e)
    try:
        return list(e)
    except:
        raise TypeError("Invalid attempt to spread non-iterable instance.")

def Ab18(e, t, r, n, o):
    ob = [16, 12, 8, 7]
    e[t] = (e[t] + e[r]) & 0xffffffff
    e[o] = Ab41(e[o] ^ e[t], ob[0])
    e[n] = (e[n] + e[o]) & 0xffffffff
    e[r] = Ab41(e[r] ^ e[n], ob[1])
    e[t] = (e[t] + e[r]) & 0xffffffff
    e[o] = Ab41(e[o] ^ e[t], ob[2])
    e[n] = (e[n] + e[o]) & 0xffffffff
    e[r] = Ab41(e[r] ^ e[n], ob[3])

def Ab23(e):
    e[12] = (e[12]+1)&0xffffffff

def Ab33(e,t):
    r=e[:]
    for _ in range(t):
        Ab18(r,0,4,8,12)
        Ab18(r,1,5,9,13)
        Ab18(r,2,6,10,14)
        Ab18(r,3,7,11,15)
    for n in range(16):
        r[n]=(r[n]+e[n])&0xffffffff
    return r

def Ab39(e,t=None):
    if t is None or t>len(e):
        t=len(e)
    return e[:t]

def Ab41(e,t):
    return ((e<<t)|(e>>(32-t)))&0xffffffff

def Ab21(e,t,r):
    n=len(r)//4
    o=len(r)%4
    i=(len(r)+3)//4
    u=[0]*i
    for a in range(n):
        s=4*a
        u[a]=r[s]|(r[s+1]<<8)|(r[s+2]<<16)|(r[s+3]<<24)
    if o>0:
        u[a]=0
        for c in range(o):
            u[a]|=r[4*a+c]<<(8*c)
    def inner(e,t,r):
        n=e[:]
        o=0
        while o+16<len(r):
            i=Ab33(n,t)
            Ab23(n)
            for u in range(16):
                r[o+u]^=i[u]
            o+=16
        a=len(r)-o
        s=Ab33(n,t)
        for c in range(a):
            r[o+c]^=s[c]
    inner(e,t,u)
    for a in range(n):
        f=4*a
        r[f]=u[a]&255
        r[f+1]=(u[a]>>8)&255
        r[f+2]=(u[a]>>16)&255
        r[f+3]=(u[a]>>24)&255
    if o>0:
        for d in range(o):
            r[4*a+d]=(u[a]>>(8*d))&255

def Ab22(e,t,r):
    n=[ord(ch) for ch in r]
    Ab21(list(Ot)+Ab12(e),t,n)
    return "".join(chr(x) for x in n)

def rand():
    global St
    rb=[4294967296,4294965248,53,0,2,11,8,7]
    e=Ab33(kt,rb[6])
    t=e[St]
    r=((rb[1]&e[St+rb[6]])>>rb[5])
    if rb[7]==St:
        Ab23(kt)
        St=rb[3]
    else:
        St+=1
    return (t+rb[0]*r)/pow(rb[4],rb[2])


def encode_x_gnarly(qg, by, nt):
    obj = {}
    obj[1] = 1
    obj[2] = 0
    obj[3] = hashlib.md5(qg.encode()).hexdigest()
    obj[4] = hashlib.md5(by.encode()).hexdigest()
    obj[5] = hashlib.md5(nt.encode()).hexdigest()
    timestamp = int(time.time() * 1000)
    obj[6] = timestamp // 1000
    obj[7] = 1245783967
    obj[8] = (timestamp * 1000) % 2147483648
    obj[9] = "5.1.0"
    obj[0] = obj[6] ^ obj[7] ^ obj[8] ^ obj[1] ^ obj[2]

    arr = [len(obj.keys())]
    for key, value in obj.items():
        arr.append(int(key))
        if isinstance(value, int):
            valArr = numToUint8Array(value)
            lenArr = numToUint8Array(len(valArr))
        else:
            valArr = list(value.encode())
            lenArr = numToUint8Array(len(valArr))
        arr.extend(lenArr)
        arr.extend(valArr)

    s = "".join(chr(x) for x in arr)
    a = 1 << 6
    b = 1 << 3
    c = a ^ b
    d = c ^ 3
    e = d & 255
    someRandomChar = chr(e)

    key = []
    keyStringArr = []
    rounds = 0
    for i in range(12):
        num = int(pow(2, 32) * rand())
        key.append(num)
        rounds = ((num & 15) + rounds) & 15
        keyStringArr.extend([num & 255, (num >> 8) & 255, (num >> 16) & 255, (num >> 24) & 255])
    rounds += 5

    x = Ab22(key, rounds, s)
    someVal = 0
    for el in keyStringArr:
        someVal += el
        someVal %= len(x) + 1
    for ch in x:
        someVal += ord(ch)
        someVal %= len(x) + 1

    keyString = "".join(chr(x) for x in keyStringArr)
    s = someRandomChar + x[:someVal] + keyString + x[someVal:]

    charSet = "u09tbS3UvgDEe6r-ZVMXzLpsAohTn7mdINQlW412GqBjfYiyk8JORCF5/xKHwacP="
    res = ""
    for i in range(3, len(s) + 1, 3):
        val = ((ord(s[i - 3]) & 255) << 16) | ((ord(s[i - 2]) & 255) << 8) | (ord(s[i - 1]) & 255)
        pos = (val >> 18) & 63
        res += charSet[pos]
        pos = (val >> 12) & 63
        res += charSet[pos]
        pos = (val >> 6) & 63
        res += charSet[pos]
        pos = val & 63
        res += charSet[pos]

    return res   
