# Task Tracker CLI

A simple command-line task tracker built in Python.  
It allows you to add, update, delete, and track tasks directly from the terminal.  
Tasks are stored locally in a JSON file.

This project was created to practice working with:
- Command-line interfaces (CLI)
- File system operations
- JSON data persistence
- Input validation and error handling

---

## Features

- Add, update, and delete tasks
- Mark tasks as todo, in-progress, or done
- List all tasks
- Filter tasks by status
- Data is stored locally in a JSON file
- No external libraries required

---

## Project Structure

task-tracker-cli/
├── task_cli.py
├── tasks.json
├── .gitignore
└── README.md


`tasks.json` is created automatically when the program runs and is not committed to the repository.

---

## Requirements

- Python 3.9 or higher
- No external dependencies

---

## How to Run

From the project directory, run:

```bash
python task_cli.py <command> [arguments]
