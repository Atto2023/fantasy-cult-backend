import requests

token = "d70dadd582dd31b0dc85ac873aba1c86"

class EntitySports:

    @classmethod
    async def cricket_series_data_live(cls):
        url = f"https://rest.entitysport.com/v2/competitions?token={token}&per_page=50&paged=1&status=live"
        response = requests.request("GET", url)
        return response.json()["response"]["items"]

    @classmethod
    async def cricket_series_data_fixture(cls):
        url = f"https://rest.entitysport.com/v2/competitions?token={token}&per_page=50&paged=1&status=fixture"
        response = requests.request("GET", url)
        return response.json()["response"]["items"]

    @classmethod
    async def series_squad_data(cls, series_id):
        url = f"https://rest.entitysport.com/v2/competitions/{series_id}/squads/?token={token}"
        response = requests.request("GET", url)
        return response.json()["response"]["squads"]
    
    @classmethod
    async def cricket_team_data(cls, team_id):
        url = f"https://rest.entitysport.com/v2/teams/{team_id}?token={token}"
        response = requests.request("GET", url)
        return response.json()["response"]
    
    @classmethod
    async def cricket_player_data(cls, player_id):
        url = f"https://rest.entitysport.com/v2/players/{player_id}/stats?token={token}"
        response = requests.request("GET", url)
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return None

    @classmethod
    async def cricket_series_match_data(cls, series_id):
        url = f"https://rest.entitysport.com/v2/competitions/{series_id}/matches/?token={token}&per_page=1000&paged=1"
        response = requests.request("GET", url)
        return response.json()["response"]["items"]

class EntitySportsLive:

    @classmethod
    async def entity_match_status(cls, match_id):
        url = f"https://rest.entitysport.com/v2/matches/{match_id}/info?token={token}"
        response = requests.request("GET", url)
        return response.json()["response"]

    @classmethod
    async def entity_series_status(cls, series_id):
        url = f"https://rest.entitysport.com/v2/competitions/{series_id}/?token={token}"
        response = requests.request("GET", url)
        return response.json()["response"]

class EntitySportsPoint:

    @classmethod
    async def entity_sports_points(cls, match_id):
        url = f"https://rest.entitysport.com/v2/matches/{match_id}/newpoint2?token={token}"
        response = requests.request("GET", url)
        return response.json()["response"]
