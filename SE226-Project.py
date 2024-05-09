import tkinter as tk
from tkinter import ttk
import re
from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime
import os

class HotelBookingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotel Booking App")
        
        # List of 10 random European cities
        self.european_cities = [
            "Paris", "London", "Berlin", "Madrid", "Rome",
            "Amsterdam", "Vienna", "Prague", "Athens", "Lisbon"
        ]
        
        self.city_label = ttk.Label(root, text="Select City:")
        self.city_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.city_var = tk.StringVar()
        self.city_dropdown = ttk.Combobox(root, textvariable=self.city_var)
        self.city_dropdown.grid(row=0, column=1, padx=10, pady=5)
        self.city_dropdown['values'] = self.european_cities
        
        self.checkin_label = ttk.Label(root, text="Check-in Date:")
        self.checkin_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.checkin_entry = ttk.Entry(root)
        self.checkin_entry.grid(row=1, column=1, padx=10, pady=5)
        
        self.checkout_label = ttk.Label(root, text="Check-out Date:")
        self.checkout_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.checkout_entry = ttk.Entry(root)
        self.checkout_entry.grid(row=2, column=1, padx=10, pady=5)
        
        self.units_label = ttk.Label(root, text="Select Currency:")
        self.units_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        self.units_var = tk.StringVar(value="Euro")
        self.euro_radio = ttk.Radiobutton(root, text="Euro", variable=self.units_var, value="Euro")
        self.euro_radio.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        self.tl_radio = ttk.Radiobutton(root, text="TL", variable=self.units_var, value="TL")
        self.tl_radio.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        
        # Validate correct date format
        self.validate_date = root.register(self.check_date_format)
        self.checkin_entry.config(validate="focusout", validatecommand=(self.validate_date, "%P"))
        self.checkout_entry.config(validate="focusout", validatecommand=(self.validate_date, "%P"))
        
        self.submit_button = ttk.Button(root, text="Submit", command=self.submit)
        self.submit_button.grid(row=5, columnspan=2, padx=10, pady=5)
        
    def check_date_format(self, new_value):
        # Check if the entered date matches the format DD/MM/YYYY
        return re.match(r'^\d{2}/\d{2}/\d{4}$', new_value) is not None
        
    def submit(self):
        city = self.city_var.get()
        checkin_date_str = self.checkin_entry.get()
        checkout_date_str = self.checkout_entry.get()
        units = self.units_var.get()

        # Convert check-in and check-out dates to the desired format (YYYY-MM-DD)
        checkin_date = datetime.strptime(checkin_date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        checkout_date = datetime.strptime(checkout_date_str, "%d/%m/%Y").strftime("%Y-%m-%d")

        # For demonstration purposes, let's print the user inputs
        print("City:", city)
        print("Check-in Date:", checkin_date)
        print("Check-out Date:", checkout_date)
        print("Units:", units)

        # URL for the query always using Euro as the currency
        url = f'https://www.booking.com/searchresults.tr.html?ss={city}&checkin={checkin_date}&checkout={checkout_date}&group_adults=2&no_rooms=1&group_children=0&selected_currency=EUR'

        headers = {
        'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }


        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        hotels = soup.findAll('div', {'data-testid': 'property-card'})

        hotels_data = {'name': [], 'points': [], 'address': [], 'distance_to_center': [], 'price': []}  # Initialize dictionary to hold hotel data

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
                distance_match = re.search(r'([\d.]+)\s*(km|m)', distance_text)
                if distance_match:
                    distance = distance_match.group(1) + distance_match.group(2)
            else:
                distance = ""
            
            # Extract the price directly
            price_element = hotel.find('span', {'data-testid': 'price-and-discounted-price'})
            price = price_element.text.strip() if price_element else "Not available"
            
            # Convert price to TL if the selected currency is TL
            if units == 'TL' and price != "Not available":
                price = round(float(price.replace('€', '').replace(',', '')) * 30, 2)  # Round to two decimal places using "round half to even" strategy
                
            # Append hotel data to dictionary
            hotels_data['name'].append(name)
            hotels_data['points'].append(points)
            hotels_data['address'].append(address)
            hotels_data['distance_to_center'].append(distance)
            hotels_data['price'].append(price)

        hotels_df = pd.DataFrame(hotels_data)
        
        # Save to CSV on desktop with UTF-8-SIG encoding
        file_path = os.path.join(os.getcwd(), 'test_hotels.csv')
        hotels_df.to_csv(file_path, header=True, index=False, encoding='utf-8-sig')


        print("Scraping and saving completed.")


def main():
    root = tk.Tk()
    app = HotelBookingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
