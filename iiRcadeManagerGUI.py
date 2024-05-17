import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog

# Path to the ADB executable
ADB_PATH = "adb"

# Path to the SQLite database
DATABASE_PATH = "/data/data/com.iircade.iiconsole/databases/Game.db"

# Path to the game folder on the device
GAME_FOLDER_PATH = "/sdcard/Game/Games"

def run_adb_command(command):
    try:
        result = subprocess.run([ADB_PATH] + command.split(), capture_output=True, text=True)
        if result.returncode != 0:
            messagebox.showerror("Error", f"ADB command failed: {result.stderr.strip()}")
            return None
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"ADB command failed: {e.stderr.strip()}")
        return None

def uninstall_game(game_id):
    db_command = f"shell sqlite3 {DATABASE_PATH} 'DELETE FROM GAME WHERE ID=\"{game_id}\";'"
    config_command = f"shell sqlite3 {DATABASE_PATH} 'DELETE FROM CONFIG WHERE ID=\"{game_id}\";'"
    
    if run_adb_command(db_command) is None:
        return
    if run_adb_command(config_command) is None:
        return
    
    if game_id.endswith(".zip"):  # MAME ROM
        remove_command = f"shell rm {GAME_FOLDER_PATH}/{game_id}"
        if run_adb_command(remove_command) is not None:
            messagebox.showinfo("Success", f"MAME ROM {game_id} uninstalled.")
    else:  # Android application
        uninstall_command = f"uninstall {game_id}"
        if run_adb_command(uninstall_command) is not None:
            messagebox.showinfo("Success", f"Android app {game_id} uninstalled.")

def list_installed_games():
    query_command = f"shell sqlite3 {DATABASE_PATH} 'SELECT * FROM GAME;'"
    output = run_adb_command(query_command)
    if output:
        games = output.split('\n')
        game_listbox.delete(0, tk.END)
        for game in games:
            details = game.split('|')
            game_number = details[0]
            game_id = details[1]
            game_name = details[3]
            game_listbox.insert(tk.END, f"Number: {game_number}, ID: {game_id}, Name: {game_name}")

def restart_game_launcher():
    command = "shell am force-stop com.iircade.iiconsole"
    if run_adb_command(command) is not None:
        messagebox.showinfo("Success", "Game launcher restarted.")

def reboot_device():
    command = "reboot"
    if run_adb_command(command) is not None:
        messagebox.showinfo("Success", "Device rebooted.")

def uninstall_game_prompt():
    selected = game_listbox.curselection()
    if not selected:
        messagebox.showwarning("Warning", "No game selected.")
        return

    selected_index = selected[0]
    game_info = game_listbox.get(selected_index)
    game_id = game_info.split(", ID: ")[1].split(", Name:")[0]
    game_name = game_info.split(", Name: ")[1]

    confirm = messagebox.askyesno("Confirm Uninstall", f"Are you sure you want to uninstall the game '{game_name}'?")
    if confirm:
        uninstall_game(game_id)
        list_installed_games()

# Create the main window
root = tk.Tk()
root.title("iiRcade Game Manager")

# Create a frame for the buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# List games button
list_button = tk.Button(button_frame, text="List Games", command=list_installed_games)
list_button.pack(side=tk.LEFT, padx=5)

# Uninstall game button
uninstall_button = tk.Button(button_frame, text="Uninstall Game", command=uninstall_game_prompt)
uninstall_button.pack(side=tk.LEFT, padx=5)

# Restart game launcher button
restart_button = tk.Button(button_frame, text="Restart Launcher", command=restart_game_launcher)
restart_button.pack(side=tk.LEFT, padx=5)

# Reboot device button
reboot_button = tk.Button(button_frame, text="Reboot Device", command=reboot_device)
reboot_button.pack(side=tk.LEFT, padx=5)

# Create a listbox to display the list of games
game_listbox = tk.Listbox(root, width=80, height=20)
game_listbox.pack(pady=10)

# Run the application
root.mainloop()
