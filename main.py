from tkinter import filedialog as tkFileDialog
import tkinter as tk
from tkinter.messagebox import askyesno as tkAskYesNo
from tkinter.messagebox import showinfo as tkShowInfo


import winsound as wsnd
import csv

from tempfile import NamedTemporaryFile
import shutil
from os import remove as osRem


CONTENT_FILE = "Files/content.csv"
PAGE_LIMIT = 25

FONT_FAMILY = "sans-serif"
FONTS = {"xl":(FONT_FAMILY, 24), "l":(FONT_FAMILY, 20), "m":(FONT_FAMILY, 16), "s":(FONT_FAMILY, 12)}


class AudioManager:
    """This is the controller for the audio files"""
    def __init__ (self):
        self.Files = {} # Name | Filename
        self.LoadFiles()

    def LoadFiles (self):
        self.Files = {}
        with open(CONTENT_FILE) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")

            for row in csv_reader:
                self.Files[row[0]] = row[1]

    def PlaySound (self, filename, loop=False):
        """Play a sound"""
        if loop: # Loop the sound if specified.
            wsnd.PlaySound("Files/Audio/" + filename, wsnd.SND_ASYNC | wsnd.SND_LOOP | wsnd.SND_FILENAME)
        else: #  Dont loop the sound.
            wsnd.PlaySound("Files/Audio/" + filename, wsnd.SND_ASYNC | wsnd.SND_FILENAME)

    def PlaySoundByTitle (self, title, loop=False):
        """Gets the filename when given a title and plays the file"""
        filename = self.Files[title]
        self.PlaySound(filename, loop=loop)

    def StopSound (self):
        """Stop any sound that is currently playing"""
        wsnd.PlaySound(None, wsnd.SND_ASYNC)

    def SoundGenerator (self, max=PAGE_LIMIT, skip=0):
        """Yields filenames that are stored in Files"""
        if max > len(self.Files)-skip:  # If there are less files to loop than the max amount loop through all the files
            iters = 0
            for title, value in self.Files.items():
                if iters < skip:
                    iters += 1
                    continue
                yield title
                iters += 1

        else: # Only loop through until there are the max amount displayed.
            iters = 0
            for title, value in self.Files.items():
                if iters < skip:
                    iters += 1
                    continue
                yield title
                iters += 1
                if iters >= max+skip:
                    break

    def DeleteEntry (self, entryName, deleteAudioFile=False):
        """Delete an entry from the CONTENT_FILE file and then reload the list."""

        # to do this, we create a temporary file and copy every rowe into it from the current file unless that row
        # has the same name as the given name.

        tempfile = NamedTemporaryFile(delete=False)

        with open(CONTENT_FILE) as csvFile, tempfile:
            reader = csv.reader(csvFile, delimiter=",")

            # loop through each element in the current file, checking if the name matches the given name
            # write the row to the temp file if it does match, otherwise ignore that line
            for row in reader:
                if row[0] == entryName:
                    # The name matches, we can delete the file if needed, if not it just dont write to the new file.
                    if deleteAudioFile:
                        # Now delete the audio file if it is set too.
                        osRem("Files/Audio/" + str(row[1]))
                else:
                    tempfile.write(bytes(",".join(row) + "\n", encoding='utf-8'))

        shutil.move(tempfile.name, CONTENT_FILE)

        self.LoadFiles()

    def AddEntry (self, file):
        """Add a audio entry to the file and also move the file to the audio folder, then reload"""
        # split the filename from the path
        filename = file.split("/")[-1]

        # Move the file to the audio folder
        shutil.move(file, "Files/Audio/" + str(filename))

        # Write the new entry to the content file setting the title as the filename without the extension
        with open(CONTENT_FILE, "a") as content:
            content.write(filename.replace(".wav", "") + "," + filename)

        # Reload the files list
        self.LoadFiles()


class Window (tk.Tk):
    """This is the main window handler."""
    def __init__ (self, *args, **kwargs):
        tk.Tk.__init__(self, *args, *kwargs)

        # Configure window
        self.title("Soundboard")
        self.geometry("1475x735")
        self.minsize(1475, 735)

        # Create the audio manager object
        self.AudioManager = AudioManager()

        # Create the page container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Create the pages holder and setup pages
        self.Pages = {}
        for page in (Home, AddRemoveAudio):
            p = page(container, self)
            self.Pages[page.pageName] = p

            p.grid(row=0, column=0, sticky="nsew")

        # Display the home page
        self.showPage("home")

    def showPage(self, pageName):
        """This function brings the chosen page to the top."""
        page = self.Pages[pageName]
        page.tkraise()
        page.PageUpdate()
        page.focus_set()


