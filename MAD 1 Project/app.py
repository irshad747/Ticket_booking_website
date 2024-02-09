from flask import Flask, render_template, request, redirect, url_for,session,flash,jsonify
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime,date
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
import datetime
from datetime import date
# Assuming your existing database configuration and models are already defined
current_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
api = Api(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"+ os.path.join(current_dir,"project.db")
db = SQLAlchemy(app)
app.app_context().push()
app.secret_key = 'mysecretkey'


class admin(db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    admin_name = db.Column(db.String,nullable=False)
    admin_email =db.Column(db.String,unique=True,nullable=False)
    admin_pass = db.Column(db.String,nullable=False,unique=True)
class user(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.Integer)
    address =db.Column(db.String)

class venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    current_capacity = db.Column(db.Integer)
    shows = db.relationship('show', backref='venue', lazy=True,cascade='all,delete')
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'location': self.location,
                'capacity': self.capacity,'current_capacity':self.current_capacity}
class show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    available_seats = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer)
    rating = db.Column(db.String)
    tag = db.Column(db.String)
    Date = db.Column(db.Date)
    poster = db.Column(db.String)
    Synopsis = db.Column(db.String)
    Description = db.Column(db.String)
    bookings = db.relationship('booking', backref='show', lazy=True,cascade='all,delete')
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'time': self.time,
                'venue_id': self.venue_id,'available_seats':self.available_seats,'price':self.price,'rating':self.rating,'tag':self.tag,'Date':self.Date.isoformat(),'poster':self.poster,'Synopsis':self.Synopsis,'Description':self.Description,'venue': self.venue.to_dict()}

class booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer,autoincrement=True,primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'))
    num_tickets = db.Column(db.Integer, nullable=False)

class ratings(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=False)
    r = db.Column(db.Integer, nullable=False)

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/User', methods=['POST','GET'])
def User_login():
    if request.method=='GET':
      
      return render_template('user_form.html')
    else: 
        
         username = request.form['User']
         password = request.form['passcode']
         req_user = user.query.filter_by(name=username, password=password).first()
         if req_user:
            userr = req_user.id
            return redirect(url_for('user_dashboard',user_id = userr))
         else:
              flash('Invalid username or password.')
              return redirect(url_for('User_login'))
# User side Website
# Registeration for new User
@app.route('/User/register',methods=['GET','POST'])
def register():
    if request.method=='GET':
        return render_template('register.html')
    else:
        
        new_user_name = request.form['name']
        new_user_email = request.form['email']
        new_user_password = request.form['pass']
        new_user = user(name=new_user_name, email=new_user_email, password=new_user_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))
# Design a user Dashboard where in i can see every show  but shows in every should be distinct
# Now designing controller for user_dashboard
@app.route('/User/<int:user_id>/dashboard', methods=['GET', 'POST'])
def user_dashboard(user_id):
    if request.method == 'GET':
        userr = user.query.filter_by(id=user_id).first()
        venues = venue.query.all()
        specific_date = date(2023, 3, 25)
        date_str = specific_date.strftime('%Y-%m-%d')
        response = requests.get(f'http://localhost:5000/shows/{date_str}')
        
        if response.status_code == 200:
            shows = response.json()['shows']
        else:
            print('Error retrieving shows: ', response.status_code)
            shows = []
        
        return render_template('user_dashboard.html', venues=venues, shows=shows, userr=userr, specific_date=specific_date)
    # click on Book ticket for any show will redirect to page where we can see all the venues which are showing that show and will also give us time for that show in that venue
    else:
         userr = user.query.filter_by(id=user_id).first()
         req_show_name = request.form['show_id']
         response = requests.get(f'http://localhost:5000/shows/byname/{req_show_name}')
         if response.status_code == 200:
            data = response.json()
            req_show = data['shows']
            venues = data['venues']
         else:
            print('Error retrieving shows and venues: ', response.status_code)
            req_show = []
            venues = []
         return render_template('display_venues_for_show.html', shows=req_show_name, venuess=venues, userr=userr, showss=req_show,the_show=req_show_name)

