#!/usr/bin/python

# pylint: disable=C0103
# pylint: disable=C0209
# pylint: disable=C0321

import os, sys, time #, getopt, string,  math
#import random, traceback, stat
#import platform

''' General utility fiunctions '''

if sys.version_info.major < 3:
    pass
else:
    #import inspect
    #if inspect.isbuiltin(time.process_time):
    if not hasattr(time, "clock"):
        #print("updating time.clock()")
        time.clock = time.process_time

# ------------------------------------------------------------------------
# Resolve path name

def respath(fname):

    try:
        ppp = str.split(os.environ['PATH'], os.pathsep)
        for aa in ppp:
            ttt = aa + os.sep + fname
            if os.path.isfile(str(ttt)):
                return ttt
    except:
        print ("Cannot resolve path", fname, sys.exc_info())
    return None

# ------------------------------------------------------------------------
# Color conversions

def str2col(strx):
    ccc = str2float(strx)
    return float2col(ccc)

def str2float( col):
    return ( float(int(col[1:3], base=16)) / 256,
                    float(int(col[3:5], base=16)) / 256, \
                        float(int(col[5:7], base=16)) / 256 )

def float2col(col):
    aa = min(col[0], 1.)
    bb = min(col[1], 1.)
    cc = min(col[2], 1.)
    return Gdk.Color(aa * 65535, bb * 65535, cc * 65535)

def float2str(col):
    aa = min(col[0], 1.)
    bb = min(col[1], 1.)
    cc = min(col[2], 1.)
    strx = "#%02x%02x%02x" % (aa * 256,  \
                        bb * 256, cc * 256)
    return strx

def col2float(col):
    rrr = [float(col.red) / 65535,
            float(col.green) / 65535,
                float(col.blue) / 65535]
    return rrr

def rgb2str(icol):
    strx = "#%02x%02x%02x" % (int(icol.red) & 0xff,  \
                        int(icol.green) & 0xff, int(icol.blue) & 0xff)
    return strx

def col2str(icol):
    strx = "#%02x%02x%02x" % (int(icol.red / 255),  \
                        int(icol.green / 255), int(icol.blue / 255))
    return strx

def rgb2col(icol):
    #print "rgb2col", icol
    col = [0, 0, 0]
    col[0] = float(icol.red) / 256
    col[1] = float(icol.green) / 256
    col[2] = float(icol.blue) / 256
    return col

def put_debug2(xstr):
    try:
        if os.isatty(sys.stdout.fileno()):
            print( xstr)
        else:
            #syslog.syslog(xstr)
            pass
            print(xstr, file=sys.stderr)

    except:
        print( "Failed on debug output.")
        print( sys.exc_info())

def put_exception(xstr):

    cumm = xstr + " "
    a,b,c = sys.exc_info()
    if a != None:
        cumm += str(a) + " " + str(b) + "\n"
        try:
            #cumm += str(traceback.format_tb(c, 10))
            ttt = traceback.extract_tb(c)
            for aa in ttt:
                cumm += "File: " + os.path.basename(aa[0]) + \
                        "  Line: " + str(aa[1]) + "\n" +  \
                        "    Context: " + aa[2] + " -> " + aa[3] + "\n"
        except:
            print( "Could not print trace stack. ", sys.exc_info())

    print(cumm)
    #syslog.syslog("%s %s %s" % (xstr, a, b))

def decode_bits(numx):
    mask = 0x80
    retx = ""
    for aa in range(8):
        strx = "0"
        if numx & mask:
            strx = "1"
        retx += "B%d=%s  " % (7-aa, strx)
        if aa == 3:
            retx += "\r"
        mask >>= 1

    return retx

# ------------------------------------------------------------------------
# Remove non printables

def clean_str(strx):

    stry = ""
    for aa in range(len(strx)):
        if strx[aa] == '\r':
            stry += "\\r"
        elif strx[aa] == '\n':
            stry += "\\n"
        elif strx[aa] == '\0':
            stry += "\\0"
        else:
            stry += strx[aa]
    return stry

def clean_str2(strx):
    stry = ""
    skip = False
    for aa in range(len(strx)):
        if skip:
            skip = False
            continue
        if strx[aa] == '\\' and strx[aa+1] == 'r':
            skip = True
        if strx[aa] == '\\' and strx[aa+1] == 'n':
            skip = True
        if strx[aa] == '\\' and strx[aa+1] == '0':
            skip = True
            pass
        else:
            stry += strx[aa]
    return stry

