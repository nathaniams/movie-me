import datetime
import os
import gspread
import pandas as pd
import requests
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials

st.title("🎬 Movie Me")
st.write("Welcome to our personal movie matchmaker!")

TMDB_API_KEY = st.secrets["TMDB_API_KEY"]


# 1. Connect to Google Sheets using Streamlit Secrets (or local credentials.json)
def init_connection():
  scope = [
      "https://spreadsheets.google.com/feeds",
      "https://www.googleapis.com/auth/drive",
  ]

  # If running on Streamlit Cloud, pull from secrets; otherwise use local credentials.json
  if "gcp_service_account" in st.secrets:
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
  else:
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scope
    )

  client = gspread.authorize(creds)
  return client


client = init_connection()

# Open your Google Sheet by its exact title
sheet = client.open("MovieRatings").sheet1


# 2. Function to fetch movie poster from TMDb API
def get_movie_poster(title, year):
  # Clean up title for URL
  clean_title = title.split(":")[0].strip()  # Removes subtitles if they cause search issues
  
  # Try searching with title and year
  url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={requests.utils.quote(clean_title)}&year={year}"
  try:
    response = requests.get(url)
    data = response.json()
    if data.get("results"):
      poster_path = data["results"][0].get("poster_path")
      if poster_path:
        return f"https://image.tmdb.org/t/p/w500{poster_path}"
        
    # Fallback without year
    url_fallback = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={requests.utils.quote(clean_title)}"
    response_fb = requests.get(url_fallback)
    data_fb = response_fb.json()
    if data_fb.get("results"):
      poster_path = data_fb["results"][0].get("poster_path")
      if poster_path:
        return f"https://image.tmdb.org/t/p/w500{poster_path}"
        
  except Exception as e:
    st.write(f"Error fetching poster: {e}")
    
  return None

# 3. Function to save rating row to Google Sheet
def save_ratings_to_csv(
    movie_title, movie_year, my_rating, spouse_rating
):  # Keeping original name so buttons work seamlessly!
  timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  # Append the row straight into your Google Sheet!
  sheet.append_row(
      [movie_title, str(movie_year), str(my_rating), str(spouse_rating), timestamp]
  )