@app.route('/User/<int:user_id>/Venues',methods=['GET','POST'])
def display_venues(user_id):
    # by clicking on cinemas on navigation bar will take to page with list of Cinemas
    if request.method=='GET':
        response = requests.get('http://localhost:5000/api/venues')
        if response.status_code == 200:
            req_venues = response.json()['venues']
        else:
            print('Error retrieving venues: ', response.status_code)
            req_venues = []
        userr = user.query.filter_by(id=user_id).first()
        return render_template('venues_list.html', venues=req_venues, userr=userr, user_id=user_id)
    else:
        ven_id = request.form['venue_id']
        # Get venue for the given venue_id
        response = requests.get(f'http://localhost:5000/venues/{ven_id}')
        if response.status_code == 200:
          req_venue = response.json()['venue']
        else:
          print('Error retrieving venue: ', response.status_code)
          req_venue = None
        # Get shows for given venue id
        response = requests.get(f'http://localhost:5000/api/shows/byvenue/{ven_id}')
        if response.status_code == 200:
          req_shows = response.json()['shows']
        else:
          print('Error retrieving shows: ', response.status_code)
          req_shows = []
        userr = user.query.filter_by(id=user_id).first()
        return render_template('display_shows_for_venue.html',shows=req_shows,venues=req_venue,user_id=user_id,userr=userr,ven_id=ven_id)


@app.route('/User/<int:user_id>/profile',methods=['GET','POST'])
def user_profile(user_id):
    if request.method=='GET':
        users = user.query.filter_by(id=user_id).first()
        booking_info = booking.query.filter_by(user_id=user_id).all()
        userr = user.query.filter_by(id=user_id).first()
        return render_template('user_profile.html',users=users,bookings=booking_info,userr=users)
    if request.method=='POST':
        re_user = user.query.filter_by(id=user_id).first()
        re_user.name = request.form['name']
        re_user.email = request.form['email']
        re_user.phone = request.form['phone']
        re_user.address = request.form['address']
        db.session.commit()
        users = user.query.filter_by(id=user_id).first()
        booking_info = booking.query.filter_by(user_id=user_id).all()
        userr = user.query.filter_by(id=user_id).first()
        return render_template('Profile_updated.html',userr=userr,users=re_user)    
@app.route('/User/<int:user_id>/search', methods=['POST'])
def search(user_id):
    location = request.form.get('location')
    tags = request.form.get('tags')
    rating = request.form.get('rating')
    movie_name = request.form.get('name')
    if not location:
        location = None
    if not tags:
        tags = None
    if not rating:
        rating = None
    if not movie_name:
        movie_name=None
    if location and not (tags or rating or movie_name):
            req_venues = venue.query.filter(venue.location.contains(location)).all()
            userr = user.query.filter_by(id=user_id).first()
            return render_template('venues_list.html',venues=req_venues,user_id=user_id,userr=userr)
    elif (tags or rating or movie_name):
        shows = show.query
        if tags:
            shows = shows.filter(show.tag.contains(tags))
        if rating:
            shows = shows.filter(show.rating.contains(rating))
        if movie_name:
            shows = shows.filter(show.name.contains(movie_name))
        shows = shows.group_by(show.name).all()
        distinct_shows = []
        for show_group in shows:
            distinct_shows.append(show_group)
        userr = user.query.filter_by(id=user_id).first()
        return render_template('user_dashboard.html',shows=distinct_shows,userr=userr)

@app.route('/Rating/<int:show_id>/<int:user_id>', methods=['POST'])
def Rating(show_id, user_id):
    rating_value = int(request.form['Rating'])

    # Check if the user has already rated this show
    existing_rating = ratings.query.filter_by(show_id=show_id,user_id=user_id).first()
    if existing_rating:
        existing_rating.r = rating_value
    else:
        new_rating = ratings(show_id=show_id, user_id=user_id, r=rating_value)
        db.session.add(new_rating)

    # Commit the changes to the database
    db.session.commit()

    # Redirect the user to their profile page
    return redirect(url_for('user_profile', user_id=user_id))
