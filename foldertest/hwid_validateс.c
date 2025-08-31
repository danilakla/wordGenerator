#include <Python.h>
#include <windows.h>
#include <intrin.h>
#include <stdint.h>
#include <string.h>
#include <openssl/sha.h>

#define HASH_SIZE 64

static uint32_t g_b7d8_hash = 0;

// --- Вычисление простого хеша блока памяти ---
static uint32_t compute_hash(void* func, size_t size) {
    uint8_t* p = (uint8_t*)func;
    uint32_t hash = 0;
    for (size_t i = 0; i < size; i++)
        hash += p[i];
    return hash;
}

// --- Anti-tamper: проверка функции ---
static int x1a2_check_integrity(void* func, size_t size) {
    return compute_hash(func, size) == g_b7d8_hash;
}

// --- Получение MachineGuid (XOR-шифрование) ---
static int a1b2c3(char* x9f2, DWORD x7e1) {
    HKEY hKey;
    DWORD dwType = REG_SZ;
    if (RegOpenKeyExA(HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Cryptography", 0, KEY_READ | KEY_WOW64_64KEY, &hKey) != ERROR_SUCCESS)
        return 0;

    DWORD dwSize = x7e1;
    LONG ret = RegQueryValueExA(hKey, "MachineGuid", NULL, &dwType, (LPBYTE)x9f2, &dwSize);
    RegCloseKey(hKey);

    // Простое XOR-шифрование для защиты строки
    for (DWORD i = 0; i < dwSize && x9f2[i]; i++)
        x9f2[i] ^= 0xAA;

    return (ret == ERROR_SUCCESS);
}

// --- Генерация HWID ---
static PyObject* b7d8(PyObject* self, PyObject* args) {
    if (!x1a2_check_integrity((void*)b7d8, HASH_SIZE))
        return Py_BuildValue("s", "TAMPERED");

    char x1b2[512] = {0};

    // --- CPU ID ---
    int y2c3[4] = {0};
    __cpuid(y2c3, 1);
    sprintf(x1b2 + strlen(x1b2), "%08X%08X", y2c3[0], y2c3[3]);

    // --- Серийник диска ---
    DWORD z3d4 = 0;
    GetVolumeInformationA("C:\\", NULL, 0, &z3d4, NULL, NULL, NULL, 0);
    sprintf(x1b2 + strlen(x1b2), "%08X", z3d4);

    // --- MachineGuid ---
    char w4e5[128] = {0};
    if (a1b2c3(w4e5, sizeof(w4e5))) {
        for (int i = 0; i < strlen(w4e5); i++)
            w4e5[i] ^= 0xAA;
        strcat(x1b2, w4e5);
    }

    // --- SHA256 ---
    unsigned char h5f6[SHA256_DIGEST_LENGTH];
    SHA256((unsigned char*)x1b2, strlen(x1b2), h5f6);

    char hwid[65];
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++)
        sprintf(hwid + i*2, "%02x", h5f6[i]);
    hwid[64] = 0;

    return Py_BuildValue("s", hwid);
}

// --- Методы модуля ---
static PyMethodDef H6methods[] = {
    {"get_hwid", b7d8, METH_NOARGS, "Generate HWID"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef H6module = {
    PyModuleDef_HEAD_INIT,
    "hwid_validate",
    NULL,
    -1,
    H6methods
};

// --- Инициализация модуля ---
PyMODINIT_FUNC PyInit_hwid_validate(void) {
    PyObject* module = PyModule_Create(&H6module);
    if (!module) return NULL;

    // Динамически вычисляем хеш функции b7d8 при загрузке модуля
    g_b7d8_hash = compute_hash((void*)b7d8, HASH_SIZE);

    return module;
}
