#!/usr/bin/env python
# Copyright 2011 Red Hat Inc.
# Author: Kushal Das <kdas@redhat.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

import os
import sys
import stat
import MySQLdb
import tempfile
import subprocess
import ConfigParser
from struct import unpack
from optparse import OptionParser

# FILE_TYPE constants help identify the file type, and serve as index
# into the TYPES list below.
FILE_REL  = 1
FILE_EXEC = 2
FILE_DSO  = 3
FILE_CORE = 4

FILE_DIR  = 5
FILE_LINK = 6
FILE_GZ   = 7
FILE_BZ   = 8
FILE_RPM  = 9

# List of file types used for verbose output.
TYPES = [None, "REL", "EXEC", "DSO", "CORE", \
          "DIR", "SYMLINK", "GZ", "BZ", "RPM"]


def filetype(path):
    """
    filetype: reads the first few bytes from - path - and tries to identify
    the file type. At present it can identify an ELF executable, shared object
    and symbolic link files.
    """

    if(not path):
        return 0

    filed = os.lstat(path)
    if (stat.S_ISDIR(filed.st_mode)):
        return FILE_DIR
    elif (stat.S_ISLNK(filed.st_mode)):
        return FILE_LINK
    elif (not stat.S_ISREG(filed.st_mode)):
        return 0

    try:
        filed = open(path, "rb")
    except IOError:
        return 0
    
    stream = filed.read(16)
    if (stream[:4] == "\x7FELF"):
        stream = filed.read(2)
        stream = unpack('h', stream)[0]
    elif (stream[:4] == 'BZh9'):
        stream = FILE_BZ
    elif (stream[:4] == '\x1F\x8B\x08\x00'):
        stream = FILE_GZ
    elif (stream[:4] == '\xED\xAB\xEE\xDB'):
        stream = FILE_RPM
    else:
        stream = 0

    filed.close()
    return stream

def get_elf_files(files):
    """
    Takes file list as input and returns ELF files among them as list.
    """
    elfs = []
    for filename in files:
        if os.path.exists(filename):
            if filetype(filename) in \
                    [FILE_REL, FILE_EXEC, FILE_DSO, \
                         FILE_CORE]:
                elfs.append(filename)
    return elfs

def removedir(dname):
    """
    removedir: forcefully removes the given directory.
    """

    if (not dname):
        return 0

    if (os.path.islink(dname) or not os.path.isdir(dname)):

        try:
            os.unlink(dname)
        except Exception, error:
            print >> sys.stderr, "could not unlink file:", error

        return 0

    for dirname in os.listdir(dname):
        removedir(os.path.join(dname, dirname))

    try:
        os.rmdir(dname)
    except Exception, error:
        print >> sys.stderr, "could not remove dir:", error

    return 0


def system(cmd):
    """ 
    Invoke a shell command. Primary replacement for os.system calls.
    """

    if (not cmd):
        return 0, None, None

    ret = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    out, err = ret.communicate()

    return ret.returncode, out, err 


def parserpm(path, config, distro="fedora"):
    """
    parse the rpm and insert data into database
    """
    filename = os.path.basename(path)

    try:
        #Find all db config 
        dbhost = config.get('darkserver','host')
        dbuser =  config.get('darkserver','user')
        dbpassword = config.get('darkserver','password')
        dbname =  config.get('darkserver','database')
    except Exception, error:
        print "Please setup the database config file first at /etc/darkserver"
        return
    
    try:
        conn = MySQLdb.connect (host = dbhost,
                                user = dbuser,
                                passwd = dbpassword,
                                db = dbname)
    except Exception, error:
        print error.message
        return
    cursor = conn.cursor ()
    
    #Create the temp dir
    destdir = tempfile.mkdtemp(suffix='.' + str(os.getpid()), dir=None)

    #Extract the rpm
    cmd = 'rpmdev-extract -C %s %s' % (destdir, path)
    code, datum, err = system(cmd)
    data = datum.split('\n')
    
    #Find out all elf files from the list
    files = [os.path.join(destdir, row) for row in data]
    elffiles = get_elf_files(files)
    
    #Return if ELF file found in the RPM
    if not elffiles:
        return
    
    #Find the lenth of the destdir name
    dest_len = len(destdir)
    
    #run eu-unstrip and parse the result
    for eachfile in elffiles:
        code, data, err = system("eu-unstrip -n -e %s" % eachfile)
        try:
            name = eachfile[dest_len+1:]
            dirname = "/" + '/'.join(os.path.dirname(name).split('/')[1:])
            sql = "INSERT INTO dark_gnubuildid VALUES"\
                  " (null, '%s','%s','%s','%s','%s')"
            sql = sql % (os.path.basename(name), dirname, \
                         data.split(' ')[1].split('@')[0], \
                         filename[:-4], distro)

            cursor.execute(sql)
        except Exception, error:
            print error
    removedir(destdir)
    conn.commit()
    


def main(args):
    """
    Main function
    """
    parser = OptionParser()
    parser.add_option("-r", "--rpm", dest="rpm",
                          help="path to the rpm file")
    
    parser.add_option("-d", "--distro", dest="distro",
                          help="distro name")


    (options, args) = parser.parse_args(args)

    if not options.distro:
        print "Please provide a distro name"
        return -1

    if not options.rpm:
        print "Please provide path to the rpm"
        return -1
    
    if not os.path.isfile(options.rpm):
        print "Please provide path to the rpm"
        return -1
    
    #let us find the db configuration
    config = ConfigParser.ConfigParser()
    config.read('/etc/darkserver.conf')
    
    parserpm(options.rpm, config, options.distro)


if __name__ == '__main__':
    main(sys.argv[1:])