# This is crafted to Py2 so has clock with the same name

start_time = time.clock()

def  get_time():

    global start_time
    if sys.version_info.major < 3:
        return time.clock()  - start_time
    else:
        return time.process_time()

def get_realtime():

    frac = math.modf(float(get_time()))
    zzz = "%.02f" % frac[0]
    sss = "%s%s" % (time.strftime("%02I:%02M:%02S"), zzz[1:])
    return sss

# Get a list of ports

'''
def serial_ports():

    """ Lists serial port names
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """

    ports = []
    if sys.platform.startswith('win'):
        ports2 = serial.tools.list_ports.comports()
        for aa in ports2:
            ports.append(aa[0])
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/ttyU[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        # rely on serial module
        ports2 = serial.tools.list_ports.comports()
        for aa in ports2:
            ports.append(aa[0])
        #raise EnvironmentError('Unsupported platform')

    #print ("ports", ports)
    result = []
    for port in ports:
        try:
            # no testing performed any more
            #s = serial.Serial(port)
            #s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    #print ("result", result)
    return result
'''

# ------------------------------------------------------------------------
# Convert octal string to integer

def oct2int(strx):
    retx = 0
    for aa in strx:
        num = ord(aa) - ord("0")
        if num > 7 or num < 0:
            break
        retx <<= 3; retx += num
    #print "oct:", strx, "int:", retx
    return retx

# ------------------------------------------------------------------------
# Convert unicode sequence to unicode char

def uni(xtab):

    #print str.format("{0:b}",  xtab[0])
    try:
        unichr
    except NameError:
        unichr = chr

    cc = 0
    try:
        if xtab[0] & 0xe0 == 0xc0:  # two numbers
            cc = (xtab[0] & 0x1f) << 6
            cc += (xtab[1] & 0x3f)
        elif xtab[0] & 0xf0 == 0xe0: # three numbers
            cc = (xtab[0] & 0x0f) << 12
            cc += (xtab[1] & 0x3f) << 6
            cc += (xtab[2] & 0x3f)
        elif xtab[0] & 0xf8 == 0xf0: # four numbers
            cc = (xtab[0] & 0x0e)  << 18
            cc += (xtab[1] & 0x3f) << 12
            cc += (xtab[2] & 0x3f) << 6
            cc += (xtab[3] & 0x3f)
        elif xtab[0] & 0xfc == 0xf8: # five numbers
            cc = (xtab[0] & 0x03)  << 24
            cc += (xtab[1] & 0x3f) << 18
            cc += (xtab[2] & 0x3f) << 12
            cc += (xtab[3] & 0x3f) << 6
            cc += (xtab[4] & 0x3f)
        elif xtab[0] & 0xfe == 0xf8: # six numbers
            cc = (xtab[0] & 0x01)  << 30
            cc += (xtab[1] & 0x3f) << 24
            cc += (xtab[2] & 0x3f) << 18
            cc += (xtab[3] & 0x3f) << 12
            cc += (xtab[4] & 0x3f) << 6
            cc += (xtab[5] & 0x3f)

        ccc = unichr(cc)
    except:
        pass

    return ccc

def is_ascii(strx):

    pos = 0; lenx = len(strx)
    while True:
        if pos >= lenx:
            break

        chh = strx[pos]
        #print (ord(chh))
        if ord(chh) > 127:
            #print (ord(chh))
            if pos == 0: pos += 1
            return pos
        pos+= 1

    return 0

def kill_non_ascii(strx):

    str2 = ""
    pos = 0; lenx = len(strx)
    while True:
        if pos >= lenx:
            break

        chh = strx[pos]
        #print (ord(chh))
        if ord(chh) <= 127:
            str2 += chh
        else:
            str2 += "*"
        pos+= 1

    return str2

# ------------------------------------------------------------------------
# Unescape unicode into displayable sequence

xtab = []; xtablen = 0