class Home (tk.Frame):
    """This is the home page of the App"""

    # This name will be used to store and navigate between pages
    pageName = "home"

    # Rows and columns of sound buttons to be displayed
    ROWS = 5
    COLS = 5

    def __init__ (self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller

        # Setup the button container and then the buttons
        self.Buttons = [] # Stored as an attribute of page so that it can be changed on the fly.
        buttonContainer = tk.Frame(self)
        buttonContainer.pack(side="top", fill="both")
        buttonContainer.grid_propagate(True)
        for _row in range(self.ROWS):
            this_row = []
            for _col in range(self.COLS):
                # Create the button and store it in the row placeholder
                btn = tk.Button(buttonContainer, text="*****", width=15, height=3, font=FONTS["xl"])
                btn.grid(row=_row, column=_col, sticky="nsew")
                this_row.append(btn)
            # Add the row to the column in the buttons holder.
            self.Buttons.append(this_row)

        # Load the titles of the sounds onto the buttons and connect the buttons to the SoundManager when clicked.
        self.loadNames()

        # The control panel at the bottom.
        controlPanel = tk.Frame(self, bg="#757575")
        controlPanel.pack(side="bottom", fill="x")

        # Stops any sound from being played.
        stopBtn = tk.Button(controlPanel, text="STOP", font=FONTS["xl"],
                            command=lambda: self.controller.AudioManager.StopSound())
        stopBtn.pack(side="left")

        # Loops the sound.
        self.doLoop = False
        self.loopBtn = tk.Button(controlPanel, text="Loop", font=FONTS["xl"],
                                 command=lambda:self.LoopClick())
        # Made an attribute of the class so that we can access it it and change the visuals later to show it is selected
        self.loopBtn.pack(side="left")

        # Edit Audio Files Page
        edit = tk.Button(controlPanel, text="Edit Audio Files", font=FONTS["xl"],
                         command=lambda: self.controller.showPage("addremaudio"))
        edit.pack(side="left")

        # Page Navigation Buttons
        self.PageNumber = 0

        nextBtn = tk.Button(controlPanel, text="-->", font=FONTS["xl"],
                            command=lambda: self.nextPage())
        nextBtn.pack(side="right")

        self.PageText = tk.Label(controlPanel, text="Page: 1", bg="#757575", font=FONTS["xl"])
        self.PageText.pack(side="right")

        prevBtn = tk.Button(controlPanel, text="<--", font=FONTS["xl"],
                            command=lambda: self.prevPage())
        prevBtn.pack(side="right")

        self.bind("<Left>", lambda event: self.__prevPageBind(event))
        self.bind("<Right>", lambda event: self.__nextPageBind(event))

    def PageUpdate(self):
        """Run an entire page update, mostly used by the controller when changing pages."""

        self.PageNumber = 0
        self.loadNames(self.PageNumber)

    def loadNames (self, pageNumber=0):
        """Loads the names into the buttons"""
        row = 0
        col = 0

        # Loop through all the titles and then update the button to reflect the title.
        for title in self.controller.AudioManager.SoundGenerator(skip=pageNumber*PAGE_LIMIT):
            if len(title) > 19:
                dispTitle = title[0:17] + "..."
            else:
                dispTitle = title

            self.Buttons[row][col].configure(text=dispTitle)
            self.Buttons[row][col].configure(command=lambda t=title: self.playSoundName(t))
            # Increase the column
            col += 1
            # If the column num is greater than the columns for this page, then reset to zero and increase the row.
            if col >= self.COLS:
                row += 1
                col = 0
                # if the rows are greater than the max amount for this page, break out the loop as all is filled.
                if row >= self.ROWS:
                    break
        else:
            # Check if it never looped or if the rows have been completed. return False if so
            # return False shows that this page had no elements
            if row >= self.ROWS or (col == 0 and row == 0):
                return False

        # Fill in the rest of the buttons with a placeholder text and clear the command
        while row < self.ROWS:
            if col >= self.COLS:
                col = 0
                row += 1
                if row >= self.ROWS:
                    break
            self.Buttons[row][col].configure(text="*****")
            self.Buttons[row][col].configure(command=lambda: None)
            col += 1

        # Return true to show that this page has elements
        return True

    def __nextPageBind(self, event):
        """function for the keybind"""
        self.nextPage()

    def __prevPageBind(self, event):
        """function for the keybind"""
        self.prevPage()

    def nextPage(self):
        """Try to change page, if it works page number increases"""
        if self.loadNames(pageNumber=self.PageNumber+1):
            self.PageNumber += 1
            self.PageText.configure(text="Page: " + str(self.PageNumber+1))

    def prevPage(self):
        """If the page isn't already 0, decrease the page and then decrease the page number"""
        if self.PageNumber >= 1:
            self.PageNumber -= 1
            self.PageText.configure(text="Page: " + str(self.PageNumber + 1))

        self.loadNames(pageNumber=self.PageNumber)

    def LoopClick(self):
        """Change the loop variable so that the sounds been looped"""
        # Switch the loop variable to the inverse of its  current state.
        self.doLoop = not self.doLoop

        # Update the button colour so that the user knows the state.
        if self.doLoop:
            self.loopBtn.configure(bg="#ee0000")
        else:
            self.loopBtn.configure(bg="#eeeeee")

    def playSoundName (self, name):
        """Runs the audio managers play sound function with the name of the audio"""
        self.controller.AudioManager.PlaySoundByTitle(name, loop=self.doLoop)


class AddRemoveAudio (tk.Frame):
    """This is the other page of the App"""

    pageName = "addremaudio"

    maxPerPage = 13

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller

        # Content frames
        contentFrame = tk.Frame(self)
        contentFrame.pack(side="top", fill="both")

        # Navigation
        navigationPanel = tk.Frame(contentFrame)
        navigationPanel.pack(side="top", fill="x")

        pageBack = tk.Button(navigationPanel, text="<--", width=15, bg="#aaaaaa", font=FONTS["xl"],
                                command=lambda: self.prevPage())
        pageBack.pack(side="left")

        self.PageNumber = 0

        self.PageText = tk.Label(navigationPanel, text="Page: " + str(self.PageNumber + 1), font=FONTS["xl"])
        self.PageText.pack(side="left")

        pageForward = tk.Button(navigationPanel, text="-->", width=15, bg="#aaaaaa", font=FONTS["xl"],
                                command=lambda: self.nextPage())
        pageForward.pack(side="right")

        # Control Buttons
        self.buttonsPanel = tk.Frame(contentFrame)
        self.buttonsPanel.pack(side="top", pady=10)

        self.loadButtons()

        # The bottom control panel
        controlPanel = tk.Frame(self, bg="#757575")
        controlPanel.pack(side="bottom", fill="x")

        # Add button to add a new audio
        add = tk.Button(controlPanel, text="Add New Audio", font=FONTS["xl"],
                        command=lambda: self.AddElement())
        add.pack(side="left")

        # Back to the sound buttons page
        bkButton = tk.Button(controlPanel, text="Back", font=FONTS["xl"],
                             command=lambda: self.controller.showPage("home"))
        bkButton.pack(side="right")

    def PageUpdate(self):
        """Run an entire page update, mostly used by the controller when changing pages."""

        self.PageNumber = 0
        self.loadButtons(self.PageNumber)

    def loadButtons (self, pageNumber=0):
        """load the names of the buttons"""

        # Clear all the current elements
        for widget in self.buttonsPanel.winfo_children():
            widget.destroy()

        row = 0

        # Loop through all the available titles for the given page and create a label and relevant buttons
        for title in self.controller.AudioManager.SoundGenerator(max=self.maxPerPage, skip=pageNumber*self.maxPerPage):
            tk.Label(self.buttonsPanel, text=title, font=FONTS["l"]).grid(row=row, column=0, sticky="nsew")

            tk.Button(self.buttonsPanel, text="Remove", font=FONTS["m"],
                      command=lambda t=title: self.DeleteElement(t)).grid(row=row, column=1, sticky="nsew")
            tk.Button(self.buttonsPanel, text="Rename", font=FONTS["m"]).grid(row=row, column=2, sticky="nsew")
            row += 1

        # Tell the user than there is no audio files if none have been found!
        if pageNumber == 0 and row == 0:
            txt = "No audio files are available.\nAdd one now by pressing the 'Add new audio' button below."
            tk.Label(self.buttonsPanel,
                text=txt).grid(row=0, column=0, columnspan=3)
            return False
        elif row == 0:
            return False

        return True

    def AddElement (self):
        """Add a new audio entry"""
        file = tkFileDialog.askopenfilename(title="Select audio file", filetypes=(("Wav files", "*.wav"),))

        self.controller.AudioManager.AddEntry(file)

    def DeleteElement (self, elementName):
        """Deletes an audio entry from the content file."""

        # Ask the user if they are sure.
        result = tkAskYesNo("Delete " + elementName, "Are you sure you want to delete {0}?".format(elementName), icon="warning")
        if result:
            self.controller.AudioManager.DeleteEntry(elementName)
        else:
            tkShowInfo("Update!", "{0} has NOT been deleted!".format(elementName))

        self.loadButtons(pageNumber=self.PageNumber)

    # TODO add the rename function

    def nextPage (self):
        """Move to the next page if there are elements there."""
        if self.loadButtons(self.PageNumber+1):
            self.PageNumber += 1
        else:
            self.loadButtons(self.PageNumber)

        self.PageText.configure(text="Page: " + str(self.PageNumber+1))

    def prevPage (self):
        """Move to the previous page if not already on the 1st (0th) page"""
        if self.PageNumber > 0:
            self.PageNumber -= 1
            self.loadButtons(self.PageNumber)
        self.PageText.configure(text="Page: " + str(self.PageNumber+1))



if __name__ == "__main__":
    window = Window()
    window.mainloop()