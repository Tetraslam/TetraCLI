import os
import sys
import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials, firestore
from rebullet import Bullet, Input, Numbers, VerticalPrompt, YesNo, SlidePrompt, colors
from rich import print

load_dotenv()

cred = credentials.Certificate(os.getenv("private_key"))
app = firebase_admin.initialize_app(cred)

db = firestore.client()

def add_document(collection: str, document_name: str, info: dict):
  doc_ref = db.collection(collection).document(document_name)
  doc_ref.set(info)


def add_project_to_firebase():
  add_project = VerticalPrompt(
    [
      Input("Project name?"),
      Bullet("Main language?",
            choices = ["C++", "Python", "Javascript", "Go", "C#", "Mojo", "Not here!"]),
      Input("Give the project a short description! "),
      ],
      spacing = 1
    )
  add_project.launch()
  add_document("projects", add_project.result[0][1], {"name": add_project.result[0][1], "language": add_project.result[1][1], "description": add_project.result[2][1]})

def read_projects_from_firebase():
  projects = []
  projects_firebase = db.collection("projects")
  projects_list = projects_firebase.stream()
  for doc in projects_list:
    projects.append(doc.to_dict())
  for project in projects:
    print(f"\n[purple][bold]Project name: {project['name']}[/bold]\nLanguage: {project['language']}\nDescription: {project['description']}\n[/purple]")


def read_profile():
  profile_collection = db.collection("profile")
  profile_stream = profile_collection.stream()
  info = []
  for doc in profile_stream:
    if doc.id == "profile":
      info.append(doc.to_dict())
  for element in info:
    print(f"\n[bold purple]About me:[/bold purple] [cyan]{element['bio']}[/cyan]")
    for i in element['favorites']:
      print(f"[bold purple]Favorite {i}:[/bold purple] [cyan]{element['favorites'][i]}[/cyan]")

def get_songs():
  import spotipy
  from spotipy.oauth2 import SpotifyOAuth
  client_id = os.getenv("spotify_client_id")
  client_secret = os.getenv("spotify_secret")
  redirect_uri = "https://open.spotify.com"

  sp = spotipy.Spotify(auth_manager = SpotifyOAuth(client_id = client_id,
                                                client_secret = client_secret, 
                                                redirect_uri = redirect_uri,
                                                scope = "user-library-read user-read-recently-played"))

  recently_played = []
  results = sp.current_user_recently_played()
  recently_played.extend(results['items'])
  while results['next']:
      results = sp.next(results)
      recently_played.extend(results['items'])
      
  last_played = []

  for track in recently_played:
      last_played.append({"name": track['track']['name'], "artist": track['track']['artists'][0]['name']})

  print(last_played)

def exit_main_menu():
  sys.exit(0)

def main_menu():
  bright_purple = colors.background["magenta"]
  bright_cyan = colors.bright(colors.foreground["cyan"])
  menu = Bullet("Welcome to TetraCLI! What would you like to do today?",
             choices = ["Add a project", "Browse projects", "Look at Tetraslam's profile", "See my recently played tracks", "Exit TetraCLI"],
             word_color = bright_cyan,
             word_on_switch = bright_cyan,
             background_on_switch = bright_purple)
  
  choice = menu.launch()
  
  if choice == "Add a project":
    add_project_to_firebase()
    main_menu()
  elif choice == "Browse projects":
    read_projects_from_firebase()
    main_menu()
  elif choice == "Look at Tetraslam's profile":
    read_profile()
    main_menu()
  elif choice == "See my recently played tracks":
    get_songs()
    main_menu()
  elif choice == "Exit TetraCLI":
    exit_main_menu()
    
  
if __name__ == "__main__":
  main_menu()

# print(project_name.result[1][1]) THIS GIVES THE RESULT