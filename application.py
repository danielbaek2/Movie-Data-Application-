import datetime
import math
import sys
import os
import psycopg2

userId = ""   # for testing purposes set to int
logged_in = False  # for testing purposes set to True


is_admin = False # not sure if we need this but just in case
curs = None
conn = None

userIndex = []
followers = 0
following = 0
collections = 0


def main(cursor, connection):
    global curs, conn, logged_in, userId, followers, following, collections, userIndex
    curs = cursor
    conn = connection
    print("Welcome to the Movies Application")
    while True:
        while not logged_in:
            command = input("Would you like to login or create an account? \n > ")
            if command == "login":
                login()
            elif command == "create":
                create()
            else:
                print("login - login to your account")
                print("create - create an account")
        while logged_in:
            command = input("Enter a command \n > ")
            if command == "logout":
                logged_in = False
                userId = ""
                userIndex = []
                followers = 0
                following = 0
                collections = 0
                print("Logged out")
            elif command == "help":
                help()
            elif command == "exit":
                return
            elif command == "view_collections":
                view_collections()
            elif command == "create_collection":
                create_collection()
            elif command == "name_collection":
                name_collection()
            elif command == "add":
                add_to_collection()
            elif command == "delete":
                remove()
            elif command == "search":
                search()
            elif command == "delete_collection":
                delete_collection()
            elif command == "follow":
                follow()
            elif command == "unfollow":
                unfollow()
            elif command == "watch_movie":
                watch_movie()
            elif command == "watch_collection":
                watch_collection()
            elif command == "rate":
                rate()
            elif command == "profile":
                profile()
            elif command == "recommend":
                recommend()
            else:
                print("Invalid command")
                help()
                
                
def recommend():
    print("recommend")
    # The application must provide a movie recommendation system with the following operations
    # The top 20 most popular movies in the last 90 days (rolling) determined by most watches
    # The top 20 most popular movies among the people I follow of all time determined by most watches
    # The top 5 new releases of the month (specify) 
    userR = input("Would you like to see the top 20 most popular movies in the last 90 days? (y/n) ")
    if userR == 'y':
        curs.execute("SELECT mid, COUNT(mid) FROM watch WHERE watchtime > current_date - interval '90 days' GROUP BY mid ORDER BY COUNT(mid) DESC LIMIT 20")
        movies = curs.fetchall()
        if movies:
            for movie in movies:
                curs.execute("SELECT title FROM movie WHERE mid = %s", (movie[0],))
                title = curs.fetchone()
                print(title[0])
        else:
            print("No movies found")
    userR = input("Would you like to see the top 20 most popular movies among the people you follow of all time? (y/n) ")
    if userR == 'y':
        curs.execute("SELECT mid, COUNT(mid) FROM watch WHERE uid IN (SELECT followeduid FROM follows WHERE followeruid = %s) GROUP BY mid ORDER BY COUNT(mid) DESC LIMIT 20", (userId,))
        movies = curs.fetchall()
        if movies:
            for movie in movies:
                curs.execute("SELECT title FROM movie WHERE mid = %s", (movie[0],))
                title = curs.fetchone()
                print(title[0])
        else:
            print("No movies found")
    userR = input("Would you like to see the top 5 new releases of the month? (y/n) ")
    if userR == 'y':
        month = input("Enter the month (1-12): ")
        year = input("Enter the year: ")
        curs.execute("SELECT mid FROM host WHERE releasedate >= %s AND releasedate < %s", (datetime.date(int(year), int(month), 1), datetime.date(int(year), int(month) + 1, 1)))
        movies = curs.fetchall()
        if movies:
            for movie in movies:
                curs.execute("SELECT title FROM movie WHERE mid = %s", (movie[0],))
                title = curs.fetchone()
                print(title[0])
        else:
            print("No movies found")

  
