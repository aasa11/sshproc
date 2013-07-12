#coding=gbk
'''
Created on 2013/07/11

@author: huxiufeng
'''

import paramiko
import time
import os
import socket
import datetime
from  ConfigParser import ConfigParser


configfile='sshhost.ini'
item_ssh_host='ssh-host' 

#----------------------It is a split line--------------------------------------

def main():

    config = ConfigParser()
    config.read(configfile)
    ksv = config.items(item_ssh_host)
    print ksv
    

    sshlist = []
    for its in ksv:
        onelist = str(its[1]).split(':')
        print onelist
        sshlist.append(onelist)
    
    sshs = []
    paramiko.util.log_to_file('paramiko.log')
    for its in sshlist:
        print its[0]+" connect: "
        s = paramiko.SSHClient()
        s.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
        try :
            s.connect(hostname = its[0],username=its[1], password=its[2], timeout = 5)
        except socket.timeout as e:
            print "connect time out , try again..."
            s.connect(hostname = its[0],username=its[1], password=its[2], timeout = 5)
        its.append(s)
        s_shell = s.invoke_shell()
        its.append(s_shell)
    print sshlist
    
    strcmd = ''    
    while True:
        strcmd = raw_input("cmd : ")
        if strcmd == 'quitssh':
            break
        
        for its in sshlist:
            print "proc on "+its[0]+':'
            s_shell = its[4]
            while not s_shell.send_ready():
                print "not send ready"
                time.sleep(3)
            ret = s_shell.send(strcmd+'\n')
            time.sleep(1)
            #print ret
            while not s_shell.recv_ready():
                print "not recv ready"
                time.sleep(5)
            
            while s_shell.recv_ready():
                output =  s_shell.recv(1024)
                print output,
            print '\n'
            
    for its in sshlist:
        its[4].close()
        its[3].close()
    


#----------------------It is a split line--------------------------------------

if __name__ == "__main__":
    main()
    print "It's ok"