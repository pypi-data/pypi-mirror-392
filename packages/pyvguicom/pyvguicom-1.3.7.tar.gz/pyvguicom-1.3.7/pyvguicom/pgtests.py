#!/usr/bin/python

# pylint: disable=C0103
# pylint: disable=C0209
# pylint: disable=C0321

import os, sys, getopt, string,  math
import random, time, traceback, stat
import platform, datetime

# Add the new line twice for more balaced string

allcr =    " " + "\r" + "\n" + \
            "\r" + "\n"

allstr =    " " + \
            string.ascii_lowercase +  string.ascii_uppercase +  \
                string.digits

allasc =      string.ascii_lowercase +  string.ascii_uppercase +  \
                string.digits + "_"
alllett =      string.ascii_lowercase +  string.ascii_uppercase
testmode = 0

alllett =   string.ascii_lowercase + string.ascii_uppercase

# ------------------------------------------------------------------------

def randascii(lenx):

    ''' Spew a lot of chars, simulate txt by add ' ' an '\n' '''

    strx = ""
    for aa in range(lenx):
        ridx = random.randint(0x20, 0x7d)
        rr = chr(ridx)
        strx += str(rr)
        if random.randint(0x00, 40) == 30:
            strx += "\n"
        if random.randint(0x00, 12) == 10:
            strx += " "
    return strx

desig = (   "St", "RD", "Valley", "Terrace", "Ave", "Hw",
            "Rd", "Lane", "Alley", "Bvld", "Boulevard",
            "Crest", "Ridge", "Hill", )

def simaddr(lenx):

    strx =  randnumstr(random.randint(2, 5)) + ". "
    strx += randupper(1)
    strx += randlower(random.randint(4, lenx // 2)) + " "

    strx += randupper(1)
    strx += randlower(random.randint(4, lenx // 2)) + " "
    strx += desig[random.randint(0, len(desig)-1)]  + "."

    return strx


def simname(lenx):
    strx = ""
    lenz = len(alllett)-1
    spidx = random.randint(3, lenx - 4)
    ridx = random.randint(0, len(string.ascii_uppercase)-1)
    strx += string.ascii_uppercase[ridx]
    for aa in range(spidx):
        ridx = random.randint(0, len(string.ascii_lowercase)-1)
        rr = string.ascii_lowercase[ridx]
        strx += str(rr)
    strx += " "
    ridx = random.randint(0, len(string.ascii_uppercase)-1)
    strx += string.ascii_uppercase[ridx]
    for aa in range(lenx - spidx):
        ridx = random.randint(0, len(string.ascii_lowercase)-1)
        rr = string.ascii_lowercase[ridx]
        strx += str(rr)
    return strx

def randisodate():
    dd = datetime.datetime.now()
    dd = dd.replace(microsecond=0)
    return dd.isoformat()

def randate():

    ''' Give us a random date in str '''

    dd = datetime.datetime.now()
    dd = dd.replace(year=random.randint(1980, 2024),
                        month=random.randint(1, 12),
                           day=random.randint(1, 28),
                             hour=0, minute=0, second=0, microsecond=0)

    return dd.strftime("%Y/%m/%d")

# ------------------------------------------------------------------------
# Get random str

def randnumstr(lenx):

    strx = ""
    for aa in range(lenx):
        ridx = random.randint(0, len(string.digits)-1)
        rr = string.digits[ridx]
        strx += str(rr)

    return strx

def randphone():

    strx = "1+ " + randnumstr(2)
    strx += " (" + randnumstr(3) + ") "
    strx += randnumstr(3) + " "
    strx += randnumstr(4)

    return strx

def randemail():

    strx =   randlower(random.randint(3, 9))  + "@"
    strx +=  randlower(random.randint(4, 12)) + "."
    strx +=  randlower(random.randint(2, 3))

    return strx

def randstr(lenx):

    strx = ""
    for aa in range(lenx):
        ridx = random.randint(0, len(allstr)-1)
        rr = allstr[ridx]
        strx += str(rr)

    return strx

def randstrrand(lenmin, lenmax):

    lenx = random.randint(lenmin, lenmax)
    strx = ""
    for aa in range(lenx):
        ridx = random.randint(0, len(allstr)-1)
        rr = allstr[ridx]
        strx += str(rr)

    return strx

def randasc(lenx):

    strx = ""
    for aa in range(lenx):
        ridx = random.randint(0, len(allasc)-1)
        rr = allasc[ridx]
        strx += str(rr)

    return strx

def randlett(lenx):

    strx = ""
    for aa in range(lenx):
        ridx = random.randint(0, len(alllett)-1)
        rr = alllett[ridx]
        strx += str(rr)

    return strx

def randlower(lenx):

    strx = ""
    for aa in range(lenx):
        ridx = random.randint(0, len(string.ascii_lowercase)-1)
        rr = string.ascii_lowercase[ridx]
        strx += str(rr)

    return strx

def randupper(lenx):

    strx = ""
    for aa in range(lenx):
        ridx = random.randint(0, len(string.ascii_uppercase)-1)
        rr = string.ascii_uppercase[ridx]
        strx += str(rr)

    return strx


# ------------------------------------------------------------------------
# Random colors

def randcol():
    return random.randint(0, 255)

def randcolstr(start = 0, endd = 255):
    rr =  random.randint(start, endd)
    gg =  random.randint(start, endd)
    bb =  random.randint(start, endd)
    strx = "#%02x%02x%02x" % (rr, gg, bb)
    return strx

# EOF