def help():
    if logged_in == False:
        print("login - login to your account") # implemented, Recorded
        print("create - create an account") # implemented, Recorded
    else: 
        print("logout - logout of your account") # implemented, Recorded
        print("exit - exit the application") # implemented - confirmed working, Recorded
        print("view_collections - view your collections") # implemented, Recorded, working
        print("create_collection - create a collection") # implemented, Recorded
        print("add - Add movie to collection") # implemented, Recorded
        print("delete - deletes movie from collection") # implemented, Recorded
        print("delete_collection - deletes collection and its contents") # implemented, Recorded
        print("name_collection - (collection) (name)") # implemented, Recorded
        print("follow - follow a user") # implemented, Recorded
        print("unfollow - unfollow a user") # implemented, Recorded
        print("rate - Add a rating to a movie") # implemented, Recorded
        print("profile - display user profile") 
        print("reccomend - display movie recommendations")

        print("watch_movie - watch a movie") # Fixed, Working
        print("watch_collection - watch all movies in a collection") # Fixed, working

        print("search - open the search menu")
        
        # Add more commands here

def profile():
    # The number of collections the user has
    # – The number of users followed by this user
    # – The number of users this user is following
    # – Their top 10 movies (by highest rating, most plays, or combination
    
    print("Profile")
    print("Number of collections: ", collections)
    print("Number of followers: ", followers)
    print("Number of people you are following: ", following)
    print("Top 10 movies: ")
    for movie in userIndex:
        print(movie)
        
        
        
def name_collection():
    print("Name collection")
    collection_name = input("Enter the name of the collection you would like to change: ")
    curs.execute("SELECT * FROM collection WHERE cname = %s", (collection_name,))
    collection = curs.fetchone()
    if collection:
        try:
            new_name = input("Enter the new name of the collection: ")
            curs.execute("UPDATE collection SET cname = %s WHERE cname = %s", (new_name, collection_name,))
            conn.commit()
            print("Collection name was changed")
            curs.execute("SELECT * FROM contains WHERE cname = %s", (collection_name,))
            contains_collections = curs.fetchall()
            if contains_collections:
                for contain_collection in contains_collections:
                    curs.execute("UPDATE contains SET cname = %s WHERE cname = %s", (new_name, collection_name,))
                    conn.commit()
        except Exception as e:
            print("An error occurred:", e)
            conn.rollback()
    else:
        print("Collection not found")

def follow():
    print("Follow user")
    useremail = input("Enter the email of the user you want to follow: ")
    curs.execute("SELECT * FROM movie_lover WHERE uemail = %s", (useremail,))
    user = curs.fetchone()
    if user:
        try:
            curs.execute("INSERT INTO follows (followeruid, followeduid) VALUES (%s, %s)", (userId, user[0]))
            conn.commit()
            print("You are now following " + user[2])
        except Exception as e:
            print("An error occurred:", e)
            conn.rollback()
    else:
        print("User not found")
        
        
def rate():
    print("Rate movie")
    movieid = int(input("Enter the movie ID: "))
    rating = round(float(input("Enter the rating: ")))
    curs.execute("SELECT * FROM movie WHERE mid = %s", (movieid,))
    movie = curs.fetchone()
    if movie:
        try:
            curs.execute("INSERT INTO review (uid, mid, score) VALUES (%s, %s, %s)", (userId, movieid, rating))
            conn.commit()
            print("Movie rated")
        except Exception as e:
            print("An error occurred:", e)
            conn.rollback()
    else:
        print("Movie not found")

def unfollow():
    print("Unfollow user")
    useremail = input("Enter the email of the user you want to unfollow: ")
    curs.execute("SELECT * FROM movie_lover WHERE uemail = %s", (useremail,))
    user = curs.fetchone()
    if user:
        try:
            curs.execute("DELETE FROM follows WHERE followeruid = %s and followeduid = %s", (userId, user[0]))
            conn.commit()
            print("You are no longer following " + user[2])
        except Exception as e:
            print("An error occurred:", e)
            conn.rollback()
    else:
        print("User not found")

def view_collections():
    print("View collections")
    try:
        curs.execute("SELECT * FROM collection WHERE uid = %s ORDER BY cname", (userId,))
        collections = curs.fetchall()
        if collections:
            for collection in collections:
                collection_name = collection[0]
                curs.execute("SELECT COUNT(m.mid), SUM(m.runtime) as total_runtime FROM contains c JOIN movie m ON c.movieid = m.mid WHERE c.uid = %s AND c.cname = %s GROUP BY c.uid, c.cname;", (userId, collection_name))
                count_and_runtime = curs.fetchone()
                if count_and_runtime and count_and_runtime[0] is not None and count_and_runtime[1] is not None:
                    hours, minutes = divmod(count_and_runtime[1], 60)
                    print(f"Collection: {collection_name}, Total Runtime: {hours} hours {minutes} minutes, Number of Movies: {count_and_runtime[0]}\n")
                else:
                    print(f"Collection: {collection_name} has no movies or runtime is not available.\n")
        else: 
            print("You have no collections")
    except Exception as e:
        print(f"An error occurred: {e}")


