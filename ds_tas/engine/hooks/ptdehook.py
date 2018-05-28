"""Hook to access the memory of Dark Souls PTDE"""
from ctypes import (
    windll, WinError, WINFUNCTYPE, POINTER, pointer, Structure, sizeof, cast
)
from ctypes.wintypes import (
    BOOL, BYTE, CHAR, DWORD, HANDLE, HMODULE,
    HWND, LPCSTR, LPCVOID, LPDWORD, LPVOID, SIZE
)


class MODULEENTRY32(Structure):
    _fields_ = [("dwSize", DWORD),
                ("th32ModuleID", DWORD),
                ("th32ProcessID", DWORD),
                ("GlblcntUsage", DWORD),
                ("ProccntUsage", DWORD),
                ("modBaseAddr", POINTER(BYTE)),
                ("modBaseSize", DWORD),
                ("hModule", HMODULE),
                ("szModule", CHAR*256),
                ("szExePath", CHAR*260)]


# def err_on_zero_or_null_check(result, func, args):
#     if not result:
#         raise WinError()
#     return args
#
#
# def quick_win_define(name, output, *args, **kwargs):
#     dllname, fname = name.split('.')
#     params = kwargs.get('params', None)
#     if params:
#         params = tuple((x, ) for x in params)
#     prototype = WINFUNCTYPE(output, *args)
#     func = prototype((fname, getattr(windll, dllname)), params)
#     err = kwargs.get('err', err_on_zero_or_null_check)
#     if err:
#         func.errcheck = err
#
#     def ret(*args2):
#         return output(func(*args2))
#     return ret
#
#
# ReadProcessMemory = quick_win_define("Kernel32.ReadProcessMemory",
#                                      BOOL, HANDLE, LPCVOID, LPVOID,
#                                      SIZE, POINTER(SIZE))
#
# WriteProcessMemory = quick_win_define("Kernel32.WriteProcessMemory",
#                                       BOOL, HANDLE, LPVOID, LPCVOID,
#                                       SIZE, POINTER(SIZE))
#
# FindWindowA = quick_win_define("User32.FindWindowA",
#                                HWND, LPCSTR, LPCSTR)
#
# GetWindowThreadProcessId = quick_win_define("User32.GetWindowThreadProcessId",
#                                             DWORD, HWND, LPDWORD)
#
# OpenProcess = quick_win_define("Kernel32.OpenProcess",
#                                HANDLE, DWORD, BOOL, DWORD)
#
# CreateToolhelp32Snapshot = quick_win_define("Kernel32.CreateToolhelp32Snapshot",
#                                             HANDLE, DWORD, DWORD)
#
# Module32First = quick_win_define("Kernel32.Module32First",
#                                  BOOL, HANDLE, POINTER(MODULEENTRY32))
#
# Module32Next = quick_win_define("Kernel32.Module32Next",
#                                 BOOL, HANDLE, POINTER(MODULEENTRY32))
#
# CloseHandle = quick_win_define("Kernel32.CloseHandle",
#                                BOOL, HANDLE)


kernel32 = windll.kernel32
user32 = windll.user32

ReadProcessMemory = kernel32.ReadProcessMemory
WriteProcessMemory = kernel32.WriteProcessMemory
OpenProcess = kernel32.OpenProcess
CreateToolhelp32Snapshot = kernel32.CreateToolhelp32Snapshot
Module32First = kernel32.Module32First
Module32Next = kernel32.Module32Next
CloseHandle = kernel32.CloseHandle
TerminateProcess = kernel32.TerminateProcess

FindWindowA = user32.FindWindowA
GetWindowThreadProcessId = user32.GetWindowThreadProcessId


