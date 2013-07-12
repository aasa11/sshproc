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
import Tkinter


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


def seesion_thread(cmdlist, sshpara, tk):
    ip = sshpara[0]
    user = sshpara[1]
    pwd = sshpara[2]
    ipmsg = ip+" "+user+" "+pwd
    #print "start connet "+ipmsg
    addtxt(tk, "start connet "+ipmsg+'\n')
    paramiko.util.log_to_file('paramiko.log')
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    try :
        s.connect(hostname = ip,username= user, password= pwd, timeout = 5)
    except socket.timeout as e:
        #print "connect "+ipmsg+" time out "+ str(e) +", try again..."
        addtxt(tk, "connect "+ipmsg+" time out "+ str(e) +", try again...\n")
        try:
            s.connect(hostname = ip,username= user, password= pwd, timeout = 5)
        except socket.timeout as e:
            #print "connect "+ipmsg+" failed" +str(e)+" ..., exit"
            addtxt(tk, "connect "+ipmsg+" failed" +str(e)+" ..., exit\n")
            return False
        
    
    
    #print "connect "+ipmsg+" success"
    addtxt(tk,"connect "+ipmsg+" success\n")
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
            #print ipmsg+" proc..."
            strcmd = cmdlist[i]

            if strcmd == 'quitssh':
                #print ipmsg+" quit..."
                addtxt(tk,ipmsg+" quit...\n")
                ssh.close()
                s.close()
                return True
            #ls will make err codingformat, so need trans it
            if strcmd.startswith("ls") :
                strcmd += " > tmplstxt; cat tmplstxt; rm tmplstxt;"

            #send cmd         
            while not ssh.send_ready():
                #print "not send ready"
                addtxt(tk, "not send ready\n")
                time.sleep(1)
            ssh.send(strcmd+'\n')
            time.sleep(1)
            #recv data
            while not ssh.recv_ready():
                #print "not recv ready"
                addtxt(tk, "not recv ready\n")
                time.sleep(1)           
            while ssh.recv_ready():
                output =  ssh.recv(1024)
                #print output,
                addtxt(tk, output)
            #print '\n'
            addtxt(tk,'\n')
        
        #change done num
        cmdnum = nowlistnum
        continue
           
def addtxt(tk, msg):
    tk.insert(Tkinter.END,msg)

def window_thread(cmdlist, para):
    root = Tkinter.Tk()
    label = Tkinter.Label(root, text=str(cmdlist))
    label.pack()
    t = Tkinter.Text(root)
    t.pack()
    #thread.start_new_thread(seesion_thread,(cmdlist, para, t))
    time.sleep(1)
    root.mainloop()

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
        thread.start_new_thread(window_thread,(cmdlist, para))
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