import re
import requests
import json
import csv
from bs4 import BeautifulSoup

#function to scrape all the desired fields using the profile's url
def scrape(profile_url):
    response2 = requests.get(profile_url)
    soup2 = BeautifulSoup(response2.content, 'html.parser')
    name = soup2.find('div',class_='name').find('h1').text
    qualification = ','.join(name.split(',')[1:])
    gender_present = soup2.find('div',class_='gender')
    if gender_present:
        gender = gender_present.find('strong').text
    else:
        gender = "-"

    expertise_present = soup2.find('div',class_='expertise')
    if expertise_present:
        expertise_element = expertise_present.find('p')
        visible_text = expertise_element.contents[0].strip()
        hidden_element = expertise_element.find('span', class_='read-more-text-hidden')
        if hidden_element:
            hidden_text = hidden_element.text.strip()
            expertise_text = visible_text + hidden_text
        else:
            expertise_text = visible_text
    else:
        expertise_text="-"


    research_present = soup2.find('div', class_='research')
    if research_present:
        research_element = research_present.find('p')
        if research_element:
            visible_text = research_element.get_text(strip=True)
            hidden_element = research_element.find('span', class_='read-more-text-show')
            if hidden_element:
                hidden_text = hidden_element.text.strip()
                research_text = visible_text + hidden_text
            else:
                research_text = visible_text
        else:
            research_text = "-"
    else:
        research_text = "-"
    research_text= research_text.rstrip('...read more')

    location_titles = soup2.find_all('div',class_= 'title')
    location_addresses = soup2.find_all('div',class_='address')
    if location_addresses:
        address=""
        for i in range(len(location_titles)):
            address += location_titles[i].find('h3').text
            address += re.sub('\s+', ' ', location_addresses[i].get_text(separator=' ').strip())
            address += ";"
        address = address.rstrip(';')
    else:
        address="-"
    address = address.rstrip(";")

    phone_numbers = soup2.find_all('div',class_= 'phone')
    phone=""
    if phone_numbers:
        for number in phone_numbers:
            if number.find('a'):
                phone += number.find('a').text
            else:
                phone += re.sub('\s+', ' ', number.get_text(separator=' ').strip())
            phone += ";"
    else:
        phone = "-"
    phone = phone.rstrip(";")

    education = ""
    edu_present = soup2.find('div',class_="section education")
    if edu_present:
        restrict_class = edu_present.find('div',class_ ='restrict')
        if restrict_class:
            ul_list = restrict_class.find_all('ul')
            for ul in ul_list:
                li_list = ul.find_all('li')
                for li in li_list:
                    education += re.sub('\s+', ' ', li.get_text(separator=' ').strip()) + "   "
    else:
        education = "-"
    education = education.rstrip('   ')
    data.append([name, qualification, gender, expertise_text, research_text, phone, address, education])

data = []
lower_page_limit = 1 #customize lower limit
upper_page_limit = 30#customize upper limit

#it's better to set feasible page limits as large limits might result in server side limitations..I tried doing it in batches to avoid these limitations
for index in range(lower_page_limit,upper_page_limit+1):  #looping through all the pages
    url = f'https://www.hopkinsmedicine.org/profiles/search?query=&page={index}&count=20'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    ul_element = soup.find('ul', class_='faculty-results-list')
    doctors = ul_element.find_all('li')
    for doctor in doctors:
        a_tag = doctor.find('a')
        link = "https://www.hopkinsmedicine.org/" + a_tag['href']
        scrape(link) #scrape each doctors profile

#storing data into csv file
with open('doctors.csv', 'a', newline='', encoding='utf-8') as csvfile: #using append mode for working in batches (w mode can also be used for writing once)
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["Name", "Title", "Gender", "Expertise", "Research_Interests", "Phone", "Location", "Education"])
    csv_writer.writerows(data)
