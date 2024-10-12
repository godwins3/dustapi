############
#
#  jmap.py
#
#  Serves as the jmap library for the dust sse client/server.
#  Both client and server will use this lib to create 
#  and interpret JMAP messages
#
############

import json
from typing import Dict, List, Tuple, Union
from logging import getLogger

# Constants
SEARCH = "search"
UPDATE = "update"
ADD_FILE = "addmail"
SEARCH_METHOD = "getEncryptedMessages"
UPDATE_METHOD = "updateEncryptedIndex"
ADD_FILE_METHOD = "putEncryptedMessage"

JMAP_HEADER = {'Content-Type': 'application/json'} 

logger = getLogger(__name__)

# Notes on JMAP spec from jmap.io/spec
'''
BASIC QUERY STRUCTURE:
[
  ["method1", {"arg1": "arg1data", "arg2": "arg2data"}, "#1"],
  ["method2", {"arg1": "arg1data"}, "#2"],
  ["method3", {}, "#3"]
]

BASIC RESPONSE STRUCTURE:
[
  ["responseFromMethod1", {"arg1": 3, "arg2": "foo"}, "#1"],
  ["responseFromMethod2", {"isBlah": true}, "#2"],
  ["anotherResponseFromMethod2", {"data": 10, "yetmoredata": "Hello"}, "#2"],
  ["aResponseFromMethod3", {}, "#3"]
] 

EXAMPLE REQ:
["getMessages", {
  "ids": [ "f123u456", "f123u457" ],
  "properties": [ "threadId", "mailboxIds", "from", "subject", "date" ]
}, "#1"]

EXAMPLE RESP:
["messages", {
  "state": "41234123231",
  "list": [
    {
      messageId: "f123u457",
      threadId: "ef1314a",
      mailboxIds: [ "f123" ],
      from: [{name: "Joe Bloggs", email: "joe@bloggs.com"}],
      subject: "Dinner on Thursday?",
      date: "2013-10-13T14:12:00Z"
    }
  ],
  notFound: [ "f123u456" ]
}, "#1"]

========

JMAP CALLS FOR SSE:

["method", {args}, "id"]

["getEncryptedMessages", 
  {
  "query": [ "(k1 n, k2 n)", "(k1 n+1, k2 n+1)", ... ]
  },
  "#1" ]

["encryptedMessages",
  {
  "results": [ "data for msg n", "data for msg n+1", ... ]
  }
  "#1" ]

  -NOTE: for returning enc messages, possbility exists for returning each
         message's data in a separate message. Just reuse id num

'''

def jmap_header() -> Dict[str, str]:
    return JMAP_HEADER

def pack_search(data: List[str], id_num: str) -> str:
    return json.dumps([SEARCH_METHOD, {"query": data}, id_num])

def pack_update(data: Dict[str, Union[str, List[str]]], id_num: str) -> str:
    return json.dumps([UPDATE_METHOD, {"index": data}, id_num])

def pack_add_file(data: str, id_num: str, filename: str) -> str:
    return json.dumps([ADD_FILE_METHOD, {"file": data, "filename": filename}, id_num])

def pack(method: str, data: Union[List[str], Dict[str, Union[str, List[str]]], str], id_num: str, filename: str = None) -> str:
    if not method:
        logger.error("Must provide a method to jmap.pack")
        raise ValueError("Must provide a method to jmap.pack")

    if method == SEARCH:
        return pack_search(data, id_num)
    elif method == UPDATE:
        return pack_update(data, id_num)
    elif method == ADD_FILE:
        if filename is None:
            logger.error("Filename is required for ADD_FILE method")
            raise ValueError("Filename is required for ADD_FILE method")
        return pack_add_file(data, id_num, filename)
    else:
        logger.error(f"Unknown method in jmap.pack: {method}")
        raise ValueError(f"Unknown method in jmap.pack: {method}")

def unpack_search(data: List[Union[str, Dict[str, List[str]]]]) -> Tuple[str, List[str], str]:
    if data[0] != SEARCH_METHOD:
        logger.error(f"Invalid method for unpack_search: {data[0]}")
        raise ValueError(f"Invalid method for unpack_search: {data[0]}")

    method, args, id_num = data
    query = args['query']

    return method, query, id_num

def unpack_update(data: List[Union[str, Dict[str, Dict[str, Union[str, List[str]]]], str]]) -> Tuple[str, Dict[str, Union[str, List[str]]], str]:
    if data[0] != UPDATE_METHOD:
        logger.error(f"Invalid method for unpack_update: {data[0]}")
        raise ValueError(f"Invalid method for unpack_update: {data[0]}")

    method, args, id_num = data
    new_index = args['index']

    return method, new_index, id_num

def unpack_add_file(data: List[Union[str, Dict[str, str], str]]) -> Tuple[str, str, str, str]:
    if data[0] != ADD_FILE_METHOD:
        logger.error(f"Invalid method for unpack_add_file: {data[0]}")
        raise ValueError(f"Invalid method for unpack_add_file: {data[0]}")

    method, args, id_num = data
    file_data = args['file']
    filename = args['filename']

    return method, file_data, filename, id_num

def unpack(method: str, data: List[Union[str, Dict[str, Union[str, List[str]]], str]]) -> Union[Tuple[str, List[str], str], Tuple[str, Dict[str, Union[str, List[str]]], str], Tuple[str, str, str, str]]:
    if not method:
        logger.error("Must provide a method to jmap.unpack")
        raise ValueError("Must provide a method to jmap.unpack")
  
    if method == SEARCH:
        return unpack_search(data)
    elif method == UPDATE:
        return unpack_update(data)
    elif method == ADD_FILE: 
        return unpack_add_file(data)
    else:
        logger.error(f"Unknown method in jmap.unpack: {method}")
        raise ValueError(f"Unknown method in jmap.unpack: {method}")

if __name__ == "__main__":
    # Add any code here that should run when the script is executed directly
    pass
