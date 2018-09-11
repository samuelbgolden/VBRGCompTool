from tkinter import Entry, Frame, Button, IntVar, Label, FLAT, StringVar, Toplevel
from Styling import *


# entry box that has light gray text in it before entry
# only used in the registration
class EntryWithPlaceholder(Entry):
    def __init__(self, master=None, placeholder='placeholder', color='gray', width=15, *args, **kwargs):
        super().__init__(master, width=width, *args, **kwargs)

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


# a frame that contains tool(s) for selecting the competitor to edit
class CompetitorSelectionFrame(Frame):
    def __init__(self, parent, db, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.db = db

        self.font = ['Tahoma', -0.0345]
        self.font[1] = round(self.font[1] * self.parent.parent.SCREEN_HEIGHT)

        self.buttonTexts = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
                            'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
                            'W', 'X', 'Y', 'Z')

        self.alphabetButtons = []

        blues = (DBLUE, BLUE, BLUE, DBLUE)
        blues = blues*7

        for i in range(0, 26):
            self.alphabetButtons.append(Button(self, text=self.buttonTexts[i], relief=FLAT, activebackground='white',
                                               bg=blues[i], fg='white', font=self.font, bd=0, highlightthickness=0,
                                               command=lambda i=i: self.show_filtered_competitors(self.buttonTexts[i])))
            self.alphabetButtons[i].grid(row=i // 2, column=i % 2, sticky='nsew')
            self.rowconfigure(i // 2, weight=1)
            self.columnconfigure(i % 2, weight=1)

    def show_filtered_competitors(self, letter):
        self.parent.competitorFrame.competitorSearchBar.foc_in()
        self.parent.competitorFrame.competitorSearchBar.insert('end', letter)


# frame containing plus and minus buttons, a number, and an amount of attempts
# used by the RouteAttemptsEntryFrame class
class RouteAttemptsEntry(Frame):
    def __init__(self, parent, num, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.num = num
        self.parent = parent
        self.isActive = False

        self.font = ['Arial', -0.02]
        self.font[1] = round(self.font[1] * self.parent.parent.parent.SCREEN_HEIGHT)
        self.numFont = ['Arial', -0.02, 'bold']
        self.numFont[1] = round(self.numFont[1] * self.parent.parent.parent.SCREEN_HEIGHT)

        self.config(bg=LBLUE)
        self.labelbg = LBLUE
        self.labelfg = 'white'
        self.buttonbg = BLUE
        self.buttonfg = 'white'

        self.plusIcon = '+'
        self.minusIcon = '-'  # im expecting these will be replaced with images in the future
        self.attemptsAmt = IntVar()
        self.attemptsAmt.set(0)

        self.numLabel = Label(self, text='#{}'.format(num), width=3, fg=self.labelfg, bg=self.labelbg, font=self.numFont)
        self.minusButton = Button(self, text=self.minusIcon, fg=self.buttonfg, bg=self.buttonbg, width=2, command=self.minus, font=self.numFont)
        self.attemptsAmtLabel = Label(self, width=2, fg=self.labelfg, bg=self.labelbg, textvariable=self.attemptsAmt, font=self.numFont)
        self.plusButton = Button(self, text=self.plusIcon, width=2, bg=self.buttonbg, fg=self.buttonfg, command=self.plus, font=self.numFont)

        self.numLabel.grid(row=0, column=0, sticky='nsew')
        self.minusButton.grid(row=0, column=1, sticky='nsew')
        self.attemptsAmtLabel.grid(row=0, column=2, sticky='nsew')
        self.plusButton.grid(row=0, column=3, sticky='nsew')

        for i in range(0, 4):
            self.columnconfigure(i, weight=1)
        self.rowconfigure(0, weight=1)

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
        self.numLabel.configure(bg=DDBLUE, fg='white')

    def deactivate(self):
        self.isActive = False
        self.numLabel.configure(bg=self.labelbg, fg=self.labelfg)


# updates table based on entered pattern in search box
class CompetitorSearchBox(EntryWithPlaceholder):
    def __init__(self, parent, *args, **kwargs):
        self.parent=parent

        self.font = ['Tahoma', -0.020]
        self.font[1] = round(self.font[1] * self.parent.parent.parent.SCREEN_HEIGHT)

        self.content = StringVar()
        super().__init__(parent, placeholder='Search competitors...', background=LLBLUE, color=DDBLUE, textvariable=self.content, font=self.font)
        self.parent = parent

        self.content.trace('w', self.update_results)

    def update_results(self, *args):
        self.parent.parent.parent.update_all()

    def clear(self):
        self.delete(0, 'end')


# static method for converting a value to an int (if it can't it becomes 0)
# used in the validation of route numbers and attempt amounts
def mk_int(s):
    s = s.strip()
    try:
        return int(s)
    except ValueError:
        return 0


# will display a toplevel window with info on how to use the QuickCommand line
def show_usage_help():
    window = Toplevel()


def disable_frame(frame):  # loops recursively through all frame children disabling their normal widgets
    for widget in frame.winfo_children():  # gets each widget that is a child of the passed widget
        if widget.winfo_class() == 'Frame':  # if the child is a frame (frames themselves cannot be disabled),
            disable_frame(widget)       # this func is called on that frame
        else:
            widget.configure(state='disable')  # disables widgets that are not frames


def enable_frame(frame):  # loops recursively through all frame children enabling child non-frame widgets
    for widget in frame.winfo_children():  # gets each widget that is a child of the passed widget
        if widget.winfo_class() == 'Frame':  # checks if child widget is a Frame
            enable_frame(widget)  # calls this func on widget if Frame
        else:
            widget.configure(state='normal')  # enables non-Frame widgets
