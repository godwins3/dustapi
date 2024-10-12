'''
 The MIT License (MIT)

 Copyright (c) 2016 Ian Van Houdt

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
'''


############
#
#  sse_client.py
#
#  Serves as SSE implementation for mail client. The routines 
#  for SSE are invoked by the client module via the API.
#
############

import socket
import os
import sys
sys.path.append(os.path.realpath('../jmap'))
from Crypto.Hash import HMAC
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto import Random
import urllib3
import bcrypt
import binascii
from argparse import ArgumentParser
import string
import anydbm
import json
from flask import Flask
import requests
import jmap
from nltk.stem.porter import PorterStemmer
import email
import re

DEBUG = 1
SEARCH = "search"
UPDATE = "update"
ADD_MAIL = "addmail"

# Default url is localhost, and the port 5000 is set by Flask on the server
DEFAULT_URL = "http://localhost:5000/"

NO_RESULTS = "Found no results for query"

# Some 'Enums' for different options in SEARCH and UPDATE
ENC_BODY = 0
ENC_HEADERS = 1
SRCH_BODY = 0
SRCH_HEADERS = 1

DELIMETER = "++?"

# TODO: Maybe strip out some of the excluded punctuation. Could be useful
# to keep some punct in the strings. We're mostly looking to strip the
# final punct (ie: '.' ',' '!' etc)
EXCLUDE = string.punctuation

app = Flask(__name__)

