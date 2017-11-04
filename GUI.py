from tkinter import *
from tkinter import filedialog
from tkinter.scrolledtext import ScrolledText


class Application(Frame):
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
        self.offLineModeButton = Button(self, text='离线模式', command=self.changeToOffLineMode)
        self.offLineModeButton.grid(row=0, column=0, rowspan=2, columnspan=2)
        self.offLineModeButton = Button(self, text='在线模式', command=self.changeToOnLineMode)
        self.offLineModeButton.grid(row=0, column=2, rowspan=2, columnspan=2)
        self.fileChooseButton = Button(self, text='开始运行', command=self.run)
        self.fileChooseButton.grid(row=2, column=0, rowspan=2, columnspan=2)
        self.fileChooseButton = Button(self, text='导出结果', command=self.saveResult)
        self.fileChooseButton.grid(row=2, column=2, rowspan=2, columnspan=2)
        self.hideBackground(12, 0, 9, 3)
        self.fileLabel = Label(self, text='文件地址:')
        self.fileLabel.grid(row=1, column=12, rowspan=2, columnspan=2)
        self.filePathEntry = Entry(self)
        self.filePathEntry.grid(row=1, column=14, rowspan=2, columnspan=7, sticky=W)
        self.fileChooseButton = Button(self, text='选择文件', command=self.chooseFile)
        self.fileChooseButton.grid(row=1, column=19, rowspan=2, columnspan=2)
        self.speakerNumberLabel = Label(self, text='预设人数:')
        self.speakerNumberLabel.grid(row=0, column=12, rowspan=2, columnspan=2)
        self.speakerNumberBox = Spinbox(self, from_ = 0, to = 100, increment = 1)
        self.speakerNumberBox.grid(row=0, column=14, rowspan=2, columnspan=7, sticky=W)
        self.hideBackground(1, 4, 19, 10)
        self.outputLabel = Label(self, text='输出：')
        self.outputLabel.grid(row=4, column=1)
        self.outputText = ScrolledText(self)
        self.outputText.grid(row=5, column=1, rowspan=9, columnspan=19)
        self.outputText.config(state=DISABLED)

        # initial widgets for online mod
        self.speakerUpdateLabel= Label(self, text='发言者： 0')
        self.speakerListBoxScrollBar = Scrollbar(self, orient=VERTICAL)
        self.speakerListBox = Listbox(self, selectmode=EXTENDED, height=5, yscrollcommand=self.speakerListBoxScrollBar.set)
        self.speakerListBoxScrollBar.config(command=self.speakerListBox.yview)
        self.addSpeakerButton = Button(self, command=self.addSpeaker, text='添加发言者')
        self.deleteSpeakerButton = Button(self, command=self.deleteSpeakers, text='删除发言者')

    def addSpeaker(self):

        self.speakerUpdateLabel.config(text='发言者： ' + str(self.speakerListBox.size()))
        self.speakerListBox.selection_clear(0, END)

    def deleteSpeakers(self):
        selectItem = self.speakerListBox.curselection()
        for x in selectItem:
            self.speakerListBox.delete(x, x)
        self.speakerUpdateLabel.config(text='发言者： ' + str(self.speakerListBox.size()))
        self.speakerListBox.selection_clear(0, END)

    def chooseFile(self):
        filePath = filedialog.askopenfilename(title='选择文件',
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
        filePath = filedialog.asksaveasfilename(title='导出结果',
                                              filetypes=[("Text files", "*.txt")],
                                              initialdir='C:/',
                                            initialfile='记录.txt')
        file = open(filePath, 'w')
        file.write(self.result)
        file.close()

    def changeToOnLineMode(self):
        if self.mode == 'offline':
            self.speakerNumberLabel.grid_forget()
            self.speakerNumberBox.grid_forget()
            self.showBackground(12, 2, 9, 1)
            self.hideBackground(4, 0, 3, 1)
            self.speakerUpdateLabel.config(text='发言者： ' + str(self.speakerListBox.size()))
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
            self.showBackground(4, 0, 8, 4)
            self.showBackground(12, 3, 7, 1)
            self.hideBackground(12, 2, 9, 1)
            self.mode = 'offline'



if __name__ == '__main__':
    app = Application()
    app.master.title('Audio Note')
    app.mainloop()