@app.route("/User/<int:user_id>/<int:show_id>/<int:venue_id>/<string:date>/<string:time>/confirm",methods=['POST','GET'])
def tickets_booked(user_id,show_id,venue_id,date,time):
    # clicking on any date time in display_venues_for_show will take to form to fill details to book show in that particular venue
    if request.method == 'GET':
     req_show = None
     response = requests.get(f'http://localhost:5000/shows/{show_id}')
     if response.status_code == 200:
        req_show = response.json().get('show')
     else:
        print('Error retrieving show: ', response.status_code)
     req_venue = None
     response = requests.get(f'http://localhost:5000/venues/{venue_id}')
     if response.status_code == 200:
        req_venue = response.json().get('venue')
     else:
        print('Error retrieving venue: ', response.status_code)
     date = date
     time = time
     userr = user.query.filter_by(id=user_id).first()
     return render_template('ticket_booking_wind.html', show_id=show_id, venue_id=venue_id, D=date, T=time, user_id=user_id, shows=req_show, venues=req_venue, userr=userr)
    else:
        no_of_tickets = int(request.form['num_tickets'])
        show_name = request.form['show_name']
        venue_name = request.form['venue_name']
        available_seats = int(request.form['available_seats'])
        D = request.form['Date']
        T = request.form['Time']
        # Get the show and venue combination
        response = requests.get(f'http://localhost:5000/showandvenue/{show_name}/{venue_name}')
        if response.status_code == 200:
          req_show = response.json().get('show')
        else:
          print('Error retrieving show and venue: ', response.status_code)
          req_show = None
        if req_show and no_of_tickets <= available_seats:
          Booking = booking(user_id=user_id, show_id=req_show['id'], num_tickets=no_of_tickets)
          # Update available seats for the show
          response = requests.put(f'http://localhost:5000/showandvenue/{show_name}/{venue_name}', json={"num_tickets": no_of_tickets})
          if response.status_code != 200:
            print('Error updating show: ', response.status_code)
          db.session.add(Booking)
          db.session.commit()
          d = D
          t = T
          userr = user.query.filter_by(id=user_id).first()
          return render_template("confirmation.html", user_id=user_id, show_name=show_name, venue_name=venue_name, d=d, t=t, show_id=req_show['id'], venue_id=req_show['venue']['id'], userr=userr)

###_______________________####______________________________####____________________________________
# Admin Side Website
@app.route('/Admin', methods=['POST','GET'])
def Admin():
    if request.method=='GET':
      return render_template('admin_form.html')
    else: 
        username = request.form['Admin']
        password = request.form['passcode']
        req_admin = admin.query.filter_by(admin_name=username, admin_pass=password).first()
        if req_admin:
            flash('You have successfully logged in!')
            return redirect(url_for('Admin_dashboard'))
        else:
              flash('Sorry you are not an admin!')
              return redirect(url_for('Admin'))

@app.route('/Admin/dashboard',methods=['GET','POST'])
def Admin_dashboard():
    if request.method=='GET':
        response = requests.get('http://localhost:5000/api/venues')
        if response.status_code == 200:
            req_venues = response.json()['venues']
        else:
            print('Error retrieving venues: ', response.status_code)
            req_venues = []
        return render_template('admin_dashboard.html',venues = req_venues)
@app.route("/Admin/add_venue",methods=['GET','POST'])
def add_venue():
    if request.method=='GET':
        return render_template("add_venue_form.html")
    else:
        name = request.form['name']
        loc = request.form['location']
        cap = request.form['Capacity']
        url = 'http://localhost:5000/api/add/venues'
        data = {'name': name, 'location': loc, 'capacity': cap, 'current_capacity': cap}
        response = requests.post(url, json=data)
        if response.status_code == 201:
          flash('Venue added successfully', 'success')
        else:
          flash('Error adding venue', 'danger')

        return redirect(url_for('Admin_dashboard'))
@app.route("/Admin/<int:venue_id>/edit_venue",methods=['GET','POST'])
def edit_venue(venue_id):
    if request.method=='GET':
        req_venue = None
        response = requests.get(f'http://localhost:5000/venues/{venue_id}')
        if response.status_code == 200:
          req_venue = response.json().get('venue')
        return render_template("edit_venue_form.html",venues=req_venue)
    else:
        venue_id = int(request.form['venue_id'])
        name = request.form['name']
        location = request.form['Location']
        capacity = request.form['Capacity']

        url = f'http://localhost:5000/api/venues/{venue_id}'
        data = {'name': name, 'location': location, 'capacity': capacity}
        response = requests.put(url, json=data)
        if response.status_code == 200:
          flash('Venue updated successfully', 'success')
        else:
          flash('Error updating venue', 'danger')

        return redirect(url_for('Admin_dashboard'))
    
