import tkinter as tk
import winsound as wsnd
import csv


CONTENT_FILE = "Files/content.csv"
PAGE_LIMIT = 25

class AudioManager:
    """This is the controller for the audio files"""
    def __init__ (self):
        self.Files = {} # Name | Filename
        self.LoadFiles()

    def LoadFiles (self):
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


class Window (tk.Tk):
    """This is the main window handler."""
    def __init__ (self, *args, **kwargs):
        tk.Tk.__init__(self, *args, *kwargs)

        # Configure window
        self.title("Soundboard")

        # Create the audio manager object
        self.AudioManager = AudioManager()

        # Create the page container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Create the pages holder and setup pages
        self.Pages = {}
        for page in (Home, Other):
            p = page(container, self)
            self.Pages[page.pageName] = p

            p.grid(row=0, column=0, sticky="nsew")

        # Display the home page
        self.showPage("home")

    def showPage(self, pageName):
        """This function brings the chosen page to the top."""
        page = self.Pages[pageName]
        page.tkraise()


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
                btn = tk.Button(buttonContainer, text=str(_col + _row*5 + 1), font=("sans-serif", 24))
                btn.grid(row=_row, column=_col, sticky="nsew")
                this_row.append(btn)
            # Add the row to the column in the buttons holder.
            self.Buttons.append(this_row)

        # Load the titles of the sounds onto the buttons and connect the buttons to the SoundManager when clicked.
        self.loadNames()

        # The control panel at the bottom.
        controlPanel = tk.Frame(self)
        controlPanel.pack(side="bottom", fill="x")

        # Stops any sound from being played.
        stopBtn = tk.Button(controlPanel, text="STOP", font=("sans-serif", 24),
                            command=lambda: self.controller.AudioManager.StopSound())
        stopBtn.pack(side="left")

        # Loops the sound.
        self.doLoop = False
        self.loopBtn = tk.Button(controlPanel, text="Loop", font=("sans-serif", 24),
                                 command=lambda:self.LoopClick())
        # Made an attribute of the class so that we can access it it and change the visuals later to show it is selected
        self.loopBtn.pack(side="left")

        # Page Navigation Buttons
        self.PageNumber = 0

        nextBtn = tk.Button(controlPanel, text="-->", font=("sans-serif", 24),
                            command=lambda: self.nextPage())
        nextBtn.pack(side="right")

        self.PageText = tk.Label(controlPanel, text="Page: 1", font=("sans-serif", 24))
        self.PageText.pack(side="right")

        prevBtn = tk.Button(controlPanel, text="<--", font=("sans-serif", 24),
                            command=lambda: self.prevPage())
        prevBtn.pack(side="right")

    def loadNames (self, pageNumber=0):
        """Loads the names into the buttons"""
        row = 0
        col = 0

        # Loop through all the titles and then update the button to reflect the title.
        for title in self.controller.AudioManager.SoundGenerator(skip=pageNumber*PAGE_LIMIT):
            self.Buttons[row][col].configure(text=title)
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
            self.Buttons[row][col].configure(command=None)
            col += 1

        # Return true to show that this page has elements
        return True

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
            self.loopBtn.configure(bg="#ffffff")

    def playSoundName (self, name):
        """Runs the audio managers play sound function with the name of the audio"""
        self.controller.AudioManager.PlaySoundByTitle(name, loop=self.doLoop)


class Other (tk.Frame):                     # This page will likely be for the adding and removing of files in real-time
    """This is the other page of the App"""

    pageName = "other"

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller


if __name__ == "__main__":
    window = Window()
    window.mainloop()