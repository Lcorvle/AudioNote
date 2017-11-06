from Tkinter import *
import tkFileDialog
import ScrolledText
import threading
from threading import Timer
import time
from PreRecorder import *
from OnlineNote import *
from OfflineNote import *


class AddSpeakerDialog(Toplevel):
    recorder = None
    record_thread = None
    frms = []
    samp = 0

    handleThread = None

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
        self.recorder = PreRecorder()

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

    def record_voice(self):
        username = self.name.get() + ".wav"

        if self.parent.profileDict.has_key(username):
            return

        self.frms, self.samp = self.recorder.pre_record()

    def control(self):
        if self.state == 'stop':
            self.hour = 0
            self.min = 0
            self.sec = 0
            self.controlButton.config(text='stop')
            self.state = 'begin'
            self.count()
            self.recorder.isOn = True

            self.record_thread = threading.Thread(target=self.record_voice)
            self.record_thread.setDaemon(True)
            self.record_thread.start()
        else:
            self.controlButton.config(text='restart')
            self.state = 'stop'

            self.recorder.isOn = False
            self.record_thread.join()

    def finish(self):
        username = self.name.get()

        oname = username + ".wav"
        self.recorder.write_wave_file(self.frms, self.samp, oname)

        self.parent.speakerListBox.insert(END, username)
        self.parent.newUserFileName = oname
        self.destroy()

