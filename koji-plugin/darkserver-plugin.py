#Koji plugin for darkserver
#The config file should be at /etc/koji-hub/plugins/
#Dependency: rpmdevtools elfutils
from koji.plugin import register_callback
import logging
import os
import sys
import stat
import tempfile
import subprocess
import MySQLdb
import json
import ConfigParser

def getconfig():
    """
    Get the server configuration as a dict
    """
    config = ConfigParser.ConfigParser()
    config.read('/etc/koji-hub/plugins/darkserver.conf')
    result = {}
    try:
        result['DB'] = config.get('darkserver','database')
        result['USER'] = config.get('darkserver','user')
        result['PASSWORD'] = config.get('darkserver','password')
        result['HOST'] = config.get('darkserver','host')
        result['PORT'] = config.get('darkserver','PORT')
    except:
        logging.getLogger('koji.plugin.darkserver').error('Problem parsing config')
    return result


def is_elf(filepath):
    """
    Finds if a file is elf or not
    """
    cmd = "file -k %s" % filepath
    data = system(cmd)
    data = data.split(": ")
    if len(data) > 1:
        if data[1].startswith('ELF'):
            return True
    return False

def find_elf_files(files):
    """
    Returns the ELF files from the list
    """
    elfs = []
    for filename in files:
        if os.path.exists(filename):
            if is_elf(filename):
                elfs.append(filename)
    return elfs

def removedir(path):
    """
    removes the dir which must be under /tmp and not a symlink
    """
    if os.path.islink(path):
        return
    if not path.startswith('/tmp'):
        return
    os.system('rm -rf %s' % path)

def system(cmd):
    """
    Invoke a shell command. Primary replacement for os.system calls.
    """
    ret = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    out, err = ret.communicate()
    return out

def parserpm(destdir, path, distro="fedora"):
    """
    parse the rpm and insert data into database
    """
    path = path.strip()
    filename = os.path.basename(path)


    #Extract the rpm
    cmd = 'rpmdev-extract -C %s %s' % (destdir, path)
    datum = system(cmd)
    data = datum.split('\n')

    #Find out all elf files from the list
    files = [os.path.join(destdir, row) for row in data]
    elffiles = find_elf_files(files)

    #Return if ELF file found in the RPM
    if not elffiles:
        return
    #Find the lenth of the destdir name
    dest_len = len(destdir)

    result = []
    #run eu-unstrip and parse the result
    for eachfile in elffiles:
        data = system("eu-unstrip -n -e %s" % eachfile)
        try:
            name = eachfile[dest_len+1:]
            dirname = "/" + '/'.join(os.path.dirname(name).split('/')[1:])
            sql = "INSERT INTO buildid_gnubuildid VALUES"\
                              " (null, '%s','%s','%s','%s','%s')"
            sql = sql % (os.path.basename(name), dirname, \
                         data.split(' ')[1].split('@')[0], \
                         filename[:-4], distro)

            result.append(sql)
        except Exception, error:
            print error

    config = getconfig()
    try:

        conn = MySQLdb.connect(config['HOST'], config['USER'], config['PASSWORD'], config['DB'])
        cursor = conn.cursor()

        for sql in result:
            cursor.execute(sql)
        conn.commit()

        logging.getLogger('koji.plugin.darkserver').info(filename)
    except Exception, e:
        logging.getLogger('koji.plugin.darkserver').error(str(e))


def run_dark_command(cbtype, *args, **kws):
    """
    This will run darkserver-import with proper tag on the rpms
    """
    if kws['type'] != 'build':
       return

    # Get the tag name from the buildroot map
    import sys
    sys.path.insert(0, '/usr/share/koji-hub')
    from kojihub import get_buildroot
    br_id = kws['brmap'].values()[0]
    br = get_buildroot(br_id)
    tag_name = br['tag_name']

    # Get the package paths set up
    from koji import pathinfo
    uploadpath = pathinfo.work()
    rpms = []
    for relpath in kws['rpms']:
        rpms.append( '%s/%s ' % (uploadpath, relpath))

    #Now parse each rpm and also log it
    for rpm in rpms:
        #Create the temp dir
        destdir = tempfile.mkdtemp(suffix='.' + str(os.getpid()), dir=None)
        try:
            parserpm(destdir, rpm, tag_name)
        except Exception, error:
            logging.getLogger('koji.plugin.darkserver').error(str(error))
        removedir(destdir)


register_callback('preImport', run_dark_command)
