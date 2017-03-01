import os
import koji
import stat
import json
import elfdata
import psycopg2
import tempfile
import subprocess
import ConfigParser

import logging
log = logging.getLogger("darkserver")

CONFIG = None
KOJI_URLS = {}



def create_rundir():
    """
    Create the required directory as /var/run/darkserver
    """
    system('mkdir -p /var/run/darkserver')


def downloadrpm(url, path):
    system("wget %s -O %s" % (url, path))


def is_elf(filepath):
    """
    Finds if a file is elf or not
    """
    elf_magic = "7f454c46"
    fobj = os.lstat(filepath)
    if (stat.S_ISDIR(fobj.st_mode)):
        return False

    f = open(filepath, 'rb')
    s = f.read(4)
    f.close()
    py_data = s.encode('hex')
    if py_data == elf_magic:
        return True
    return False


def find_elf_files(files):
    """
    Returns the ELF files from the list
    """
    elfs = []
    for filename in files:
        if os.path.exists(filename) and os.path.isfile(filename):
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


def loadconfig():
    """
    Get the server configuration as a dict
    We also load different URLS
    """
    global CONFIG
    global KOJI_URLS
    path = '/etc/darkserver/darkjobworker.conf'
    result = {}
    try:
        config = ConfigParser.ConfigParser()
        config.read(path)

        result['DB'] = config.get('darkserver','database')
        result['USER'] = config.get('darkserver','user')
        result['PASSWORD'] = config.get('darkserver','password')
        result['HOST'] = config.get('darkserver','host')
        result['PORT'] = config.get('darkserver','port')
        result['UNIQUE'] = config.get('darkserver','unique')
    except Exception, e:
        log.Error(str(e))
    CONFIG = result
    koji_path = './data/koji_info.json'
    if not os.path.exists(koji_path):
        koji_path = '/etc/darkserver/koji_info.json'
    print koji_path
    with open(koji_path) as fobj:
        KOJI_URLS = json.load(fobj)



def get_unstrip_buildid(filepath):
    data = system("eu-unstrip -n -e %s" % filepath)
    return data.split(' ')[1].split('@')[0]


def parserpm(destdir, path, distro="fedora", kojiid=None, instance="primary", url=None):
    """
    parse the rpm and insert data into database
    """
    path = path.strip()
    filename = os.path.basename(path)

    log.info('Extracting: %s' % path)
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

    for eachfile in elffiles:
        # Using the new module
        data = elfdata.get_buildid(eachfile)
        if not data: #run eu-unstrip and parse the result
            data = get_unstrip_buildid(eachfile)
        if not data:
            continue
        try:
            name = eachfile[dest_len + 1:]
            dirname = "/" + '/'.join(os.path.dirname(name).split('/')[1:])
            sql = "INSERT INTO buildid_gnubuildid VALUES"\
                              " (null, '%s','%s','%s','%s','%s', %s, '%s', '%s')"
            sql = sql % (os.path.basename(name), dirname, \
                         data, \
                         filename[:-4], distro, str(kojiid), instance, url)

            result.append(sql)
        except Exception, error:
            log.Error(str(error))
    #Save the result in the database
    save_result(result)

def save_result(results):
    config = CONFIG
    try:

        conn = psycopg2.connect("dbname='{0}' user='{1}' password='{2}' host='{3}'".format(config['DB'],\
                                                    config['USER'], config['PASSWORD'], config['HOST']))
        cursor = conn.cursor()

        for sql in results:
            log.info(sql)
            cursor.execute(sql)
        conn.commit()
        conn.close()
    except Exception, error:
        log.error(str(error))



def do_buildid_import(instance, idx, distro, key):
    """
    Import the buildids from the given Koji URL
    """
    insd = KOJI_URLS.get(instance, None)
    if not insd:
        return
    koji_session = koji.ClientSession(insd['hub'])
    build_rpms = koji_session.listBuildRPMs(idx)
    for rpm in build_rpms:
        if rpm['arch'] in ['noarch', 'src']: # We don't want noarch
            continue
        # We also do not want the devel packages
        if rpm['name'].find('-devel') != -1:
            continue
        fname = "%s-%s-%s.%s.rpm" % (rpm['name'], rpm['version'], rpm['release'], rpm['arch'])
        url = "%s/%s/%s/%s/%s/%s" % (insd['pkgs'], rpm['name'], rpm['version'], rpm['release'], rpm['arch'], fname)
        log.info('Found %s' % fname)
        #Create the temp dir
        destdir = tempfile.mkdtemp(suffix='.' + str(os.getpid()), dir=None)
        destdir1 = tempfile.mkdtemp(suffix='.' + str(os.getpid()), dir=None)
        file_path = os.path.join(destdir1, fname)
        log.info('Downloading %s' % fname)
        downloadrpm(url, file_path)
        try:
            parserpm(destdir, file_path, distro, kojiid=idx,
                     instance=instance, url=url)
        except Exception, error:
            log.error(str(error))
            #Remove the temp dir
        removedir(destdir)
        removedir(destdir1)
        log.info('Import done for %s' % fname)