def create_collection():
    name = input("Enter the name of the collection: ")
    curs.execute("SELECT * FROM collection WHERE uid = %s", (userId,))
    collections = curs.fetchall()
    if name in collections:
        print("You already have a collection with that name")
    else:
        try:
            curs.execute("INSERT INTO collection (cname, uid) VALUES (%s, %s)", (name, userId))
            conn.commit()
            print("Collection created")
        except Exception as e:
            print("An error occurred:", e)
            conn.rollback()
        
def delete_collection():
    collectionName = input("Enter the name of the collection: ")
    curs.execute("SELECT * FROM collection WHERE uid = %s and cname = %s", (userId, collectionName))
    collections = curs.fetchall()
    if not collections:
        print("Collection not found")
    else:
        try:
            curs.execute("DELETE FROM collection WHERE uid = %s and cname = %s", (userId, collectionName))
            curs.execute("DELETE FROM contains WHERE cname = %s", (collectionName,))
            conn.commit()
            print("Collection deleted")
        except Exception as e:
            print("An error occurred:", e)
            conn.rollback()
    
def add_to_collection():
    print("Add to collection")
    movieid = input("Enter the movie ID: ")
    collectionName = input("Enter the collection name: ")
    curs.execute("SELECT * FROM movie WHERE mid = %s", (movieid,))
    movie = curs.fetchone()
    if movie:
        print("Movie found")
        curs.execute("SELECT * FROM collection WHERE uid = %s and cname = %s", (userId, collectionName))
        collections = curs.fetchone()
        if collections:
            try:
                curs.execute("INSERT INTO contains (movieid, cname, uid) VALUES (%s, %s, %s)", (movieid, collectionName, userId))
                conn.commit()
                print("Movie added to collection")
            except Exception as e:
                print("An error occurred:", e)
                conn.rollback()
        else: 
            print("Collection not found")
    else:
        print("Movie not found")
        
def remove():
    print("Remove from collection")
    collectionName = input("Enter the collection name: ")
    curs.execute("SELECT * FROM collection WHERE uid = %s and cname = %s", (userId, collectionName))
    collections = curs.fetchone()
    if not collections:
        print("Collection not found")
        exit()
    else: 
        print("Collection found")
    movieid = input("Enter the movie ID: ")
    curs.execute("SELECT * FROM movie WHERE mid = %s", (movieid,))
    movie = curs.fetchone()
    if movie:
        print("Movie found")
    else:
        print("Movie not found")
        exit()
    if movie and collections:
        try:
            curs.execute("DELETE FROM contains WHERE movieid = %s and cname = %s and uid = %s", (movieid, collectionName, userId))
            conn.commit()
            print("Movie removed from collection")
        except Exception as e:
            print("An error occurred:", e)
            conn.rollback()

def watch_movie():
    movieid = input("Enter a movie id: ")
    curs.execute("SELECT * FROM movie WHERE mid = %s", (movieid,))
    movie = curs.fetchone()
    if movie:
        print("Movie found ", movie)
    else:
        print("Movie not found")
        exit()
    try:
        watchdate = datetime.datetime.now()
        curs.execute("INSERT INTO watch (uid, mid, watchtime) VALUES (%s, %s, %s)", (userId, movieid, watchdate))
        conn.commit()
        print("Movie watched!")
    except Exception as e:
        print("An error occurred:", e)
        conn.rollback()

def watch_collection():
    cname = input("Enter a collection name: ")
    curs.execute("SELECT movieid FROM contains WHERE uid = %s AND cname = %s", (userId,cname,))
    movies = curs.fetchall()
    watchdate = datetime.datetime.now()
    
    for movie in movies:
        try:
            curs.execute("INSERT INTO watch (mid, watchtime, uid) VALUES (%s, %s, %s)", (movie[0], watchdate, userId,))
            conn.commit()
            print("Movie watched!")
        except Exception as e:
            print("An error occurred:", e)
            conn.rollback()




