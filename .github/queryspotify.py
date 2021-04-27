from spotipy import Spotify, SpotifyOAuth, CacheHandler
import time
import json
import os
from typing import Optional
from github import Github


class SecretsCacheHandler(CacheHandler):
    def __init__(
        self,
        repository_name,
        github_access_token: str,
        token_info_string=None,
        secret_cache_name="SPOTIPY_CACHE",
    ):
        CacheHandler.__init__(self)
        # Create github api client from token or secret name containing token
        if github_access_token != None:
            self.github_client = Github(github_access_token)
        else:
            raise Exception(
                "You must provide token or secret name containing your github access token in order to instantiate the cache handler"
            )

        self.secret_cache_name = secret_cache_name
        self.repository_name = repository_name

        if token_info_string is None:
            self.token_info = None
        else:
            self.token_info = json.loads(token_info_string)

    @property
    def repo(self):
        if self._repo is None:
            self._repo = self.github_client.get_repo(self.repository_name)
        return self._repo

    def save_token_to_cache(self, token_info):
        self.token_info = token_info

        # `token_info` will be a python dict. convert it to a JSON string.
        token_string = json.dumps(token_info)
        # save the `token_string` to your secrets
        self._repo.create_secret(
            secret_name=self.secret_cache_name, unencrypted_value=token_string
        )

    def get_cached_token(self):
        return self.token_info

    def _debug_make_token_expired(self):
        # print("_test_make_token_expired")
        self.token_info["expires_at"] = int(time.time())


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

