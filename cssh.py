'''
Created on 2013/07/12

@author: huxiufeng
'''

import ConfigParser
import paramiko
import time
import socket
import Tkinter
import threading
from multiprocessing import Queue
import thread

class ccfg:
    def __init__(self,filename):
        self.filename = filename
        self.paras = []

    def readcfg(self, item_key):
        config = ConfigParser.ConfigParser()
        config.read(self.filename)
        ksv = config.items(item_key)
        print ksv
        
        self.paras = []
        i = 0
        for its in ksv:
#            outlist = []
#            outlist.append(i)
#            outlist.extend(str(its[1]).split(':'))
            outlist = str(its[1]).split(':')
            print outlist
            self.paras.append(outlist)
            i+=1
        
        return
    
    def getparas(self):
        return self.paras
        


class cssh(threading.Thread):
    def __init__(self, index, sshpara, cmdqueue, tt):
        threading.Thread.__init__(self) 
        self.index = index
        self.ip = sshpara[0]
        self.name = sshpara[1]
        self.pwd = sshpara[2]
        self.home = sshpara[3]
        self.tt = tt
        paramiko.util.log_to_file('paramiko.log')
        self.connected = False
        self.isstop = False
        self.queue = cmdqueue
        
        self.msgip = " "+self.ip+":"+self.name+":"+self.pwd+" "
        self.txtindex = 0
        
    def printf(self, msg):
        try :
            self.tt.insert(Tkinter.END, msg)
            self.tt.yview(Tkinter.END)
            self.txtindex += msg.count('\n')
            
            if self.txtindex > 500:
                self.tt.insert(Tkinter.END, "need delete")
                self.tt.delete(0.0,300.0)
                self.txtindex = self.txtindex-300
        except Exception, e:
            pass
        
    def getrecv(self):
        while self.ssh.recv_ready():
            output = self.ssh.recv(1024)
            try:
                out2 = output.decode('gbk').encode('utf-8')
            except:
                out2 = output
            self.printf(out2)
        
    def connect(self):
        if self.connected :
            return True
        self.printf("start connect"+self.msgip+"...\n")
        self.s = paramiko.SSHClient()
        self.s.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
        try :
            self.s.connect(hostname = self.ip,username=self.name, password=self.pwd, timeout = 5)
        except socket.timeout as e:
            self.printf( "connect time out ,"+e+" try again...\n")
            try:
                self.s.connect(hostname = self.ip,username=self.name, password=self.pwd, timeout = 5)
            except socket.timeout as e:
                self.printf( "connect time out ,"+e+" return error...\n")
                return False
            
        self.printf("connect "+self.msgip+" success.\n")
        self.connected = True   
        self.ssh = self.s.invoke_shell()
        if self.home == None or self.home =="None" or self.home =='':
            self.sendcmd("\n")
        else:
            cmd = self.home+"\n"
            self.sendcmd(cmd)
        self.getrecv()
                
        return True
    
    def close(self):
        if not self.connected:
            return True
        self.ssh.close()
        self.s.close()
        self.printf("close "+self.msgip+".\n")
        self.connected = False
        return
    
    def sendcmd(self, cmd):
        if not self.connected:
            self.printf("not connected...\n")
            return False
        
#        if cmd == 'esc\n':
#            self.ssh.
#            return True
        
        self.getrecv()
        while not self.ssh.send_ready():
            self.printf("not send ready....\n")
            time.sleep(0.5)
        self.getrecv()
        self.ssh.send(cmd)
        while not self.ssh.recv_ready():
            #self.printf("not recv ready....\n")
            time.sleep(0.5)
        self.getrecv()
        return True
    
    def docmd(self,cmd):
        if cmd == "sshconnect":
            self.connect()
        elif cmd == "sshclose":
            self.close()
        elif cmd.startswith("winshow "):
            self.printf(cmd)
        else :
            cmd = self.modcmd(cmd)
            self.sendcmd(cmd)
            
    def modcmd(self,cmd):
        if cmd.startswith("ls"):
            cmd += " > lstmptxt; cat lstmptxt; rm lstmptxt;"
        cmd += '\n'
        
        return cmd
            
    def run(self):
        while True:
            if self.isstop:
                self.close()
                return
            
            #self.queue = Queue()
            if self.queue.empty():
                time.sleep(0.5)
                if self.connected:
                    self.getrecv()
                continue
            
            cmd = self.queue.get(block = False)
            self.docmd(cmd)
            
    def stop(self):
        self.isstop = True
                
        
class sshwin:
    def __init__(self,filename, item_key):
        self.cfg = ccfg(filename)
        self.cfg.readcfg(item_key)      
        self.queues = []
        self.switchnum = []
        for i in self.cfg.getparas():
            self.switchnum.append(1)
        
    def getrowcol(self,num):
        if num == 1:
            return 1,1
        if num == 2:
            return 1,2
        if num == 3:
            return 1,3
        if num == 4:
            return 2,2
        if num <= 6:
            return 2,3
        if num <=9:
            return 3,3
        return 3,4
        
    def buildwin(self, isstop, isclose):
        self.root = Tkinter.Tk()
        self.root.title("muti-control ssh terminal")
        cfgs = self.cfg.getparas()
        num = len(cfgs)
        row ,col = self.getrowcol(num)
        index = 0
        for i in range(row):
            if index >= num:
                break
            for j in range(col):
                if index >= num:
                    break
                que = Queue()
                self.queues.append(que)
                tt = Tkinter.Text(self.root, height =15,width = 45)
                tt.grid(row=i,column = j)
                print cfgs[index]
                ssh = cssh(index,cfgs[index], que,tt)
                ssh.start()        
                index +=1
        
        self.root.mainloop()
                
    def closewin(self):
        pass
        
        
    def getcmd(self):
        cmd = raw_input("cmd: ")
        if cmd == "sshquit":
            return False
        
        if cmd.startswith("switch "):
            self.changeswitch(cmd)
            cmd = "winshow terminals in control"
                         
        for i in range(0,len(self.switchnum)):
            if self.switchnum[i]>0:
                self.queues[i].put(cmd)
        
        return True
    
    def changeswitch(self, cmd):
        cmds = cmd.split(' ')
        op = 0
        if cmds[1] == 'on':
            op = 1
        elif cmds[1] == 'only':
            for i in range(len(self.switchnum)):
                self.switchnum[i] = 0
                op = 1
        elif cmds[1] == 'offly':
            for i in range(len(self.switchnum)):
                self.switchnum[i] = 1
                op = 0
                
        
            
        if cmds[2] == 'all':
            for i in range(len(self.switchnum)):
                self.switchnum[i] = op
        else:
            opnum = cmds[2].split(",")
            
            for i in opnum:
                try:
                    i = int(i)
                except:
                    continue
                if i >=len(self.switchnum) or i < 0:
                    continue
                self.switchnum[i] = op
        print "oper terminals : "
        for i in range(len(self.switchnum)):
            if self.switchnum[i] > 0:
                print str(i)+ " : on ",
            else:
                print str(i) + " : off ",
        print '\n'
        
    
    def dossh(self):
        thread.start_new_thread(self.buildwin, (False, False))
        time.sleep(1)
        while True:
            ret = self.getcmd()
            if not ret:
                break
        self.closewin()
        return


#----------------------It is a split line--------------------------------------

def main():
    filename = "sshhost.ini"
    item_key = "ssh-host"
    win = sshwin(filename, item_key)
    win.dossh()
    
#----------------------It is a split line--------------------------------------

if __name__ == "__main__":
    main()
    print "It's ok"