def search():
    print("d - search by director")
    print("c - search by cast")
    print("s - search by studio")
    print("t - search by title")
    print("r - search by release date")
    print("g - search by genre")
    searchtype = input("> ")

    movies = []
    if searchtype == "d":
        director = input("Enter the director: ")
        curs.execute("SELECT * FROM movie WHERE mid IN (SELECT mid FROM directs WHERE conid IN (SELECT conid FROM contributor WHERE contributor.contributorname LIKE %s))", (director,))
        movies = curs.fetchall()
    elif searchtype == "c":
        cast = input("Enter the cast member: ")
        curs.execute("SELECT * FROM movie WHERE mid IN (SELECT mid FROM produce WHERE conid IN (SELECT conid FROM contributor WHERE contributor.contributorname LIKE %s))", (cast,))
        movies = curs.fetchall()
    elif searchtype == "s":
        studio = input("Enter the studio: ")
        curs.execute("SELECT * FROM movie WHERE mid IN (SELECT mid from publish where sid IN (select sid from studio where studioname like %s))", (studio,))
        movies = curs.fetchall()
    elif searchtype == "t":
        title = input("Enter the title: ")
        curs.execute("SELECT * FROM movie WHERE title = %s", (title,))
        movies = curs.fetchall()
    elif searchtype == "r":
        date_entry = input('Enter a release date in YYYY-MM-DD format:')
        year, month, day = map(int, date_entry.split('-'))
        date1 = datetime.date(year, month, day)
        curs.execute("SELECT * FROM movie WHERE mid IN (SELECT mid FROM host where pid = 42 and releasedate = %s)", (date1,))
        movies = curs.fetchall()
    elif searchtype == "g":
        genre = input('Enter a genre:')
        curs.execute("SELECT * FROM movie WHERE mid IN (SELECT mid FROM moviegenre where gid IN  (SELECT gid from genre where genrename = %s))", (genre,))
        movies = curs.fetchall()
    else:
        print("Invalid search type")
        search()
    

 




    if movies:
        moviesandrelease = []
        print("(movieid, rating, runtime, title, user rating, cast, director)")
        for movie in movies:
            # Fetch the director
            curs.execute("SELECT contributorname FROM contributor WHERE conid IN (SELECT conid FROM directs WHERE mid = %s)", (movie[0],))
            director = curs.fetchone()
            director_name = director[0] if director else "Unknown"

            # Fetch the cast
            curs.execute("SELECT contributorname FROM contributor WHERE conid IN (SELECT conid FROM produce WHERE mid = %s)", (movie[0],))
            cast = curs.fetchall()
            cast_list = ", ".join([member[0] for member in cast]) if cast else "Unknown"

            moviesandrelease.append((movie[0], movie[1], movie[2], movie[3], movie[4], cast_list, director_name))

        moviesandrelease.sort()
        moviesandrelease = sorted(moviesandrelease, key = lambda x: x[0]) # sort by movieid

        for movie in moviesandrelease:
            print('Movie ID: ' + str(movie[0]) + ', Rating: ' + str(movie[1]) + ', Runtime: ' + str(movie[2]) + ', Title: ' + movie[3] + ', User Rating: ' + str(movie[4]) + ', Cast: ' + movie[5] + ', Director: ' + movie[6])


 


        print("would you like to sort your query? (it is already sorted by movie name)")
        print("n - no")
        print("s - studio")
        print("g - genre")
        print("d - date")
        sortType = input("> ")

        moviesandrelease_sorted = []
        if sortType == "d":
            print("(release date, rating, runtime, title, movie id)")
            moviesandrelease_sorted = sorted(moviesandrelease, key = lambda x: x[4])
            for movie in moviesandrelease_sorted:
                curs.execute("SELECT releasedate FROM host WHERE mid = %s", (movie[0],))
                releasedate = curs.fetchone()
                print(str(releasedate[0]) + ', ' + str(movie[1])+ ', ' + str(movie[2])+ ', ' + str(movie[3]) + ', ' + str(movie[0]))

        elif sortType == "s":
            print("(studio, movieid, rating, runtime, title, release date)")
            
            for movie in moviesandrelease:
                curs.execute("SELECT studioname FROM studio WHERE sid IN (SELECT sid FROM publish where mid = %s)", (movie[0],))
                
                studioname = curs.fetchone()
                if studioname:
                    moviesandrelease_sorted.append((studioname[0], movie[0], movie[1], movie[2], movie[3], movie[4]))
            
            moviesandrelease_sorted = sorted(moviesandrelease_sorted, key=lambda x: x[0])
            for movie in moviesandrelease_sorted:
                print(str(movie[0]) + ', ' + str(movie[1])+ ', ' + str(movie[2])+ ', ' + str(movie[3]) + ', ', str(movie[4])+ ', ', str(movie[4]))

        elif sortType == "g":
            print("(genre, movieid, rating, runtime, title, release date")
            
            for movie in moviesandrelease:
                curs.execute("SELECT genrename FROM genre WHERE gid IN (SELECT gid FROM moviegenre where mid = %s)", (movie[0],))
                genre = curs.fetchone()[0]
                moviesandrelease_sorted.append((genre, movie[0], movie[1], movie[2], movie[3], movie[4]))
            
            moviesandrelease_sorted = sorted(moviesandrelease_sorted, key=lambda x: x[0])
            for movie in moviesandrelease_sorted:
                print(str(movie[0]) + ', ' + str(movie[1])+ ', ' + str(movie[2])+ ', ' + str(movie[3]) + ', ', str(movie[4])+ ', ', str(movie[4]))




        



        

        

    else:
        print("No movies found")



