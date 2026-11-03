import tkinter as tk
from database import create_schema
from gui import CampusHubApp

def main():
    #Ensure the database and tables are created before the app opens
    create_schema()

    #Launch the Tkinter GUI
    root = tk.Tk()
    app = CampusHubApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
