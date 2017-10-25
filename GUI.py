from tkinter import *
import tkinter.dnd as dnd


class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.master.geometry('500x300+500+200')
        self.master.minsize(500, 300)
        self.createWidgets()

    def createWidgets(self):
        self.helloLabel = Label(self, text='Hello, world!')
        self.helloLabel.grid()
        self.quitButton = Button(self, text='Quit', command=self.quit)
        self.quitButton.grid()

if __name__ == '__main__':
    dnd.test()
    # app = Application()
    # app.master.title('Audio Note')
    # app.mainloop()