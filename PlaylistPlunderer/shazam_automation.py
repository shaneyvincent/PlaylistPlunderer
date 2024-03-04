import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import time
import json
import os
import sys

# Function to get playlist length
def get_playlist_length():
    applescript_command = """
    tell application "Music"
        set thePlaylist to playlist "Playlist Plunderer"
        return count of tracks of thePlaylist
    end tell
    """
    result = subprocess.run(["osascript", "-e", applescript_command], capture_output=True, text=True)
    return int(result.stdout.strip())

# Function to play song in iTunes
def play_song_in_itunes(song_index, position_percentage):
    applescript_command = f"""
    tell application "Music"
        set thePlaylist to playlist "Playlist Plunderer"
        set theTracks to tracks of thePlaylist
        set theTrack to item {song_index} of theTracks
        play theTrack
        delay 2
        set player position to (duration of theTrack) * {position_percentage}
    end tell
    """
    subprocess.run(["osascript", "-e", applescript_command], text=True)

# Function to stop music
def stop_music():
    applescript_command = """
    tell application "Music"
        stop
    end tell
    """
    subprocess.run(["osascript", "-e", applescript_command], text=True)



# Function to add comment to iTunes
def add_comment_to_itunes(song_index, comment):
    applescript_command = f"""
    tell application "Music"
        set thePlaylist to playlist "Playlist Plunderer"
        set theTracks to tracks of thePlaylist
        set theTrack to item {song_index} of theTracks
        set theComment to comment of theTrack
        if theComment is not "" then
            set comment of theTrack to "{comment} - " & theComment
        else
            set comment of theTrack to "{comment}"
        end if
    end tell
    """
    subprocess.run(["osascript", "-e", applescript_command], text=True)

def run_automation(num_iterations):
    global should_stop
    should_stop = False  # Reset the stop flag at the start

    # Initialize driver as None before the try block
    driver = None


    try:
            # Set up ChromeDriver options
        # Set up ChromeDriver
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

            # Set the browser window size and position
        driver.set_window_size(350, 250)
        screen_width = driver.execute_script("return screen.width;")
        screen_height = driver.execute_script("return screen.height;")
        driver.set_window_position(screen_width - 350, screen_height - 250)

        # Correctly fetching the playlist length here without 'driver' parameter
        playlist_length = get_playlist_length()
    
            # Define positions based on the number of iterations
        positions = {
            1: ["0.25"],
            2: ["0.25", "0.50"],
            3: ["0.25", "0.50", "0.75"]
        }.get(num_iterations, ["0.25", "0.50", "0.75"])  # Default to three positions

        shazam_results = {}
  
  
        for song_index in range(1, playlist_length + 1):
            song_results = {}
            no_match_count = 0
            for position in positions:
                play_song_in_itunes(song_index, float(position))
                driver.get('https://www.shazam.com/')
                time.sleep(10)

            # Attempt to find and click the Shazam button to identify the song
            try:
                shazam_button = driver.find_element(By.CLASS_NAME, "shazam-button")
                shazam_button.click()
                time.sleep(23)  # Adjust sleep as needed for Shazam to identify the song
            except NoSuchElementException:
                print(f"Could not find the Shazam button for Song {song_index} at {float(position) * 100}%")
                sys.stdout.flush()
                continue  # Skip this iteration if the Shazam button isn't found

        # Initialize variables for song details as "Not found"
        song_title = "Not found"
        artist_name = "Not found"
        album_name = "Not found"
        genre = "Not found"

        # Try to capture song details from Shazam's response
        try:
            song_title = driver.find_element(By.CSS_SELECTOR, "h1.title.line-clamp-2").text
        except NoSuchElementException:
            pass  # If not found, keep "Not found"
        try:
            artist_name = driver.find_element(By.CSS_SELECTOR, "h2.artist.ellip").text
        except NoSuchElementException:
            pass
        try:
            album_name = driver.find_element(By.CLASS_NAME, "playlist-title").text
        except NoSuchElementException:
            pass
        try:
            genre = driver.find_element(By.CLASS_NAME, "genre").text
        except NoSuchElementException:
            pass

        # Process captured details
        if song_title != "Not found" or artist_name != "Not found":
            song_results[position] = {
                "title": song_title,
                "artist": artist_name,
                "album": album_name,
                "genre": genre
            }
        else:
            no_match_count += 1

    # After trying all positions for a song
    if no_match_count == len(positions):
        # If no details were found for any position, mark as not found
        add_comment_to_itunes(song_index, "Shazam not found")
    else:
        # If details were found for at least one position, save the results
        shazam_results[f"Song {song_index}"] = song_results

    # Outside the loop, after processing all songs
    json_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'shazam_results.json')
    with open(json_file_path, 'w') as json_file:
        json.dump(shazam_results, json_file, indent=4)


except Exception as e:
    print(f"An error occurred: {e}")
except KeyboardInterrupt:
    print("Shazam automation stopped.")
    sys.stdout.flush()
finally:
    if driver is not None:
        driver.quit()
    stop_music()
# Function to update iTunes metadata
def update_itunes_metadata(song_index, field, value):
    if not value or value == "Not found":
        return  # Skip updating if the value is empty or not found
    escaped_value = value.replace('"', '\\"')
    applescript_command = f"""
    tell application "Music"
        set thePlaylist to playlist "Playlist Plunderer"
        set theTracks to tracks of thePlaylist
        set theTrack to item {song_index} of theTracks
        set {field} of theTrack to "{escaped_value}"
    end tell
    """
    subprocess.run(["osascript", "-e", applescript_command], text=True)

# Function to check match for updating metadata
def check_match(attribute_data, required_matches):
    count = {}
    for value in attribute_data.values():
        if value != "Not found":
            count[value] = count.get(value, 0) + 1

    for key, val in count.items():
        if val >= required_matches:
            return key
    return None

# Process results and update metadata
for song_key, song_data in shazam_results.items():
    song_index = int(song_key.split()[1])

    if num_iterations == 1:
        required_matches = 1
    elif num_iterations == 2:
        required_matches = 2
    else:  # num_iterations == 3
        required_matches = 2

    title_result = check_match({pos: data['title'] for pos, data in song_data.items()}, required_matches)
    artist_result = check_match({pos: data['artist'] for pos, data in song_data.items()}, required_matches)
    album_result = check_match({pos: data['album'] for pos, data in song_data.items()}, required_matches)
    genre_result = check_match({pos: data['genre'] for pos, data in song_data.items()}, required_matches)

    # Update metadata based on results
    if title_result:
        update_itunes_metadata(song_index, 'name', title_result)
    if artist_result:
        update_itunes_metadata(song_index, 'artist', artist_result)
    if album_result:
        update_itunes_metadata(song_index, 'album', album_result)
    if genre_result:
        update_itunes_metadata(song_index, 'genre', genre_result)



