from flask import Flask, redirect, render_template, request, session
from app import app
from app import spotify_service
import re

PROFILE_ITEM_COUNT = 5
TOP_ARTISTS_COUNT = 50
TOP_TRACKS_COUNT = 50

# App routes
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/authenticate')
def authenticate():
    return redirect(spotify_service.AUTH_URL)

@app.route('/callback')
def callback():
    auth_token = request.args['code']
    auth_header = spotify_service.authorize(auth_token)
    session['auth_header'] = auth_header

    return redirect('profile')

@app.route('/profile')
def profile():
    if 'auth_header' in session:
        auth_header = session['auth_header']

        # Get profile data
        profile_data = spotify_service.get_user_profile(auth_header)
        profile_data['first_name'] = profile_data['display_name'].partition(' ')[0]
        profile_pic = 'https://via.placeholder.com/150'
        if len(profile_data['images']) > 0:
            profile_pic = profile_data['images'][0]['url']

        # Get most recently played tracks
        recently_played = spotify_service.get_recently_played(auth_header)
        track_count = len(recently_played["items"])
        if track_count > PROFILE_ITEM_COUNT:
            track_count = PROFILE_ITEM_COUNT

        recent_tracks = {}
        for item in recently_played["items"]:
            # Verify that there are no repeats
            if item["track"]["id"] not in recent_tracks.keys():
                # remove text enclosed within parentheses from track name
                item["track"]["name"] = re.sub(r'\([^)]*\)', '', item["track"]["name"])
                recent_tracks[item["track"]["id"]] = item
            if len(recent_tracks) == track_count:
                break

        top_artists = spotify_service.get_top_artists(auth_header, 'short_term', PROFILE_ITEM_COUNT)

        return render_template('profile.html',
                                profile=profile_data,
                                profile_pic=profile_pic,
                                recent_tracks=recent_tracks.values(),
                                top_artists=top_artists["items"])
    
    return render_template('profile.html')

@app.route('/top-artists')
def top_artists():
    if 'auth_header' in session:
        auth_header = session['auth_header']

        # Get profile data
        profile_data = spotify_service.get_user_profile(auth_header)
        profile_data['first_name'] = profile_data['display_name'].partition(' ')[0]
        profile_pic = 'https://via.placeholder.com/150'
        if len(profile_data['images']) > 0:
            profile_pic = profile_data['images'][0]['url']
        
        top_artists_all = spotify_service.get_top_artists(auth_header, 'long_term', TOP_ARTISTS_COUNT)
        top_artists_six = spotify_service.get_top_artists(auth_header, 'medium_term', TOP_ARTISTS_COUNT)

        return render_template('top-artists.html',
                                profile=profile_data,
                                profile_pic=profile_pic,
                                top_artists_all=top_artists_all['items'],
                                top_artists_six=top_artists_six['items'])

@app.route('/top-tracks')
def top_tracks():
    if 'auth_header' in session:
        auth_header = session['auth_header']

        # Get profile data
        profile_data = spotify_service.get_user_profile(auth_header)
        profile_data['first_name'] = profile_data['display_name'].partition(' ')[0]
        profile_pic = 'https://via.placeholder.com/150'
        if len(profile_data['images']) > 0:
            profile_pic = profile_data['images'][0]['url']
        
        top_tracks_all = spotify_service.get_top_tracks(auth_header, 'long_term', TOP_TRACKS_COUNT)
        top_tracks_six = spotify_service.get_top_tracks(auth_header, 'medium_term', TOP_TRACKS_COUNT)

        for item in top_tracks_all['items']:
            item['name'] = re.sub(r'\([^)]*\)', '', item["name"])
        for item in top_tracks_six['items']:
            item['name'] = re.sub(r'\([^)]*\)', '', item["name"])

        return render_template('top-tracks.html',
                                profile=profile_data,
                                profile_pic=profile_pic,
                                top_tracks_all=top_tracks_all['items'],
                                top_tracks_six=top_tracks_six['items'])