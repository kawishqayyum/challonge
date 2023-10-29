import json
import requests
import pandas as pd
from datetime import datetime


with open('config.json', mode='r') as config:
    data = json.load(config)

API_KEY = data.get('API_KEY')
BASE_URL = 'https://api.challonge.com'


def convert_datetime(df, column_name):
    format_string = '%Y-%m-%dT%H:%M:%S.%f%z'
    return datetime.strptime(df[column_name], format_string)


def get_tourney_participants(tournament_id):
    url = f'{BASE_URL}/v1/tournaments/{tournament_id}/participants.json'
    response = requests.get(url, params=params, headers=headers)

    data = response.json()
    participants = [part.get('participant') for part in data]

    return participants


params = {
    'api_key': API_KEY,
    'state': 'ended'
}

headers = {
    'Accept':
        'text/html,application/xhtml+xml,application/xml;'
        'q=0.9,image/avif,image/webp,image/apng,*/*;'
        'q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/117.0.0.0 Safari/537.36',
}

tournies_columns = [
    'id',
    'name',
    'game_name',
    'description',
    'tournament_type',
    'started_at',
    'completed_at',
    'game_id',
    'participants_count',
    'full_challonge_url',
]

tournament_index_url = f'{BASE_URL}/v1/tournaments.json'
response = requests.get(tournament_index_url, params=params, headers=headers)
tournaments = response.json()
tournaments = [tournament.get('tournament') for tournament in tournaments]
tournies_df = pd.DataFrame(tournaments)

fifa_tournies_df = tournies_df[tournies_df.game_name.str.contains('FIFA')]
fifa_tournies_df.reset_index(drop=True, inplace=True)
fifa_tournies_df = fifa_tournies_df[tournies_columns]

fifa_tournies_df['started_at'] = fifa_tournies_df.apply(
    convert_datetime,
    args=('started_at',),
    axis=1
)

fifa_tournies_df['completed_at'] = fifa_tournies_df.apply(
    convert_datetime,
    args=('completed_at',),
    axis=1
)

fifa_tournies_df['duration'] = pd.to_timedelta(
    fifa_tournies_df.completed_at - fifa_tournies_df.started_at
)

fifa_tournies_df.to_csv('tournies.csv', index=False)

