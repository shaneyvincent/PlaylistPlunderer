Playlist Plunderer: 
Automate iTunes library organization with Shazam. Correct track info with minimal effort. #MusicOrganization #iTunes #Shazam


requirements for app
macOS 10.15.7 or higher
blackhole for internal listening 

CHROME DRIVER
chrome driver should automatically update 

INSTALL APP REQUIREMENTS

install app requirements by running requirements.txt command in terminal


requirements for unbundled hardline version of app

macOS 10.15.7 or higher
blackhole for internal listening 

install python 
3.12 or higher

PYQT5 5.15

Selenium 4.17



CHROME DRIVER

chrome driver replace location in users/your name

new macs  ARM chrome driver, older intel mac need 64x chrome driver

chrome driver version must match chrome version

https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/122.0.6261.6/mac-arm64/chromedriver-mac-arm64.zip

https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/122.0.6261.6/mac-x64/chromedriver-mac-x64.zip

update path to chrome driver in automation_script.py


UPDATE PATHS IN SCRIPTS
update paths to images, and scripts and folders to there new location 

INSTALL APP REQUIREMENTS

install app requirements by running requirements.txt command in terminal

in terminal create a virtual environment

activate virtual environment

navigate to PlaylistPlunderer

run requirements.txt 

Launch App

How to use

Create a playlist in iTunes called Playlist Plunderer

The track dragged into this playlist will be run through PlaylistPlunderer auto Shazam
Each track consists of four attributes that can be updated
Song Title, Artist, Album, and Genre

ITERATIONS
Iterations give you the option to select how many times you would like to use Shazam to scan a song in the playlist. you can select between one two or three times.

 to avoid confusion with similar songs, remixes a cappella, DJ blending mixes fade in and other issues that may cause Shazam to mistakenly identify a song, each iteration begins playing the track at a particular point in the track where it is most likely to catch a match.

1 iteration
 at one iteration. It will begin playing each track a quarter of the way into each track.

2 iteration
At two iterations it will play each song twice, the first time it will begin playing at a quarter of the way into the track and the second time it will begin playing halfway through the track. 

3 iteration
At three iterations it will play each song three times, the first time it will begin at a quarter of the way into the track and the second time it will begin playing halfway through the track and the third time it will begin playing 3/4 of the way through the track.

 each iteration will stop after Shazam returns a result. You can read these results in the window while updates occur in iTunes.


Iteration Rules

1 iteration (fastest)
PlaylistPlunderer will only update an attribute field returned by Shazam. If any one of the four attribute fields are not returned by Shazam, then no changes will occur to that field in iTunes.
If no match is found, PlaylistPlunderer will prepend ‘Shazam not found’ to the comment section in iTunes

2 iterations (strict)
PlaylistPlunderer will only update an attribute field returned from Shazam that matched on both iterations. If any one of the four attribute fields do not match on both iterations then no changes to that attribute field will occur in iTunes.
If no match is returned by Shazam in one of the two iterations then ‘Shazam not found’ will be prepended to the common section in iTunes

3 iterations (slowest, most accurate)
PlaylistPlunderer will only update an attribute field returned from Shazam that has matched at least two times out of the three iterations. If any one of the four attribute field do not match at least two times out of the three iterations then no changes to that attribute field will occur in iTunes.
If no match is returned by Shazam in two out of the three iterations or more  then ‘Shazam not found’ will be prepended to the comment section in iTunes

Internal Listening
PlaylistPlunderer can work with internal audio as well so while it's running, you do not have to hear it go through the playlist however, in order for this functionality to work, you have to set your system input an output to internal listening using a program like sound flower or black hole



1. Installing Playlist Plunderer and Its Prerequisites
"To install Playlist Plunderer, the most crucial step is setting up the requirements.txt file via terminal. Open your terminal, navigate to the Playlist Plunderer folder, and run pip install -r requirements.txt. This command installs all necessary Python packages for both versions of our app. Ensure your macOS is version 10.15.7 or higher, and you have Chrome Driver compatible with your Chrome version installed, along with Blackhole for internal listening. This setup is key to getting your music organized efficiently."


2. Correcting Metadata for a Single Track
"Correcting metadata for a single track is simple. Drag your track into the Playlist Plunderer playlist in iTunes. Our app starts at a strategic point in the song to ensure accurate Shazam matching. Watch as Playlist Plunderer updates your song's metadata seamlessly."

3. Understanding Iterations
"Iterations in Playlist Plunderer are about balancing accuracy and time. The more iterations you choose, from 1 to 3, the more thorough the search for each song, as the app scans different parts of the track to ensure a match. This means a higher chance of accurate metadata correction. However, keep in mind that more iterations also mean more time is required to process your playlist. It's all about finding the right balance for your needs."

4. Batch Processing Multiple Songs
"To batch process multiple songs, simply add them to your Playlist Plunderer playlist in iTunes. Our app will sequentially process each track, ensuring your entire music library is organized and accurately labeled in no time."

5. When Metadata Doesn't Update
"If a song's metadata doesn't update, it's typically because Shazam didn't provide that particular field, returned 'no match found,' or there was a discrepancy in the results for that attribute across iterations. Playlist Plunderer aims to ensure accuracy by only updating metadata when there's clear confirmation from Shazam, preserving the integrity of your music library."

6. How to Set Up Internal Listening with Blackhole for Silent Operation
"For silent operation, install Blackhole and set it as your system's audio output. This way, Playlist Plunderer can process your songs without playing them out loud, perfect for uninterrupted work or leisure."


7. What to Do If Playlist Plunderer Finds Multiple Matches for a Song
"When multiple matches are found, the iteration level you've selected plays a crucial role. For an attribute to be considered a match and thus suitable for updating the metadata in iTunes, it must align a certain number of times across iterations: once for one iteration, twice for two iterations, and at least two out of three times for three iterations. This system ensures that only the most accurate metadata is used to update your songs, maintaining the quality and accuracy of your music library." it will leave any fields that do not meet he match criteria untouched. 

6. How to Set Up Internal Listening with Blackhole for Silent Operation
"For silent operation, install Blackhole and set it as your system's audio output. This way, Playlist Plunderer can process your songs without playing them out loud, perfect for uninterrupted work or leisure."

