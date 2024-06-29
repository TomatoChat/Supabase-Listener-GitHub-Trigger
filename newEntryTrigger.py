import logging
logging.basicConfig(level=logging.INFO)

from dotenv import load_dotenv
load_dotenv()

import os
import asyncio
from supabase import create_client, Client
import requests


supabase: Client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
lastCheckedTime = None


def triggerGithubAction(githubKey:str=os.getenv('GH_KEY'), githubActionName:str=os.getenv('GH_ACTION'), githubProfileName:str=os.getenv('GH_PROFILE'), githubRepoName:str=os.getenv('GH_REPO')) -> int:
    logging.info(f'Triggering {githubActionName} action...')

    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'token {githubKey}'
    }
    body = {
        'event_type': f'{githubActionName}'
    }
    url = f'https://api.github.com/repos/{githubProfileName}/{githubRepoName}/dispatches'
    response = requests.post(url, headers=headers, json=body)

    response.raise_for_status()

    return response.status_code


async def checkForNewEntry():
    global lastCheckedTime
    if lastCheckedTime is None:
        response = supabase.table(os.getenv('SUPABASE_TABLE')).select('*').order('created_at', desc=True).limit(1).execute()

        if response.data:
            lastCheckedTime = response.data[0]['created_at']
        
        logging.info(f'Initial check, setting baseline: {lastCheckedTime}')
        return

    response = supabase.table(os.getenv('SUPABASE_TABLE')).select('*').gt('created_at', lastCheckedTime).execute()
    newEntry = response.data

    if newEntry:
        logging.info(f'Found {len(newEntry)} new entries since {lastCheckedTime}')

        lastCheckedTime = newEntry[-1]['created_at']
        githubActionResponse = triggerGithubAction()

        logging.info(f'GitHub action trigger response: {githubActionResponse}')
    else:
        logging.info(f'No new entries found since last check...')


async def runListener(waitingTime=10):
    while True:
        await checkForNewEntry()
        await asyncio.sleep(waitingTime)


if __name__ == "__main__":
    asyncio.run(runListener())