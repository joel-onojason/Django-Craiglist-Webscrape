from django.shortcuts import render
from requests.compat import quote_plus  #Automatically add %20 in spaces in your search
from bs4 import BeautifulSoup
import requests
from . import models

# Create your views here.
def home(request):
    return render(request, 'base.html')


def new_search(request):
    if request.method == 'POST':
        BASE_CRAIGLIST_URL = 'https://losangeles.craigslist.org/search/sss?query={}'
        search = request.POST.get('search')
        models.Search.objects.create(search=search)
        final_url = BASE_CRAIGLIST_URL.format(quote_plus(search))

        #Getting the webpage, creating a Response object.
        response = requests.get(final_url)

        #Extracting the source code of the page
        data = response.text

        #Passing the source code to Beautiful Soup to create a BeautifulSoup object for it.
        soup = BeautifulSoup(data, features='html.parser')

        #Extracting all the <li> tags whose class name is 'result-row' into a list
        post_listings = soup.find_all('li', {'class': 'result-row'})

        final_postings = []
        for post in post_listings:
            post_title = post.find(class_='result-title hdrlnk').text
            post_url = post.find('a').get('href')

            if post.find(class_='result-price'):
                post_price = post.find(class_='result-price').text
            else:
                post_price = 'N/A'

            if post.find(class_='result-image').get('data-ids'):
                post_image_id = post.find(class_='result-image').get('data-ids').split(',')[0].split(':')[1]
                post_image_url = "https://images.craiglist.org/{}_300x300.jpg".format(post_image_id)
                # print(post_image_url)
            else:
                post_image_url = 'https://losangeles.craigslist.org/images/peace.jpg'

            final_postings.append((post_title, post_url, post_price, post_image_url))

        context = {'search': search,
                   'final_postings': final_postings,
                   }

        return render(request, 'craiglist_app/new_search.html', context)
    return render(request, 'craiglist_app/new_search.html')