# Notes

A simple desktop app for writing and organizing personal notes. 
Built with Python and PyQt6, with all notes stored locally in a SQLite database.

## Features
- Create, edit, and delete notes
- Bold and underline text formatting
- Notes are listed in a sidebar, with the most recent note at the top
- Warns before discarding unsaved changes
- All data stored locally
- Soft pink theme with custom serif fonts (EB Garamond / Cormorant Garamond)

## Requirements
- Python 3.10 or newer
- Windows 10/11

## Getting Started
1. **Clone the repository**
   ```bash
   git clone https://github.com/systemfel13/notes-app.git
   cd notes-app
   ```

2. **Create a virtual environment and activate it**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```bash
   python main.py
   ```

   The database file (`notes.db`) is created automatically on first launch.

## Desktop Shortcut
To create a shortcut on your Windows desktop, run:

```bash
python create_shortcut.py
```

This creates a `.lnk` file on your desktop that launches the app without showing a terminal window.
You can pin it to the taskbar by right-clicking the shortcut and selecting **Show more options > Pin to taskbar**.