class PTDEHook:
    """
    Hook Dark Souls

    Provides functions to read and write the memory of dark souls
    """

    def __init__(self):
        # Declare instance variables
        self.w_handle = None
        self.process_id = None
        self.handle = None
        self.xinput_address = None
        self.debug = False

        # Actually get the hook
        self.acquire()

    def __del__(self):
        self.release()

    def acquire(self):
        """
        Acquire a hook into the game window.
        """
        self.w_handle = FindWindowA(None, b"DARK SOULS")
        self.process_id = DWORD(0)
        GetWindowThreadProcessId(self.w_handle, pointer(self.process_id))
        # Open process with PROCESS_TERMINATE, PROCESS_VM_OPERATION,
        # PROCESS_VM_READ and PROCESS_VM_WRITE access rights
        flags = 0x1 | 0x8 | 0x10 | 0x20
        self.handle = OpenProcess(flags, False, self.process_id)
        self.xinput_address = self.get_module_base_address("XINPUT1_3.dll")
        self.debug = self.is_debug()

    def release(self):
        """
        Release the hooks
        """

        if not (self.handle or self.w_handle):
            return

        handles = [self.handle, self.w_handle]
        for handle in handles:
            try:
                # If the application is closed this will fail
                CloseHandle(handle)
            except OSError:
                pass

    def force_quit(self):
        result = TerminateProcess(self.handle)
        if result == 0:
            print('Quit Failed')
        else:
            print('Quit Successful.')
            self.release()

    def get_module_base_address(self, module_name):
        lpszModuleName = module_name.encode("ascii")
        # TH32CS_SNAPMODULE and TH32CS_SNAPMODULE32
        hSnapshot = CreateToolhelp32Snapshot(0x8 | 0x10, self.process_id)
        ModuleEntry32 = MODULEENTRY32()
        ModuleEntry32.dwSize = sizeof(MODULEENTRY32)
        if Module32First(hSnapshot, pointer(ModuleEntry32)):
            while True:
                if ModuleEntry32.szModule == lpszModuleName:
                    dwModuleBaseAddress = ModuleEntry32.modBaseAddr
                    break
                if Module32Next(hSnapshot, pointer(ModuleEntry32)):
                    continue
                else:
                    break
        CloseHandle(hSnapshot)
        return cast(dwModuleBaseAddress, LPVOID).value

    def is_debug(self):
        """
        Identify if the debug build of Dark Souls is running.

        :return: True if running the debug build, False otherwise.
        """
        return self.read_memory(0x400080, 4) == b"\xb4\x34\x96\xce"

    def read_memory(self, address, length):
        out = (BYTE*length)()
        ReadProcessMemory(self.handle, LPVOID(address), pointer(out),
                          SIZE(length), pointer(SIZE(0)))
        return bytes(out)

    def write_memory(self, address, data):
        ptr = pointer((BYTE*len(data))(*data))
        WriteProcessMemory(self.handle, LPVOID(address), ptr,
                           SIZE(len(data)), pointer(SIZE(0)))

    def write_int(self, address, value, length, signed=False):
        try:
            data = value.to_bytes(length, byteorder='little', signed=signed)
        except AttributeError:
            attr_type = str(type(value)).strip("<>acls ")
            raise TypeError(f"Expected 'int' instead of {attr_type}")
        self.write_memory(address, data)

    def read_int(self, address, length, signed=False):
        out = self.read_memory(address, length)
        return int.from_bytes(out, byteorder='little', signed=signed)

    def read_input(self):
        """
        Returns a list of 20 integers.

        index: meaning (values)
        0: dpad_up (0 or 1)
        1: dpad_down (0 or 1)
        2: dpad_left (0 or 1)
        3: dpad_right (0 or 1)
        4: start (0 or 1)
        5: back (0 or 1)
        6: left_thumb (0 or 1)
        7: right_thumb (0 or 1)
        8: left_shoulder (0 or 1)
        9: right_shoulder (0 or 1)
        10: a (0 or 1)
        11: b (0 or 1)
        12: x (0 or 1)
        13: y (0 or 1)
        14: l_trigger (0 to 255)
        15: r_trigger (0 to 255)
        16: l_thumb_x (-32,768 to 32,767)
        17: l_thumb_y (-32,768 to 32,767)
        18: r_thumb_x (-32,768 to 32,767)
        19: r_thumb_y (-32,768 to 32,767)
        """
        ptr = self.xinput_address + 0x10C44
        ptr = self.read_int(ptr, 4)
        ptr = self.read_int(ptr, 4)
        if ptr == 0:
            raise RuntimeError("Couldn't find the pointer to the controller")
        ptr += 0x28

        data = self.read_memory(ptr, 12)
        out = [0]*20

        buttons = int.from_bytes(data[0:2], byteorder='little')
        for n in range(0, 10):
            out[n] = (buttons >> n) & 1
        for n in range(12, 16):
            out[n-2] = (buttons >> n) & 1

        out[14] = int.from_bytes(data[2:3], byteorder='little')
        out[15] = int.from_bytes(data[3:4], byteorder='little')
        out[16] = int.from_bytes(data[4:6], byteorder='little', signed=True)
        out[17] = int.from_bytes(data[6:8], byteorder='little', signed=True)
        out[18] = int.from_bytes(data[8:10], byteorder='little', signed=True)
        out[19] = int.from_bytes(data[10:12], byteorder='little', signed=True)

        return out

    def write_input(self, inputs):
        """
        Expects a list of 20 integers.

        index: meaning (values)
        0: dpad_up (0 or 1)
        1: dpad_down (0 or 1)
        2: dpad_left (0 or 1)
        3: dpad_right (0 or 1)
        4: start (0 or 1)
        5: back (0 or 1)
        6: left_thumb (0 or 1)
        7: right_thumb (0 or 1)
        8: left_shoulder (0 or 1)
        9: right_shoulder (0 or 1)
        10: a (0 or 1)
        11: b (0 or 1)
        12: x (0 or 1)
        13: y (0 or 1)
        14: l_trigger (0 to 255)
        15: r_trigger (0 to 255)
        16: l_thumb_x (-32,768 to 32,767)
        17: l_thumb_y (-32,768 to 32,767)
        18: r_thumb_x (-32,768 to 32,767)
        19: r_thumb_y (-32,768 to 32,767)
        """
        data = bytes()

        buttons = 0
        for n in range(0, 10):
            buttons = buttons | (inputs[n] << n)
        for n in range(12, 16):
            buttons = buttons | (inputs[n-2] << n)
        data += buttons.to_bytes(2, byteorder="little")

        data += inputs[14].to_bytes(1, byteorder="little")
        data += inputs[15].to_bytes(1, byteorder="little")
        data += inputs[16].to_bytes(2, byteorder="little", signed=True)
        data += inputs[17].to_bytes(2, byteorder="little", signed=True)
        data += inputs[18].to_bytes(2, byteorder="little", signed=True)
        data += inputs[19].to_bytes(2, byteorder="little", signed=True)

        ptr = self.xinput_address + 0x10C44
        ptr = self.read_int(ptr, 4)
        ptr = self.read_int(ptr, 4)
        if ptr == 0:
            raise RuntimeError("couldn't find the pointer to the controller")
        ptr += 0x28

        self.write_memory(ptr, data)

    def controller(self, state):
        """
        if state == True -> enables controller
        if state == False -> disables controller
        """
        if state:
            self.write_memory(self.xinput_address + 0x6945,
                              b'\xe8\xa6\xfb\xff\xff')
        else:
            self.write_memory(self.xinput_address + 0x6945,
                              b'\x90\x90\x90\x90\x90')

    def background_input(self, state):
        """
        if state == True -> enables input while the game is in backgound
        if state == False -> disables input while the game is in backgound
        """
        if self.debug:
            ptr = 0xF75BF3
        else:
            ptr = 0xF72543
        if state:
            self.write_memory(ptr, b'\xb0\x01\x90')
        else:
            self.write_memory(ptr, b'\x0f\x94\xc0')

    def igt(self):
        """
        Get the In Game Time

        :return: In game time in milliseconds
        """
        if self.debug:
            ptr = 0x137C8C0
        else:
            ptr = 0x1378700
        ptr = self.read_int(ptr, 4)
        if ptr == 0:
            raise RuntimeError("Couldn't find the pointer to IGT")
        ptr += 0x68
        return self.read_int(ptr, 4)

    def frame_count(self):
        """
        Get the number of frames that have been shown
        since the start of the game.

        :return: Frame count
        """
        if self.debug:
            ptr = 0x137C7C4
        else:
            ptr = 0x1378604
        ptr = self.read_int(ptr, 4)
        if ptr == 0:
            raise RuntimeError("Couldn't find the pointer to the frame count")
        ptr += 0x58
        return self.read_int(ptr, 4)
