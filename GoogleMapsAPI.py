# References:
# https://developers.google.com/places/web-service/intro
# https://developers.google.com/maps/documentation/

# Get API Key here
# https://developers.google.com/places/web-service/get-api-key

import requests

apiKey = 'APIKEY'

def GetPlace(searchTerm):
    # What do you want to search for?
    searchType = 'textquery' # either 'textquery' or 'phonenumber'

    # Which information do you want returned?
    fields = []
    fields.append('formatted_address')
    fields.append('geometry')
    fields.append('icon')
    fields.append('id')
    fields.append('name')
    fields.append('permanently_closed')
    fields.append('photos')
    fields.append('place_id')
    fields.append('plus_code')
    #fields.append('scope') # This was on the documentation but doesnt seem to work
    fields.append('types')
    fields.append('opening_hours') # 'Place Search' only returns open now; Use 'Place Details' for full hours
    fields.append('price_level')
    fields.append('rating')
    returnFields = ','''.join(fields)

    # Build the url
    # There are other searches available that gives more details
    url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={}&inputtype={}&fields={}&key={}'.format(searchTerm, searchType, returnFields, apiKey)

    # Make the call and get the JSON
    r = requests.get(url)

    return r.json()

def GetDirections(origin, destination):
    url = 'https://maps.googleapis.com/maps/api/directions/json?origin={}&destination={}&key={}'.format(origin, destination, apiKey)
    r = requests.get(url)
    return r.json()

r = GetPlace('YVR')
print(r)

r = GetDirections('YVR','V7R4S6')
print(r)
