import asyncio
import random
import time

from actions.user_actions import GitHubFollowActions

if __name__ == "__main__":
    # asyncio.run(GitHubFollowActions.follow_batch(355))
    asyncio.run(GitHubFollowActions.unfollow_batch(955))
    print()
    while True:
        try:
            asyncio.run(GitHubFollowActions.follow_batch(355))
            asyncio.run(GitHubFollowActions.unfollow_batch(955))

        except Exception as e:
            print(e)
        sleep_hours = random.uniform(8, 10)
        time.sleep(sleep_hours * 3600)
