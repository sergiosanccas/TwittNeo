# -*- coding: utf-8 -*-
__author__ = 'Sergio Sanchez Castell '
__version__ = 'v_2.0'
__email__ = "sergio.tendi[at]gmail[dot]com"
__status__ = "Production"

import tweepy
import ConfigParser
import sys
import argparse
import datetime
from time import sleep, strftime, time
from neo4j.v1 import GraphDatabase, basic_auth


class Configuration():
    """Configuration information"""

    # ----------------------------------------------------------------------
    def __init__(self):
        try:
            # Read  configuration file ("user_token.conf")
            config = ConfigParser.RawConfigParser()
            config.read('user_token_test.conf')

            CONSUMER_KEY = config.get('Twitter OAuth', 'CONSUMER_KEY')
            CONSUMER_SECRET = config.get('Twitter OAuth', 'CONSUMER_SECRET')
            ACCESS_TOKEN = config.get('Twitter OAuth', 'ACCESS_TOKEN')
            ACCESS_TOKEN_SECRET = config.get('Twitter OAuth', 'ACCESS_TOKEN_SECRET')

            # User authentication
            auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

            # Tweepy (a Python library for accessing the Twitter API)
            self.api = tweepy.API(auth)

            # Access user and password of neo4j server
            URL = config.get('NEO4J Basic_auth', 'URL')
            USER = config.get('NEO4J Basic_auth', 'USER')
            PASS = config.get('NEO4J Basic_auth', 'PASSWORD')

            # Driver for Neo4j
            self.driver = GraphDatabase.driver(URL, auth=basic_auth(USER, PASS))

        except Exception, e:
            print("Error en el archivo de configuracion:", e)
            sys.exit(1)




##########################################################################################################################################
'''
	Parameters: definimos los parametros que se le puede pasar
'''


class Parameters:
    """Global program parameters"""

    # ----------------------------------------------------------------------
    def __init__(self, **kwargs):
        try:
            config = Configuration()
            self.api = config.api
            self.driver = config.driver
            self.screen_name = kwargs.get("username")
            self.tweets = kwargs.get("tweets")
            self.sdate = kwargs.get("sdate")
            self.edate = kwargs.get("edate")

            self.program_name = "Tweeneo"
            self.program_version = "v2.0"
            self.program_date = "01/10/2016"
            self.program_author_name = "Sergio Sanchez Castell"
            self.program_author_twitter = "@SergioTendi"
            self.program_author_companyname = "Universidad Alcala Henares"

        except Exception, e:
            print("Error en Parameters:", e)
            sys.exit(1)




