import requests
from bs4 import BeautifulSoup
import pandas 
import argparse
import connect

parser=argparse.ArgumentParser()
parser.add_argument("--page_num_MAX",help="Enter the number of page to parse",type=int)
parser.add_argument("--dbname",help="Enter the name of db",type=str)
args=parser.parse_args()

headers = {
	'user-agent': 'Mozilla/70.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
}

oyo_url="https://www.oyorooms.com/hotels-in-bangalore/page="
page_num_MAX=3
scraped_info_list=[]

connect.connect(args.dbname)

for page_num in range(1,page_num_MAX):
    url=oyo_url+str(page_num)
    print("Get request for : "+url)
    req=requests.get(url, verify=True, headers=headers)
    content=req.content
    
    soup=BeautifulSoup(content,"html.parser")
    all_hotels= soup.find_all("div",{"class":"hotelCardListing"})
    
    for hotel in all_hotels:
        hotel_dict={}
        hotel_dict["name"]=hotel.find("h3",{"class": "listingHotelDescription__hotelName"}).text
        hotel_dict["address"]=hotel.find("span",{"itemprop": "streetAddress"}).text
        hotel_dict["price"]=hotel.find("span", {"class": "listingPrice__finalPrice"}).text
        try:
            hotel_dict["Rating"]=hotel.find("span", {"class": "hotelRating__rattingSummary"}).text
        except AttributeError:
            hotel_dict["Rating"]=None
            pass
        parent_amenities_elements=hotel.find("div",{"class":"amenitywrapper"})

        amenities_list=[]

        try:
            for amenity in parent_amenities_elements.find_all("div",{"class":"amenityWrapper__amenity"}):
                amenities_list.append(amenity.find("span",{"class":"d-body-sm"}).text.strip())

            hotel_dict["amenities"]=', '.join(amenities_list[:-1])

            scraped_info_list.append(hotel_dict)
            connect.insert_into_table(args.dbname,tuple(hotel_dict.values()))
        except AttributeError:
            pass
        #print(hotel_name,hotel_address,hotel_price,hotel_price)  
dataFrame=pandas.DataFrame(scraped_info_list)
print("Creating csv file......Oyo")
dataFrame.to_csv("Oyo.csv")
connect.get_hotel_info(args.dbms)
