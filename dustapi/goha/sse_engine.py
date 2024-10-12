############
#
#  sse_server.py
#
#  Serves as SSE implementation for mail server. The routines 
#  for SSE are invoked by the server module via the API.
#
############

import os
import binascii
import dbm
import string
from typing import List, Tuple, Dict, Any
from Crypto.Hash import HMAC, SHA256
from Crypto.Cipher import AES
from dustapi.responses import JsonResponse
from dustapi.helpers import secure_filename

# Constants
UPDATE = "update"
SEARCH = "search"
ADD_FILE = "addmail"
SEARCH_METHOD = "getEncryptedMessages"
UPDATE_METHOD = "updateEncryptedIndex"
ADD_FILE_METHOD = "putEncryptedMessage"

SRCH_BODY = 0
SRCH_HEADERS = 1

HEADERS = ["from", "sent", "date", "to", "subject", "cc"]

DELIMETER = "++?"

DEBUG = 1

class SSEEngine:
    def __init__(self, upload_folder: str, allowed_extensions: set):
        self.upload_folder = upload_folder
        self.allowed_extensions = allowed_extensions
        self.index = None  # We'll initialize this when needed

    def initialize_index(self):
        self.index = dbm.open("index", "c")

    def add_mail(self, file: bytes, filename: str, id_num: str) -> Dict[str, str]:
        filename = secure_filename(filename)
        path = os.path.join(self.upload_folder, filename)
        with open(path, "wb") as f:
            f.write(file)
        return {"results": "GOOD ADD FILE"}

    def update(self, new_index: List[Tuple[str, str, str]]) -> Dict[str, str]:
        if not self.index:
            self.initialize_index()

        for i in new_index:
            i0 = i[0].encode('ascii', 'ignore')
            i1 = i[1].encode('ascii', 'ignore')
            match = i0

            try:
                if i[2]:
                    i2 = i[2].encode('ascii', 'ignore')
                    match = i2
            except IndexError:
                pass

            for k in list(self.index.keys()):
                if match == k:
                    del self.index[k]
                    break

            self.index[i0] = i1

        return {"results": "GOOD UPDATE"}

    def search(self, query: List[Tuple[str, str, str]]) -> Dict[str, Any]:
        if not self.index:
            self.initialize_index()

        M = []
        for i in query:
            k1 = i[0].encode('ascii', 'ignore')
            k2 = i[1].encode('ascii', 'ignore')
            c = i[2].encode('ascii', 'ignore') if len(i) > 2 else None

            d = self.new_get(k1, c)
            if d:
                m = self.dec(k2, d)
                m = ''.join(filter(lambda x: x in string.printable, m))
                for msg in m.split(DELIMETER):
                    if msg and msg not in M:
                        M.append(msg)

        if not M:
            return {"results": "Found no results for query"}

        buf = []
        for m in M:
            path = os.path.join(self.upload_folder, m)
            with open(path, "rb") as fd:
                buf.append(binascii.hexlify(fd.read()).decode())

        return {"results": buf}

    def new_get(self, k1: str, c: str) -> str:
        F = self.PRF(k1, c or '')
        return self.index.get(F)

    @staticmethod
    def dec(k2: str, d: str) -> str:
        d_bin = binascii.unhexlify(d)
        iv = d_bin[:16]
        cipher = AES.new(k2[:16], AES.MODE_CBC, iv)
        doc = cipher.decrypt(d_bin[16:])
        return doc.decode()

    @staticmethod
    def PRF(k: str, data: str) -> str:
        hmac = HMAC.new(k.encode(), data.encode(), SHA256)
        return hmac.hexdigest()

    def response(self, event_generator):
        async def streaming_response():
            async for event in event_generator:
                yield event

        return JsonResponse(streaming_response())

# The following functions are kept for reference but are not used in the class
def get(index_n, k1, count):
    cc = 0
    while cc < count:
        F = PRF(k1, str(cc))
        if (DEBUG > 1): 
            print("index key = " + index_n[0])
            print("PRF of k1 and %d = %s\n" % (cc, F))
        if F == index_n[0]:
            print("C: " + str(cc))
            return index_n[1]
        cc = cc + 1
    return 0

def get_header(index_n, k1, header):
    F = PRF(k1, header)
    if (DEBUG > 1): 
        print("index key = " + index_n[0])
        print("PRF of k1 and %s = %s\n" % (header, F))
    if F == index_n[0]:
        return index_n[1]
    return 0

def get_index_len(index):
    count = 0
    for k, v in index.items():
        count = count + 1
        if (DEBUG > 1):
            print("K: " + k)
            print("V: " + v)
            print("\n")
    return count

def PRF(k: str, data: str) -> str:
    hmac = HMAC.new(k.encode(), data.encode(), SHA256)
    return hmac.hexdigest()