##########################################################################################################################################
# --------------------------------------------------------------------------
class User:
    """Information about a Twitter user"""
    screen_name = ""
    name = ""
    id = ""
    created_at = ""
    followers_count = ""
    statuses_count = ""
    location = ""
    geo_enabled = ""
    description = ""
    expanded_description = ""
    url = ""
    expanded_url = ""
    tweets_average = ""

    informacion_usuario = []

    # ----------------------------------------------------------------------
    def set_user_information(self, api):
        try:
            self.screen_name = api.screen_name
            self.name = api.name
            self.id = api.id
            self.created_at = api.created_at
            self.followers_count = api.followers_count
            self.friends_count = api.friends_count
            self.statuses_count = api.statuses_count
            self.location = api.location
            self.geo_enabled = api.geo_enabled
            self.time_zone = api.time_zone

            td = datetime.datetime.today() - self.created_at
            self.tweets_average = round(float(self.statuses_count / (td.days * 1.0)), 2)

            self.url = api.url

            if len(api.entities) > 1:
                if api.entities['url']['urls']:
                    self.expanded_url = api.entities['url']['urls'][0]['expanded_url']
                else:
                    self.expanded_url = ""
            else:
                self.expanded_url = ""

            try:
                self.description = api.description
                if api.entities['description']['urls']:
                    tmp_expanded_description = api.description
                    url = api.entities['description']['urls'][0]['url']
                    expanded_url = api.entities['description']['urls'][0]['expanded_url']
                    self.expanded_description = tmp_expanded_description.replace(url, expanded_url)
                else:
                    self.expanded_description = ""
            except:
                self.expanded_description = ""

            self.profile_image_url = str(api.profile_image_url).replace("_normal", "")


        except Exception, e:
            sys.exit(1)

    # ----------------------------------------------------------------------
    def show_user_information(self):
        try:
            string = "USER INFORMATION "

            print ("General Information")
            print ("Screen Name:\t\t\t" + self.screen_name)
            print ("User Name:\t\t\t" + self.name)
            print ("Twitter Unique ID:\t\t" + str(self.id))
            print ("Account created at:\t\t" + self.created_at.strftime('%m/%d/%Y'))
            print ("Followers:\t\t\t" + '{:,}'.format(self.followers_count))
            print ("Friends:\t\t\t" + '{:,}'.format(self.friends_count))
            print ("Tweets:\t\t\t\t" + '{:,}'.format(self.statuses_count))
            try:
                print ("Location:\t\t\t" + str(self.location))
            except:
                print ("Location:")
            print ("Time zone:\t\t\t" + str(self.time_zone))
            print ("Geo enabled:\t\t\t" + str(self.geo_enabled))

            print ("URL:\t\t\t\t" + str(self.url))
            if self.expanded_url:
                print ("Expanded URL:\t\t\t" + str(self.expanded_url))

            print ("Description:\t\t\t" + str(self.description.encode('utf-8')).replace("\n", " "))
            if self.expanded_description:
                print (
                    "Expanded Description:\t\t" + str(self.expanded_description.encode('utf-8')).replace("\n",
                                                                                                         " "))

            print ("Profile image URL:\t\t" + str(self.profile_image_url))

            print ("Tweets average:\t\t\t" + str(self.tweets_average) + " tweets/day")

        except Exception, e:
            sys.exit(1)

        # ----------------------------------------------------------------------

    def insert_user_information(self, driver):
        try:

            sesion = driver.session()

            sql = "MERGE (p1:User {screen_name:{screen_name},user_name:{user_name},id:{id},create_date:{create_date},followers:{followers},friends:{friends},location:{location},time_zone:{time_zone},profile_image:{profile_image}})"


            sesion.run(sql, parameters={"screen_name": str(self.screen_name),
                                        "user_name": str(self.name), "id": str(self.id),
                                        "create_date": self.created_at.strftime('%m/%d/%Y'),
                                        "followers": self.followers_count, "friends": self.friends_count,
                                        "location": self.location, "time_zone": str(self.time_zone),
                                        "profile_image": str(self.profile_image_url)})

            sesion.close()

        except Exception, e:
            print("Error insert user information", e)


##########################################################################################################################################
class follower:
    follow = []

    def get_followers(self, args, parameters):


        for page in tweepy.Cursor(parameters.api.followers, screen_name=args.username).pages():
            for follower in page:
                self.follow.append([follower.name, follower.id])


    # ----------------------------------------------------------------------------------------------------------------------------------------

    def insert_follow(self, driver, args):
        sesion = driver.session()
        for follower in self.follow:
            sql = '''
			MATCH (n:User) WHERE n.screen_name = {username}
			MERGE (p1:Follower {screen_name:{name},id:{id}})
			MERGE (p1)-[:FOLLOW]->(n)
			'''
            sesion.run(sql, parameters={"name": follower[0], "id": follower[1], "username": str(args.username)})

        sesion.close()


##########################################################################################################################################
class friends:
    friends = []

    def get_friends(self, args, parameters):

        try:

            for page in tweepy.Cursor(parameters.api.friends, screen_name=args.username, count=150).pages():
                for friend in page:
                    self.friends.append([friend.name, friend.id])


        except Exception, e:

            print("Error get friends", e)

    # ----------------------------------------------------------------------------------------------------------------------------------------

    def insert_friends(self, driver, args):
        try:
            sesion = driver.session()

            for friend in self.friends:
                sql = '''
				MATCH (n:User) WHERE n.screen_name = {username}
				MERGE (p1:Friend {screen_name:{name},id:{id}})
				MERGE (p1)<-[:FRIEND]-(n)
				'''
                sesion.run(sql, parameters={"name": friend[0], "id": friend[1], "username": str(args.username)})

            sesion.close()
        except Exception, e:
            # show_error(e)
            print("Error insert friends", e)


