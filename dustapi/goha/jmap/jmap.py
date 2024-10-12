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

FILE = "[JMAP] "
SEARCH = "search"
UPDATE = "update"
ADD_FILE = "addmail"
SEARCH_METHOD = "getEncryptedMessages"
UPDATE_METHOD = "updateEncryptedIndex"
ADD_FILE_METHOD = "putEncryptedMessage"

JMAP_HEADER = {'Content-Type': 'application/json'} 

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

def jmap_header():
    return JMAP_HEADER

def pack_search(data, id_num):
    return json.dumps([SEARCH_METHOD, {"query": data}, id_num])

def pack_update(data, id_num):
    return json.dumps([UPDATE_METHOD, {"index": data}, id_num])

def pack_add_file(data, id_num, filename):
    return json.dumps([ADD_FILE_METHOD, {"file": data, "filename": filename}, id_num])

def pack(METHOD, data, id_num, filename=None):
    FUNC = "jmap.pack"
    message = None

    if not METHOD:
        print(FILE + "Must provide a method to " + FUNC)
        return -1

    if METHOD == SEARCH:
        message = pack_search(data, id_num)

    elif METHOD == UPDATE:
        message = pack_update(data, id_num)

    elif METHOD == ADD_FILE:
        message = pack_add_file(data, id_num, filename)

    else:
        print(FILE + "Unknown METHOD in " + FUNC)
        return -1

    return message

def unpack_search(data):

    if data[0] != SEARCH_METHOD:
        return -1

    method = data[0]
    id_num = data[2]

    # Limit scope to args (data[1])
    data = data[1]
    query = data['query']

    return (method, query, id_num)


def unpack_update(data):
    
    if data[0] != UPDATE_METHOD:
        return -1

    method = data[0]
    id_num = data[2]

    # Limit scope to args (data[1])
    data = data[1]
    new_index = data['index']

    return (method, new_index, id_num)

def unpack_add_file(data):

    if data[0] != ADD_FILE_METHOD:
        return -1

    method = data[0]
    id_num = data[2]

    # Limit scope to args (data[1])
    data = data[1]

    file = data['file']
    filename = data['filename']

    return (method, file, filename, id_num)

def unpack(METHOD, data):
    FUNC = "jmap.unpack"

    if not METHOD:
        print(FILE + "Must provide a method to " + FUNC)
        return -1
  
    if METHOD == SEARCH:
        return unpack_search(data)
    elif METHOD == UPDATE:
        return unpack_update(data)
    elif METHOD == ADD_FILE: 
        return unpack_add_file(data)
    else:
        print(FILE + "Unknown METHOD in " + FUNC)
        return -1

