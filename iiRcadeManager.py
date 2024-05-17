import subprocess

# Path to the ADB executable
ADB_PATH = "adb"

# Path to the SQLite database
DATABASE_PATH = "/data/data/com.iircade.iiconsole/databases/Game.db"

# Path to the game folder on the device
GAME_FOLDER_PATH = "/sdcard/Game/Games"

def run_adb_command(command):
    try:
        result = subprocess.run([ADB_PATH] + command.split(), capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"ADB command failed: {e.stderr.strip()}")
        return None

def uninstall_game(game_id):
    # Connect to the SQLite database via ADB
    db_command = f"shell sqlite3 {DATABASE_PATH} 'DELETE FROM GAME WHERE ID=\"{game_id}\";'"
    config_command = f"shell sqlite3 {DATABASE_PATH} 'DELETE FROM CONFIG WHERE ID=\"{game_id}\";'"
    
    run_adb_command(db_command)
    run_adb_command(config_command)
    
    if game_id.endswith(".zip"):  # MAME ROM
        # Remove the game file from the game folder
        remove_command = f"shell rm {GAME_FOLDER_PATH}/{game_id}"
        run_adb_command(remove_command)
        print(f"MAME ROM {game_id} uninstalled.")
    else:  # Android application
        # Uninstall the Android application
        uninstall_command = f"uninstall {game_id}"
        run_adb_command(uninstall_command)
        print(f"Android app {game_id} uninstalled.")

def list_installed_games():
    # Query the SQLite database for all games
    query_command = f"shell sqlite3 {DATABASE_PATH} 'SELECT * FROM GAME;'"
    output = run_adb_command(query_command)
    if output:
        games = output.split('\n')
        for game in games:
            details = game.split('|')
            game_number = details[0]
            game_id = details[1]
            game_name = details[3]
            print(f"{game_number}. ID: {game_id}, Name: {game_name}")

def restart_game_launcher():
    # Restart the game launcher
    command = "shell am force-stop com.iircade.iiconsole"
    run_adb_command(command)
    print("Game launcher restarted.")

def reboot_device():
    # Reboot the device
    command = "reboot"
    run_adb_command(command)
    print("Device rebooted.")

def main():
    while True:
        command = input("Enter a command (list/uninstall/restart/reboot/exit): ").strip().lower()
        if command == "list":
            list_installed_games()
        elif command == "uninstall":
            game_id = input("Enter the game ID to uninstall: ").strip()
            uninstall_game(game_id)
        elif command == "restart":
            restart_game_launcher()
        elif command == "reboot":
            reboot_device()
        elif command == "exit":
            break
        else:
            print("Invalid command. Please enter 'list', 'uninstall', 'restart', 'reboot', or 'exit'.")

if __name__ == "__main__":
    main()