########
#
# SSE_Client
#
########
class SSE_Client():

    def __init__(self):

        # TODO: placeholder for password. Will eventually take
        # as an arg of some sort
        self.password = b"password"

        # TODO: need to sort out use of salt. Previously, salt was
        # randomly generated in initKeys, but the resulting pass-
        # words k & kPrime were different on each execution, and 
        # decryption was impossible. Hardcoding salt makes dectyption
        # possible but may be a bad short cut
        self.iv = None
        self.salt = "$2b$12$ddTuco8zWXF2.kTqtOZa9O"

        # Two keys, generated/Initialized by KDF
        (self.k, self.kPrime) = self.initKeys()

        # Two K's: generated/initialized by PRF
        self.k1 = None
        self.k2 = None

        # client's cipher (AES w/ CBC)
        self.cipher = self.initCipher()

        # Stemming tool (cuts words to their roots/stems)
        self.stemmer = PorterStemmer()

    def initKeys(self):
        # initialize keys k & kPrime
        # k used for PRF; kPrime used for Enc/Dec
        # return (k, kPrime)

        #hashed = bcrypt.hashpw(self.password, bcrypt.gensalt())
        hashed = bcrypt.hashpw(self.password, self.salt)

        if(DEBUG > 1):
            print("len of k = %d" % len(hashed))
            print("k = %s" % hashed)

        # Currently k and kPrime are equal
        # TODO: Sort out requirements of k and kPrime
        # Research uses both, but not sure the difference
        return (hashed, hashed)


    def initCipher(self):
        # initialize Cipher, using kPrime
        # return new Cipher object

        # TODO: fix key. Currently just a hack: AES keys must be
        # 16, 24 or 32 bytes long, but kPrime is 60
        key = self.kPrime[:16]

        # generates 16 byte random iv
        self.iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CBC, self.iv)

        return cipher


    def encryptMail(self, infile, outfile):

        # read in infile (opened file descriptor)
        buf = infile.read()
        if buf == '': 
            print("[Enc] mail to encrypt is empty!\nExiting\n")
            exit(1)

        if (DEBUG > 1): print("[Enc] mail to encrypt: %s\n" % (buf))

        # pad to mod 16
        while len(buf)%16 != 0:
            buf = buf + "\x08"

        # write encrypted data to new file
        outfile.write(self.iv + self.cipher.encrypt(buf))

    def decryptMail(self, buf, outfile=None):
        # Just pass in input file buf and fd in which to write out

        if buf == '': 
            print("[Dec] mail to decrypt is empty!\nExiting\n")
            exit(1)

        # self.kPrime[:16] is the  first 16 bytes of kPrime, ie: enc key
        # buf[:16] is the iv of encrypted msg
        cipher = AES.new(self.kPrime[:16], AES.MODE_CBC, buf[:16])

        # decrypt all but first 16 bytes (iv)
        # if outfile is supplied, write to file
        if (outfile):
            outfile.write(cipher.decrypt(buf[16:]))
        # else print to terminal
        else:
            tmp = cipher.decrypt(buf[16:])
            print(tmp)


    def encryptMailID(self, k2, document, word=None, index_IDs=None):

        # Encrypt doc id (document) with key passed in (k2)

        # set up new cipher using k2 and random iv
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(k2[:16], AES.MODE_CBC, iv)

        # pad to mod 16
        while len(document)%16 != 0:
            document = document + "\x08"

        # If word and index_IDs are supplied, then we're updated the 
        # existing list of ids for a corresponding word/term.
        # This is used so that we can encrypt a list of mailIDs, rather
        # than just a single one, speeding up SEARCH routine later.
        if word and index_IDs:
            IDs = index_IDs[word]
            IDs = IDs + DELIMETER + document 

            while len(IDs)%16 != 0:
                IDs = IDs + "\x08"

            encId = iv + cipher.encrypt(IDs)

        # Else, encrypt single document (likely meaning it's the first time
        # a particular word has been found in the mail, so the first ID to
        # get added to the index for that word
        else:
            encId = iv + cipher.encrypt(document)

        if (DEBUG > 1):
            print("New ID for '%s' = %s" % 
                 (document, (binascii.hexlify(encId))))

        return binascii.hexlify(encId)


    def update(self, infilename, outfilename):

        # First update index and send it
        data = self.update_index(infilename)
        message = jmap.pack(UPDATE, data, "1")
        r = self.send(UPDATE, message)
        data = r.json()
        results = data['results']
        print("Results of UPDATE: " + results)
        
        # Then encrypt msg
        infile = open(infilename, "r")     
        outfilename_full = "enc_mail/" + outfilename   
        outfile = open(outfilename_full, "w+")
        self.encryptMail(infile, outfile)
        infile.close()
        
        outfile.seek(0)
        data = binascii.hexlify(outfile.read())
        message = jmap.pack(ADD_MAIL, data, "1", outfilename)

        # Then send message
        r = self.send(ADD_MAIL, message, outfilename)        
        data = r.json()
        results = data['results']
        print("Results of UPDATE/ADD FILE: " + results)

        outfile.close()


    def update_index(self, document):

        # Open file, read it's data, and close it
        infile = open(document, "r")
        msg = email.message_from_file(infile)
        infile.close()

        # Parse body of email and return list of words
        word_list = self.parseDocument(msg)

        # Parse headers of email, then extend list of words
        (word_list_extended, header_list) = self.parseHeader(msg)
        word_list.extend(word_list_extended)


        if (DEBUG > 1): print("[Update] Words from doc: " + word_list)

        # Encrypt the index to send to the server (body terms)
        index = self.encryptIndex(document.split("/")[1], word_list,
                                  ENC_BODY)

        # Encrypt index for each header found in message
        for i in header_list:
            index.extend(self.encryptIndex(document.split("/")[1], i,
                                           ENC_HEADERS))

        if (DEBUG > 1):
            print("\n[Client] Printing list elements to add to index")
            for x in index:
                print("%s\n%s\n\n" % (x[0], x[1]))

        return index


    def parseDocument(self, infile):

        # Iterate through email's body, line-by-line, word-by-word,
        # strip unwanted characters, skip duplicates, and add to list
        word_list = None
        for line in email.Iterators.body_line_iterator(infile):
            for word in line.split():
                try:
                    if any(s in EXCLUDE for s in word):
                        word = self.removePunctuation(word)
                        word = self.stemmer.stem(word)
                    word = word.lower()
                    word = word.encode('ascii', 'ignore')
                    if  word not in word_list and '\x08' not in word:
                        word_list.append(word)
                # except catches case of first word in doc, and an
                # empty list cannot be iterated over
                except:
                    if any(s in EXCLUDE for s in word):
                        word = self.removePunctuation(word)
                    word = self.stemmer.stem(word)
                    word = word.lower()
                    word = word.encode('ascii', 'ignore')
                    word_list = [word]

        return word_list


    def parseHeader(self, msg):

        # TODO: need to strip some punctuation, but not all. Email addrs
        # may want to be split on '.' and dates may need some stripping.
        # Currently just adds entirety of header to index
        header_list_standard = []

        # Set up list for each field to be searched. Sloppy, but will get
        # the job done
        header_list = []
        header_list_from = ["from"]
        header_list_sent = ["sent"]
        header_list_date = ["date"]
        header_list_to = ["to"]
        header_list_subject = ["subject"]
        header_list_cc = ["cc"]

        regex = r"[\w']+"

        # Go through each of the specified headers and add the words to the
        # corresponding list, then append each of those lists to the main
        # header list that gets returned (a list of lists, each sub-list 
        # containing data for a particular header, the first term of those
        # lists being the header name).

        for i in ["from", "sent", "date", "to", "subject", "cc"]:
            if msg[i] != None:
                header_list_standard.append(msg[i])

                if i == "from":
                    header_list_from.append(msg[i])
                    tmp = re.findall(regex, msg[i])
                    for j in tmp:
                        if j != "com":
                            header_list_from.append(j)
                            header_list_standard.append(j)
                    header_list.append(header_list_from)

                elif i == "sent":
                    header_list_sent.append(msg[i])
                    tmp = re.findall(regex, msg[i])
                    for j in tmp:
                        header_list_sent.append(j)
                        header_list_standard.append(j)
                    header_list.append(header_list_sent)

                elif i == "date":
                    header_list_date.append(msg[i])
                    tmp = re.findall(regex, msg[i])
                    for j in tmp:
                        header_list_date.append(j)
                        header_list_standard.append(j)
                    header_list.append(header_list_date)

                elif i == "to":
                    header_list_to.append(msg[i])
                    tmp = re.findall(regex, msg[i])
                    for j in tmp:
                        if j != "com":
                            header_list_to.append(j)
                            header_list_standard.append(j)
                    header_list.append(header_list_to)

                elif i == "subject":
                    header_list_subject.append(msg[i])
                    tmp = re.findall(regex, msg[i])
                    for j in tmp:
                        header_list_subject.append(j)
                        header_list_standard.append(j)
                    header_list.append(header_list_subject)

                elif i == "cc":
                    header_list_cc.append(msg[i])
                    tmp = re.findall(regex, msg[i])
                    for j in tmp:
                        if j != "com": 
                            header_list_cc.append(j)
                            header_list_standard.append(j)
                    header_list.append(header_list_cc)

        if (DEBUG > 1):
            print(header_list_standard)
            print(header_list)
        return (header_list_standard, header_list)


    def removePunctuation(self, string):
        return ''.join(ch for ch in string if ch not in EXCLUDE)


    def encryptIndex(self, document, word_list, TYPE):

        # This is where the meat of the SSE update routine is implemented

        if (DEBUG > 1): 
            print("Encrypting index of words in '%s'" % document)

        L = []
        index = anydbm.open("index", "c")
        index_IDs = anydbm.open("index_IDs", "c")
       
        # For each word, look through local index to see if it's there. If
        # not, set c = 0, and apply the PRF. Otherwise c == number of 
        # occurences of that word/term/number 

        for w in word_list:

            # Initialize K1 and K2
            k1 = self.PRF(self.k, ("1" + w))
            k2 = self.PRF(self.k, ("2" + w))

            # If TYPE == ENC_HEADERS, we're parsing a header list. [0] 
            # will be type of header, which we'll use to disguise the 
            # words of the header (instead of c).  Also, pass over if on 
            # first iteration of list, because that will just be the type
            # of header (see parseHeader()).
            if TYPE == ENC_HEADERS:
                header = word_list[0]
                if w == header:
                    continue

            if (DEBUG > 1): print("k1 = %s\nk2 = %s\n" % (k1, k2))

            # counter "c" (set as 0 if not in index), otherwise set
            # as number found in index (refers to how many documents
            # that word appears in
            c = 0
            found = 0
            try:
                c = int(index[w])
                found = 1
                if (DEBUG > 1): 
                    print("Found '%s' in db. C = %d" % (w, c))
            except:
                c = 0
 
            # Set l as the PRF of k1 (1 || w) and c (num of occur) if 
            # parsing the body (ENC_BODY).
            # If parsing header list, then PRF k1 and header term.
            if TYPE == ENC_BODY:
                l = self.PRF(k1, str(c))
                lprime = self.PRF(k1, str(c-1))
            else:
                l = self.PRF(k1, header)
                lprime = None

            # Update encryptMailID() opens index_IDs and appends
            # new document to list with DELIMETER and encrypts all.
            # Set d as encrypted mail id [list]
            if not found:
                d = self.encryptMailID(k2, document)
            else:
                d = self.encryptMailID(k2, document, w, index_IDs)

            if (DEBUG > 1):
                print("w = " + w + "\tc = " + str(c))
                print("l = %s\nd = %s\n" % (l, d))

            # Increment c (1 indexed, not 0), then add unecrypted
            # values to local index, and append encrypted/hashed
            # values to L, the list that will extend the remote index
            c = c + 1
            if TYPE == ENC_BODY:
                index[w] = str(c)
                if found:
                    IDs = index_IDs[w]
                    if document not in IDs.split(DELIMETER):
                        index_IDs[w] = IDs + DELIMETER + document
                else:
                    index_IDs[w] = document
            else:
                index[w] = str(c) + ":" + header

            L.append((l, d, lprime))

        index.close()
        index_IDs.close()

        return L


    def search(self, query, header=None, TYPE=SRCH_BODY):

        index = anydbm.open("index", "r")
        query = query.split()

        # Generate list of querys (may be just 1)
        L = []
        for i in query:
            if (DEBUG > 1): print(repr(i))
            i = i.lower()

            # For each term of query, first try to see if it's already in
            # index. If it is, send c along with k1 and k2. This will 
            # massively speed up search on server (1.5 minutes to < 1 sec)
            try:
                c = index[i]
            except:
                c = None

            # Use k, term ('i') and '1' or '2' as inputs to a pseudo-random
            # function to generate k1 and k2. K1 will be used to find the 
            # correct encrypted entry for the term on the server, and k2
            # will be used to decrypt the mail ID(s)
            k1 = self.PRF(self.k, ("1" + i))
            k2 = self.PRF(self.k, ("2" + i))

            # If no 'c' (term not in local index so likely not on server),
            # just send k1 and k2. Will take a long time to return false
            # TODO, should the client just kill any search for a term not
            # in local index?  Can we rely on the local index always being
            # up to date?
            if not c:
                L.append((k1, k2))
            # Otherwise send along 'c'-1. 
            else:
                c = str(int(c)-1)
                L.append((k1, k2, c))

            if (DEBUG > 1): 
                print("k1 = " + k1)
                print("k2 = " + k2)

        # FIXME: Don't like the additions made for searching headers
        if TYPE == SRCH_HEADERS:
            Lprime = [header]
            Lprime.extend(L)
            message = jmap.pack(SEARCH, Lprime, "1") 

        else:
            message = jmap.pack(SEARCH, L, "1")

        # Send data and unpack results.
        r = self.send(SEARCH, message) 
        ret_data = r.json()
        results = ret_data['results']
        print("Results of SEARCH:")

        if results == NO_RESULTS:
            print(results)
            return -1

        # Print out messages that are returned from server
        # TODO: Should recieve and print out mail, or just recieve mailIDs
        # and resend requests for those messages?

        # FIXME: hack to decide if server is returning encrypted msgs (1)
        # or just the decrypted IDs (0)
        FILES = 1
        for i in results:
            if (FILES):
                self.decryptMail(binascii.unhexlify(i), )
            else: 
                print(i)


    def PRF(self, k, data):
        hmac = HMAC.new(k, data, SHA256)
        return hmac.hexdigest()


    def send(self, routine, data, filename = None, in_url = DEFAULT_URL):

        url = in_url

        # Currently, each server url is just <IP>/<ROUTINE>, so just append
        # routine to url, and set up headers with jmap package.

        if routine == SEARCH:
            url = url + SEARCH
            headers = jmap.jmap_header()
        elif routine == UPDATE:
            url = url + UPDATE
            headers = jmap.jmap_header()
        elif routine == ADD_MAIL:
            url = url + ADD_MAIL
            # For sending mail, need to do a little extra with the headers
            headers = {'Content-Type': 'application/json',
                       'Content-Disposition': 
                       'attachment;filename=' + filename}
        else:
            print("[Client] Error: bad routine for send()")
            exit(1)

        if (DEBUG > 1): 
            print(url)
            print(data)

        # Send to server using requests's post method, and return results
        # to calling method
        return requests.post(url, data, headers = headers)


    def testSearch(self, index):
        '''
        Method for testing locally if the encryption in the update
        routine is actually accurate. 
        -create a static search term (ie: "the")
        -generate hashes with self.k (ie generate k1 and k2)
        -implement the backend get() and dec() methods to see if they
         return the correct data
        -try with search query that isn't in index
        '''

        # 'Client' activities
        query = "This"
        k1 = self.PRF(self.k, ("1" + query))
        k2 = self.PRF(self.k, ("2" + query))

        if (DEBUG > 1): 
            print("[testSearch]\nk1:%s\nk2:%s" % (k1, k2))

        # 'Server' activities
        c = 0
        found = 0
        while c < len(index):
            if (DEBUG): print("c = " + str(c))
            result = self.testGet(index, k1, c)
            if result: break
            c = c + 1

        if not result:
            print("NOT FOUND in INDEX")

        else:
            print("FOUND RESULT")


    def testGet(self, index, k, c):

        cc = 0
        while cc < len(index):
            F = self.PRF(k, str(c))
            if (DEBUG > 1):
                print("[Get] F: " + F)
                print("[Get] Idx: " + index[cc][0] + "\n")
            if F == index[cc][0]:
                return F
            cc = cc + 1



