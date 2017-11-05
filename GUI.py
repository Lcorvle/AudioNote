from Tkinter import *
import tkFileDialog
import ScrolledText
from threading import Timer
import time
# from OnlineNote import *
# from OfflineNote import *


class AddSpeakerDialog(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self)
        self.title('Add speakers')
        self.parent = parent
        row1 = Frame(self)
        row1.pack(fill="x")
        Label(row1, text='name:', width=8).pack(side=LEFT)
        self.name = StringVar()
        self.nameEntry = Entry(row1, textvariable=self.name, width=20)
        self.nameEntry.pack(side=LEFT)
        self.nameEntry.insert(0, 'user1')
        row2 = Frame(self)
        row2.pack(fill="x", ipadx=1, ipady=1)
        Label(row2, text='time:', width=8).pack(side=LEFT)
        self.timeLabel = Label(row2, text='0', width=8)
        self.timeLabel.pack(side=LEFT)
        Button(row2, text="finish", command=self.finish).pack(side=RIGHT)
        self.controlButton = Button(row2, text="begin", command=self.control)
        self.controlButton.pack(side=RIGHT)
        self.state = 'stop'
        self.timer = None
        self.hour = 0
        self.min = 0
        self.sec = 0

    def count(self):
        t = str(self.hour) + ':'
        if self.min < 10:
            t += '0' + str(self.min) + ':'
        else:
            t += str(self.min) + ':'
        if self.sec < 10:
            t += '0' + str(self.sec)
        else:
            t += str(self.sec)
        self.timeLabel.config(text=t)
        self.parent.update()
        self.sec += 1
        if self.sec == 60:
            self.sec = 0
            self.min += 1
        if self.min == 60:
            self.min = 0
            self.hour += 1
        if self.state == 'begin':
            self.timeLabel.after(1000, self.count)

    def control(self):
        if self.state == 'stop':
            self.hour = 0
            self.min = 0
            self.sec = 0
            self.controlButton.config(text='stop')
            self.state = 'begin'
            self.count()
        else:
            self.controlButton.config(text='restart')
            self.state = 'stop'

    def finish(self):
        username = self.name.get()
        self.parent.speakerListBox.insert(END, username)
        self.destroy()