def create():
    print("\nCreate account")
    curs.execute("select max(uid) from movie_lover")
    uid = curs.fetchone()[0] + 1
    email = input("Email: ").lower()
    username = input("Username: ")
    password = input("Password: ")
    firstname = input("First Name: ")
    lastname = input("Last Name: ")
    creationdate = datetime.datetime.now()
    try:
        curs.execute("INSERT INTO movie_lover (uid, uemail, username, password, firstname, lastname, creationdate) VALUES (%s, %s, %s, %s, %s, %s, %s)", (uid, email, username, password, firstname, lastname, creationdate))
        conn.commit()
        print("Account created \n\n")
        login()
    except Exception as e:
        print("An error occurred:", e)
        conn.rollback()

def login():
    global logged_in, is_admin, userId, followers, following, userIndex, collections
    print("Login")
    email = input('email: ').lower()
    password = input('password: ')

    if email == 'admin' and password == 'password':
        print('admin')
        is_admin = True
        # do the admin things here

    curs.execute("SELECT * FROM movie_lover WHERE uemail = %s AND password = %s", (email, password))

    user = curs.fetchone()
    
    if user:
        logged_in = True
        userId = str(user[0])
        print("User ID: " + userId)
        print("Welcome " + user[2]) # username
        
        # update access date
        curs.execute("UPDATE movie_lover SET lastaccess = %s WHERE uid = %s", (datetime.datetime.now(), userId))
        conn.commit() 
        curs.execute("SELECT count(*) from follows where followeduid = %s", (userId, )) # I don't quite understand why, but that comma is necessary
        info = curs.fetchone()
        followers =  str(info[0]) if info else "0"
        
        curs.execute("SELECT count(*) from follows where followeruid = %s", (userId, )) # the comma makes it a tuple?
        info = curs.fetchone()
        following = str(info[0]) if info else "0"
        
        curs.execute("SELECT COUNT(cname) FROM collection WHERE uid = %s", (userId,))
        collections = curs.fetchone()
        collections = collections[0] if collections else 0
        
        print("You have " + followers + " followers")
        print("You are following " + following + " people")
        
        
        
        curs.execute("SELECT * FROM review WHERE uid = %s ORDER BY score DESC LIMIT 10", (userId,))
        top_movies = curs.fetchall()
        
        if top_movies:
            for movie in top_movies:
                curs.execute("SELECT title FROM movie WHERE mid = %s", (movie[1],))
                title = curs.fetchone()
                userIndex = userIndex + [title[0] + " - " + str(movie[2])]
    else:
        print("Invalid email or password\n\n")




if __name__ == "__main__":
    print("run from db_connection.py")
    
        
#except:
    #print("Connection failed")





