from multiprocessing import shared_memory
import struct
import sys

TYPE_INT = 1
TYPE_FLOAT = 2
TYPE_STR = 3
TOTAL_SIZE = 64
MAX_DATA_SIZE = 60

def createurml(varname, vardata, callgetvalue=False):    
    if isinstance(vardata, int):
        code = TYPE_INT
        data_bytes = struct.pack("i", vardata)
    elif isinstance(vardata, float):
        code = TYPE_FLOAT
        data_bytes = struct.pack("f", vardata)
    elif isinstance(vardata, str):
        code = TYPE_STR
        encoded_str = vardata.encode('utf-8')
        if len(encoded_str) > MAX_DATA_SIZE: return
        data_bytes = encoded_str.ljust(MAX_DATA_SIZE, b'\0') 
    else: return

    try:
        shm = shared_memory.SharedMemory(create=True, size=TOTAL_SIZE, name=varname)
    except:
        return

    try:
        shm.buf[:4] = struct.pack("i", code)
        shm.buf[4:4 + len(data_bytes)] = data_bytes
        
        input(f"Press Enter to close and release memory... ")
        
    except:
        pass
    
    finally:
        try:
            shm.close()
            shm.unlink()
        except:
            pass

if __name__ == "__main__":
    try:
        createurml(varname="x", vardata="test", callgetvalue=False)
        createurml(varname="x", vardata=3.14)
        createurml(varname="x", vardata=2)
        
    except:
        pass
