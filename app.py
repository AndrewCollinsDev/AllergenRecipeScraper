import lxml
from lxml import etree
import requests
from urllib.parse import urljoin, quote
from flask import Flask, render_template, jsonify, request
import random

app = Flask(__name__)

@app.route('/', methods=['GET'])
def search():
    return render_template('app_search.html')

@app.route('/app_result', methods=['POST'])
def prototype_results():
    def get_content(url):
        response = requests.get(url)
        parser = etree.HTMLParser()
        return etree.fromstring(response.text, parser)
    sq = request.form.get('search_terms')
    allergens_to_avoid = request.form.getlist('allergen')  # This will be a Python list
    allergen_dict = {
        "cereals_containing_gluten": ["wheat", "spelt", "Khorasan wheat", "rye", "barley", "oat", "oats", "flour", "bread", "pasta", "couscous", "cake", "cakes", "biscuit", "biscuits", "pastry", "pastries"],
        "crustaceans": ["prawn", "prawns", "crab", "crabs", "lobster", "lobsters", "crayfish", "shrimp", "shrimps", "shellfish"],
        "eggs": ["egg", "eggs", "mayonnaise", "mousse", "mousses", "souffle", "souffles", "paste", "pastes", "baked goods"],
        "fish": ["fish", "anchovy", "anchovies", "tuna", "salmon", "fish sauce", "sushi", "surimi"],
        "peanuts": ["peanut", "peanuts", "peanut butter", "peanut oil", "groundnut", "groundnuts"],
        "soybeans": ["soy", "soybean", "soybeans", "soy sauce", "tofu", "tempeh", "soybean oil", "edamame", "soy protein", "soya"],
        "milk": ["milk", "cheese", "butter", "cream", "yogurt", "yoghurt", "casein", "whey", "lactose"],
        "nuts": ["almond", "almonds", "hazelnut", "hazelnuts", "walnut", "walnuts", "cashew", "cashews", "pecan", "pecans", "Brazil nut", "Brazil nuts", "pistachio", "pistachios", "macadamia nut", "macadamia nuts", "nut oil"],
        "celery": ["celery", "celeriac", "celery salt", "celery seed", "celery seeds"],
        "mustard": ["mustard", "mustard seed", "mustard seeds", "mustard oil", "mustard greens"],
        "sesame": ["sesame", "sesame seed", "sesame seeds", "sesame oil", "tahini"],
        "sulphur_dioxide_sulphites": ["dried fruit", "meat product", "meat products", "soft drink", "soft drinks", "vegetable", "vegetables", "wine", "beer"],
        "lupin": ["lupin", "lupin seed", "lupin seeds", "lupin flour"],
        "molluscs": ["mussel", "mussels", "snail", "snails", "squid", "whelk", "whelks", "oyster sauce", "clam", "clams", "octopus", "scallop", "scallops", "abalone"]
    }
    base_url = 'https://www.bbcgoodfood.com'
    search_url = '/search?q='+ quote(str(sq)) 
    complete_search_url = urljoin(base_url, search_url)
    search_dom = get_content(complete_search_url)

    href_list = search_dom.xpath('//a[contains(@class, "link d-block")]/@href')

    # Make href_list a set to remove duplicates, then convert back to list
    href_list = list(set(href_list))

    # Limit href_list to first 5 items
    href_list = href_list[:10]

    recipes = []


    # Fetch the title and ingredients for each recipe
    for href in href_list:
        recipe_url = urljoin(base_url, href)
        recipe_dom = get_content(recipe_url)

        # Fetch the title
        try:
            title = recipe_dom.xpath('//div[contains(@class, "headline post-header__title post-header__title--masthead-layout")]/h1/text()')[0]
        except IndexError:
            continue

        ingredients_list = recipe_dom.xpath('//section[contains(@class, "recipe__ingredients col-12 mt-md col-lg-6")]/section/ul/li')
        ingredients = [''.join(li.itertext()).strip() for li in ingredients_list]

        # Check for allergens
        should_skip = False
        for allergen in allergens_to_avoid:
            allergen_aliases = allergen_dict.get(allergen, [])
            for alias in allergen_aliases:
                if any(alias in ingredient for ingredient in ingredients):
                    should_skip = True
                    break

            if should_skip:
                break

        if not should_skip:
            recipes.append({
                'link': recipe_url,
                'title': title,
                'ingredients': ingredients})
            
    if recipes == []:
        recipes.append({
            'link': '',
            'title':'There are no matches',
        })
    
    return render_template('app_result.html', recipes=recipes)







import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)