# Combined Master Queue: Fresh Recent Hits + Main Library
MOVIE_QUEUE = [
    # 🌟 FRESH IN OUR HEADS (Top Recent Hits 2023–2026)
    ("Deadpool & Wolverine", 2024),
    ("Dune: Part Two", 2024),
    ("Oppenheimer", 2023),
    ("Barbie", 2023),
    ("Spider-Man: Across the Spider-Verse", 2023),
    ("Inside Out 2", 2024),
    ("Twisters", 2024),
    ("Civil War", 2024),
    ("Furiosa: A Mad Max Saga", 2024),
    ("Kingdom of the Planet of the Apes", 2024),
    # 🎥 MAIN MOVIE LIBRARY
    ("Clayface", 2025),
    ("Man on Fire", 2004),
    ("Joker: Folie à Deux", 2024),
    ("Meg 2: The Trench", 2023),
    ("Inception", 2010),
    ("Interstellar", 2014),
    ("The Dark Knight", 2008),
    ("Top Gun: Maverick", 2022),
    ("Avatar: The Way of Water", 2022),
    ("The Matrix", 1999),
    ("Gladiator", 2000),
    ("The Lord of the Rings: The Fellowship of the Ring", 2001),
    ("The Lord of the Rings: The Two Towers", 2002),
    ("The Lord of the Rings: The Return of the King", 2003),
    ("Jurassic Park", 1993),
    ("Star Wars: Episode IV - A New Hope", 1977),
    ("The Empire Strikes Back", 1980),
    ("The Avengers", 2012),
    ("Guardians of the Galaxy", 2014),
    ("Blade Runner 2049", 2017),
    ("Arrival", 2016),
    ("Mad Max: Fury Road", 2015),
    ("The Batman", 2022),
    ("Logan", 2017),
    ("Bad Boys: Ride or Die", 2024),
    ("Dune", 2021),
    ("Free Guy", 2021),
    ("Shang-Chi and the Legend of the Ten Rings", 2021),
    ("No Time to Die", 2021),
    ("Tenet", 2020),
    ("1917", 2019),
    ("Ford v Ferrari", 2019),
    ("Avengers: Endgame", 2019),
    ("Ready Player One", 2018),
    ("Mission: Impossible - Fallout", 2018),
    ("Black Panther", 2018),
    ("Baby Driver", 2017),
    ("Wonder Woman", 2017),
    ("Thor: Ragnarok", 2017),
    ("Deadpool", 2016),
    ("The Martian", 2015),
    ("Star Wars: The Force Awakens", 2015),
    ("Ex Machina", 2014),
    ("Gravity", 2013),
    ("Parasite", 2019),
    ("Pulp Fiction", 1994),
    ("Fight Club", 1999),
    ("Forrest Gump", 1994),
    ("The Godfather", 1972),
    ("The Godfather Part II", 1974),
    ("The Silence of the Lambs", 1991),
    ("Se7en", 1995),
    ("Shutter Island", 2010),
    ("The Departed", 2006),
    ("Whiplash", 2014),
    ("Memento", 2000),
    ("The Prestige", 2006),
    ("Once Upon a Time in Hollywood", 2019),
    ("Joker", 2019),
    ("Us", 2019),
    ("A Star Is Born", 2018),
    ("Django Unchained", 2012),
    ("The Dark Knight Rises", 2012),
    ("Skyfall", 2012),
    ("Argo", 2012),
    ("The Social Network", 2010),
    ("Inglourious Basterds", 2009),
    ("District 9", 2009),
    ("Slumdog Millionaire", 2008),
    ("No Country for Old Men", 2007),
    ("There Will Be Blood", 2007),
    ("Casino Royale", 2006),
    ("Brokeback Mountain", 2005),
    ("Batman Begins", 2005),
    ("Eternal Sunshine of the Spotless Mind", 2004),
    ("Lost in Translation", 2003),
    ("A Beautiful Mind", 2001),
    ("Crouching Tiger, Hidden Dragon", 2000),
    ("The Sixth Sense", 1999),
    ("Saving Private Ryan", 1998),
    ("Good Will Hunting", 1997),
    ("Titanic", 1997),
    ("Fargo", 1996),
    ("The Usual Suspects", 1995),
    ("The Shawshank Redemption", 1994),
    ("Schindler's List", 1993),
    ("Goodfellas", 1990),
    ("Alien", 1979),
    ("2001: A Space Odyssey", 1968),
    ("Catch Me If You Can", 2002),
    ("Everything Everywhere All at Once", 2022),
    ("Knives Out", 2019),
    ("Glass Onion", 2022),
    ("Superbad", 2007),
    ("Step Brothers", 2008),
    ("Anchorman", 2004),
    ("Tropic Thunder", 2008),
    ("The Wolf of Wall Street", 2013),
    ("The Truman Show", 1998),
    ("Amélie", 2001),
    ("Spirited Away", 2001),
    ("Princess Mononoke", 1997),
    ("WALL-E", 2008),
    ("Up", 2009),
    ("Coco", 2017),
    ("Moana 2", 2024),
    ("Kung Fu Panda 4", 2024),
    ("Ghostbusters: Frozen Empire", 2024),
    ("Bohemian Rhapsody", 2018),
    ("Zootopia", 2016),
    ("Moana", 2016),
    ("Inside Out", 2015),
    ("Frozen", 2013),
    ("Her", 2013),
    ("Toy Story 3", 2010),
    ("Avatar", 2009),
    ("Ratatouille", 2007),
    ("The Incredibles", 2004),
    ("Finding Nemo", 2003),
    ("Spider-Man", 2002),
    ("Toy Story 2", 1999),
    ("Toy Story", 1995),
    ("The Lion King", 1994),
    ("Groundhog Day", 1993),
    ("Aladdin", 1992),
    ("Back to the Future", 1985),
    ("Star Wars", 1977),
    ("Get Out", 2017),
    ("A Quiet Place", 2018),
    ("Hereditary", 2018),
    ("Pan's Labyrinth", 2006),
    ("The Grand Budapest Hotel", 2014),
    ("The Aviator", 2004),
    ("The Bourne Identity", 2002),
    ("Minority Report", 2002),
    ("Ocean's Eleven", 2001),
    ("The Green Mile", 1999),
    ("The Matrix Reloaded", 2003),
    ("The Matrix Revolutions", 2003),
    ("Pirates of the Caribbean: The Curse of the Black Pearl", 2003),
    ("King Kong", 2005),
    ("V for Vendetta", 2005),
    ("300", 2006),
    ("The Bourne Ultimatum", 2007),
    ("Wall Street", 1987),
    ("Die Hard", 1988),
    ("Predator", 1987),
    ("Terminator", 1984),
    ("Blade Runner", 1982),
    ("The Shining", 1980),
    ("Apocalypse Now", 1979),
    ("Taxi Driver", 1976),
    ("Jaws", 1975),
    ("The Sting", 1973),
    ("A Clockwork Orange", 1971),
    ("The Graduate", 1967),
    ("The Good, the Bad and the Ugly", 1966),
    ("Dr. Strangelove", 1964),
    ("North by Northwest", 1959),
    ("Vertigo", 1958),
    ("Sunset Boulevard", 1950),
    ("All About Eve", 1950),
    ("Casablanca", 1942),
    ("Citizen Kane", 1941),
    ("Gone with the Wind", 1939),
]

