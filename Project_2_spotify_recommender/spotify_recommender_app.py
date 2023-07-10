def song_recommender():
    import pandas as pd
    import spotipy
    import config
    from spotipy.oauth2 import SpotifyClientCredentials
    from IPython.display import IFrame
    from random import randrange
    from fuzzywuzzy import fuzz, process
    import pickle
    
    # Model Choice
    def load(filename = "filename.pickle"): 
        try: 
            with open(filename, "rb") as f: 
                return pickle.load(f) 
        except FileNotFoundError: 
            print("File not found!")

    # 85 Clusters, 14000 Tracks
    kmeansFile = "Model/kmeans85df6.pickle" 
    scalerFile = "Model/scaler85df6.pickle"
    # 120 Clusters, 17000 Tracks
    # kmeans = "Model/kmeans120df8.pickle"
    # scaler = "Model/scaler120df8.pickle"

    kmeans = load(filename=kmeansFile)
    scaler = load(filename=scalerFile)

    # Local Data
    dfs = pd.read_csv("dfs85df6.csv", sep=";")
    X = pd.read_csv("dfsTraining85df6.csv", sep=";")
    dfTop100 = pd.read_csv("dfTop100.csv", sep=";")
    
    ### define functions ###################
    ### recommendation getter function
    def get_recommendationIDs_from_features(songID1):
        songFeatures = sp.audio_features(songID1)
        # create dataframe out of list of song features
        songFeaturesdf=pd.DataFrame(songFeatures)  
        songFeaturesdf=songFeaturesdf[["danceability","energy","loudness","speechiness","acousticness",
            "instrumentalness","liveness","valence","tempo","id","duration_ms"]]
        # use only selected song features
        songFeatures1 = songFeaturesdf.iloc[:,0:9]
        # scale features of recommended song 
        X_scaled = scaler.transform(songFeatures1)
        X_scaled_df = pd.DataFrame(X_scaled, columns = X.columns)
        # predict target cluster
        targetCluster = kmeans.predict(X_scaled_df)[0]
        # filter dataframe for target cluster
        dfSelected = dfs.loc[dfs["cluster"] == targetCluster]
        # select two random tracks from filtered dataframe
        recommendationIDs = []
        recommendationIDs.append(dfSelected.iloc[randrange(0,len(dfSelected))]["id"])
        recommendationIDs.append(dfSelected.iloc[randrange(0,len(dfSelected))]["id"])
        return recommendationIDs
    ### display player function
    def display_player(songID1):
        player_url = f"https://open.spotify.com/embed/track/{songID1}"
        display(IFrame(player_url, width="480", height="180"))
    ### yes-answer function
    def yes_answer(songID1):
        # Get recommendation IDs
        recommendationIDs = get_recommendationIDs_from_features(songID1)
        # display player
        display_player(recommendationIDs[0])
        print("Would you like a further suggestion? Type 'yes' or 'no': ")
        further_suggestion = input()
        if further_suggestion.lower() == "yes":
            # display player
            display_player(recommendationIDs[1]) 
        elif answer.lower() == "no":
            print()
        else:
            print("Please type 'yes' or 'no'")
    ### no-answer function
    def no_answer(songID1):
        # display player
        display_player(songID1)
        # Ask user whether this is the right track.
        answer = input("Is this the right track? Type 'yes' or 'no': ")
        return answer
    ### ########################
    
    # user credentials
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id= config.client_id,
                                                               client_secret= config.client_secret))
    # ask for user input
    inputString = input("enter song and/or artist name: ")

    # prepare top100 list for fuzzywuzzy
    columnList = []
    columnList.extend(dfTop100['0'].tolist())
    
    # check whether song is contained in Top 100
    #result = dfTop100[dfTop100['0'].str.contains(val)]['0'].values
    bestMatches1 = process.extract(inputString, columnList, scorer=fuzz.ratio, limit=3)
    bestMatches2 = []
    for match, score in bestMatches1:
        if score >= 60:
            bestMatches2.append(match)

    if len(bestMatches2) > 0:
        # search for song
        songData = sp.search(q=bestMatches2[0], limit=5)
        # get song ID
        songID = songData['tracks']['items'][0]['id']
        print('Song is present in the Top 100')
        # Display player
        display_player(songID)
        print('Recommending random song out of Top 100')
        songAndArtistTop100 = dfTop100.iloc[randrange(0,100),][0]
        # search for song
        songData = sp.search(q=songAndArtistTop100, limit=3)
        # get song ID
        songID = songData['tracks']['items'][0]['id']
        # Display player
        display_player(songID)
    else:
        print('Song is not Present in the Top 100')
        print('Recommending according to Spotify features')
    
        # search for song
        numberOfSelectedTracks, selectedTracksIndex = [12, 12]
        songData = sp.search(q=inputString.lower(), limit=numberOfSelectedTracks, market="GB")    
        # get song IDs - make sure song IDs are unique
        songIDs = []
        numberOfResults = 0
        while(numberOfResults < 3):
            i = numberOfSelectedTracks - selectedTracksIndex
            songID = songIDs.append(songData['tracks']['items'][i]['id'])
            selectedTracksIndex -= 1
            if songID not in songIDs:
                songIDs.append(songIDs)
                numberOfResults += 1

        songIDs.append(songData['tracks']['items'][0]['id'])
        songIDs.append(songData['tracks']['items'][1]['id'])
        songIDs.append(songData['tracks']['items'][2]['id'])

        print("The original track") #1 original
        next_answer = no_answer(songIDs[0])
        if next_answer.lower() == "yes": #1 recommendations
            yes_answer(songIDs[0])

        elif next_answer.lower() == "no": #2 original
            next_answer = no_answer(songIDs[1])
            if next_answer.lower() == "yes": #2 recommendations
                yes_answer(songIDs[1])

            elif next_answer.lower() == "no": #3 original
                next_answer = no_answer(songIDs[2])
                if next_answer.lower() == "yes": #3 recommendations
                    yes_answer(songIDs[2])

                elif next_answer.lower() == "no":
                    print("Please try another song or try to be more specific.")
                else:
                    print("Please type 'yes' or 'no'.")
            else:
                print("Please type 'yes' or 'no'.")
        else:
            print("Please type 'yes' or 'no'.")

    return()