from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from colorama import Fore, Style, init
import subprocess
import time
import json
import os
import csv
#special import for loading bar, yes its lazy
from tqdm import tqdm
# Function to clear the terminal screen
def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


#load settings into memory
settings_file = 'settings.json'

# Default settings structure
default_settings = {
    "csv_file": "info.csv",
    "json_file": "image_scrape_result.json",
    "update_all_entries" : False
}






##START OF: MAIN CSV PARSING AND SCRAPING FUNCTIONALITY
#------------------------------------------------------------
# Function to write the formatted data back to the JSON file
def write_to_json(data):
    settings = load_settings()
    json_path = settings["json_file"]

    # Get the size of the file before writing (if it exists)
    if os.path.exists(json_path):
        pre_size = os.path.getsize(json_path)
    else:
        pre_size = 0  # If the file doesn't exist, it's size is 0

    # Write the JSON data to the file
    with open(json_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    # Get the size of the file after writing
    post_size = os.path.getsize(json_path)

    # Calculate the difference in size
    size_difference = post_size - pre_size

    print("Json file information written.")
    print(f"File size before writing: {pre_size} bytes")
    print(f"File size after writing: {post_size} bytes")
    print(f"Difference in size: {size_difference} bytes")


# Function to scrape business data from google maps
def scrape_google_maps_info(business_url, id, verbose=False, debug=False):
    

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    print(f'Opening Selenium driver, scraping URL with Instance ID #{id} ...')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(business_url)
        print("Selenium instance established, page loading... this may take a while")
        # Allow time for the page to load
        
        # --- Name ---
        try:
            name_element = driver.find_element(By.CSS_SELECTOR, "h1.DUwDvf.lfPIob")
            name = name_element.text.strip()
        except Exception as e:
            if verbose:
                print("Error scraping name.")
            if debug:
                print(e)
            name = "none"
        
        # --- Address ---
        try:
            address_element = driver.find_element(
                By.CSS_SELECTOR, 
                "div.rogA2c:not(.ITvuef) > div.Io6YTe.fontBodyMedium.kR99db.fdkmkc"
            )
            address = address_element.text.strip()

        except Exception as e:
            if verbose:
                print("Error scraping address.")
            if debug:
                print(e)
            address = "none"
        
        # --- Website ---
        try:
            website_element = driver.find_element(
                By.CSS_SELECTOR,
                "a.CsEnBe[aria-label^='Website:'] div.rogA2c.ITvuef > div.Io6YTe.fontBodyMedium.kR99db.fdkmkc"
            )
            website = website_element.text.strip()
          

        except Exception as e:
            if verbose:
                print("Error scraping field -> (website) ErrorLog: @Element Instance Unavailable")
            if debug:
                print(e)
            website = "none"
        
        # --- Phone Number ---
        try:
            phone_button = driver.find_element(
                By.CSS_SELECTOR, 
                "button.CsEnBe[aria-label^='Phone:']"
            )
            phone_label = phone_button.get_attribute("aria-label")
            phone_number = phone_label.replace("Phone:", "").strip()

        except Exception as e:
            if verbose:
                print("Error scraping field -> (phone number) ErrorLog: @Element Instance Unavailable")
            if debug:
                print(e)
            phone_number = "none"
        
        # --- Type ---
        try:
            type_element = driver.find_element(By.CSS_SELECTOR, "button.DkEaL")
            business_type = type_element.text.strip()
    
        except Exception as e:
            if verbose:
                print("Error scraping field -> (type) ErrorLog: @Element Instance Unavailable ")
            if debug:
                print(e)
            business_type = "none"

        # --- Image URL ---
        try:
            img_element = driver.find_element(
                By.CSS_SELECTOR, "button.aoRNLd.kn2E5e.NMjTrf.lvtCsd img"
            )
            img_url = img_element.get_attribute("src")
        except Exception as e:
            if verbose:
                print("Error scraping image URL.")
            if debug:
                print(e)
            img_url = "none"

        result = {
            "id": id,
            "business_url": business_url,
            "image": img_url,
            "name": name,
            "address": address,
            "website": website,
            "phone": phone_number,
            "type": business_type,
        }
        
        
    except Exception as main_exception:
        if debug:
            print(main_exception)
        result = None
    finally:
        driver.quit()
    
    return result


# Function to read the existing data from JSON and handle file reading
def read_existing_data():
    existing_data = []
    settings = load_settings()
    json_path = settings["json_file"]
    
    try:
        with open(json_path, 'r') as json_file:
            file_content = json_file.read().strip()
            #print(f"File content: {file_content}")  # Debugging print

            if file_content:  # Only load if the file content is not empty
                # Try parsing the content as JSON
                loaded_data = json.loads(file_content)

                # If the loaded data is a dictionary (not a list), convert it into a list
                if isinstance(loaded_data, dict):
                    existing_data = [loaded_data]  # Wrap in a list
                elif isinstance(loaded_data, list):
                    existing_data = loaded_data  # Use as is
                else:
                    existing_data = []  # If the data is neither, reset to empty list
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading JSON file: {e}")  # Debugging error message
        existing_data = []  # If file doesn't exist or error occurs, use an empty list

    return existing_data



def is_valid_url(url):
    """
    A simple URL validation function that checks whether the URL 
    starts with 'http://' or 'https://'.
    """
    url = url.strip()
    return url.startswith("http://") or url.startswith("https://")

def remove_invalid_links_from_csv(csv_file_path):
    """
    Reads the CSV file at csv_file_path, filters out rows where the 
    'business_url' is not a valid link, and rewrites the CSV with only valid entries.
    """
    valid_rows = []
    removed_count = 0
    
    # Read the CSV file and filter rows.
    with open(csv_file_path, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            url = row.get("business_url", "").strip()
            if is_valid_url(url):
                valid_rows.append(row)
            else:
                removed_count += 1

    # Write back only the valid rows.
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=["business_url"])
        writer.writeheader()
        writer.writerows(valid_rows)
    
    print(f"Removed {removed_count} invalid entries from {csv_file_path}.")

# Function to read the CSV and iterate through each link
def process_csv(csv_file_path, verbose=False):
    
    settings = load_settings();
    csv_file = settings["csv_file"]
    update_all_entries = settings["update_all_entries"]

    remove_invalid_links_from_csv(csv_file)
    # Load the existing data from the JSON file to check for duplicates
    existing_data = read_existing_data()

    # Now that we have loaded the existing data, create a set of URLs for quick lookup
    existing_urls = {entry['business_url'] for entry in existing_data}
   

    new_entries = []  # Store new entries to append to the existing data
    entry_count = 0  # Counter to track the number of entries processed

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        max_entries = sum(1 for row in csvfile) - 1
    

    #need to do this here
    #TODO: find how to move outside of this function 
    with tqdm(total=max_entries, desc="Processing CSV", ncols=100,
              bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} entries') as pbar:
        print()
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            # Iterate through each row and feed the URL to the scrape function
            for row in reader:

                

                business_url = row["business_url"]
                if business_url:  # Make sure the URL is not empty
                    # Check if the URL is already in the JSON data using the existing_urls set
                    if business_url not in existing_urls or update_all_entries:
                        pbar.update(1)
                        print()

        
                        result = scrape_google_maps_info(business_url, entry_count)

                        # Add the result to the new_entries list
                        new_entries.append(result)
                        print(f"Scraped: {business_url}")
                        clear_terminal()

                        # Add the business URL to the set to avoid further duplicates in this session
                        existing_urls.add(business_url)
                        entry_count += 1
                        
                    else:
                        
                        print(f'{business_url} entry already present | skipping...')
                            
                        entry_count+=1
                        pbar.update(1)
                        
                       
                        

        clear_terminal()
        # Combine the existing data and the new entries
        updated_data = existing_data + new_entries

        # Write the updated data back to the JSON file
        write_to_json(updated_data)
        print(f"All new data has been added and saved to ")




    

#------------------------------------------------------------------------------------------------
#END OF: MAIN CSV PARSING AND SCRAPING FUNCTIONALITY





#START OF: SYSTEM PROCESSING FUNCTIONS
#-----------------------------------------------------------------------------



def add_url_to_csv(csv_file_path, new_url, verbose=False):
    # Open the CSV file to append the new URL under the "business_url" column
    with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
        # Create a DictWriter to write data as a dictionary
        fieldnames = ['business_url']  # Define the column name
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Check if the file is empty or if it's the first time writing, so we need to write the header
        if file.tell() == 0:
            writer.writeheader()  # Write the header if the file is empty

        # Write the new URL in the "business_url" column
        writer.writerow({'business_url': new_url})
    if  verbose:
        print(f"URL added to 'business_url' column: {new_url}")
        
def delete_business():
    settings = load_settings()  # Assumes settings contains "csv_file" and "json_file" paths
    csv_file = settings["csv_file"]
    json_file = settings["json_file"]
    
    # Ask the user how they want to identify the business to delete.
    print("\nDelete Business Entry")
    print("----------------------")
    deletion_method = input("Delete by (1) Business Name or (2) Business URL? (Enter 1 or 2): ").strip()
    
    if deletion_method not in ["1", "2"]:
        print("Invalid option. Aborting deletion.")
        return
    
    search_value = input("Enter the search value: ").strip()
    
    # --- Update the JSON file ---
    try:
        with open(json_file, 'r', encoding='utf-8') as jf:
            data = json.load(jf)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return

    # Determine which entries to delete based on the chosen method.
    if deletion_method == "1":
        # Delete by business name (case-insensitive)
        deleted_urls = [entry.get("business_url") for entry in data if entry.get("name", "").lower() == search_value.lower()]
        new_data = [entry for entry in data if entry.get("name", "").lower() != search_value.lower()]
    else:
        # Delete by business URL (exact match)
        deleted_urls = [search_value]
        new_data = [entry for entry in data if entry.get("business_url", "") != search_value]

    if len(new_data) == len(data):
        print("No matching entry found in JSON file.")
        time.sleep(1)
        input("hit enter to continue")

    else:
        with open(json_file, 'w', encoding='utf-8') as jf:
            json.dump(new_data, jf, indent=4)
        print("Updated JSON file. Deleted the matching entry(ies).")
        time.sleep(1)
    
    # --- Update the CSV file ---
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as cf:
            reader = csv.DictReader(cf)
            rows = list(reader)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    # Filter out rows with business URLs in the deleted_urls list.
    new_rows = [row for row in rows if row.get("business_url", "") not in deleted_urls]

    if len(new_rows) == len(rows):
        print("No matching entry found in CSV file.")
    else:
        # Overwrite CSV with the filtered rows.
        with open(csv_file, 'w', newline='', encoding='utf-8') as cf:
            writer = csv.DictWriter(cf, fieldnames=["business_url"])
            writer.writeheader()
            writer.writerows(new_rows)
        print("Updated CSV file. Deleted the matching entry(ies).")
        time.sleep(1)
   

# Function to load settings from the JSON file
def load_settings():
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as file:
            return json.load(file)
    else:
        save_settings(default_settings)  # Create default settings if not found
        return default_settings

#-----------------------------------------------------------------------------
#END OF: SYSTEM PROCESSING FUNCTIONS








#START OF: CLI FUNCTION CALLS
#----------------------------------------------------------------------------




import random

#fake api fetch
def fetch_from_google_api(query):
    print("\nGoogle API Connection")
    print("---------------------------")
    
    # Simulate establishing connection
    print("[*] Establishing secure connection to Google API...", end="\r")
    time.sleep(1)
    print("[+] Connection established successfully.               ")

    # Simulate sending request
    print(f"[>] Sending query: '{query}' to Google API...")
    time.sleep(random.uniform(0.5, 1.5))
    
    # Simulate API response time
    print("[...] Waiting for response...", end="\r")
    time.sleep(random.uniform(1, 3))
    print("[✓] Data received from Google API.               ")
    
    # Simulate fake response
    fake_data = {
        "query": query,
        "results": [
            {"title": "Google Api Result Task 1/3", "url": "https://google.com/api_header"},
            {"title": "Google PROTO Server Address Result Task 2/3", "url": "https://google.com/placeit/geocache"},
            {"title": "Google HTTPS tunnel link established Task 3/3", "url": "https://google.com/api/returntosender"},
        ],
        "status": "success",
        "request_time": round(random.uniform(0.5, 2.5), 2),
    }
    
    # Print fake API response logs
    print("\nAPI Response")
    print("---------------------------")
    print(f"[*] Query: {fake_data['query']}")
    print(f"[*] Request Time: {fake_data['request_time']}s")
    print("[*] Results:")
    
    for i, result in enumerate(fake_data["results"], start=1):
        print(f"    [{i}] {result['title']} -> {result['url']}")

    print("\n[✓] API request completed successfully!\n")
    
    return fake_data





# Initialize colorama
init(autoreset=True)


# Function to save settings to the JSON file
def save_settings(settings):
    with open(settings_file, 'w') as file:
        json.dump(settings, file, indent=4)

# Function to update CSV file path
def update_csv_file(new_csv):
    settings = load_settings()
    settings["csv_file"] = new_csv
    save_settings(settings)
    print(Fore.GREEN + f"CSV file path updated to: {new_csv}" + Style.RESET_ALL)

# Function to update JSON file path
def update_json_file(new_json):
    settings = load_settings()
    settings["json_file"] = new_json
    save_settings(settings)
    print(Fore.GREEN + f"JSON file path updated to: {new_json}" + Style.RESET_ALL)

def update_param(new_param):
    settings = load_settings()
    settings["update_all_entries"] = new_param
    save_settings(settings)
    print(Fore.GREEN + f"Param changed to {new_param}" + Style.RESET_ALL)

# Add URL to CSV function
def add_url():
    
    settings = load_settings()
    csv_file = settings["csv_file"]
    print(Fore.GREEN + f"Adding URL to CSV file: {csv_file}" + Style.RESET_ALL)
    url = input(Fore.CYAN + "Enter URL: " + Style.RESET_ALL).strip()
    if is_valid_url(url):
        add_url_to_csv(csv_file, url)  # Call the function from centurion
        input(Fore.BLUE + "\nProcessing complete. Press Enter to return to the menu..." + Style.RESET_ALL)
    elif url.lower() == "back":
        return
    else:
        print(Fore.RED + "Incorrect URL Entered into portal, (TYPE BACK TO EXIT)")
        add_url()

# Process CSV function
def process_csv_file():
    settings = load_settings()
    csv_file = settings["csv_file"]
    print(Fore.GREEN + f"Processing CSV file: {csv_file}" + Style.RESET_ALL)
    clear_terminal();
    process_csv(csv_file)  # Call the function from centurion
    input(Fore.BLUE + "\nProcessing complete. Press Enter to return to the menu..." + Style.RESET_ALL)


def resolve_deltas():
    confirmation = input("Are you sure you want to resolve deltas? This will run a bash script. (y/n): ").strip().lower()

    if confirmation == 'y':
        try:
            print("Running the bash script to resolve deltas...")
            # Replace 'path_to_your_script.sh' with the actual path of your bash script
            subprocess.run(["bash", "./auto_commit_push.sh"], check=True)
            time.sleep(1)
            print("Deltas resolved successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error while running the bash script: {e}")
    else:
        print("Delta resolution canceled.")

#-----------------------------------------------------------------------------
#END OF: CLI FUNCTION CALLS











    

