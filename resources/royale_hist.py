import aiohttp
from config import clash_royale_key



async def fetch_player_data(tag): 
    
    url = f'https://api.clashroyale.com/v1/players/%23{tag}/battlelog'
    
    headers = {
        'Authorization': f'Bearer {clash_royale_key}'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            try:
                response = await response.json()
                last_match = response[0]
            except:
                return
            
            return {
                'player_tag' : '#' + tag,
                'match_id' : last_match['battleTime'].split('.')[0],
                'type' : last_match['type'],
                'gamemode' : last_match['gameMode']['name'],
                'is_ladder_tournament' : last_match['isLadderTournament'],
                'team' : { player['tag'] : { 'username' : player['name'], 'tag' : player['tag'], 'deck' : player['cards'], 'elixir_leaked' : player['elixirLeaked'] } for player in last_match['team'] },
                'opponent' : { player['tag'] : { 'username' : player['name'], 'tag' : player['tag'], 'deck' : player['cards'], 'elixir_leaked' : player['elixirLeaked'] } for player in last_match['opponent'] if player['name'] != '' },
                'crowns' : last_match['team'][0]['crowns'],
                'result' : 'WIN' if last_match['team'][0]['crowns'] > last_match['opponent'][0]['crowns'] else 'LOSS'
            }
    