class Application(Frame):
    onlineNote = None
    offlineNote = None

    newUserFileName = ""
    profileDict = {}
    nameDict = {}

    recordThread = None

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.master.geometry('720x500+200+30')
        self.master.minsize(640, 485)
        #self.master.maxsize(700, 515)
        self.result = ''
        self.rowNum = 15
        self.colNum = 24
        self.mode = 'offline'
        self.state = 'stop'
        self.createUI()
        self.nameDict["00000000-0000-0000-0000-000000000000"] = "Unknown"
        self.onlineNote = OnlineNote(self)
        self.offlineNote = OfflineNote(self)

    def createBackground(self):
        for i in range(self.colNum):
            Label(self).grid(row=self.rowNum - 1, column=i, padx=11, pady=3)
        for j in range(self.rowNum):
            Label(self).grid(row=j, column=0, padx=11, pady=3)
            Label(self).grid(row=j, column=self.colNum - 1, padx=11, pady=3)

    def createUI(self):
        # initial widgets for off-line mode
        self.createBackground()
        self.changeModeButton = Button(self, text='offline mode', command=self.changeMode)
        self.changeModeButton.grid(row=0, column=1, rowspan=2, columnspan=2, sticky=W)
        
        self.runButton = Button(self, text='run', command=self.run)
        self.runButton.grid(row=2, column=1, rowspan=2, columnspan=2, sticky=W)
        self.exportButton = Button(self, text='export', command=self.saveResult)
        self.exportButton.grid(row=2, column=3, rowspan=2, columnspan=3, sticky=E)
        self.fileLabel = Label(self, text='file path:')
        self.fileLabel.grid(row=1, column=12, rowspan=2, columnspan=2)
        self.filePathEntry = Entry(self)
        self.filePathEntry.grid(row=1, column=14, rowspan=2, columnspan=7, sticky=W)
        self.fileChooseButton = Button(self, text='import file', command=self.chooseFile)
        self.fileChooseButton.grid(row=1, column=21, rowspan=2, columnspan=2)
        self.speakerNumberLabel = Label(self, text='number:')
        self.speakerNumberLabel.grid(row=0, column=12, rowspan=2, columnspan=2)
        self.speakerNumberBox = Spinbox(self, from_ = 0, to = 100, increment = 1)
        self.speakerNumberBox.grid(row=0, column=14, rowspan=2, columnspan=7, sticky=W)
        self.outputLabel = Label(self, text='output: ')
        self.outputLabel.grid(row=4, column=1, columnspan=2)
        self.outputText = ScrolledText.ScrolledText(self)
        self.outputText.grid(row=5, column=1, rowspan=9, columnspan=22)

        # initial widgets for online mod
        self.speakerUpdateLabel= Label(self, text='speaker: 0')
        self.speakerListBoxScrollBar = Scrollbar(self, orient=VERTICAL)
        self.speakerListBox = Listbox(self, selectmode=EXTENDED, height=5, yscrollcommand=self.speakerListBoxScrollBar.set)
        self.speakerListBoxScrollBar.config(command=self.speakerListBox.yview)
        self.addSpeakerButton = Button(self, command=self.addSpeaker, text='add')
        self.deleteSpeakerButton = Button(self, command=self.deleteSpeakers, text='delete')

        self.changeMode()
        self.changeMode()

    def addSpeaker(self):
        pw = AddSpeakerDialog(self)
        self.wait_window(pw)
        self.speakerUpdateLabel.config(text='speaker: ' + str(self.speakerListBox.size()))
        self.speakerListBox.selection_clear(0, END)

        pid = self.onlineNote.handler.add_profile("en-us", self.newUserFileName)
        self.profileDict[self.newUserFileName] = pid
        self.nameDict[pid] = self.newUserFileName

    def deleteSpeakers(self):
        selectItem = self.speakerListBox.curselection()
        for x in selectItem:
            val = self.speakerListBox.get(x, x)[0]
            val = val + ".wav"
            pid = self.profileDict[val]
            self.onlineNote.handler.recognizer.delete_profile(pid)
            self.profileDict.pop(val)
            self.nameDict.pop(pid)
            self.speakerListBox.delete(x, x)
        self.speakerUpdateLabel.config(text='speaker: ' + str(self.speakerListBox.size()))
        self.speakerListBox.selection_clear(0, END)


    def chooseFile(self):
        filePath = tkFileDialog.askopenfilename(title='import file',
                                   filetypes=[("Audio files", "*.wav")],
                                   initialdir='C:/')

        self.filePathEntry.delete(0, END)
        self.filePathEntry.insert(0, filePath)

    def startRecord(self):
        self.onlineNote.isOn = True
        self.onlineNote.start_note()

    def run(self):
        filePath = self.filePathEntry.get()
        self.outputText.delete(1.0, END)
        if self.state == 'run':
            self.runButton.config(state=NORMAL)
            self.runButton.config(text='waiting')
            self.runButton.config(state=DISABLED)
        else:
            self.changeModeButton.config(state=DISABLED)
            self.exportButton.config(state=DISABLED)
            self.filePathEntry.config(state=DISABLED)
            self.fileChooseButton.config(state=DISABLED)
            self.speakerNumberBox.config(state=DISABLED)
            self.addSpeakerButton.config(state=DISABLED)
            self.deleteSpeakerButton.config(state=DISABLED)
            self.runButton.config(text='stop')
            if self.mode == 'offline':
                self.runButton.config(text='running')
                self.runButton.config(state=DISABLED)
        self.master.update()

        if self.mode == 'online':
            if self.state == 'stop':
                self.handleThread = threading.Thread(target=self.startRecord())
                self.handleThread.start()
                self.state = 'run'
            else:
                self.state = 'stop'
                self.onlineNote.end_note()
		self.onlineNote.threads = []
        else:
            a = self.speakerNumberBox.get()
            self.offlineNote.handler(filePath, int(a))
            self.changeModeButton.config(state=NORMAL)
            self.exportButton.config(state=NORMAL)
            self.filePathEntry.config(state=NORMAL)
            self.fileChooseButton.config(state=NORMAL)
            self.speakerNumberBox.config(state=NORMAL)
            self.addSpeakerButton.config(state=NORMAL)
            self.deleteSpeakerButton.config(state=NORMAL)
            self.runButton.config(state=NORMAL)
            self.runButton.config(text='run')
            
            
        self.master.update()

    def saveResult(self):
        filePath = tkFileDialog.asksaveasfilename(title='export file',
                                              filetypes=[("Text files", "*.txt")],
                                              initialdir='C:/',
                                            initialfile='record.txt')
        if filePath:
            file = open(filePath, 'w')
            result = self.outputText.get(1.0, END)
            file.write(result)
            file.close()

    def changeMode(self):
        self.outputText.delete(1.0, END)
        if self.mode == 'offline':
            self.speakerNumberLabel.grid_forget()
            self.speakerNumberBox.grid_forget()
            self.fileLabel.grid_forget()
            self.filePathEntry.grid_forget()
            self.fileChooseButton.grid_forget()
            self.speakerUpdateLabel.config(text='speaker: ' + str(self.speakerListBox.size()))
            self.speakerUpdateLabel.grid(row=0, column=14, columnspan=7, sticky=W)
            self.speakerListBox.grid(row=1, column=15, rowspan=3, columnspan=5, sticky=N+S+W+E)
            self.speakerListBoxScrollBar.grid(row=1, column=17, rowspan=3, sticky=W+N+S)
            self.addSpeakerButton.grid(row=0, column=21, rowspan=2, columnspan=2)
            self.deleteSpeakerButton.grid(row=2, column=21, rowspan=2, columnspan=2)
            self.mode = 'online'
            self.changeModeButton.config(text='online')
        else:
            self.state = 'stop'
            self.runButton.config(text='run')
            self.speakerListBoxScrollBar.grid_forget()
            self.speakerUpdateLabel.grid_forget()
            self.speakerListBox.grid_forget()
            self.addSpeakerButton.grid_forget()
            self.deleteSpeakerButton.grid_forget()
            self.fileLabel.grid(row=1, column=12, rowspan=2, columnspan=2)
            self.filePathEntry.grid(row=1, column=14, rowspan=2, columnspan=7, sticky=W)
            self.fileChooseButton.grid(row=1, column=21, rowspan=2, columnspan=2)
            self.speakerNumberLabel.grid(row=0, column=12, rowspan=2, columnspan=2)
            self.speakerNumberBox.grid(row=0, column=14, rowspan=2, columnspan=7, sticky=W)
            self.mode = 'offline'
            self.changeModeButton.config(text='offline')
        self.master.update()



if __name__ == '__main__':
    app = Application()
    app.master.title('Audio Note')
    app.mainloop()
