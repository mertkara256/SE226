import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from tkcalendar import DateEntry
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from PIL import Image, ImageTk
import csv

# Create main application window
root = tk.Tk()
root.title("Hotel Booking App")
root.geometry("450x450")
root.configure(bg='lightblue')


style = ttk.Style()
style.configure('TLabel', background='lightblue', foreground='black')

#image
image_path = "booking.png"
original_image = Image.open(image_path)
resized_image = original_image.resize((250, 150))
image = ImageTk.PhotoImage(resized_image)
image_label = tk.Label(root, image=image, background="darkblue")
image_label.grid(row=11, column=1, padx=10, pady=10, sticky="se")

# List of 10 random European cities
european_cities = [
    "Paris", "London", "Berlin", "Madrid", "Rome",
    "Amsterdam", "Vienna", "Prague", "Athens", "Lisbon"
]

# City Selection
city_label = ttk.Label(root, text="Select City:")
city_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
city_var = tk.StringVar()
city_dropdown = ttk.Combobox(root, textvariable=city_var)
city_dropdown.grid(row=0, column=1, padx=10, pady=5)
city_dropdown['values'] = european_cities

# Check-in Date Entry
checkin_label = ttk.Label(root, text="Check-in Date:")
checkin_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
checkin_entry = DateEntry(root, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/MM/yyyy')
checkin_entry.grid(row=1, column=1, padx=10, pady=5)

# Check-out Date Entry
checkout_label = ttk.Label(root, text="Check-out Date:")
checkout_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
checkout_entry = DateEntry(root, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/MM/yyyy')
checkout_entry.grid(row=2, column=1, padx=10, pady=5)

# Currency Selection
units_label = ttk.Label(root, text="Select Currency:")
units_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
units_var = tk.StringVar(value="Euro")
euro_radio = ttk.Radiobutton(root, text="Euro", variable=units_var, value="Euro")
euro_radio.grid(row=3, column=1, padx=10, pady=5, sticky="w")
tl_radio = ttk.Radiobutton(root, text="TL", variable=units_var, value="TL")
tl_radio.grid(row=4, column=1, padx=10, pady=5, sticky="w")

# Function to validate date format
def check_date_format(date_string):
    # Regular expression pattern to match "DD/MM/YYYY" format
    date_pattern = r'^\d{2}/\d{2}/\d{4}$'
    
    # Check if the date string matches the pattern
    match = re.match(date_pattern, date_string)
    
    # If there is a match, the date string is in the correct format
    if match:
        return True
    else:
        return False

validate_date = root.register(check_date_format)
checkin_entry.config(validate="focusout", validatecommand=(validate_date, "%P"))
checkout_entry.config(validate="focusout", validatecommand=(validate_date, "%P"))

# Function to handle form submission
def submit():
    city = city_var.get()
    checkin_date_str = checkin_entry.get()
    checkout_date_str = checkout_entry.get()
    units = units_var.get()

    # Convert check-in and check-out dates to the desired format (YYYY-MM-DD)
    try:
        checkin_date = datetime.strptime(checkin_date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        checkout_date = datetime.strptime(checkout_date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Error", "Invalid date format. Please enter dates in DD/MM/YYYY format.")
        return

    # Check if checkout date is after check-in date
    if checkin_date >= checkout_date:
        messagebox.showerror("Error", "Check-out date must be after the check-in date.")
        return

    # URL for the query always using Euro as the currency
    url = f'https://www.booking.com/searchresults.tr.html?ss={city}&checkin={checkin_date}&checkout={checkout_date}&group_adults=2&no_rooms=1&group_children=0&selected_currency=EUR'

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Error if there's no internet
    except requests.RequestException as e:
        messagebox.showerror("Error", f"Failed to fetch data from the server, make sure you have an internet connection.")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    hotels = soup.findAll('div', {'data-testid': 'property-card'})

    hotels_data = []  # Initialize list to hold hotel data

    # Loop over the first 10 hotel elements and extract the desired data
    for hotel in hotels[:10]:
        # Extract the hotel name, points, address, distance, and price
        name_element = hotel.find('div', {'data-testid': 'title'})
        name = name_element.text.strip()
        points_element = hotel.find('span', class_='a3332d346a')  # Assuming this class uniquely identifies the points
        points = points_element.text.strip() if points_element else "NOT GIVEN"
        address_element = hotel.find('span', {'data-testid': 'address'})
        address = address_element.text.strip() if address_element else ""
        distance_element = hotel.find('span', {'data-testid': 'distance'})
        if distance_element:
            distance_text = distance_element.text.strip()
            distance_match = re.search(r'([\d,]+)\s*(km|m)', distance_text)
            if distance_match:
                distance = distance_match.group(1) + distance_match.group(2)
        else:
            distance = ""

        # Extract the price directly
        price_element = hotel.find('span', {'data-testid': 'price-and-discounted-price'})
        price = price_element.text.strip() if price_element else "Not available"

        # Convert price to TL if the selected currency is TL
        if units == 'TL' and price != "Not available":
            # Strip the "€" sign and any spaces
            price_value = price.strip("€").strip()
            # Remove dots and commas from the price
            price_numeric = float(price_value.replace('.', '').replace(',', ''))
            # Convert and round to two decimal places
            price_tl = round(price_numeric * 30, 2)
            price = f"{price_tl} TL"

        hotel_data = {
            'Name': name,
            'Points': points,
            'Address': address,
            'Distance to Center': distance,
            'Price': price
        }

        hotels_data.append(hotel_data)

    # Sorting hotels based on price in ascending order
    show_hotel_data(hotels_data)

    # Save data to CSV file
    save_to_csv(hotels_data)

# Function to extract points from hotel data
def extract_points(hotel):
    numbers = re.findall(r'\d+', hotel['Points'])
    if numbers:
        points_str = ''.join(numbers)
        return int(points_str)
    return float('-inf')

# Function to display hotel data in a new window
def show_hotel_data(hotels_data):
    sorted_hotels = sorted(hotels_data, key=extract_points, reverse=True)

    hotel_window = tk.Toplevel(root)
    hotel_window.title("Hotel Attributes")

    tree = ttk.Treeview(hotel_window)
    tree['columns'] = ('Name', 'Points', 'Address', 'Distance to Center', 'Price')
    tree.heading('#0', text='Index')
    tree.heading('Name', text='Name')
    tree.heading('Points', text='Points')
    tree.heading('Address', text='Address')
    tree.heading('Distance to Center', text='Distance to Center')
    tree.heading('Price', text='Price')

    for i, hotel in enumerate(sorted_hotels):
        tree.insert('', 'end', text=str(i + 1), values=(hotel['Name'], hotel['Points'], hotel['Address'], hotel['Distance to Center'], hotel['Price']))
        if (i == 4):
            break

    tree.pack(expand=True, fill='both')

# Function to save hotel data to a CSV file
def save_to_csv(hotels_data):
    file_path = "hotels_data.csv"

    fieldnames = ['Name', 'Points', 'Address', 'Distance to Center', 'Price']

    df = pd.DataFrame(hotels_data)
    df.to_csv(file_path, index=False, encoding='utf-8')

# Create submit button
submit_button = ttk.Button(root, text="Submit", command=submit)
submit_button.grid(row=5, columnspan=2, padx=10, pady=5)

# Run the application
root.mainloop()
