import ctypes
import hashlib
import winreg

# ---------------------------
# Загружаем DLL для CPUID
# ---------------------------
lib = ctypes.CDLL("./cpuid.dll")

def get_cpuid(function_id=1):
    arr = (ctypes.c_int * 4)()
    lib.get_cpuid(arr, function_id)
    # Возвращаем как строку EAX + EDX
    return f"{arr[0]:08X}{arr[3]:08X}"

# ---------------------------
# Серийник системного диска
# ---------------------------
def get_volume_serial(drive="C:\\"):
    serial_number = ctypes.c_uint(0)
    ctypes.windll.kernel32.GetVolumeInformationA(
        ctypes.c_char_p(drive.encode('utf-8')),
        None,
        0,
        ctypes.byref(serial_number),
        None,
        None,
        None,
        0
    )
    return f"{serial_number.value:08X}"

# ---------------------------
# MachineGuid из реестра с XOR
# ---------------------------
def get_machine_guid():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Cryptography",
            0,
            winreg.KEY_READ | winreg.KEY_WOW64_64KEY
        )
        guid, _ = winreg.QueryValueEx(key, "MachineGuid")
        winreg.CloseKey(key)
        guid_bytes = bytearray(guid, 'utf-8')
        for i in range(len(guid_bytes)):
            guid_bytes[i] ^= 0xAA
        return guid_bytes.decode('latin1')
    except Exception:
        return ""

# ---------------------------
# Генерация HWID
# ---------------------------
def get_hwid():
    hwid_str = get_cpuid()
    hwid_str += get_volume_serial()
    hwid_str += get_machine_guid()
    
    sha256 = hashlib.sha256()
    sha256.update(hwid_str.encode('utf-8'))
    return sha256.hexdigest()

# ---------------------------
