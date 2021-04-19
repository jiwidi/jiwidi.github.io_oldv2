import sys
import spotipy
import spotipy.util as util

from github import Github


# scope = 'user-read-recently-played'
# username = 'jiwidi'
# token = util.prompt_for_user_token(username, scope, redirect_uri="http://localhost:8888/callback/")

# print(token)

# if token:
#     sp = spotipy.Spotify(auth=token)
#     results = sp.current_user_recently_played()
#     for item in results['items']:
#         track = item['track']
#         print(track['name'] + ' - ' + track['artists'][0]['name'])
# else:
#     print("Can't get token for", username)


g =Github('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')
repository = g.get_repo("jiwidi/jiwidi.github.io")
repository.create_secret(secret_name="MAIN_TOKEN", unencrypted_value='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')