@app.route("/Admin/<int:venue_id>/delete_venue")
def delete_venue_confirmation(venue_id):
    venue_to_delete = None
    response = requests.get(f'http://localhost:5000/venues/{venue_id}')
    if response.status_code == 200:
      venue_to_delete = response.json().get('venue')
    return render_template('delete_venue_confirmation.html', venues=venue_to_delete)
@app.route("/Admin/<int:venue_id>/delete_venue_confirmed",methods=['POST'])
def delete_venue(venue_id):
    url = f'http://localhost:5000/api/venue/{venue_id}'
    
    # Send a DELETE request to the API
    response = requests.delete(url)
    if response.status_code == 200:
        # Redirect to the Admin dashboard
        return redirect(url_for('Admin_dashboard'))
    else:
        # Handle the error response
        return f"Error deleting venue with id {venue_id}: {response.text}", response.status_code
@app.route("/Admin/<int:venue_id>/add_show",methods=['GET','POST'])
def add_show(venue_id):
    if request.method=='GET':
        req_ven = None
        response = requests.get(f'http://localhost:5000/venues/{venue_id}')
        if response.status_code == 200:
          req_ven = response.json().get('venue')
        venue_name = req_ven['name']
        seats_left = req_ven['current_capacity']
        return render_template("add_show_form.html",venue_name=venue_name,venues=req_ven,seats_left=seats_left)
    else:
        show_data = {
        'name': request.form['name'],
        'Time': request.form['Time'],
        'venue_id': request.form['venue_id'],
        'Available_seats': request.form['Available_seats'],
        'Ratings': request.form['Ratings'],
        'Tags': request.form['Tags'],
        'price': request.form['price'],
        'Date': request.form['Date'],
        'Synopsis': request.form['Synopsis'],
        'Description': request.form['Description'],
        }

        # Send a POST request to the API
        url = 'http://localhost:5000/api/show'
        response = requests.post(url, data=show_data)
        if response.status_code == 201:
        # Redirect to the Admin dashboard
          return redirect(url_for('Admin_dashboard'))
        else:
        # Handle the error response
          return f"Error adding show: {response.text}", response.status_code
@app.route("/Admin/<int:show_id>/edit",methods=['GET','POST'])
def edit_show(show_id):
    if request.method=='GET':
        url = f'http://localhost:5000/shows/{show_id}'
        response = requests.get(url)
        response_data = response.json()
        req_show = response_data['show']

        # Get the venue object from the show object
        req_venue = req_show['venue']
        venue_name = req_venue['name']
        return render_template("edit_show_form.html",show_id=show_id,shows=req_show,venue_name=venue_name)
    else:
        url = f'http://localhost:5000/api/show/update/{show_id}'
        response = requests.put(url, data=request.form)

        # Check if the request was successful
        if response.status_code == 200:
          # Redirect to the admin dashboard
          return redirect(url_for('Admin_dashboard'))
        else:
          # Handle the error response
          return f"Error updating show with id {show_id}: {response.text}", response.status_code
@app.route("/Admin/<int:show_id>/delete_show")
def delete_show_confirmation(show_id):
    show_to_delete = None
    response = requests.get(f'http://localhost:5000/shows/{show_id}')
    if response.status_code == 200:
      show_to_delete = response.json().get('show')
    return render_template('delete_show_confirmation.html', shows=show_to_delete)
    print ("hello")

