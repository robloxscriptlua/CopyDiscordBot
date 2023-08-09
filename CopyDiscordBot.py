import aiohttp
import asyncio
import re
from colorama import Fore, init
import pyperclip

init()

# Replace 'YOUR_USER_TOKEN' with your actual user token
USER_TOKEN = "YOUR_USER_TOKEN"

# Replace 'YOUR_CHANNEL_IDS' with the actual channel IDs where you want to fetch messages
CHANNEL_IDS = ["YOUR_CHANNEL_IDS", "YOUR_CHANNEL_IDS", "YOUR_CHANNEL_IDS"]

# Replace 'SPECIFIC_USER_ID' with the ID of the user whose messages you want to copy
SPECIFIC_USER_ID = "SPECIFIC_USER_ID"

searches = 0

async def fetch_messages(channel_id, session, semaphore):
    latest_message_id = None
    while True:
        async with semaphore:
            url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
            params = {"limit": 1}
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    messages = await response.json()
                    if messages:
                        message = messages[0]
                        message_id = message["id"]
                        if message_id != latest_message_id:
                            latest_message_id = message_id
                            content = message.get("content")
                            user_id = message.get("author", {}).get("id")
                            if content and user_id == SPECIFIC_USER_ID:
                                content = re.sub(r'^\s*#\s+|\s*\|\s*|"', '', content)  # Removes "# ", "|" with or without spaces, and double quotes from the text if encountered
                                pyperclip.copy(content)
                                print(
                                    f"{Fore.GREEN}Message contents copied to clipboard: {content}"
                                )
                        else:
                            global searches
                            searches += 1
                            print(
                                f"{Fore.YELLOW}No new messages detected, working ({searches}) Response: {response.status}"
                            )
                else:
                    print(f"Failed to fetch messages. Status Code: {response.status}")

        await asyncio.sleep(0.2)  # Fetch messages every 0.2 seconds

async def main():
    semaphore = asyncio.Semaphore(10)  # Limit the number of concurrent connections
    async with aiohttp.ClientSession(
        headers={"Authorization": f"{USER_TOKEN}"}
    ) as session:
        tasks = [
            fetch_messages(channel_id, session, semaphore) for channel_id in CHANNEL_IDS
        ]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