def unescape(strx):

    #print " x[" + strx + "]x "

    global xtab, xtablen
    retx = u""; pos = 0; lenx = len(strx)

    while True:
        if pos >= lenx:
            break

        chh = strx[pos]

        if chh == '\\':
            #print "backslash", strx[pos:]
            pos2 = pos + 1; strx2 = ""
            while True:
                if pos2 >= lenx:
                    # See if we accumulated anything
                    if strx2 != "":
                        xtab.append(oct2int(strx2))
                    if len(xtab) > 0:
                        #print "final:", xtab
                        if xtablen == len(xtab):
                            retx += uni(xtab)
                            xtab = []; xtablen = 0
                    pos = pos2 - 1
                    break
                chh2 = strx[pos2]
                if chh2  >= "0" and chh2 <= "7":
                    strx2 += chh2
                else:
                    #print "strx2: '"  + strx2 + "'"
                    if strx2 != "":
                        octx = oct2int(strx2)
                        if xtablen == 0:
                            if octx & 0xe0 == 0xc0:
                                #print "two ",str.format("{0:b}", octx)
                                xtablen = 2
                                xtab.append(octx)
                            elif octx & 0xf0 == 0xe0: # three numbers
                                #print "three ",str.format("{0:b}", octx)
                                xtablen = 3
                                xtab.append(octx)
                            elif octx & 0xf8 == 0xf0: # four numbers
                                print("four ",str.format("{0:b}", octx))
                                xtablen = 4
                                xtab.append(octx)
                            elif octx & 0xfc == 0xf8: # five numbers
                                print("five ",str.format("{0:b}", octx))
                                xtablen = 5
                                xtab.append(octx)
                            elif octx & 0xfe == 0xfc: # six numbers
                                print("six ",str.format("{0:b}", octx))
                                xtablen = 6
                                xtab.append(octx)
                            else:
                                #print "other ",str.format("{0:b}", octx)
                                #retx += unichr(octx)
                                retx += chr(octx)
                        else:
                            xtab.append(octx)
                            #print "data ",str.format("{0:b}", octx)
                            if xtablen == len(xtab):
                                retx += uni(xtab)
                                xtab = []; xtablen = 0

                    pos = pos2 - 1
                    break
                pos2 += 1
        else:

            if xtablen == len(xtab) and xtablen != 0:
                retx += uni(xtab)
            xtab=[]; xtablen = 0

            try:
                retx += chh
            except:
                pass
        pos += 1

    #print "y[" + retx + "]y"
    return retx

# ------------------------------------------------------------------------
# Give the user the usual options for true / false - 1 / 0 - y / n

def isTrue(strx):
    if strx == "1": return True
    if strx == "0": return False
    uuu = strx.upper()
    if uuu == "TRUE": return True
    if uuu == "FALSE": return False
    if uuu == "Y": return True
    if uuu == "N": return False
    return False

# ------------------------------------------------------------------------
# Return True if file exists

def isfile(fname):

    try:
        ss = os.stat(fname)
    except:
        return False

    if stat.S_ISREG(ss[stat.ST_MODE]):
        return True
    return False

def put_exception2_old(xstr):

    cumm = xstr + " "
    a,b,c = sys.exc_info()
    if a != None:
        cumm += str(a) + " " + str(b) + "\n"
        try:
            #cumm += str(traceback.format_tb(c, 10))
            ttt = traceback.extract_tb(c)
            for aa in ttt:
                cumm += "File: " + os.path.basename(aa[0]) + \
                        " Line: " + str(aa[1]) + "\n" +  \
                    "   Context: " + aa[2] + " -> " + aa[3] + "\n"
        except:
            print( "Could not print trace stack. ", sys.exc_info())

    put_debug2(cumm)
    #syslog.syslog("%s %s %s" % (xstr, a, b))

# Create a one way hash of a name. Not cryptographically secure,
# but it can make a good unique name in hex.

def hash_name(strx):

    lenx = len(strx);  hashx = int(0)
    for aa in strx:
        bb = ord(aa)
        hashx +=  int((bb << 12) + bb)
        hashx &= 0xffffffff
        hashx = int(hashx << 8) + int(hashx >> 8)
        hashx &= 0xffffffff

    return "%x" % hashx

# Expand tabs in string
def untab_str(strx, tabstop = 4):
    res = ""; idx = 0; cnt = 0
    xlen = len(strx)
    while True:
        if idx >= xlen: break
        chh = strx[idx]
        if  chh == "\t":
            # Generate string
            spaces = tabstop - (cnt % tabstop)
            ttt = ""
            for aa in range(spaces):
                ttt += " "
            res += ttt
            cnt += spaces
        else:
            cnt += 1
            res += chh
        idx += 1
    return res

