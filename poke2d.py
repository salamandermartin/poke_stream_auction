import requests

prefix_url = 'https://pokeapi.co/api/v2/pokemon/'

def get_pokemon_2d(pokemon_name: str):
    pokemon_name = pokemon_name.replace(" ", "-").lower()    

    pokemon_url = prefix_url + pokemon_name
    sprite_url = pokemon_url

    response = requests.get(sprite_url).json()
    return response['sprites']['front_default']
