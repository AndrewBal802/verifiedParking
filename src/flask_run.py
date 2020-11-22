from flask import Flask, flash, redirect, render_template, request, url_for, g, Response, session
import readParkingLots
import connectToDB
import API
import gmaps
app = Flask(__name__)
app.secret_key = "super secret key"


global parkingOwnerAuthentication
parkingOwnerAuthentication = [False]

@app.route("/", methods = ['GET', 'POST'])
def home():
    title = "Welcome to verifiedParking"
    return render_template("index.html", title=title ) 



@app.route("/login_parkinglotowner", methods = ['GET', 'POST'])
def login_parkinglotowner():
    if request.method == 'POST':
        if "login" in request.form:
            isValid = connectToDB.findOwner('ParkingLotOwners', request.form['username'], request.form['password'])
            if (isValid == True):
                print("VALID")
                parkingOwnerAuthentication[0] = True
                session['ownerUsername'] = request.form['username']
                return redirect(url_for('parkinglotowner'))
            else:
                print("NOT VALID")
                #parkingOwnerAuthentication = False
                return render_template("login_parkinglotowner.html", error = "INVALID CREDENTIALS" ) 

        elif "register" in request.form:
            return redirect(url_for('registerOwner.html'))

    return render_template("login_parkinglotowner.html" )


@app.route("/parkinglotowner", methods = [ 'GET', 'POST'])
def parkinglotowner():
    if parkingOwnerAuthentication[0] == True:
        ownerUsername = session.get('ownerUsername', None) 

        if request.method == 'POST':
            if "enters" in request.form:
                connectToDB.modifyOwnerCurrentCapacity('ParkingLotOwners', ownerUsername, 1)
            elif "exits" in request.form:
                connectToDB.modifyOwnerCurrentCapacity('ParkingLotOwners', ownerUsername, -1)
        return render_template("parkinglotowner.html", ownerUsername = ownerUsername)
    else:
        return redirect(url_for('login_parkinglotowner')) 

@app.route("/register_owner", methods = ['GET', 'POST'])
def register_owner():
    return render_template("registerOwner.html")

@app.route("/user", methods = ['GET', 'POST'])
def user():
    if request.method == 'POST':
        if "locationButton" in request.form:
            user_input = request.form['location']
            user_location = API.LocationConvertion(user_input)
            database = readParkingLots.readParkingLots("parking-in-city-of-las-vegas-1.csv")
	    #for x in range(len(database)):
	    #    print(database[x])
            bestfive = API.BestFive(user_location, database)
	    #for x in range(5):
	    #    print(database[bestfive[x][0]]['Location'])
            destination_string = []
            destination_coordinate = []
            
            streetName = []

            for x in range(len(bestfive)):
                temp = database[bestfive[x][0]]['Location'].split("\n")[0] + " Las Vegas"
                streetName.append(temp)
                destination_string.append(temp)
            for x in range(len(bestfive)):
                destination_coordinate.append(API.LocationConvertion(destination_string[x]))
            API.Demo(destination_coordinate)

            session['userLocation'] = user_location
            session['streetName'] = streetName
            return redirect(url_for('user_viewparking')) 
            
            
    return render_template("user.html")

@app.route("/user_viewparking", methods = ['GET', 'POST'])
def user_viewparking():
    htmlCode = ""
    with open("templates/export.html") as f:
        userLocation = session.get('userLocation', None) 
        streetName = session.get('streetName', None)
        for line in f:
            if ("</body>" in line):
                htmlCode += "<h2><strong>List of Available Parking</strong> </h2><br>\n" 
                for i in range(len(streetName)):
                    url = API.GetDirection(str(userLocation), str(streetName[i]))
                    htmlCode += "<a href=" + "\""+ url+ "\">"+ str(streetName[i]) + "</a><br>\n"

                    
            else:
                htmlCode += line

    htmlCode += "</body>\n"
    htmlCode += "</html>\n"

    return htmlCode


if __name__ == "__main__":
    app.run(debug=True)
    #app.run()
