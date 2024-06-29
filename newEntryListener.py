import logging
logging.basicConfig(level=logging.INFO)

from dotenv import load_dotenv
load_dotenv()

import os
import asyncio
from supabase import create_client, Client

supabase: Client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
lastCheckedTime = None


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
    else:
        logging.info(f'No new entries found since last check...')


async def runListener(waitingTime=10):
    while True:
        await checkForNewEntry()
        await asyncio.sleep(waitingTime)


if __name__ == "__main__":
    asyncio.run(runListener())