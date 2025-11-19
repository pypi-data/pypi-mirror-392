
from urllib.parse import urlparse, parse_qs
import json,hmac,string,secrets,requests,names,random,datetime,pytz,platform,os,hashlib,time
def ms_token() -> str:
        
        return requests.post('https://mssdk-va.tiktok.com/web/common?',headers={'user-agent':f"Mozilla/{user_ag()}"}).cookies.get_dict()['msToken']

def user_ag():
    acak_device = random.choice(['Windows NT 10.0; Win64; x64', 'Windows NT 10.0; WOW64', 'Windows NT 10.0', 'Macintosh; Intel Mac OS X 13_2', 'X11; Linux x86_64'])
    browser_version = (f'{random.randrange(90, 108)}.0.{random.randrange(4200, 4900)}.{random.randrange(40, 150)}')
    return ('5.0 ({}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} Safari/537.36'.format(acak_device, browser_version,random.randrange(10, 60)))
def IID():
    return "AadCFwpTyztA5j9L" + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(9))
def email():
    return names.get_last_name().lower()+str(random.randint(1,20))+"@gmail.com" ,names.get_full_name()

def XBN(i):
    if i==5:
        Xn=f'useast{i}'
    else:
        Xn=f'useast{i}a'
    return Xn

def taem_zo():
    while 1:
        try:
            timezone_name = random.choice(pytz.country_timezones[random.choice(['CA','US','ES','FR','DE','PT','UA','IE','DK',
                    'RO','NO','NL','IL','IE','PL','GB','IT','BE','HR',
                    'RU','SP','SE','IS','GR','FI','EE','CH','BG','AL',
                   'SK','SL','MT','MK','LT','LV','AT','SI'
                    ]).lower()]);break
        except:continue
    offset        = round(datetime.datetime.now(pytz.timezone(timezone_name)).utcoffset().total_seconds())
    return timezone_name,offset


def get_os_api(android_version):
    android_api_map = {
        "9": 28,
        "10": 29,
        "11": 30,
        "12": 31,
        "12L": 32,
        "13": 33,
        "14": 34,
        "15": 35,
        "16": 36,
        "17": 37,
        "18": 38
    }

    return android_api_map.get(android_version, "28")

def get_host_abi():
    machine = platform.machine().lower()
    if 'arm64' in machine or 'aarch64' in machine:
        abi = 'arm64-v8a'
    elif 'arm' in machine:
        abi = 'armeabi-v7a'
    elif 'x86_64' in machine:
        abi = 'x86_64'
    elif 'x86' in machine:
        abi = 'x86'
    else:
        abi = 'arm64-v8a'

    return abi

def RMOV(A_P_R):
    try:
        os.remove(f'\sdcard\{A_P_R}.txt')
    except:
        try:
            os.remove(f'/sdcard/{A_P_R}.txt')
        except:
            try:
                os.remove(f'{A_P_R}.txt')
            except:
                pass

def sev_fai(A_P_R,em):
    try:
        with open(f'\sdcard\{A_P_R}.txt','a') as Prox1y:
            Prox1y.write(f'{em}\n')
    except:
        try:
            with open(f'/sdcard/{A_P_R}.txt','a') as Prox1y:
                Prox1y.write(f'{em}\n')
        except:
            with open(f'{A_P_R}.txt','a') as Prox1y:
                Prox1y.write(f'{em}\n')

def hashed_id(value):
        hashed_id = value + "aDy0TUhtql92P7hScCs97YWMT-jub2q9"
        type = "2" if "@" in value else "3"
        hashed_value = hashlib.sha256(hashed_id.encode()).hexdigest()
        return f"hashed_id={hashed_value}&type={type}"

def generate_request_id():
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=18))

    return f"{timestamp}{random_part}"

def _xor(string):
    return "".join([hex(ord(c) ^ 5)[2:] for c in string])
def random_hex(length=32):
        return ''.join(random.choice('0123456789abcdef') for _ in range(length))
class Gorgon:
    def __init__(self):
        pass
    def Hrr(self, n):
        out = []
        while True:
            b = n & 0x7F
            n >>= 7
            if n:
                out.append(b | 0x80)
            else:
                out.append(b)
                break
        return bytes(out)
    def vgeta(self, num, data):
        ttxp = (num << 3) | 2
        return self.Hrr(ttxp) + self.Hrr(len(data)) + data
    def Quick(self, num, s):
        s = s.encode() if isinstance(s, str) else s
        return self.vgeta(num, s)
    def Enc(self, num, TikTok, url=None):
        if TikTok is None and url:
            TikTok = {k: v[0] for k, v in parse_qs(urlparse(url).query).items()}
        if TikTok is None:
            return b""
        if isinstance(TikTok, dict):
            TikTok = json.dumps(TikTok, separators=(",", ":"))
        elif not isinstance(TikTok, str):
            TikTok = str(TikTok)
        return self.Quick(num, TikTok)
    def build(self, params=None, cookies=None, data=None, payload=None, url=None):
        
        gon = b""
        gon += self.Enc(1, params, url)
        gon += self.Enc(2, cookies)
        gon += self.Enc(3, data or payload)
        
        return gon
    def Encoder(self, params=None, cookies=None, data=None, payload=None, url=None):
        builded = self.build(params, cookies, data, payload, url)
       
        msg = builded + "7263291a".encode() + "1233".encode()
        h = hmac.new("97551682".encode(), msg, hashlib.md5).hexdigest()       
        a = f"{random.randint(0, 0xFFFF):04x}"
        b = f"{random.randint(0, 0xFFFF):04x}"
        c = f"{random.randint(0, 0xFFFF):04x}"
        final = f"8404{a}{b}0000{h}{c}"
        unix = int(time.time())
        return {"x-gorgon": final,"x-khronos":unix}


def afr_Gorgon(params,cookies, data):
    return Gorgon().Encoder(params=params,cookies=cookies, data=data)
