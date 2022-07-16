from flask import Flask, render_template, request
import requests
from flask_fontawesome import FontAwesome
import folium
import csv
from folium.plugins import HeatMap
import datetime
from flask import Response
import statistics
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io

#create venv for flask
#https://stackoverflow.com/questions/31252791/flask-importerror-no-module-named-flask

#running prgram after installation

#cd flask
#source bin/activate
#FLASK_APP=hello.py flask run

# open traffic collisions dataset

def loadList(fileName):
    with open(fileName,newline='') as csv_file:
        reader = csv.reader(csv_file)
        dataList = list(reader)
    return dataList

automobile = loadList('/Users/andrew.hua/Desktop/Y10 Coding/Automobile.csv')
tvolume = loadList("/Users/andrew.hua/Desktop/Y10 Coding/traffic-volumes-data.csv")

# initiating flask, creating webpages

plt.rcParams["figure.autolayout"] = True

app = Flask(__name__)
fa = FontAwesome(app)

@app.route("/directions", methods = ["POST", "GET"])
def get_directions():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST':
        global starting
        global ending
        starting = request.form.get('startpoint')
        ending = request.form.get("endpoint")
        print(starting)
        print(ending)
        # working with directions api

        start = starting
        end = ending
        rawstart = start
        rawend = end
        start = start.replace(" ", "+")
        end = end.replace(" ", "+")
        #print(start)
        #print(end)
        directionslist = []
        endpoints = []
        waypoints = []
        requesturl = "https://maps.googleapis.com/maps/api/directions/json?origin=" + start + "&destination=" + end + "&key=AIzaSyAbskEvIMBcbppePATVCTLwVf31gxXXq9w"
        #print(requesturl)
        apirequest = requests.get(requesturl).json()


        # get info on distance, duration, and directions
        distance = apirequest['routes'][0]['legs'][0]["distance"]["text"]
        duration = apirequest['routes'][0]['legs'][0]["duration"]["text"]

        myList = []
        myList.append(apirequest['routes'][0]['legs'][0]["start_location"]["lat"])
        myList.append(apirequest['routes'][0]['legs'][0]["start_location"]["lng"])
        waypoints.append(myList)

        for i in range(0,len(apirequest['routes'][0]['legs'][0]['steps'])):
            myList=[]
            step = apirequest['routes'][0]['legs'][0]['steps'][i]['html_instructions']

            endpoints.append(apirequest['routes'][0]['legs'][0]['steps'][i]['end_location'])
            myList.append(apirequest['routes'][0]['legs'][0]['steps'][i]['end_location']["lat"])
            myList.append(apirequest['routes'][0]['legs'][0]['steps'][i]['end_location']["lng"])
            waypoints.append(myList)

            nonocharlist = ["<b>", "</b>", """<div style="font-size:0.9em">""", "</div>", "<wbr/>"]
            for element in nonocharlist:
                if element == """<div style="font-size:0.9em">""":
                    step = step.replace(element," ")
                else:
                    step = step.replace(element, "")
            directionslist.append(step)

        #print(directionslist)

        #print(waypoints)

        # working with traffic volume api 

        # traffic volume
        # traffic volume
        # traffic volume
        # traffic volume
        # traffic volume
        # traffic volume
        # traffic volume
        # traffic volume
        # traffic volume


        color = []

        for j in range(len(directionslist)):
            trafficurl = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?key=1SjA5xJYjygfrzY76gBLnYwAKkNy8cHW&point=" + str(endpoints[j]['lat']) + "," + str(endpoints[j]['lng'])
            #print(trafficurl)
            trafficapi = requests.get(trafficurl).json()
            #print(trafficapi['flowSegmentData']['currentTravelTime']/trafficapi['flowSegmentData']['freeFlowTravelTime'])
            if trafficapi['flowSegmentData']['currentTravelTime']/trafficapi['flowSegmentData']['freeFlowTravelTime'] < 0.6:
                color.append("red")
            elif trafficapi['flowSegmentData']['currentTravelTime']/trafficapi['flowSegmentData']['freeFlowTravelTime'] < 0.9:
                color.append("yellow")
            else:
                color.append("white")

        #color = ['white', 'red', 'yellow', 'white', 'white']
        #for testing purposes
        print(color)

    return render_template('directionswebsite.html', content=directionslist, volume=color, distancetravelled = distance, timetaken = duration, begin = rawstart, destination = rawend)

@app.route("/")
def form():
    return render_template('form.html')


@app.route("/heatmap")
def fetch_heatmap():
    basemap = folium.Map(location=[43.6532, -79.3832], control_scale = False, zoom_start=13)
    heat = HeatMap(data=coords,radius=14)
    heat.add_to(basemap)
    return basemap._repr_html_()


@app.route("/averagetraffic")
def fetch_averagebargraph():
    graph = Figure()

    axis = graph.add_subplot(1, 1, 1)

    axis.bar(days, averages)
    # below is taken from tutorialspoint 
    # compatability with flask
    output = io.BytesIO()
    FigureCanvas(graph).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

@app.route("/mediantraffic")
def fetch_medianbargraph():
    graph = Figure()

    axis = graph.add_subplot(1, 1, 1)

    axis.bar(days, medians)
    # below is taken from tutorialspoint 
    # compatability with flask
    output = io.BytesIO()
    FigureCanvas(graph).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')



# create readable data points for heatmap
coords = []
for i in range(1,len(automobile)):
    a=[]
    if automobile[i][4] == '2019' or automobile[i][4] == '2018' or automobile[i][4] == '2017':
        a.append(automobile[i][15]) # lat
        a.append(automobile[i][16]) # long
        coords.append(a)

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
totals = [0,0,0,0,0,0,0]
count = [0,0,0,0,0,0,0]
averages = [0,0,0,0,0,0,0]
mediantotal = [[],[],[],[],[],[],[]]
medians = []

for i in range(1,len(tvolume)):
    countdate = tvolume[i][8]
    month = int(countdate[:2])
    day = int(countdate[3:5])
    year = int(countdate[6:])
    countdate = datetime.date(year, month, day)
    dayofweek = countdate.strftime("%a")
    for element in days: # iterate through each day of the week
        if dayofweek == element: # find a matching day of week
            totals[days.index(element)] = totals[days.index(element)] + int(tvolume[i][9]) # add corresponding traffic volume count
            count[days.index(element)] += 1
            mediantotal[days.index(element)].append(int(tvolume[i][9]))

for i in range(len(averages)):
    averages[i] = totals[i]/count[i]


for item in mediantotal:
    myMedian = statistics.median(item)
    medians.append(myMedian)