
from __future__ import print_function
import requests
from Adafruit_Thermal import *
from PIL import Image
import datetime
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
start_time=0
while(True):
    now = datetime.datetime.now()
    if start_time!=now.day:
        start_time=now.day
        #set button pin
        buttonPin = 18

        GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(17,GPIO.OUT)
        prevButtonState = GPIO.input(buttonPin)


        #Narrowed movie list
        movFin=[[] for i in range(4)]
        #Release date interval(eg.Movies that'll be released 10 days from now)
        rDate=10

        print("Getting data for upcoming movies. Interval: "+str(rDate)+" days")
        parameters = {"api_key": "[Your_API_KEY]", "language": "en-US","region":"US", "page":1}
        response = requests.get("https://api.themoviedb.org/3/movie/upcoming", params=parameters)
        data = response.json()

        for movies in data["results"]:
             date_time_str2=movies["release_date"]
             date_time_obj2 = datetime.datetime.strptime(date_time_str2, '%Y-%m-%d')
             delta = date_time_obj2 - now
             if delta.days < rDate and delta.days>0 :
                 print(movies["title"])
                 print(movies["release_date"])
                 movFin[0].append(movies["title"].encode('utf-8'))
                 movFin[1].append(movies["release_date"])
                 movFin[2].append(movies["poster_path"])
                 movFin[3].append(movies["overview"])

        mCount = len(movFin[0])
        print("upcoming movie count: "+str(mCount))
        GPIO.output(17,GPIO.LOW)
        print("Waiting for action...")
        while(mCount>=1 and datetime.datetime.now().day==start_time):
            GPIO.output(17,GPIO.HIGH)
            input_state = GPIO.input(buttonPin)
            if input_state == False:
                print("Button pressed")
                #get data
                poster_id = movFin[2][mCount-1]
                movie_title = movFin[0][mCount-1]
                release_date = movFin[1][mCount-1]
                overview = movFin[3][mCount-1]

                print("Getting poster for: "+movie_title)

                #convert release date type
                date_time_str=release_date
                date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d')

                #delta = date_time_obj - now
                #print(delta.days)


                poster = "https://image.tmdb.org/t/p/w500/"+poster_id
                printer = Adafruit_Thermal("/dev/serial0",19200,timeout=5)
                #resize poster for printing
                basewidth = 384
                img = Image.open(requests.get(poster, stream=True).raw)
                wpercent = (basewidth/float(img.size[0]))
                hsize = int((float(img.size[1])*float(wpercent)))
                img = img.resize((basewidth,hsize), Image.ANTIALIAS)

                print("Getting Release-date and overview")
                print("Done!")
                print("Printing")
                printer.printImage(img, True)
                printer.justify('C')
                printer.boldOn()
                #printer.println(movie_title)
                printer.println(date_time_obj.strftime("%d-%m-%Y"))
                printer.boldOff()
                #printer.println(now.strftime("%d-%m-%Y %H:%M"))
                printer.feed(1)
                printer.println(overview)
                printer.feed(3)
                mCount-=1
                print("movies left: "+str(mCount))
                GPIO.cleanup()
