# 📘 **PythoNauts Assistant CLI**

**PythoNauts Assistant CLI** — is a console assistant that allows you to:
- store contacts (phones, emails, addresses, birthdays)
- manage notes with tags
- search and view records
- use command auto-completion
- conveniently work with colored terminal hints
- show contact list in a table view

The application works locally and saves your data in  
**`~/.pn-assistant/addressbook.pkl`**, regardless of your operating system.

---

## 🚀 Installation

### 1. Install via PyPI (recommended)

```

pip install pn-assistant

```

### 2. Run the program

After installation, a new command becomes available:

```

pn-assistant

```

This launches the PythoNauts Assistant CLI interface.

---

## 📂 Where are data stored?

Contacts and notes are stored not in the package, but in your home directory:

- Linux / macOS: `/home/USER/.pn-assistant/addressbook.pkl`
- Windows: `C:\Users\USER\.pn-assistant\addressbook.pkl`

The file is created automatically.

---

## 📜 Main Features

### 👥 **Contact Management**
```
       Action       |         Command
--------------------------------------------------------
Add contact         | `add John 380991234567`
Change phone        | `change John 380991234567 0671234567`
Delete contact      | `delete John`
Show phone          | `phone John`
Show email          | `email John`
Show birthday       | `birthday John`
Show full info      | `contact John`
Show all contacts   | `all`
```

### ✉ **Email**
```
     Action      |            Command
--------------------------------------------------------
Add email        | `add-email John example@gmail.com`
Change email     | `change-email John old@gmail.com new@gmail.com`
Delete email     | `delete-email John example@gmail.com`
```

### 🎂 **Birthdays**
```
            Action           |     Command
--------------------------------------------------------
Add birthday                 | `add-birthday John 2000-01-31`
Show birthday                | `birthday John`
Birthdays within next 7 days | `birthdays`
Within the next 35 days      | `birthdays 35`
```

### 🏠 **Addresses**
```
   Action     |     Command
--------------------------------------------------------
Add address   | `add-address John Kyiv, Lesi Ukrainky 12`
```

### 📝 **Notes**
```
      Action      |     Command
--------------------------------------------------------
Add note          | `add-note`
Delete note       | `delete-note`
Edit note         | `change-note`
Find by title     | `find-note-by-title`
Find by tag       | `find-note-by-tag`
Show all notes    | `all-notes`
```

### 🤖 **General Commands**
```
    Action    |     Command
--------------------------------------------------------
Greeting      | `hello`
Exit          | `exit` or `close`
Help          | `help`
```

### 🧩 **Command Auto-completion**

The application supports:
- suggestions while typing (tab to complete)
- nearest command search (`Did you mean..?`)
- a colored interface (via `colorama`)
- output of contacts as a table (using `prettytable`)

---
## ❓ FAQ

Where are my contacts stored?
```
~/.pn-assistant/addressbook.pkl (Linux/macOS) 
or
C:\Users\USER\.pn-assistant\addressbook.pkl (Windows).
```
Why do I still see old data after uninstalling the package?
```
Data remains in addressbook.pkl. To start fresh — delete this file.
```
Can I transfer my data to another computer?
```
Yes, copy addressbook.pkl to the same location on the new machine.
```
How do I add a new command or change the assistant’s behavior?
```
Edit the code in src/personal_assistant and 
reinstall the package locally (pip install -e .).
```
## ⌨️ Quick Usage Examples

#### Add a contact
`pn-assistant> add John 380991234567`

#### Add an email
`pn-assistant> add-email John john@gmail.com`

#### Check birthday
`pn-assistant> birthday John`

#### View all contacts
`pn-assistant> all`

## 💠 System Requirements
- Python ≥ 3.9
- Packets: colorama, prettytable, prompt_toolkit, wcwidth
- Works on Linux, macOS and Windows

## 📦 Project Structure (for developers)

```
personal-assistant/
│
├── src/personal_assistant/
│   ├── addressbook.py
│   ├── colorize.py
│   ├── command_use.py
│   ├── commands.py
│   ├── errors.py
│   ├── fields.py
│   ├── input_parser.py
│   ├── main.py
│   ├── notes.py
│   ├── pickle_data.py
│   ├── record.py
│   ├── utils.py
│   └── **init**.py
│
├── pyproject.toml
├── setup.cfg
├── requirements.txt
└── README.md
```

## 🛠 Development & Local Installation

### Clone the repository

```
git clone https://github.com/yulikafsd/personal_assistant
cd personal_assistant
```

### Local installation in development mode

```
pip install -e .
```

### Run the local version

```
assistant
```

---

## 📤 Publishing to PyPI

### Build the distribution

```
python -m build
```

### Upload

```
twine upload dist/*
```

---

## 📝 License & Contribution
The project is licensed under **MIT License**.
Contributions: via pull request or issue on GitHub.

---

## ❤️ Authors

Team **PythoNauts**  
Your personal CLI assistant for working with contacts and notes.

## 📫 Contact / Support
- GitHub: https://github.com/yulikafsd/personal_assistant
- Email: ju.zagorovsky@gmail.com