import os
import string
import sys
from json import dumps

class spaceType:
    FREE_FOR_USER = 'FREE_FOR_USER'
    TOTAL_DISK_SPACE = 'TOTAL_DISK_SPACE'
    TOTAL_FREE = 'TOTAL_FREE'
    ERROR = 'ERROR'


if sys.platform == "win32":
    from ctypes import WINFUNCTYPE, windll, POINTER, byref, c_ulonglong
    from ctypes.wintypes import BOOL, DWORD, LPCWSTR
else:
    import subprocess
    import statvfs

class reader:
    def __init__(self):
        self.data = []

    def readDir(self, path):
        listing = os.listdir(path)
        for listobj in listing:
            fullpath = os.path.join(path, listobj)
            if(os.path.isdir(fullpath)):
                print "current dir is: " + listobj
            else:
                print "current file is: " + listobj
        return

    def getDriveInfo(self):
        retval = {}

        # Windows
        if sys.platform == "win32":
            # http://msdn.microsoft.com/en-us/library/windows/desktop/aa364972%28v=vs.85%29.aspx
            drives = []
            bitmask = windll.kernel32.GetLogicalDrives()
            for letter in string.uppercase:
                if bitmask & 1:
                    retval[letter] = self.getFreeSpace(letter + ':');
                bitmask >>= 1

        # OSX
        if sys.platform == "darwin":
            from posix import popen
            df = subprocess.Popen(["df", "-kl"], stdout=subprocess.PIPE)
            output = df.communicate()[0]
            output = output.split("\n")
            for out in output:
                parts = out.split()
                try:
                    retval[parts[0]] = self.getFreeSpace(parts[0], parts)
                except:
                    pass

        # Linux
        if sys.platform == "linux2":
            df = subprocess.Popen(["df"], stdout=subprocess.PIPE)
            output = df.communicate()[0]
            output = output.split("\n")
            for out in output:
                parts = out.split()
                try:
                    retval[parts[4]] = self.getFreeSpace(parts[4])
                except:
                    pass

        return dumps(retval)

    def getFreeSpace(self, path = '/', data = {}):
        retval = {}
        if sys.platform == "win32":
            if(path == '/'):
                path = 'c:'
            #http://msdn.microsoft.com/en-us/library/windows/desktop/aa364937%28v=vs.85%29.aspx
            PULARGE_INTEGER = POINTER(c_ulonglong)
            GetDiskFreeSpaceExW = WINFUNCTYPE(BOOL, LPCWSTR, PULARGE_INTEGER, PULARGE_INTEGER, PULARGE_INTEGER)(("GetDiskFreeSpaceExW", windll.kernel32))
            GetLastError = WINFUNCTYPE(DWORD)(("GetLastError", windll.kernel32))

            n_free_for_user = c_ulonglong(0)
            n_total         = c_ulonglong(0)
            n_free          = c_ulonglong(0)

            check = GetDiskFreeSpaceExW(path,
                byref(n_free_for_user),
                byref(n_total),
                byref(n_free))

            if check == 0:
                retval[spaceType.ERROR] = "Windows error " + repr(GetLastError()) + " attempting to get disk statistics for " + path
            else:
                retval[spaceType.FREE_FOR_USER] = n_free_for_user.value
                retval[spaceType.TOTAL_DISK_SPACE] = n_total.value
                retval[spaceType.TOTAL_FREE] = n_free.value
        else:
            if os.statvfs(path):
                print data
                retval[spaceType.FREE_FOR_USER] = (int(data[3]) * 1024)
                retval[spaceType.TOTAL_DISK_SPACE]  = (int(data[1]) * 1024)
                retval[spaceType.TOTAL_FREE] = (int(data[3]) * 1024)
            #print retval
        return retval

