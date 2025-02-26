import centurion as ct
from colorama import Fore, Style
import pyfiglet
import argparse

import time
import csv
import json
import os



# Settings menu for editing the CSV and JSON file paths
def settings_menu():
    settings = ct.load_settings()
    ct.clear_terminal()  # Clear the terminal each time we show the menu
    print(Fore.YELLOW + "\nSettings Menu" + Style.RESET_ALL)
    print("Current settings: ")
    print(f"-- CSV File Path: {settings['csv_file']}")
    print(f"-- JSON File Path: {settings['json_file']}")
    print(f"-- Reupdate All Entries: {settings['update_all_entries']}")
    

    choice = input(Fore.BLUE + "\nEnter your choice (Enter Number#): \n 1. Change CSV filepath \n 2. Change JSON filepath\n 3. Change UpdateAll Paramater\n 4. Back\n-->" + Style.RESET_ALL).strip()

    if choice == "1":
        new_csv = input(Fore.CYAN + "Enter new CSV file path: " + Style.RESET_ALL).strip()
        ct.update_csv_file(new_csv)
    elif choice == "2":
        new_json = input(Fore.CYAN + "Enter new JSON file path: " + Style.RESET_ALL).strip()
        ct.update_json_file(new_json)
    elif choice == "3":
        if settings["update_all_entries"]:
            new_param = False
        else:
            new_param = True
        
        
        ct.update_param(new_param)

    elif choice == "4":
        return
    else:
        print(Fore.RED + "Invalid choice. Returning to main menu." + Style.RESET_ALL)

def file_processing_menu():
    while True:
        ct.clear_terminal()
        print(Fore.LIGHTBLUE_EX + "\nFile Processing Menu" + Style.RESET_ALL)
        print("Available Options:")
        print(Fore.CYAN + "add_entry" + Style.RESET_ALL + "    \t- Add a URL to the CSV file")
        print(Fore.CYAN + "delete_entry" + Style.RESET_ALL + " \t- Delete a URL from the CSV and JSON files")
        print(Fore.CYAN + "back" + Style.RESET_ALL + "      \t- Return to main menu")
        choice = input(Fore.BLUE + "Enter option: " + Style.RESET_ALL).strip().lower()
        if choice == "back":
            break
        elif choice == "add_entry":
            ct.add_url()
        elif choice == "delete_entry":
            ct.delete_business()
        else:
            print(Fore.RED + "Unknown option. Please try again." + Style.RESET_ALL)
           


def server_functions_menu():
    while True:
        ct.clear_terminal()
        print(Fore.LIGHTBLUE_EX + "\nServer Functions Menu" + Style.RESET_ALL)
        print("Available Options:")
        print(Fore.CYAN + "resolve_deltas" + Style.RESET_ALL + "\t- Run the bash script to resolve deltas")
        print(Fore.CYAN + "process_csv" + Style.RESET_ALL + "\t- Process the CSV file")
        print(Fore.CYAN + "fetch_api" + Style.RESET_ALL + "\t- gets google API information")
        print(Fore.CYAN + "back" + Style.RESET_ALL + "\t- Return to main menu")
        choice = input(Fore.BLUE + "Enter option: " + Style.RESET_ALL).strip().lower()
        if choice == "back":
            break
        elif choice == "resolve_deltas":
            ct.resolve_deltas()
        elif choice == "process_csv":
            ct.process_csv_file()
        elif choice == "fetch_api":
            ct.fetch_from_google_api("Buisnesses in Little portugal")
            input("Hit Enter to continue... ")
        else:
            print(Fore.RED + "Unknown option. Please try again." + Style.RESET_ALL)
            

def cli():
    Style.BRIGHT
    while True:
        # Clear the terminal and print the welcome logo and main menu
        ct.clear_terminal()

        # Print the welcome logo using pyfiglet (bigger font)
        logo = pyfiglet.figlet_format("centurion", font="doh", width =1000)
        print(Fore.LIGHTBLUE_EX + logo + Style.RESET_ALL)
        print(Fore.BLUE + "Welcome to the Centurion CLI, the server manager for Atlas" + Style.RESET_ALL)

        settings = ct.load_settings()
        print(Fore.WHITE + "\nCurrent Settings:" + Style.RESET_ALL)
        print(Fore.CYAN + "CSV File:" + Style.RESET_ALL +  f"{settings['csv_file']}")
        print(Fore.CYAN + "JSON File:" + Style.RESET_ALL + f"{settings['json_file']}")

        # Main menu
        print(Fore.BLUE + "\nAvailable Commands:")
        print(Fore.CYAN + "server_functions" + Style.RESET_ALL + "  \t- Open server executive functions panel")
        print(Fore.CYAN + "file_processing" + Style.RESET_ALL + "    \t- Opens localhost file processing functions")
        print(Fore.CYAN + "master_update" + Style.RESET_ALL + "    \t- Runs All Server Functions, and automatically resolves deltas")
        print(Fore.CYAN + "Settings" + Style.RESET_ALL + "       \t\t- Opens setting/config ")
        
        command = input(Fore.BLUE + "Enter command: " + Style.RESET_ALL).strip()

        if command.lower() == "exit":
            print(Fore.RED + "Exiting Centurion CLI. Goodbye!" + Style.RESET_ALL)
            break
        elif command == "settings":
            settings_menu()
        elif command == "server_functions":
            server_functions_menu()
        elif command == "file_processing":
            file_processing_menu()
        elif command == "master_update":
            ct.fetch_from_google_api("Businesses in little portugal")
            time.sleep(4)
            ct.process_csv_file()
            ct.resolve_deltas()
        else:
            print(Fore.RED + "Unknown command. Please try again." + Style.RESET_ALL)


          

# Argument parsing setup
def parse_args():
    # Initialize argument parser
    parser = argparse.ArgumentParser(description="Scrape Google Maps data")
    
    # Add flags/arguments
    parser.add_argument('--verbose', action='store_true', help='Print verbose output')
    parser.add_argument('--debug', action='store_true', help='Print full stack trace on error')
    parser.add_argument('--addUrl', type=str, help='Adds Url to the Info CSV and then processes its info')
    parser.add_argument('--fast', action='store_true', help='Optimizes centurion by getting rid of text and thread sleep instance for maximum scraping speed')
    # Parse the arguments
    args = parser.parse_args()

if __name__ == '__main__':
    parse_args()
    cli()