##########################################################################################################################################

def numer_retweets(tweet, args, driver):
    mentions = []
    hashtags = []
    try:
        '''

        print ("ID:", tweet.id)
        print ("User ID:", tweet.user.id)
        print ("Text:", tweet.text.encode('utf-8'))
        print ("Created:", tweet.created_at)
        print ("Geo:", tweet.geo)
        print ("Contributors:", tweet.contributors)
        print ("Coordinates:", tweet.coordinates)
        print ("Favorited:", tweet.favorited)
        print ("User MEntions:", tweet.entities['user_mentions'])
        for i in tweet.entities['hashtags']:
            hashtags.append(i['text'])
        print ("Hastag", hashtags)
        print ("In reply to screen name:", tweet.in_reply_to_screen_name)
        print ("In reply to status ID:", tweet.in_reply_to_status_id)
        print ("In reply to status ID str:", tweet.in_reply_to_status_id_str)
        print ("In reply to user ID:", tweet.in_reply_to_user_id)
        print ("In reply to user ID str:", tweet.in_reply_to_user_id_str)
        print ("Place:", tweet.place)
        print ("Retweeted:", tweet.retweeted)
        print ("Retweet count:", tweet.retweet_count)
        print ("Source:", tweet.source)
        print ("Truncated:", tweet.truncated)
        print "-------------------"
        '''
        # Vamos  a ver si el tweet tiene menciones
        for i in tweet.entities['user_mentions']:
            mentions.append(i['screen_name'].encode('utf-8'))

        # Insertamos el twwet
        #sesion = driver.session()

        '''
        sql = "MATCH (n:User) WHERE n.screen_name = {username} MERGE (tw:Tweet {id_tweet:{id},id_user:{id_user},create_date:{create_date},text:{text},favourited:{favourited},geolocalizacion:{geo},place:{place},hashtags:{hashtags},respuesta_aScrrenName:{respuestaSName},respuesta_statusID:{respuestaSID},is_retweeted:{retweeted},retweeted_count:{retweeted_count},source:{source}})MERGE (n)-[:TWEET]->(tw)"

        sesion.run(sql, parameters={"username": str(args.username).encode('utf-8'), "id": str(tweet.id), "id_user": str(tweet.user.id),
                                    "create_date": tweet.created_at.strftime('%m/%d/%Y'),
                                    "text": tweet.text.encode('utf-8'), "favourited": str(tweet.favorited),
                                    "geo": str(tweet.geo), "place": str(tweet.place),
                                    "hashtags": hashtags, "respuestaSName": str(tweet.in_reply_to_screen_name),
                                    "respuestaSID": str(tweet.in_reply_to_user_id),
                                    "retweeted": tweet.retweeted, "retweeted_count": tweet.retweet_count,
                                    "source": str(tweet.source).encode('utf-8')})

        sesion.close()
        '''
        parameters ={"username": str(args.username).encode('utf-8'), "id": str(tweet.id), "id_user": str(tweet.user.id),
                                    "create_date": tweet.created_at.strftime('%m/%d/%Y'),
                                    "text": tweet.text.encode('utf-8'), "favourited": str(tweet.favorited),
                                    "geo": str(tweet.geo), "place": str(tweet.place),
                                    "hashtags": hashtags, "respuestaSName": str(tweet.in_reply_to_screen_name),
                                    "respuestaSID": str(tweet.in_reply_to_user_id),
                                    "retweeted": tweet.retweeted, "retweeted_count": tweet.retweet_count,
                                    "source": str(tweet.source).encode('utf-8')}
        print parameters
    # print sql

    except Exception, e:
        # show_error(e)
        print("Error insert tweets", e)