# ------------------------------------------------------------------------
# Get am pm version of a number

def ampmstr(bb):

    dd = "AM"
    if bb == 12:
        dd = "PM"
    elif bb > 12:
        bb -= 12
        dd = "PM"
    return "%02d %s" % (bb, dd)

# ------------------------------------------------------------------------
# Let the higher level deal with errors.

def  readfile(strx, sep = None):

    text = []

    if strx == "":
        return text

    # Now read and parse
    f = open(strx, "rb");  buff2 = f.read();  f.close()
    if sys.version_info.major < 3:
        buff = buff2
    else:
        try:
            buff = buff2.decode('UTF-8')
        except UnicodeDecodeError:
            buff = buff2.decode('cp437')

    buff2 = ""

    if not sep:
        # Deteremine separator, use a partial length search
        if buff.find("\r\n", 0, 300) >= 0:
            sep = "\r\n"
        elif buff.find("\n\r", 0, 300) >= 0:
            sep = "\n\r"
        elif buff.find("\r", 0, 300) >= 0:
            sep = "\r"
        else:
            sep = "\n"

    text2 = str.split(buff, sep)

    #if "Makefile" in strx:
    #    print(strx, "sep: '"+ sep + "'", ord(sep[0]), ord(sep[1]))

    # Clean out spuriously occurring \r and \n
    # Example: ST Microelectronics Makefiles

    text = []
    for aa in text2:
        #print("'%s\n" % aa)
        bb = aa.replace("\r", "")
        cc = bb.replace("\n", "")
        text.append(cc)
    #text2 = []

    return text

# -----------------------------------------------------------------------
# Call func with all processes, func called with stat as its argument
# Function may return True to stop iteration

def withps(func, opt = None):

    ret = False
    dl = os.listdir("/proc")
    for aa in dl:
        fname = "/proc/" + aa + "/stat"
        if os.path.isfile(fname):
            ff = open(fname, "r").read().split()
            ret = func(ff, opt)
        if ret:
            break
    return ret

# ------------------------------------------------------------------------
# Print( an exception as the system would print it)

def print_exception(xstr):
    cumm = xstr + " "
    a,b,c = sys.exc_info()
    if a != None:
        cumm += str(a) + " " + str(b) + "\n"
        try:
            #cumm += str(traceback.format_tb(c, 10))
            ttt = traceback.extract_tb(c)
            for aa in ttt:
                cumm += "File: " + os.path.basename(aa[0]) + \
                        " Line: " + str(aa[1]) + "\n" +  \
                    "   Context: " + aa[2] + " -> " + aa[3] + "\n"
        except:
            print("Could not print trace stack. ", sys.exc_info())
    print( cumm)

# -----------------------------------------------------------------------
# Sleep just a little, but allow the system to breed

if sys.version_info[0] < 3 or \
    (sys.version_info[0] == 3 and sys.version_info[1] < 3):
    timefunc = time.clock
else:
    timefunc = time.process_time

# ------------------------------------------------------------------------
# Create temporary file, return name. Empty string ("") if error.

def tmpname(indir, template):

    fname = ""
    if not os.access(indir, os.W_OK):
        print( "Cannot access ", indir)
        return fname

    cnt = 1
    while True:
        tmp = indir + "/" + template + "_" + str(cnt)
        if not os.access(tmp, os.R_OK):
            fname = tmp
            break
        # Safety valve
        if cnt > 10000:
            break
    return fname

class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def writelines(self, datas):
        self.stream.writelines(datas)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)

# Time to str and str to time

def time_n2s(ttt):
    sss = time.ctime(ttt)
    return sss

def time_s2n(sss):
    rrr = time.strptime(sss)
    ttt = time.mktime(rrr)
    return ttt


# ------------------------------------------------------------------------

def leadspace(strx):

    ''' Count lead spaces '''

    cnt = 0
    for aa in range(len(strx)):
        bb = strx[aa]
        if bb == " ":
            cnt += 1
        elif bb == "\t":
            cnt += 1
        elif bb == "\r":
            cnt += 1
        elif bb == "\n":
            cnt += 1
        else:
            break
    return cnt

if __name__ == '__main__':
    print("This file was not meant to run directly")

# EOF
