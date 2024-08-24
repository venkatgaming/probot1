import requests
from bs4 import BeautifulSoup
import json
import concurrent.futures

def fetch_pokemon_data(pokemon_id):
    base_url = 'https://pokemon.gameinfo.io/en/pokemon/'
    url = f'{base_url}{pokemon_id}-bulbasaur'
    
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Check if request was successful
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract Pokémon name
            pokemon_name = soup.find('h1').text.strip()
            
            # Extract vulnerabilities
            vulnerabilities = []
            vulnerable_table = soup.find('table', class_='weaknesses weak')
            if vulnerable_table:
                for row in vulnerable_table.find_all('tr'):
                    type_tag = row.find('a', class_='type')
                    percentage_tag = row.find('span', class_='_xx')  # Find percentage span
                    if type_tag and percentage_tag:
                        pokemon_type = type_tag.text.strip()
                        percentage = percentage_tag.text.strip()
                        vulnerabilities.append({
                            'type': pokemon_type,
                            'percentage': percentage
                        })
            
            # Extract resistances
            resistances = []
            resistant_table = soup.find('table', class_='weaknesses res')
            if resistant_table:
                for row in resistant_table.find_all('tr'):
                    type_tag = row.find('a', class_='type')
                    percentage_tag = row.find('span', class_='_xx')  # Find percentage span
                    if type_tag and percentage_tag:
                        pokemon_type = type_tag.text.strip()
                        percentage = percentage_tag.text.strip()
                        resistances.append({
                            'type': pokemon_type,
                            'percentage': percentage
                        })
            
            # Prepare data dictionary for this Pokémon
            pokemon_data = {
                'id': pokemon_id,
                'name': pokemon_name,
                'vulnerable_to': vulnerabilities,
                'resistant_to': resistances
            }
            
            return pokemon_data
        
        else:
            print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Request Exception occurred for {url}: {str(e)}")
        return None

# Function to fetch data using ThreadPoolExecutor
def fetch_all_pokemon_data(pokemon_ids):
    all_pokemon_data = []
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Map the fetch_pokemon_data function to all pokemon_ids using threads
        results = executor.map(fetch_pokemon_data, pokemon_ids)
        
        # Iterate over results and append valid data to all_pokemon_data
        for result in results:
            if result:
                all_pokemon_data.append(result)
    
    return all_pokemon_data

# List of Pokémon IDs you want to fetch data for (Gen 1 to Gen 8)
pokemon_ids = list(range(1, 809))  # Adjust range according to the total number of Pokémon

# Fetch all Pokémon data
all_pokemon_data = fetch_all_pokemon_data(pokemon_ids)

# Save all data to a JSON file
output_file = 'pokemon_data_by_id.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_pokemon_data, f, ensure_ascii=False, indent=4)

print(f"Successfully saved Pokémon data to {output_file}")