class Application(Frame):
    onlineNote = None
    offlineNote = None

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.master.geometry('670x500+200+30')
        self.master.minsize(640, 485)
        self.master.maxsize(700, 515)
        self.result = ''
        self.rowNum = 15
        self.colNum = 21
        self.mode = 'offline'
        # self.onlineNote = OnlineNote()
        # self.offlineNote = OfflineNote()
        self.createUI()

    def hideBackground(self, left, top, width, height):
        for i in range(width):
            for j in range(height):
                self.background[left + i][top + j].grid_forget()

    def showBackground(self, left, top, width, height):
        for i in range(width):
            for j in range(height):
                self.background[left + i][top + j].grid(row=top + j, column=left + i)

    def createUI(self):
        # initial widgets for off-line mode
        self.background = []
        for i in range(self.colNum):
            row = []
            for j in range(self.rowNum):
                backgroundLabel = Label(self, bg='red')
                backgroundLabel.grid(row=j, column=i, padx=11, pady=3)
                row.append(backgroundLabel)
            self.background.append(row)
        self.hideBackground(0, 0, 4, 4)
        self.offLineModeButton = Button(self, text='offline mode', command=self.changeToOffLineMode)
        self.offLineModeButton.grid(row=0, column=0, rowspan=2, columnspan=2)
        self.offLineModeButton = Button(self, text='online mode', command=self.changeToOnLineMode)
        self.offLineModeButton.grid(row=0, column=2, rowspan=2, columnspan=2)
        self.fileChooseButton = Button(self, text='run', command=self.run)
        self.fileChooseButton.grid(row=2, column=0, rowspan=2, columnspan=2)
        self.fileChooseButton = Button(self, text='export', command=self.saveResult)
        self.fileChooseButton.grid(row=2, column=2, rowspan=2, columnspan=2)
        self.hideBackground(12, 0, 9, 3)
        self.fileLabel = Label(self, text='file path:')
        self.fileLabel.grid(row=1, column=12, rowspan=2, columnspan=2)
        self.filePathEntry = Entry(self)
        self.filePathEntry.grid(row=1, column=14, rowspan=2, columnspan=7, sticky=W)
        self.fileChooseButton = Button(self, text='import file', command=self.chooseFile)
        self.fileChooseButton.grid(row=1, column=19, rowspan=2, columnspan=2)
        self.speakerNumberLabel = Label(self, text='number:')
        self.speakerNumberLabel.grid(row=0, column=12, rowspan=2, columnspan=2)
        self.speakerNumberBox = Spinbox(self, from_ = 0, to = 100, increment = 1)
        self.speakerNumberBox.grid(row=0, column=14, rowspan=2, columnspan=7, sticky=W)
        self.hideBackground(1, 4, 19, 10)
        self.outputLabel = Label(self, text='output: ')
        self.outputLabel.grid(row=4, column=1)
        self.outputText = ScrolledText.ScrolledText(self)
        self.outputText.grid(row=5, column=1, rowspan=9, columnspan=19)
        self.outputText.config(state=DISABLED)

        # initial widgets for online mod
        self.speakerUpdateLabel= Label(self, text='speaker: 0')
        self.speakerListBoxScrollBar = Scrollbar(self, orient=VERTICAL)
        self.speakerListBox = Listbox(self, selectmode=EXTENDED, height=5, yscrollcommand=self.speakerListBoxScrollBar.set)
        self.speakerListBoxScrollBar.config(command=self.speakerListBox.yview)
        self.addSpeakerButton = Button(self, command=self.addSpeaker, text='add')
        self.deleteSpeakerButton = Button(self, command=self.deleteSpeakers, text='delete')

    def addSpeaker(self):
        pw = AddSpeakerDialog(self)
        self.wait_window(pw)
        self.speakerUpdateLabel.config(text='speaker: ' + str(self.speakerListBox.size()))
        self.speakerListBox.selection_clear(0, END)


    def deleteSpeakers(self):
        selectItem = self.speakerListBox.curselection()
        for x in selectItem:
            self.speakerListBox.delete(x, x)
        self.speakerUpdateLabel.config(text='speaker: ' + str(self.speakerListBox.size()))
        self.speakerListBox.selection_clear(0, END)

    def chooseFile(self):
        filePath = tkFileDialog.askopenfilename(title='import file',
                                   filetypes=[("Audio files", "*.mp3")],
                                   initialdir='C:/')

        self.filePathEntry.delete(0, END)
        self.filePathEntry.insert(0, filePath)

    def run(self):
        filePath = self.filePathEntry.get()
        self.outputText.config(state=NORMAL)
        a = self.speakerNumberBox.get()
        self.outputText.insert(1.0, str(a) + '\n')
        self.outputText.config(state=DISABLED)

    def saveResult(self):
        filePath = tkFileDialog.asksaveasfilename(title='export file',
                                              filetypes=[("Text files", "*.txt")],
                                              initialdir='C:/',
                                            initialfile='record.txt')
        if filePath:
            file = open(filePath, 'w')
            file.write(self.result)
            file.close()

    def changeToOnLineMode(self):
        if self.mode == 'offline':
            self.speakerNumberLabel.grid_forget()
            self.speakerNumberBox.grid_forget()
            self.showBackground(12, 2, 9, 1)
            self.hideBackground(4, 0, 3, 1)
            self.speakerUpdateLabel.config(text='speaker: ' + str(self.speakerListBox.size()))
            self.speakerUpdateLabel.grid(row=0, column=5, columnspan=7, sticky=W)
            self.hideBackground(6, 0, 6, 4)
            self.speakerListBox.grid(row=1, column=6, rowspan=3, columnspan=5, sticky=N+S+W+E)
            self.speakerListBoxScrollBar.grid(row=1, column=11, rowspan=3, sticky=W+N+S)
            self.hideBackground(12, 2, 3, 2)
            self.addSpeakerButton.grid(row=2, column=12, rowspan=2, columnspan=3)
            self.hideBackground(16, 2, 3, 2)
            self.deleteSpeakerButton.grid(row=2, column=16, rowspan=2, columnspan=3)
            self.fileLabel.grid(row=0, column=12, rowspan=2, columnspan=2)
            self.filePathEntry.grid(row=0, column=14, rowspan=2, columnspan=7, sticky=W)
            self.fileChooseButton.grid(row=0, column=19, rowspan=2, columnspan=2)
            self.mode = 'online'

    def changeToOffLineMode(self):
        if self.mode == 'online':
            self.speakerListBoxScrollBar.grid_forget()
            self.speakerUpdateLabel.grid_forget()
            self.speakerListBox.grid_forget()
            self.addSpeakerButton.grid_forget()
            self.deleteSpeakerButton.grid_forget()
            self.fileLabel.grid(row=1, column=12, rowspan=2, columnspan=2)
            self.filePathEntry.grid(row=1, column=14, rowspan=2, columnspan=7, sticky=W)
            self.fileChooseButton.grid(row=1, column=19, rowspan=2, columnspan=2)
            self.speakerNumberLabel.grid(row=0, column=12, rowspan=2, columnspan=2)
            self.speakerNumberBox.grid(row=0, column=14, rowspan=2, columnspan=7, sticky=W)
            self.hideBackground(12, 2, 9, 1)
            self.showBackground(4, 0, 1, 1)
            self.showBackground(12, 3, 7, 1)
            self.mode = 'offline'



if __name__ == '__main__':
    app = Application()
    app.master.title('Audio Note')
    app.mainloop()