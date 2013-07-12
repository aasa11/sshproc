'''
Created on 2013/07/11

@author: huxiufeng
'''
import Tkinter
import time
import thread


root = Tkinter.Tk()

t = Tkinter.Text(root)
t.pack()
for i in range(1,10):      
    t.insert(1.0,'0123456789\n') 
label = Tkinter.Label(root, text="Hello Tkinter")
label.pack()

def addtext(tt,b):
    for i in range(100):
        tt.insert(Tkinter.END,'this is '+str(i)+'msg\n')
        time.sleep(1)
        
def newwindow(a,b):
    root2 = Tkinter.Tk() 
    label = Tkinter.Label(root2, text="Hello Tkinter")
    label.pack()
    root2.mainloop()

#thread.start_new_thread(addtext, (t, 0))
thread.start_new_thread(newwindow, (1, 2))


time.sleep(1000)
#root.mainloop()



#----------------------It is a split line--------------------------------------

def main():
    pass
    
#----------------------It is a split line--------------------------------------

if __name__ == "__main__":
    main()
    print "It's ok"