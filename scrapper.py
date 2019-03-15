from bs4 import BeautifulSoup
from urllib.parse import urljoin 
import requests
import re
from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait as wait

# Download IMDB's Top 250 data
url = 'http://www.imdb.com/chart/top'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'lxml')

movies = soup.select('td.titleColumn')
links = [a.attrs.get('href') for a in soup.select('td.titleColumn a')]
crew = [a.attrs.get('title') for a in soup.select('td.titleColumn a')]
ratings = [b.attrs.get('data-value') for b in soup.select('td.posterColumn span[name=ir]')]
votes = [b.attrs.get('data-value') for b in soup.select('td.ratingColumn strong')]

imdb = []
dataset = []
# Store each item into dictionary (data), then put those into a list (imdb)
for index in range(0, len(movies)):
    # Seperate movie into: 'place', 'title', 'year'
    movie_string = movies[index].get_text()
    movie = (' '.join(movie_string.split()).replace('.', ''))
    movie_title = movie[len(str(index))+1:-7]
    year = re.search('\((.*?)\)', movie_string).group(1)
    place = movie[:len(str(index))-(len(movie))]
    data = {"movie_title": movie_title,
            "year": year,
            "place": place,
            "star_cast": crew[index],
            "rating": ratings[index],
            "vote": votes[index],
            "link": links[index]}
    imdb.append(data)

for item in imdb:
    #print(item['place'], '-', item['movie_title'], '('+item['year']+') -', 'Starring:', item['star_cast'],  item['link'])
    url =  'http://www.imdb.com'+ item['link'][:17]+'reviews'
    driver = webdriver.Chrome('/home/dev/Downloads/chromedriver_linux64/chromedriver')
    driver.get(url)

    labtn = driver.find_element_by_id('load-more-trigger')
    labtn.click()

    wait(driver, 15).until(lambda x: len(driver.find_elements_by_css_selector("div.lister-item-content")) > 39)
    source_code = driver.page_source
    soup = BeautifulSoup(source_code, 'lxml')
    containers=soup.find_all('div', class_ = 'lister-item-content')
    reviews = []
    for container in containers:
        if container.find('a', class_ = 'title' ) is not None:
            title = container.a.text.strip()
            bar = container.find('div', class_ = 'ipl-ratings-bar')
            if bar is None:
                continue
            else:
                rating = bar.text.strip()  
                content_cont = container.find('div', class_ = 'text show-more__control')
                if content_cont is not None:
                    content = content_cont.text.strip()
                else:
                    content_cont = container.find('div', class_ = 'text show-more__control clickable')
                    content = content_cont.text.strip()
                content = title+content
                data2 = {
                    "user_rating": rating,
                    "content" : content  
                }
                reviews.append(data2)
    
    movies = {
        "title" : item['movie_title'],
        "rating" : item['rating'],
        "reviews": reviews
    }
    dataset.append(movies) 
    print(movies)           
    driver.quit()

print(dataset)
