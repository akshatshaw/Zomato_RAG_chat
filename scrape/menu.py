import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json


df = pd.read_csv('restaurant_data.csv')

# Initialize a list to store all restaurant menu data
all_restaurant_menus = []

# Selenium WebDriver
driver = webdriver.Chrome()

for index, row in df.iterrows():
    restaurant_name = row['names']
    restaurant_link = row['links']
    
    print(f"Processing {restaurant_name} at {restaurant_link}")
    
    restaurant_data = {
        'name': restaurant_name,
        'link': restaurant_link,
        'rating': row['ratings'],
        'price_for_one': row['price for one'],
        'cuisine': row['cuisine']
    }
    
    try:
        # Visit the restaurant page
        driver.get(restaurant_link)
        
        # Wait 
        time.sleep(2)
        
        try:
            menu_tab = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Menu') or contains(text(), 'Order Online')]"))
            )
            menu_tab.click()
            time.sleep(2)  
        except:
            print(f"No menu tab found for {restaurant_name}")
            continue
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(3):  # Scroll a few times to load more content
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        # Get the page source
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        menu_items = []
        
        # Look for the menu item containers with class "sc-jNLVlY cFMmph"
        item_containers = soup.find_all('div', {'class': 'sc-jNLVlY cFMmph'})
        
        for container in item_containers:
            item_data = {}
            
           
            name_tag = container.find('h4', {'class': 'sc-cGCqpu chKhYc'})
            if name_tag:
                item_data['name'] = name_tag.text.strip()
            
            
            desc_tag = container.find('p', {'class': 'sc-gsxalj jqiNmO'})
            if desc_tag:
                item_data['description'] = desc_tag.text.strip()
            
            # Extract price if available
            price_div = container.find('div', {'class': 'sc-17hyc2s-3 jOoliK sc-bPzAnn hoAnki'})
            if price_div:
                flex_div = price_div.find('div', {'class': 'sc-17hyc2s-1 cCiQWA'})
                if flex_div:
                    item_data['price'] = flex_div.text.strip()
            
            if item_data:
                menu_items.append(item_data)
        
        # If no items found with exact class names, try a more flexible approach
        if not menu_items:
            print(f"No menu items found with exact class names for {restaurant_name}, trying flexible approach")
            
            # Try to find menu items with any h4 tag within divs that might contain menu items
            for div in soup.find_all('div'):
                h4_tag = div.find('h4')
                if h4_tag:
                    item_data = {'name': h4_tag.text.strip()}
                    
                    # Look for description in a p tag after the h4
                    p_tag = div.find('p')
                    if p_tag:
                        item_data['description'] = p_tag.text.strip()
                    
                    # Look for price in any div with text that looks like a price
                    price_div = div.find('div', string=lambda text: text and '₹' in text)
                    if price_div:
                        item_data['price'] = price_div.text.strip()
                    
                    menu_items.append(item_data)
        
        restaurant_data['menu_items'] = menu_items
        print(f"Found {len(menu_items)} menu items for {restaurant_name}")
        
    except Exception as e:
        print(f"Error processing {restaurant_name}: {e}")
    
    all_restaurant_menus.append(restaurant_data)
    
    time.sleep(1)
    

# Close the WebDriver
driver.quit()

# Create a flattened version for CSV
flattened_data = []
for restaurant in all_restaurant_menus:
    restaurant_name = restaurant['name']
    rating = restaurant.get('rating', '')
    price_for_one = restaurant.get('price_for_one', '')
    cusine = restaurant.get('cuisine', '')
    for item in restaurant['menu_items']:
        flattened_data.append({
            'restaurant_name': restaurant_name,
            'rating': rating,
            'price_for_one': price_for_one,
            'cuisine': cusine,
            'item_name': item.get('name', ''),
            'description': item.get('description', ''),
            'price': item.get('price', '')
        })

# Save as CSV
menu_df = pd.DataFrame(flattened_data)
menu_df = menu_df.drop_duplicates()
menu_df.to_csv('restaurant_menus.csv', index=False)


with open("restaurant_menus.json", "w", encoding="utf-8") as f:
    f.write(menu_df.to_json(orient="records", indent=2, force_ascii=False))

print(f"Extracted menu data for {len(all_restaurant_menus)} restaurants")
print(f"Total menu items: {len(flattened_data)}")

