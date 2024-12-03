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
    '''
    Triggers a GitHub Actions workflow by making a POST request to the GitHub API.

    Parameters:
    - githubKey (str): The personal access token for GitHub authentication.
    - githubActionName (str): The name of the action (workflow) to trigger.
    - githubProfileName (str): The GitHub username or organization name where the repository is hosted.
    - githubRepoName (str): The name of the repository where the action is defined.

    Returns:
    - int: The HTTP status code from the response, indicating the result of the operation.

    Raises:
    - requests.HTTPError: If the request to the GitHub API fails, an HTTP error will be raised with details about the failure.

    Logs an informational message indicating that the specified GitHub action is being triggered.
    '''

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


async def checkForNewEntry() -> None:
    '''
    Checks for new entries in a Supabase table since the last checked time.

    This asynchronous function queries the Supabase table specified via the environment variable 'SUPABASE_TABLE'. It retrieves the latest entry if 'lastCheckedTime' is None, setting it as the baseline for future checks. If 'lastCheckedTime' is already set, the function retrieves any entries with a 'created_at' timestamp greater than this baseline. If new entries are found, it updates 'lastCheckedTime' to the timestamp of the most recent entry and triggers a GitHub action.

    Global Variables:
    - lastCheckedTime (datetime): Stores the timestamp of the last check.

    Returns:
    - None
    '''

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


async def runListener(waitingTime:int=10):
    '''
    Continuously checks for new entries at specified intervals.

    This asynchronous function runs in an infinite loop, calling the `checkForNewEntry` function and then pausing execution for a specified waiting time (in seconds). The default waiting time is set to 10 seconds, but it can be adjusted by passing a different value when calling the function. 

    Parameters:
    - waitingTime (int): The number of seconds to wait between each check for new entries. Default is 10 seconds. 

    Note:
    This function is intended to be used with an event loop and relies on the `checkForNewEntry` function to perform the actual checking logic. Ensure that the checking mechanism can handle the frequency at which this function calls it.
    '''

    while True:
        await checkForNewEntry()
        await asyncio.sleep(waitingTime)


if __name__ == '__main__':
    asyncio.run(runListener())