import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import re
from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
import os
import csv

# Function to extract points from hotel data
def extract_points(hotel):
    # Extract numeric parts using regular expression
    numbers = re.findall(r'\d+', hotel['Points'])
    if numbers:
        points_str = ''.join(numbers)  # Merge all numeric parts
        return int(points_str)  # Convert merged string to integer
    return float('-inf')  # Return negative infinity if no numbers found

# Function to display hotel data in a new window
def show_hotel_data(hotels_data):
    # Sort hotels based on extracted points in descending order
    sorted_hotels = sorted(hotels_data, key=lambda x: extract_points(x), reverse=True)
    
    # Create hotel window
    hotel_window = tk.Toplevel(root)
    hotel_window.title("Hotel Attributes")
    
    # Create treeview to display hotel data
    tree = ttk.Treeview(hotel_window)
    tree['columns'] = ('Name', 'Points', 'Address', 'Distance to Center', 'Price')
    tree.heading('#0', text='Index')
    tree.heading('Name', text='Name')
    tree.heading('Points', text='Points')
    tree.heading('Address', text='Address')
    tree.heading('Distance to Center', text='Distance to Center')
    tree.heading('Price', text='Price')

    # Insert hotel data into treeview
    for i, hotel in enumerate(sorted_hotels):
        tree.insert('', 'end', text=str(i+1), values=(hotel['Name'], hotel['Points'], hotel['Address'], hotel['Distance to Center'], hotel['Price']))
        if (i==4):
            break

    tree.pack(expand=True, fill='both')

# Function to save hotel data to a CSV file
def save_to_csv(hotels_data):
    # Define the file path
    file_path = "hotels_data.csv"

    # Define the fieldnames for the CSV file
    fieldnames = ['Name', 'Points', 'Address', 'Distance to Center', 'Price']

    # Write data to CSV file
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for hotel in hotels_data:
            writer.writerow(hotel)

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

    # URL for the query always using Euro as the currency
    url = f'https://www.booking.com/searchresults.tr.html?ss={city}&checkin={checkin_date}&checkout={checkout_date}&group_adults=2&no_rooms=1&group_children=0&selected_currency=EUR'

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Error if theres no internet
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

# Create main application window
root = tk.Tk()
root.title("Hotel Booking App")

# List of 10 random European cities
european_cities = [
    "Paris", "London", "Berlin", "Madrid", "Rome",
    "Amsterdam", "Vienna", "Prague", "Athens", "Lisbon"
]

# Create city selection label and dropdown
city_label = ttk.Label(root, text="Select City:")
city_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
city_var = tk.StringVar()
city_dropdown = ttk.Combobox(root, textvariable=city_var)
city_dropdown.grid(row=0, column=1, padx=10, pady=5)
city_dropdown['values'] = european_cities

# Create check-in date label and entry
checkin_label = ttk.Label(root, text="Check-in Date:")
checkin_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
checkin_entry = ttk.Entry(root)
checkin_entry.grid(row=1, column=1, padx=10, pady=5)

# Create check-out date label and entry
checkout_label = ttk.Label(root, text="Check-out Date:")
checkout_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
checkout_entry = ttk.Entry(root)
checkout_entry.grid(row=2, column=1, padx=10, pady=5)

# Create currency selection labels and radio buttons
units_label = ttk.Label(root, text="Select Currency:")
units_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
units_var = tk.StringVar(value="Euro")
euro_radio = ttk.Radiobutton(root, text="Euro", variable=units_var, value="Euro")
euro_radio.grid(row=3, column=1, padx=10, pady=5, sticky="w")
tl_radio = ttk.Radiobutton(root, text="TL", variable=units_var, value="TL")
tl_radio.grid(row=4, column=1, padx=10, pady=5, sticky="w")

# Validate correct date format
def check_date_format(new_value):
    # Check if the entered date matches the format DD/MM/YYYY
    return re.match(r'^\d{2}/\d{2}/\d{4}$', new_value) is not None

validate_date = root.register(check_date_format)
checkin_entry.config(validate="focusout", validatecommand=(validate_date, "%P"))
checkout_entry.config(validate="focusout", validatecommand=(validate_date, "%P"))

# Create submit button
submit_button = ttk.Button(root, text="Submit", command=submit)
submit_button.grid(row=5, columnspan=2, padx=10, pady=5)

# Run the application
root.mainloop()