# Initialize tracking index and temporary storage in session state
if "movie_index" not in st.session_state:
  st.session_state.movie_index = 0
if "my_rating" not in st.session_state:
  st.session_state.my_rating = None
if "spouse_rating" not in st.session_state:
  st.session_state.spouse_rating = None

# Check if we've reached the end of the list
if st.session_state.movie_index >= len(MOVIE_QUEUE):
  st.balloons()
  st.success("🎉 You've rated through the entire master movie queue! Amazing job.")

  if st.button("Restart Queue"):
    st.session_state.movie_index = 0
    st.rerun()
else:
  current_title, current_year = MOVIE_QUEUE[st.session_state.movie_index]

  st.subheader(
      f"Movie {st.session_state.movie_index + 1} of {len(MOVIE_QUEUE)}"
  )
  st.markdown(f"### 🎥 {current_title} ({current_year})")

  # Display Poster
  poster_url = get_movie_poster(current_title, current_year)
  if poster_url:
    st.image(poster_url, width=300)
  else:
    st.warning("Poster could not be loaded.")

  # --- PERSON 1: YOUR RATING ---
  st.markdown("#### 👤 Your Rating:")
  col1, col2, col3, col4, col5 = st.columns(5)
  with col1:
    if st.button("1-Nope!", key="my_1"):
      st.session_state.my_rating = 1
  with col2:
    if st.button("2-Meh", key="my_2"):
      st.session_state.my_rating = 2
  with col3:
    if st.button("3-Okay", key="my_3"):
      st.session_state.my_rating = 3
  with col4:
    if st.button("4-PrettyGood", key="my_4"):
      st.session_state.my_rating = 4
  with col5:
    if st.button("5-Loved it", key="my_5"):
      st.session_state.my_rating = 5

  if st.session_state.my_rating:
    st.info(f"Your selected score: {st.session_state.my_rating}/5")

  st.write("---")

  # --- PERSON 2: SPOUSE'S RATING ---
  st.markdown("#### 👤 Spouse's Rating:")
  scol1, scol2, scol3, scol4, scol5 = st.columns(5)
  with scol1:
    if st.button("1-Nope!", key="sp_1"):
      st.session_state.spouse_rating = 1
  with scol2:
    if st.button("2-Meh", key="sp_2"):
      st.session_state.spouse_rating = 2
  with scol3:
    if st.button("3-Okay", key="sp_3"):
      st.session_state.spouse_rating = 3
  with scol4:
    if st.button("4-PrettyGood", key="sp_4"):
      st.session_state.spouse_rating = 4
  with scol5:
    if st.button("5-Aligned/Loved", key="sp_5"):
      st.session_state.spouse_rating = 5

  if st.session_state.spouse_rating:
    st.info(f"Spouse's selected score: {st.session_state.spouse_rating}/5")

  st.write("---")

  # Action Buttons: Skip or Save Both
  col_skip, col_save = st.columns(2)

  with col_skip:
    if st.button("⏭️ Didn't watch / Skip Movie"):
      st.session_state.my_rating = None
      st.session_state.spouse_rating = None
      st.session_state.movie_index += 1
      st.rerun()

  with col_save:
    if st.button("💾 Save... Next", type="primary"):
      if (
          st.session_state.my_rating is not None
          and st.session_state.spouse_rating is not None
      ):
        save_ratings_to_csv(
            current_title,
            current_year,
            st.session_state.my_rating,
            st.session_state.spouse_rating,
        )
        st.success(
            f"Saved to Google Sheets! You: {st.session_state.my_rating}/5 |"
            f" Spouse: {st.session_state.spouse_rating}/5"
        )

        st.session_state.my_rating = None
        st.session_state.spouse_rating = None
        st.session_state.movie_index += 1
        st.rerun()
      else:
        st.warning(
            "Please make sure both you and your spouse have selected a rating"
            " (or use Skip if you haven't seen it)."
        )