##########################################################################################################################################

"""===================================== get_userdata ===========================================
==   Obtiene todos los datos del usuario que se le a introducido        =========================
==   Se le pasa args y parameters                                    ============================
=================================================================================================
"""

def get_userdata(args, parameters):
    api = parameters.api.get_user(args.username)
    user = User()  # Creamos una clase usuario, con todos los datos del usuriario a buscar
    followers = follower()
    friend = friends()

    # Buscamos toda la información del usuario y la insertamos en la base de datos como un nodo con todos los atributos
    user.set_user_information(api)
    user.show_user_information()
    #user.insert_user_information(parameters.driver)

    # Followers del usuario
    #followers.get_followers(args,parameters)
    #followers.insert_follow(parameters.driver,args)

    # Friends del usuario
    #friend.get_friends(args,parameters)
    #friend.insert_friends(parameters.driver,args)

    page = 1
    contador_tweets = 0

    while True:
        timeline = parameters.api.user_timeline(screen_name=args.username, include_rts=args.tweets, count=args.tweets, page=page)

        if timeline:

            for tweet in timeline:
                contador_tweets += 1
                if tweet_restringido(tweet, args):
                    numer_retweets(tweet, args, parameters.driver)

                sys.stdout.write("\r\t" + str(contador_tweets) + " tweets analyzed")
                sys.stdout.flush()
                if contador_tweets >= int(args.tweets):
                    print
                    break
        else:
            print
            break
        page += 1
        if contador_tweets >= int(args.tweets):
            print
            break

    print


##########################################################################################################################################
####################                                FUNCIONES AUXILIARES                                ##################################
##########################################################################################################################################


"""===================================== tweet_restringido ===========================================
==   Mra si existe restriccion en las fechas                        ==================================
==   Si se ha limitado la fecha, debemos de comprobar el tweet      ==================================
======================================================================================================
"""


def tweet_restringido(tweet, args):
    try:
        valid = 1

        date = str(tweet.created_at.strftime('%Y/%m/%d'))
        if date < args.sdate or date > args.edate:
            valid = 0

        return valid

    except Exception, e:
        print("Error en tweet_restringido ", e)
        sys.exit(1)


##########################################################################################################################################
# ----------------------------------------------------------------------------------------------------------------------------------------
def main():
    """ Main function"""
    try:
        parameters = Parameters()


        # Imprimimos la cabecera con la onformación principal del programa
        print "+++ "
        print "+++ " + parameters.program_name + " " + parameters.program_version + " - \"Get detailed information about a Twitter user\""
        print "+++ " + parameters.program_author_name + "----->" + parameters.program_author_twitter
        print "+++ " + parameters.program_author_companyname
        print "+++ " + parameters.program_date
        print "+++ "
        print

        parser = argparse.ArgumentParser(
                version='Tweeneo 1.0',
                description='Aplicación de twitter que inserta datos en bbdd Neo4J')
        parser.add_argument('-t', '--tweets', dest='tweets', default=200,
                            help='numero de tweets para analizar (default: 200)')
        parser.add_argument('username', default='twitter', help='Twitter user name')
        parser.add_argument('--sdate', dest='sdate', default='1900/01/01',
                            help='filtra los resultados por fecha de inicio (format: yyyy/mm/dd)')
        parser.add_argument('--edate', dest='edate', default='2100/01/01',
                            help='filtra los resultados por fecha final (format: yyyy/mm/dd)')

        args = parser.parse_args()

        if args.sdate:
            parameters.sdate = args.sdate
        else:
            parameters.sdate = "1900/01/01"

        if args.edate:
            parameters.edate = args.edate
        else:
            parameters.edate = "2100/01/01"

        print "Buscando informacion sobre  @" + args.username
        print "\n"

        get_userdata(args, parameters)

    except Exception, e:
        # show_error(e)
        print("Error main", e)
        sys.exit(1)


if __name__ == '__main__':
    main()
