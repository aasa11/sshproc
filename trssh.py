'''
Created on 2013/07/11

@author: huxiufeng
'''
import os
import ConfigParser
import paramiko
import time
import socket
import thread


#read parafile
def parseConfigfile(filename, item_key):
    config = ConfigParser.ConfigParser()
    config.read(filename)
    ksv = config.items(item_key)
    print ksv
    
    sshlist = []
    for its in ksv:
        onelist = str(its[1]).split(':')
        print onelist
        sshlist.append(onelist)
    #print sshlist
    return sshlist


def seesion_thread(cmdlist, sshpara):
    ip = sshpara[0]
    user = sshpara[1]
    pwd = sshpara[2]
    ipmsg = ip+" "+user+" "+pwd
    print "start connet "+ipmsg
    paramiko.util.log_to_file('paramiko.log')
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    try :
        s.connect(hostname = ip,username= user, password= pwd, timeout = 5)
    except socket.timeout as e:
        print "connect "+ipmsg+" time out "+ str(e) +", try again..."
        try:
            s.connect(hostname = ip,username= user, password= pwd, timeout = 5)
        except socket.timeout as e:
            print "connect "+ipmsg+" failed" +str(e)+" ..., exit"
            return False
        
    
    
    print "connect "+ipmsg+" success"
    time.sleep(1)
    ssh = s.invoke_shell()
    
    cmdnum = 0
    while True:
        nowlistnum = len(cmdlist)
        #waitfor cmd
        if cmdnum == nowlistnum:
            time.sleep(1)
            continue 
        #proc cmd
        for i in range(cmdnum, nowlistnum):
            print ipmsg+" proc..."
            strcmd = cmdlist[i]

            if strcmd == 'quitssh':
                print ipmsg+" quit..."
                ssh.close()
                s.close()
                return True
            #ls will make err codingformat, so need trans it
            if strcmd.startswith("ls") :
                strcmd += " > tmplstxt; cat tmplstxt; rm tmplstxt;"

            #send cmd         
            while not ssh.send_ready():
                print "not send ready"
                time.sleep(1)
            ssh.send(strcmd+'\n')
            time.sleep(1)
            #recv data
            while not ssh.recv_ready():
                print "not recv ready"
                time.sleep(1)           
            while ssh.recv_ready():
                output =  ssh.recv(1024)
                print output,
            print '\n'
        
        #change done num
        cmdnum = nowlistnum
        continue
           





#----------------------It is a split line--------------------------------------

def main():
    filename='sshhost.ini'
    item_key='ssh-host' 
    
    sshlist = parseConfigfile(filename, item_key)
    
    cmdpack = []
    #create ssh thread
    for para in sshlist:
        cmdlist = []
        cmdpack.append(cmdlist)
        thread.start_new_thread(seesion_thread,(cmdlist, para))
    print "start threads ok\n"    
    time.sleep(5)
    
    #getcmd
    while True:
        cmd = raw_input("cmd: ")         
        for l in cmdpack:
            l.append(cmd)
            
        if cmd == 'quitssh':
            time.sleep(3)
            return 
        
    
#----------------------It is a split line--------------------------------------

if __name__ == "__main__":
    main()
    print "It's ok"