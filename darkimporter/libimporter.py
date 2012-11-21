import os
import sys
import time
import redis
import koji
import stat
import json
import MySQLdb
import tempfile
import subprocess
import logging
import requests
import ConfigParser
from .utils import log
from retask.queue import Queue
from retask.task import Task
from BeautifulSoup import BeautifulSoup


def get_redis_config():
    """
    Get the server configuration as a dict
    """
    path = './data/redis_server.json'
    if not os.path.exists(path):
        path = '/etc/darkserver/redis_server.json'

    try:
        with open(path) as fobj:
            config = json.load(fobj)
            return config
    except Exception, e:
        log('get_redis_config',str(e), 'error')
    return None


def redis_connection():
    """
    Returns the rdb object.
    """
    try:
        config = get_redis_config()
        rdb = redis.Redis(config['host'], config['port'], config['db'],\
                             config['password'])
        return rdb
    except Exception, e:
        log('redis_connection',str(e), 'error')
        return

def log_status(name, text):
    """
    Saves the status for the given name in redis.

    :arg name: Name of the process
    :arg text: Text to be saved
    """
    pid = str(os.getpid())
    key = "%s:%s" % (name, pid)
        
    try:
        rdb = redis_connection()
        if not rdb:
            
            return None
        rdb.set(key, text)
        return True
    except Exception, e:
        log(key, str(e), 'error')

def remove_redis_keys(name):
    """
    Removes the temporary statuses
    """
    pid = str(os.getpid())
    key = "%s:%s" % (name, pid)
    try:
        rdb = redis_connection()
        if not rdb:
            log(key, 'redis is missing', 'error')
            return None     
        rdb.delete(key)
    except Exception, e:
        log(key, str(e), 'error')


def check_shutdown():
    """
    Check for shutdown for a gracefull exit.
    """
    pid = str(os.getpid())
    rdb = redis_connection()
    try:
        if not rdb:
            log(key, 'redis is missing', 'error')
            return False
        shutdown = rdb.get('shutdown:%s' % pid)
        if shutdown:
            rdb.delete('shutdown:%s' % pid)
            return True
    except Exception, e:
        log(key, str(e), 'error')
    return False

def create_rundir():
    """
    Create the required directory as /var/run/darkserver
    """
    system('mkdir -p /var/run/darkserver')


def downloadrpm(url, path):
    system("wget %s -O %s" % (url, path))

def get_distro(idx):
    """
    Guess the distro name from rpm releases
    """
    path = './data/dark-distros.json'
    if not os.path.exists('./data/dark-distros.json'):
        path = '/etc/darkserver/dark-distros.json'

    distro = json.load(open(path))
    kojiurl="http://koji.fedoraproject.org/kojihub"
    kc = koji.ClientSession(kojiurl, {'debug': False, 'password': None,\
                        'debug_xmlrpc': False, 'user': None})    
    res = kc.getBuild(idx)
    for name in distro:
        if res['release'].find(name) != -1:
            return name
        
    return None


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



def getconfig():
    """
    Get the server configuration as a dict
    """
    path = '/etc/darkserver/darkjobworker.conf'
    result = {}
    try:
        config = ConfigParser.ConfigParser()
        config.read(path)
        
        result['DB'] = config.get('darkserver','database')
        result['USER'] = config.get('darkserver','user')
        result['PASSWORD'] = config.get('darkserver','password')
        result['HOST'] = config.get('darkserver','host')
        result['PORT'] = config.get('darkserver','PORT')
    except Exception, e:
        log('getconfig', str(e), 'error')
    return result


def parserpm(destdir, path, distro="fedora"):
    """
    parse the rpm and insert data into database
    """
    path = path.strip()
    filename = os.path.basename(path)

    key = 'darkjobworker:' + str(os.getpid())
    log(key, 'Extracting: %s' % path, 'info')
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
            log(key, str(error), 'error')
    #Save the result in the database
    save_result(result)

def save_result(results):
    key = 'darkjobworker:' + str(os.getpid())
    config = getconfig()
    try:

        conn = MySQLdb.connect(config['HOST'], config['USER'], config['PASSWORD'], config['DB'])
        cursor = conn.cursor()

        for sql in results:
            cursor.execute(sql)
        conn.commit()
        conn.close()
    except Exception, error:
        log(key, str(error), 'error')


