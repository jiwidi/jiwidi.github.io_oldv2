# Exploiting github secrets

In the music [music](ee) of this webpage you can find the latest artist I've listened to in spotify, this list is refreshed every day at 00:00. This automated job was kind of a pain in the ass to get working as that data is actually not public, you need to use an auth based spotify API to get this results. Having to deal with authentification was a big no for me as I designed this webpage to run "server-less" or more accurate "maintenance-less", I run it in github pages so I dont need to serve it myself and can rely in the more professional uptime github can provide. If someone visits your webpage as a programmer as is offline that will not speak good for you.

So, how do I still refresh this list and run in github pages? I found an "unconventional" use of github secrets where I store my auth tokens, using it as filesystem of my missing server. Let's go into the steps to make this work:


## Create a script that queries your user data

By using [spotipy](https://github.com/plamere/spotipy) python API for spotify I was able to write a very simple script that did the job.

```python

from spotipy import Spotify, SpotifyOAuth, CacheFileHandler

username = "your username"
scope = "user-read-recently-played"
redirect_uri = "your redirect uri"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="YOUR_APP_CLIENT_ID",
                                               client_secret="YOUR_APP_CLIENT_SECRET",
                                               redirect_uri="YOUR_APP_REDIRECT_URI",
                                               scope=scope))

results = spotify.current_user_recently_played()
results["date_run"] = time.time()

with open(".github/spotify_query_results.json", "w+") as f:
    json.dump(results, f)
```

This script would take your `client_id`, `client_secret` and `redirect_uri` defined at your spotify dev account and run the query for you. You can define those values in the script itself but then anyone would be able to see them in the github repo and break your security.

### Bad solution
Why don't  we store the values for the auth tokens in github secrets? That's what they are made for right? As long as we pass the secrets to the script in the github action yaml we only need a few modifications:

```python

from spotipy import Spotify, SpotifyOAuth, CacheFileHandler
import os
username = "your username"
scope = "user-read-recently-played"
redirect_uri = "your redirect uri"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.environ["YOUR_APP_CLIENT_ID"],
                                               client_secret=os.environ["YOUR_APP_CLIENT_SECRET"],
                                               redirect_uri=os.environ["YOUR_APP_REDIRECT_URI"],
                                               scope=scope))

results = spotify.current_user_recently_played()
results["date_run"] = time.time()

with open(".github/spotify_query_results.json", "w+") as f:
    json.dump(results, f)
```

This will work but what will you do when your token expires? The code has no way to ask for a new code and it will need your human input to make the script work again. This is were the funs begins.

### Nice solution

If we look closer on how the `SpotifyOAuth` object works we can find the parameter `CacheHandler` that will help us with this task. This object can refresh your token automatically if its expired as long as it has another spotify token called `refreshToken`. This `refreshToken` is a one time use only token to refresh the auth token, when the token is used the handler will ask for a new `refreshToken` to store in memory as json for next time the main token expires. If this `refreshToken` is one time use only this means even if we added it to github secrets this will only solve the issue of the first solution once, we need to find a solution to store the new `refreshToken` spotify provides us while staying "maintenance-less" and not revealing any secret information in our github repo.

Let's use github secrets as our filesystem! Why dont we write a custom `CacheHandler` that instead of writting to a json file writes into github secrets? Sort of making a github secret a file to read and write from.

```python
from spotipy import Spotify, SpotifyOAuth, CacheHandler
from github import Github

class SecretsCacheHandler(CacheHandler):
    def __init__(
        self,
        repository_name,
        github_access_token=None,
        github_access_token_secret_name=None,
        secret_cache_name="SPOTIPY_CACHE",
    ):
        CacheHandler.__init__(self)
        # Create github api client from token or secret name containing token
        if github_access_token != None:
            self.github_client = Github(github_access_token)
        elif github_access_token_secret_name != None:
            self.github_client = Github(os.environ[github_access_token_secret_name])
        else:
            raise Exception(
                "You must provide token or secret name containing your github access token in order to instantiate the cache handler"
            )

        self.secret_cache_name = secret_cache_name
        self.repository = self.github_client.get_repo(repository_name)

    def save_token_to_cache(self, token_info):
        # `token_info` will be a python dict. convert it to a JSON string.
        token_string = json.dumps(token_info)
        # save the `token_string` to your secrets
        self.repository.create_secret(
            secret_name=self.secret_cache_name, unencrypted_value=token_string
        )

    def get_cached_token(self):
        # Retrieve secret from enviorment
        token_string = os.environ[self.secret_cache_name]

        # Convert the string back to a dict and return it
        token_info = json.loads(token_string)

        return token_info


username = "jiwidi"
scope = "user-read-recently-played"

spotify = Spotify(
    auth_manager=SpotifyOAuth(
        scope=scope,
        cache_handler=SecretsCacheHandler(
            repository_name="jiwidi/jiwidi.github.io",
            github_access_token_secret_name="MAIN_TOKEN",
        ),
    )
)

results = spotify.current_user_recently_played()
results["date_run"] = time.time()

with open(".github/spotify_query_results.json", "w+") as f:
    json.dump(results, f)
```

This script will use [pygithub](https://github.com/PyGithub/PyGithub) library to update the token with the content that would have gone into a json file instead. This will also need a github auth token but that one we can store in the secrets as well. Now we only need to setup the github action to run it daily and store results into a file of our repositoy.

### Setting up the github action

```yaml
name: SPOTIFYQUERY

# Controls when the action will run.
on:
  #Run every day at midnight
  schedule:
    - cron: "0 0 * * *"

  # Allows you to run this workflow manually from the Actions tab
  workflow_dispatch:

# A workflow run is made up of one or more jobs that can run sequentially or in parallel
jobs:
  # This workflow contains a single job called "build"
  build:
    # The type of runner that the job will run on
    runs-on: ubuntu-latest

    # Steps represent a sequence of tasks that will be executed as part of the job
    steps:
      # Checks-out your repository under $GITHUB_WORKSPACE, so your job can access it
      - uses: actions/checkout@v2

      # Set up python environment
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8

      - name: Set up python libraries
        run: python -m pip install requests spotipy==2.18

      - name: Latest pytigt
        run: python -m pip install git+git://github.com/PyGithub/PyGithub@master

      # Run our spotify query with custom secretCacheHandler
      - name: Run spotify query
        run: python .github/queryspotify.py
        env:
          SPOTIPY_CLIENT_SECRET: ${{ secrets.SPOTIPY_CLIENT_SECRET}}
          SPOTIPY_CLIENT_ID: ${{ secrets.SPOTIPY_CLIENT_ID}}
          SPOTIPY_REDIRECT_URI: ${{ secrets.SPOTIPY_REDIRECT_URI}}
          SPOTIPY_CACHE: "${{ secrets.SPOTIPY_CACHE}}"
          MAIN_TOKEN: '${{ secrets.MAIN_TOKEN}}'

      #Update repo with new recent artist
      - name: Commit and Push
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add -A
          git commit -m "A robot updating spotify query results. Beep beep boop"
          git push
```


