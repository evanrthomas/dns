"""
Query ...
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                      ID                       |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |QR|   Opcode  |AA|TC|RD|RA|   Z    |   RCODE   |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    QDCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    ANCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    NSCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    ARCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                                               |
    /                     QNAME                     /
    /                                               /
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                     QTYPE                     |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                     QCLASS                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

    >>>>>>>>>> HEADER
    ID      to be resent on reply (to keep track of multiple in flight requests
    QR      0=query 1=answer
    OPCODE  0=standard 1=inverse 2=status 3-15=reserved
    AA      authoritative answer?
    TC      truncated? (if length greater than allowed on transmission channel, idk what that means)
    RD      recursuion desired?
    RA      recursion available?
    Z       reserved
    RCODE   response code. 0=No error, 1=formatted wrong (400), 2=server failure (500)
                           3=i'm an authority for this domain name and it doesn't exist (404)
                           4=not implemented
                           5=refused (403)
                           6-15=reserved

    QDCOUNT: #entries in question section
    ANCOUNT: #RR's in answer section
    NSCOUNT: #RR's in authority section
    ARCOUNT: #RR's in additional section
    <<<<<<<<<< HEADER
    >>>>>>>>>> BODY
    QNAME:  something like en.lichess.org. Encoded as i1|e1|i2|e2|i3|e3|null
            where i1 is length of firest label and e1 is first label
    QTYPE:  question type (A record, MX record, zone transfer, *)
    QCLASS: asdfasd
    <<<<<<<<<< BODY

RESP


All RRs have the same top level format shown below:

                                    1  1  1  1  1  1
      0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                                               |
    /                                               /
    /                      NAME                     /
    |                                               |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                      TYPE                     |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                     CLASS                     |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                      TTL                      |
    |                                               |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                   RDLENGTH                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--|
    /                     RDATA                     /
    /                                               /
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+


where:

NAME            an owner name, i.e., the name of the node to which this
                resource record pertains.

TYPE            two octets containing one of the RR TYPE codes.

CLASS           two octets containing one of the RR CLASS codes.

TTL             a 32 bit signed integer that specifies the time interval
                that the resource record may be cached before the source
                of the information should again be consulted.  Zero
                values are interpreted to mean that the RR can only be
                used for the transaction in progress, and should not be
                cached.  For example, SOA records are always distributed
                with a zero TTL to prohibit caching.  Zero values can
                also be used for extremely volatile data.

RDLENGTH        an unsigned 16 bit integer that specifies the length in
                octets of the RDATA field.
"""

import socket
from functools import reduce

concat = lambda arr: reduce(lambda a,b: a + b, arr)
def sample_query():
    ID      = b'\xff\xff'
    junk    = b'\x00\x00'  # doesn't work unless I set RD bit ... why?
    qdcount = b'\x00\x01'
    ancount = b'\x00\x00'
    nscount = b'\x00\x00'
    arcount = b'\x00\x00'
    header  = ID + junk + qdcount + ancount + nscount + arcount


    labels   = ['en', 'lichess', 'org']

    qname    = concat([bytes([len(label)]) + label.encode('utf-8') for label in labels]) + b'\x00'
    qtype    = b'\x00\x01' # for A record
    qclass   = b'\x00\x01' # for (internet class), instead of chaos system ... whatever that means
    question = qname + qtype + qclass

    return header + question

def pprint_header(header):
    ID, info1, info2 = header[:2], header[2], header[3]

    qr = (info1 & 128) >> 7
    opcode = (info1 & (64 + 32 + 16 + 8)) >> 3
    aa = (info1 & 4) >> 2
    tc = (info1 & 2) >> 1
    rd = (info1 & 1) >> 0

    ra = (info2 & 128) >> 7
    rcode = (info2 & (8 + 4 + 2 + 1))

    qdcount = int.from_bytes(header[4:6], byteorder='big')
    ancount = int.from_bytes(header[6:8], byteorder='big')
    nscount = int.from_bytes(header[8:10], byteorder='big')
    arcount = int.from_bytes(header[10:12], byteorder='big')

    print('HEADER')
    print('\tID {}'.format(int.from_bytes(ID, byteorder='big')))
    print('\tqr {}'.format(qr))
    print('\topcode {}'.format(opcode))
    print('\taa {}'.format(aa))
    print('\ttc {}'.format(tc))
    print('\trd {}'.format(rd))
    print('\tra {}'.format(ra))
    print('\trcode {}'.format(rcode))
    print('\tqdcount {}'.format(qdcount))
    print('\tancount {}'.format(ancount))
    print('\tnscount {}'.format(nscount))
    print('\tarcount {}'.format(arcount))


def pprint_body(body):
    print(body)

def pprint(result):
    header, body = result[:12], result[12:]
    pprint_header(header)
    pprint_body(body)
    ID, rest = header[:2], header[2:]

nameserver = 'a.gtld-servers.net' #com nameserver
# nameserver = 'a2.org.afilias-nst.info.' #org nameserver
# nameserver = '8.8.8.8' # google nameserver
# nameserver = '127.0.1.1' # dns forwarder
query = sample_query()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #AF_INET ?? idk SOCK_DGRAM=udp
print('sending ...')
print(query[:2])
print(query[2:4])
print(query[4:])
bytes_sent = sock.sendto(query, (nameserver, 53))
print('size of query {}'.format(len(query)))
print('bytes sent {}'.format(bytes_sent))
result = sock.recv(1024)
pprint(result)