def do_buildid_import(mainurl, idx):
    """
    Import the buildids from the given Koji URL
    """
    key = 'darkjobworker:' + str(os.getpid())
    if not mainurl:
        return
    #Guess the distro name
    distro = get_distro(idx)
    if not distro: #We don't want to import this build
        return
    req = requests.get(mainurl)
    soup = BeautifulSoup(req.content)
    for link in soup.findAll('a'):
        name = link.get('href')
        if name.endswith('.rpm') and not name.endswith('.src.rpm'):
            rpm = name.split('/')[-1]
            log(key, 'found %s' % rpm, 'info')
            if rpm.endswith('noarch.rpm'): #No need to check noarch
                continue
            elif rpm.find('-devel-') != -1: #Don't want to process devel packages
                continue 
            #Create the temp dir
            destdir = tempfile.mkdtemp(suffix='.' + str(os.getpid()), dir=None)
            destdir1 = tempfile.mkdtemp(suffix='.' + str(os.getpid()), dir=None)
            rpm = os.path.join(destdir1, rpm)
            log(key, 'downloading %s' % rpm, 'info')
            log_status('darkjobworker', 'Downloading %s' % rpm)
            downloadrpm(name, rpm)
            try:
                log_status('darkjobworker', 'Parsing %s' % rpm)
                parserpm(destdir, rpm, distro)
            except Exception, error:
                log(key, str(error), 'error')
            #Remove the temp dir
            removedir(destdir)   
            removedir(destdir1) 
            log_status('darkjobworker', 'Import done for %s' % rpm)


def produce_jobs(idx):
    key = 'darkproducer:%s' % str(os.getpid())
    log(key, "starting with %s" % str(idx), 'info')
    kojiurl = 'http://koji.fedoraproject.org/'
    kojiurl2 = kojiurl + 'kojihub'
    kc = koji.ClientSession(kojiurl2, {'debug': False, 'password': None,\
                        'debug_xmlrpc': False, 'user': None})

    jobqueue = Queue('jobqueue')
    jobqueue.connect()
    buildqueue = Queue('buildqueue')
    buildqueue.connect()
    #lastbuild = {'id':None, 'time':None}
    rdb = redis_connection()
    if not rdb:
        log(key, 'redis is missing', 'error')
        return None
    rdb.set('darkproducer-id', idx)
    while True:
        if check_shutdown():
            break
        try:
            rdb.set('darkproducer-status', '1')
            idx = int(rdb.get('darkproducer-id'))
            res = kc.getBuild(idx)
            url = kojiurl + 'koji/buildinfo?buildID=%s' % idx
            if not res:
                #FIXME!!
                #http://koji.fedoraproject.org/koji/buildinfo?buildID=367374
                #missing build from db :(
                #if lastbuild['id'] != idx:
                #    lastbuild['id'] = idx
                #    lastbuild['time'] = time.time.now()
                #else:
                #    diff = time.time.now() - lastbuild['time']
                #    if diff > 300:
                #We have a buildid stuck, raise alarm
                

                #We reached to the new build yet to start
                #Time to sleep
                log(key, "Sleeping with %s" % idx, 'info')
                time.sleep(60)
                continue
            if res['state'] == 1:
                #completed build now push to our redis queue    
                info = {'url': url, 'jobid': idx}
                task = Task(info)
                jobqueue.enqueue(task)
                log(key, "In job queue %s" % idx, 'info')
                rdb.incr('darkproducer-id')
                continue

            if res['state'] == 0:
                #building state
                info = {'url': url, 'jobid': idx, 'kojiurl': kojiurl2}
                task = Task(info)
                buildqueue.enqueue(task)
                log(key, "In build queue %s" % idx, 'info')
                rdb.incr('darkproducer-id')
                continue
            else:
		rdb.incr('darkproducer-id')

        except Exception, error:
            log(key, str(error), 'error')
    rdb.set('darkproducer-status', '0')


def monitor_buildqueue():
    """
    This function monitors the build queue.

    If the build is still on then it puts it back to the queue.
    If the build is finished then it goes to the job queue.
    """
    key = 'darkbuildqueue:%s' % str(os.getpid())
    jobqueue = Queue('jobqueue')
    jobqueue.connect()
    buildqueue = Queue('buildqueue')        
    buildqueue.connect()
    rdb = redis_connection()
    if not rdb:
        log(key, 'redis is missing', 'error')
        return None
    rdb.set('darkbuildqueue-status', '1')
    while True:
        if check_shutdown():
            break
        try:
            time.sleep(60)
            length = buildqueue.length
            if  length == 0:
                log(key, "Sleeping, no buildqueue job", 'info')
                time.sleep(60)
                continue
            task = buildqueue.dequeue()
            kojiurl = task.data['kojiurl']
            idx = task.data['jobid']
            kc = koji.ClientSession(kojiurl, {'debug': False, 'password': None,\
                            'debug_xmlrpc': False, 'user': None})
            
            res = kc.getBuild(idx)
            if not res:
                #We reached to the new build yet to start
                #Time to sleep
                log(key, "build deleted %s" % idx, 'error')
                continue
            if res['state'] == 1:
                #completed build now push to our redis queue
                jobqueue.enqueue(task)
                log(key, "in job queue %s" % idx, 'info')
                continue

            if res['state'] == 0:
                #building state
                buildqueue.enqueue(task)
                log(key, "in build queue %s" % idx, 'info')
                continue

        except Exception, error:
            log(key, str(error), 'error')
    rdb.set('darkbuildqueue-status', '0')

