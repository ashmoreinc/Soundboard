import tkinter as tk
import threading

class GetInput:
    """Creates a new window to get the input from a question answer is saved to Data attribute"""
    def __init__ (self, parent, title=None, question=None, font=None):
        top = self.top = tk.Toplevel(parent)

        if title:
            top.title(str(title))

        if question:
            _questionBox = tk.Label(top, text=str(question))
            if font:
                try:
                    _questionBox.configure(font=font)
                except:
                    raise TypeError("font must be a tuple in format (font-family [str], font-size [int])")

            _questionBox.pack(side="top", fill="x")

        self.Entry = tk.Entry(top, font=font)
        self.Entry.pack(side="top", fill="x")

        buttonFrame = tk.Frame(top)
        buttonFrame.pack(side="top", fill="x")

        # Enter Button
        tk.Button(top, text="Enter", font=font,
                  command=lambda: self.Enter()).pack(side="left")

        # Cancel Button
        tk.Button(top, text="Cancel", font=font,
                  command=lambda: self.Cancel()).pack(side="right")

        self.Data = None

    def Enter(self):
        """Function run when the enter key is pressed."""
        self.Data = self.Entry.get()
        self.KillSelf()

    def Cancel(self):
        """Function run when cancel is pressed."""
        print("Cancelled!")
        self.KillSelf()

    def KillSelf(self):
        """Destroys the main holding window"""
        self.top.destroy()