def main():

    # Set-up a command-line argument parser

    # TODO: Fix argument parser. It works for what it is, but I don't 
    # have a good enough grasp of the argparser package to fine tune it 
    # ie: some options shouldnt require an argument but do (ie: '-i' 
    # should be a standalone option, but currently requires a following,
    # unused argument

    parser = ArgumentParser()
    parser.add_argument('-s', '--search', metavar='search', dest='search',
                        nargs='*')
    parser.add_argument('-S', '--search-header', metavar='search_header', 
                        dest='search_header', nargs=2)
    parser.add_argument('-u', '--update', metavar='update', dest='update',
                        nargs=1)
    parser.add_argument('-e', '--encrypt', metavar='encrypt_file', 
                        dest='encrypt_file', nargs=2)
    parser.add_argument('-d', '--decrypt', metavar='decrypt_file',
                        dest='decrypt_file', nargs=2)
    parser.add_argument('-i', '--inspect_index', dest='inspect_index')
    parser.add_argument('-t', '--test_http', dest='test_http')
    args = parser.parse_args()
 
    sse = SSE_Client()

    if args.encrypt_file:
        if (DEBUG): 
            print("Encrypting %s\nOutput %s\n"
            % (args.encrypt_file[0], args.encrypt_file[1]))

        infile = open(args.encrypt_file[0], "r")        
        outfile = open(args.encrypt_file[1], "w+")

        sse.encryptMail(infile, outfile)

        infile.close()
        outfile.close()

    elif args.decrypt_file:
        if (DEBUG): 
            print("Decrypting %s\nOutput %s" 
            % (args.decrypt_file[0], args.decrypt_file[1]))

        infile = open(args.decrypt_file[0], "r")
        buf = infile.read()
        outfile = open(args.decrypt_file[1], "w+")

        sse.decryptMail(buf, outfile)

        infile.close()
        outfile.close()

    elif args.update:
        if (DEBUG):
            print("Updating index with document %s" % args.update[0])

        infilename = args.update[0]
        outfilename = args.update[0].split("/")[1]
        sse.update(infilename, outfilename)

    elif args.search:
        if (DEBUG):
           print("Searching remote index for word(s): '%s'" 
                  % args.search[0])

        sse.search(args.search[0])

    elif args.search_header:
        if (DEBUG):
           print("Searching remote index for word(s):'%s' in header: '%s'" 
                  % (args.search_header[1], args.search_header[0]))

        query = args.search_header[1]
        header = args.search_header[0].lower()
        sse.search(query, header, SRCH_HEADERS)

    elif args.inspect_index:
        if (DEBUG): print("Inspecting the index")
        index = anydbm.open("index", "r")
        for k, v in index.iteritems():
            print("k:%s\tv:%s" % (k, v))

        index.close()

        index = anydbm.open("index_IDs", "r")
        for k, v in index.iteritems():
            print("k:%s\tv:%s" % (k, v))

        index.close()

    elif args.test_http:
        url = "http://localhost:5000/search"
        k1 = "c18d3a0d0a6278ee206447b13cbb46f182c7bb5d038398887a9506e673a1c016"
        k2 = "ccb215ad2018660ad49668bca3c7f4222dc737f2346bf9853d06917d77771655"
        k = []
        k.append(k1)
        k.append(k2)
        #values = { 'k1' : k1, 'k2' : k2 }
        values = { 'query' : k }
        data = urllib3.urlencode(values)
        req = urllib3.Request(url, data)  
        response = urllib3.urlopen(req)
        data = response.read()
        print(data)

    else:
        print("Must specify a legitimate option")
        exit(1)


if __name__ == "__main__":
    main()