@app.route('/Admin/<int:show_id>/delete_show_confirmed', methods=['POST'])
def delete_show(show_id):
    # Send a DELETE request to the API to delete the show object
    url = f'http://localhost:5000/api/show/delete/{show_id}'
    response = requests.delete(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Redirect to the admin dashboard
        return redirect(url_for('Admin_dashboard'))
    else:
        # Handle the error response
        return f"Error deleting show with id {show_id}: {response.text}", response.status_code
    

#################_______________All The APIs _______#################_________________############
class ShowResource(Resource):
    def get(self, show_date):
        try:
            # Parse the date string into a datetime.date object
            show_date = datetime.datetime.strptime(show_date, "%Y-%m-%d").date()
        except ValueError:
            return {"message": "Invalid date format. Expected format: 'YYYY-MM-DD'."}, 400

        shows_from_date = show.query.filter(show.Date>=show_date).distinct(show.name).group_by(show.name).all()

        # Convert the shows_on_date list into a list of dictionaries
        show_list = [s.to_dict() for s in shows_from_date]

        return {"shows": show_list}
# Register the ShowResource with the API under the route "/shows/<string:show_date>"
api.add_resource(ShowResource, "/shows/<string:show_date>")


class ShowByNameResource(Resource):
    def get(self, show_name):
        req_show = show.query.filter_by(name=show_name).all()
        venues = []
        for s in req_show:
            venuee = s.venue
            if venuee not in venues:
                venuee_dict = venuee.to_dict()
                venuee_dict['shows'] = [s.to_dict() for s in venuee.shows]
                venues.append(venuee_dict)

        # Convert the req_show list into a list of dictionaries
        show_list = [s.to_dict() for s in req_show]

        return {"shows": show_list, "venues": venues}

api.add_resource(ShowByNameResource, "/shows/byname/<string:show_name>")

class ShowByIdResource(Resource):
    def get(self, show_id):
        req_show = show.query.get(show_id)
        if req_show:
            return jsonify({"show": req_show.to_dict()})
        else:
            return {"message": "Show not found"}, 404
class VenueByIdResource(Resource):
    def get(self, venue_id):
        req_venue = venue.query.get(venue_id)
        if req_venue:
            return {"venue": req_venue.to_dict()}
        else:
            return {"message": "Venue not found"}, 404
api.add_resource(ShowByIdResource, "/shows/<int:show_id>")
api.add_resource(VenueByIdResource, "/venues/<int:venue_id>")

from flask_restful import Resource, reqparse

class ShowAndVenueResource(Resource):
    def get(self, show_name, venue_name):
        req_show = show.query.join(venue).\
            filter(show.name == show_name, venue.name == venue_name).first()
        if req_show:
            return {"show": req_show.to_dict()}
        else:
            return {"message": "Show and venue combination not found"}, 404

    def put(self, show_name, venue_name):
        parser = reqparse.RequestParser()
        parser.add_argument('num_tickets', type=int, required=True)
        args = parser.parse_args()

        req_show = show.query.join(venue).\
            filter(show.name == show_name, venue.name == venue_name).first()
        if req_show:
            if args['num_tickets'] <= req_show.available_seats:
                req_show.available_seats -= args['num_tickets']
                db.session.commit()
                return {"message": "Show updated successfully", "show": req_show.to_dict()}
            else:
                return {"message": "Insufficient available seats"}, 400
        else:
            return {"message": "Show and venue combination not found"}, 404
api.add_resource(ShowAndVenueResource, "/showandvenue/<string:show_name>/<string:venue_name>")
class VenueListResource(Resource):
    def get(self):
        venues = venue.query.all()
        return {"venues": [v.to_dict() for v in venues]}
api.add_resource(VenueListResource, "/api/venues")
class ShowsByVenueResource(Resource):
    def get(self, venue_id):
        req_shows = show.query.filter_by(venue_id=venue_id).all()
        return {"shows": [s.to_dict() for s in req_shows]}
api.add_resource(ShowsByVenueResource, "/api/shows/byvenue/<int:venue_id>")
class AddVenueResource(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True, help="No venue name provided")
        self.reqparse.add_argument('location', type=str, required=True, help="No venue location provided")
        self.reqparse.add_argument('capacity', type=int, required=True, help="No venue capacity provided")
        self.reqparse.add_argument('current_capacity', type=int, required=False, help="No venue current capacity provided")

    def post(self):
        args = self.reqparse.parse_args()
        new_venue = venue(name=args['name'], location=args['location'], capacity=args['capacity'], current_capacity=args['current_capacity'])
        db.session.add(new_venue)
        db.session.commit()

        return {'message': 'Venue added successfully'}, 201
api.add_resource(AddVenueResource, "/api/add/venues")

class UpdateVenueResource(Resource):
    def put(self, venue_id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Name is required')
        parser.add_argument('location', type=str, required=True, help='Location is required')
        parser.add_argument('capacity', type=int, required=True, help='Capacity is required')
        args = parser.parse_args()

        venue_to_update = venue.query.get(venue_id)

        if venue_to_update:
            venue_to_update.name = args['name']
            venue_to_update.location = args['location']
            venue_to_update.capacity = args['capacity']

            shows = show.query.filter_by(venue_id=venue_id)
            booked_seats = 0
            for s in shows:
                booked_seats += s.available_seats

            venue_to_update.current_capacity = args['capacity'] - booked_seats
            db.session.commit()

            return {'message': 'Venue updated successfully'}, 200
        else:
            return {'message': 'Venue not found'}, 404
api.add_resource(UpdateVenueResource, '/api/venues/<int:venue_id>')

class delVenueResource(Resource):
    def delete(self, venue_id):
        # Get the venue by its ID
        target_venue = venue.query.get(venue_id)

        # If the venue is not found, return a 404 error
        if target_venue is None:
            return {'message': f"Venue with id {venue_id} not found."}, 404

        # Delete the venue's shows
        show.query.filter_by(venue_id=venue_id).delete()

        # Delete the venue
        db.session.delete(target_venue)

        # Commit the changes
        db.session.commit()

        return {'message': f"Venue with id {venue_id} and its corresponding shows have been deleted."}, 200

# Add the API resource for the venue
api.add_resource(delVenueResource, '/api/venue/<int:venue_id>')


class ShowDeleterResource(Resource):
    def delete(self, show_id):
        # Get the show object by its ID
        show_to_delete = show.query.get(show_id)

        # If the show is not found, return a 404 error
        if show_to_delete is None:
            return {'message': f"Show with id {show_id} not found."}, 404

        # Update the venue's current_capacity
        req_ven = show_to_delete.venue
        req_ven.current_capacity += show_to_delete.available_seats

        # Delete the show object from the database
        db.session.delete(show_to_delete)
        db.session.commit()

        # Return a success message
        return {'message': f"Show with id {show_id} deleted successfully."}, 200

# Add the API resource for the show deleter
api.add_resource(ShowDeleterResource, '/api/show/delete/<int:show_id>')



class AddShowResource(Resource):
    def post(self):
        # Get the form data from the request
        name = request.form['name']
        time = request.form['Time']
        venue_id = request.form['venue_id']
        avail_seats = request.form['Available_seats']
        rating = request.form['Ratings']
        tags = request.form['Tags']
        price = request.form['price']
        Date = request.form['Date']
        Date = datetime.strptime(Date, '%Y-%m-%d')
        Synopsis = request.form['Synopsis']
        Description = request.form['Description']

        # Find the venue and update its current_capacity
        req_ven = venue.query.filter_by(id=venue_id).first()
        req_ven.current_capacity = req_ven.current_capacity - int(avail_seats)

        # Create a new show object
        new_show = show(name=name, time=time, venue_id=venue_id, available_seats=avail_seats, price=price, rating=rating, tag=tags, Date=Date, poster=None, Synopsis=Synopsis, Description=Description)

        # Add the new show to the database
        db.session.add(new_show)
        db.session.commit()

        return {'message': f"Show '{name}' has been added successfully."}, 201

# Add the API resource for the show
api.add_resource(AddShowResource, '/api/show')

class ShowUpdaterResource(Resource):
    def put(self, show_id):
        # Get the show object by its ID
        new_show = show.query.get(show_id)

        # If the show is not found, return a 404 error
        if new_show is None:
            return {'message': f"Show with id {show_id} not found."}, 404

        # Update the show object with the new data
        old_reserved_seats = new_show.available_seats
        new_show.name = request.form['name']
        new_show.time = request.form['Time']
        new_show.available_seats = request.form['Available_seats']
        new_show.rating = request.form['Ratings']
        new_show.tags = request.form['Tags']
        new_show.price = request.form['price']
        new_show.Date = request.form['Date']
        new_show.Synopsis = request.form['Synopsis']
        new_show.Description = request.form['Description']
        new_ven = new_show.venue
        new_show.venue_id = new_ven.id

        if int(old_reserved_seats) != int(request.form['Available_seats']):
            difference = int(old_reserved_seats) - int(request.form['Available_seats'])
            new_ven.current_capacity = new_ven.current_capacity + difference

        # Commit the changes to the database
        db.session.commit()

        # Return the updated show object as a JSON object
        return jsonify({"show": new_show.to_dict()})

# Add the API resource for the show updater
api.add_resource(ShowUpdaterResource, '/api/show/update/<int:show_id>')







if __name__ == '__main__':
    app.run(debug=True)
