from spotipy import Spotify, SpotifyOAuth, CacheHandler
import time
import json
import os
from github import Github


class SecretsCacheHandler(CacheHandler):
    def __init__(
        self,
        repository_name,
        github_access_token=None,
        secret_cache_name="SPOTIPY_CACHE",
    ):
        CacheHandler.__init__(self)
        # Create github api client from token or secret name containing token
        if github_access_token != None:
            self.github_client = Github(github_access_token)
        else:
            raise Exception(
                "You must provide token containing your github access token in order to instantiate the cache handler"
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
            github_access_token=os.environ["MAIN_TOKEN"],
        ),
    )
)

results = spotify.current_user_recently_played()
results["date_run"] = time.time()

with open(".github/spotify_query_results.json", "w+") as f:
    json.dump(results, f)

