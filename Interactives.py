from tkinter import Entry, StringVar, Listbox, ACTIVE, END, Frame, Button, IntVar, Label
import re


class EntryWithPlaceholder(Entry):
    def __init__(self, master=None, placeholder='placeholder', color='grey', width=15):
        super().__init__(master, width=width)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()

    def replace_placeholder(self):
        self.delete('0', 'end')
        self.put_placeholder()


class AutocompleteEntry(Entry):
    def __init__(self, master=None, autocompleteList=None, *args, **kwargs):

        # Listbox length
        if 'listboxLength' in kwargs:
            self.listboxLength = kwargs['listboxLength']
            del kwargs['listboxLength']
        else:
            self.listboxLength = 8

        # Custom matches function
        if 'matchesFunction' in kwargs:
            self.matchesFunction = kwargs['matchesFunction']
            del kwargs['matchesFunction']
        else:
            def matches(fieldValue, acListEntry):
                pattern = re.compile('.*' + re.escape(fieldValue) + '.*', re.IGNORECASE)
                return re.match(pattern, acListEntry)

            self.matchesFunction = matches

        Entry.__init__(self, master, *args, **kwargs)
        self.focus()

        self.autocompleteList = autocompleteList

        self.var = self["textvariable"]
        if self.var == '':
            self.var = self["textvariable"] = StringVar()

        self.var.trace('w', self.changed)
        self.bind("<Right>", self.selection)
        self.bind("<Up>", self.moveUp)
        self.bind("<Down>", self.moveDown)

        self.listboxUp = False

    def changed(self, name, index, mode):
        if self.var.get() == '':
            if self.listboxUp:
                self.listbox.destroy()
                self.listboxUp = False
        else:
            words = self.comparison()
            if words:
                if not self.listboxUp:
                    self.listbox = Listbox(width=self["width"], height=self.listboxLength)
                    self.listbox.bind("<Button-1>", self.selection)
                    self.listbox.bind("<Right>", self.selection)
                    self.listbox.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
                    self.listboxUp = True

                self.listbox.delete(0, END)
                for w in words:
                    self.listbox.insert(END, w)
            else:
                if self.listboxUp:
                    self.listbox.destroy()
                    self.listboxUp = False

    def selection(self, event):
        if self.listboxUp:
            self.var.set(self.listbox.get(ACTIVE))
            self.listbox.destroy()
            self.listboxUp = False
            self.icursor(END)

    def moveUp(self, event):
        if self.listboxUp:
            if self.listbox.curselection() == ():
                index = '0'
            else:
                index = self.listbox.curselection()[0]

            if index != '0':
                self.listbox.selection_clear(first=index)
                index = str(int(index) - 1)

                self.listbox.see(index)  # Scroll!
                self.listbox.selection_set(first=index)
                self.listbox.activate(index)

    def moveDown(self, event):
        if self.listboxUp:
            if self.listbox.curselection() == ():
                index = '0'
            else:
                index = self.listbox.curselection()[0]

            if index != END:
                self.listbox.selection_clear(first=index)
                index = str(int(index) + 1)

                self.listbox.see(index)  # Scroll!
                self.listbox.selection_set(first=index)
                self.listbox.activate(index)

    def comparison(self):
        return [w for w in self.autocompleteList if self.matchesFunction(self.var.get(), w)]


class RouteAttemptsEntry(Frame):
    def __init__(self, parent, num, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.num = num
        self.parent = parent
        self.isActive = False

        self.plusIcon = '+'
        self.minusIcon = '-'  # im expecting these will be replaced with imgs in the future
        self.attemptsAmt = IntVar()
        self.attemptsAmt.set(0)

        self.numLabel = Label(self, text='#{}'.format(num), width=3)
        self.minusButton = Button(self, text=self.minusIcon, width=2, command=self.minus)
        self.attemptsAmtLabel = Label(self, width=2, textvariable=self.attemptsAmt)
        self.plusButton = Button(self, text=self.plusIcon, width=2, command=self.plus)

        self.numLabel.pack(side='left')
        self.minusButton.pack(side='left')
        self.attemptsAmtLabel.pack(side='left')
        self.plusButton.pack(side='left')

    def plus(self):
        if self.attemptsAmt.get() > 0:
            self.attemptsAmt.set(self.attemptsAmt.get() + 1)
        elif self.parent.not_five_routes_selected():
            self.attemptsAmt.set(self.attemptsAmt.get() + 1)
            self.activate()
        self.parent.parent.competitorInfoFrame.update_from_route_buttons()

    def minus(self):
        if self.attemptsAmt.get() != 0:
            self.attemptsAmt.set(self.attemptsAmt.get() - 1)
        if self.attemptsAmt.get() == 0:
            self.deactivate()
        self.parent.parent.competitorInfoFrame.update_from_route_buttons()

    def activate(self):
        self.isActive = True
        self.numLabel.configure(bg='green', fg='white')

    def deactivate(self):
        self.isActive = False
        self.numLabel.configure(bg='SystemButtonFace', fg='black')
