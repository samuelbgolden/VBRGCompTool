from tkinter import Entry, Frame, Button, IntVar, Label


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


def mk_int(s):
    s = s.strip()
    try:
        return int(s)
    except ValueError:
        return 0

