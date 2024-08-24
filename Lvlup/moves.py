import aiohttp
import asyncio
import math

# Limit the number of concurrent API requests
SEMAPHORE = asyncio.Semaphore(10)  # Adjust the number based on your needs

# Function to get Pokémon data from PokeAPI
async def get_pokemon_data(session, pokemon_name):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
    async with SEMAPHORE:
        async with session.get(url) as response:
            return await response.json()

# Function to get move data from PokeAPI
async def get_move_data(session, move_name):
    url = f"https://pokeapi.co/api/v2/move/{move_name.lower()}"
    async with SEMAPHORE:
        async with session.get(url) as response:
            return await response.json()

# Function to get type effectiveness data from PokeAPI
async def get_type_data(session, type_name):
    url = f"https://pokeapi.co/api/v2/type/{type_name.lower()}"
    async with SEMAPHORE:
        async with session.get(url) as response:
            return await response.json()

# Function to calculate type effectiveness
def calculate_type_effectiveness(move_type, opponent_types, type_data):
    effectiveness = 1
    damage_relations = type_data["damage_relations"]

    double_damage_to = {t["name"] for t in damage_relations["double_damage_to"]}
    half_damage_to = {t["name"] for t in damage_relations["half_damage_to"]}
    no_damage_to = {t["name"] for t in damage_relations["no_damage_to"]}

    for opponent_type in opponent_types:
        if opponent_type in no_damage_to:
            return 0
        if opponent_type in half_damage_to:
            effectiveness *= 0.5
        if opponent_type in double_damage_to:
            effectiveness *= 2

    return effectiveness

# Function to calculate damage
async def calculate_damage(session, move, opponent_types, attacker_level, attacker_stats, attacker_types):
    power = move["power"] or 0
    accuracy = move["accuracy"] or 100
    move_type = move["type"]["name"]
    
    # Get type data for the move type
    type_data = await get_type_data(session, move_type)
    
    # Calculate type effectiveness
    type_multiplier = calculate_type_effectiveness(move_type, opponent_types, type_data)
    
    # Apply Same Type Attack Bonus (STAB)
    stab = 1.5 if move_type in attacker_types else 1
    
    # More sophisticated damage formula
    attack_stat = attacker_stats['attack'] if move["damage_class"]["name"] == "physical" else attacker_stats['special-attack']
    damage = (((2 * attacker_level / 5 + 2) * power * attack_stat / 50) + 2) * type_multiplier * stab * (accuracy / 100)
    
    # Print detailed move data
    print(f"Move: {move['name']}, Type: {move_type}, Power: {power}, Accuracy: {accuracy}, Type Multiplier: {type_multiplier}, STAB: {stab}, Calculated Damage: {damage}")
    
    return damage

# Function to find the best move for a Pokémon
async def find_best_move_for_pokemon(pokemon_name, moves, opponent_name, attacker_level, attacker_stats):
    async with aiohttp.ClientSession() as session:
        attacker_data = await get_pokemon_data(session, pokemon_name)
        attacker_types = [t["type"]["name"] for t in attacker_data["types"]]
        opponent_data = await get_pokemon_data(session, opponent_name)
        opponent_types = [t["type"]["name"] for t in opponent_data["types"]]

        move_data_tasks = [get_move_data(session, move) for move in moves]
        move_data = await asyncio.gather(*move_data_tasks)

        # Check for type effectiveness and calculate damage for each move
        move_effectiveness_and_damage = await asyncio.gather(
            *[calculate_damage(session, move, opponent_types, attacker_level, attacker_stats, attacker_types) for move in move_data]
        )
        
        move_effectiveness_and_damage = list(zip(move_data, move_effectiveness_and_damage))

        # Sort by damage
        move_effectiveness_and_damage.sort(key=lambda x: -x[1])

        best_move = move_effectiveness_and_damage[0][0]
        print(best_move["name"])
    return best_move["name"]

