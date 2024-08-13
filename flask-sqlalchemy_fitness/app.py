#Task 1: Setting Up Flask with Flask-SQLAlchemy - 
# Initialize a new Flask project and set up a virtual environment.
#  - Install Flask, Flask-SQLAlchemy, and Flask-Marshmallow. 
# - Configure Flask-SQLAlchemy to connect to your database. -
#  Define `Members` and `WorkoutSessions` models using Flask-SQLAlchemy ORM.

#Expected Outcome: A Flask project connected to a database using SQLAlchemy with ORM models for `Members` and `WorkoutSessions`.

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from marshmallow import fields, validate, ValidationError


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Babinz2023!@localhost/fitness_center_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)


class MemberSchema(ma.Schema):
      id = fields.Integer(required = True)
      name = fields.String(required= True)
      age = fields.Integer()

      class Meta:
          fields = ("id", "name", "age")


class WorkoutSchema(ma.Schema):
      session_id = fields.Integer(required = True)
      member_id = fields.Integer(required= True)
      session_date = fields.Date()
      duration_minutes = fields.Integer()
      activity = fields.String()
      calories_burned = fields.Integer()

      class Meta:
         fields = ("id", "session_id", "member_id", "session_date", "duration_minutes", "activity", "calories_burned")



member_schema = MemberSchema()
members_schema = MemberSchema(many= True)


workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many= True)





class Member(db.Model):
      __table_name__ = "Members"

      id = db.Column(db.Integer, primary_key = True)
      name= db.Column(db.String(255), nullable = False)
      age = db.Column(db.String(8))
      sessions = db.relationship('WorkoutSession', backref= 'member')
      

class WorkoutSession(db.Model):
      __table_name__ = "WorkoutSessions"

      session_id = db.Column(db.Integer, primary_key = True)
      member_id= db.Column(db.Integer, db.ForeignKey('member.id'), nullable = False)
      session_date = db.Column(db.Date)
      duration_minutes = db.Column(db.Integer)
      activity = db.Column(db.String(255))
      calories_burned = db.Column(db.Integer)
      





# Task 2: Implementing CRUD Operations for Members Using ORM - 

# Create Flask routes to add, retrieve, update, and delete members using the ORM models.
# 
#  - Apply HTTP methods: POST to add, GET to retrieve, PUT to update, and DELETE 
# to delete members. - Handle errors effectively and return appropriate JSON responses.

# Expected Outcome: Functional API endpoints for managing members in the database 
# using Flask-SQLAlchemy, with proper error handling.




@app.route('/', methods =['GET'])

def home():
    return "Welcome to the Fitness Center DB!!"

@app.route('/members', methods=['GET'])

def get_members():
      members = Member.query.all()
      return  members_schema.jsonify(members)

@app.route('/members', methods=['POST'])
def add_a_member():
   try:
     member_data = member_schema.load(request.json)
   except ValidationError as e:
     print(f'Validation Error: {e}')
     return jsonify(e.messages), 400

   new_member = Member(id = member_data["id"], name = member_data["name"], age = member_data["age"])
   db.session.add(new_member)
   db.session.commit()
       
   return jsonify({"message": "New member added successfully"}), 201


@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    member = Member.query.get_or_404(id)

    try:
    
      member_data = member_schema.load(request.json)
     #catch errors in input during update

    except ValidationError as e:
      print(f'Validation Error: {e}')
      return jsonify(e.messages), 400

    member.id  = member_data['id']
    member.name = member_data['name']
    member.age = member_data['age']

    db.session.commit()

    return jsonify({"message": "Member updated successfully"}), 201

  
@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    
    return jsonify({"message": "Member deleted successfully"}), 201





# _________________________******************____________________________



#Task 3: Managing Workout Sessions with ORM 
# - Develop routes to 
# schedule, update, and view workout sessions using SQLAlchemy.

#  Implement a route to retrieve all workout sessions for a specific member.

#Expected Outcome: A comprehensive set of endpoints for scheduling and viewing workout
#  sessions using Flask-SQLAlchemy, with detailed information about each session.

#route to get all workouts for a member
@app.route('/workouts/member_sessions/<int:id>', methods=['GET'])

def get_member_sessions(id):
      
      id = Member.query.get('id')
      sessions = WorkoutSession.query.filter(id==id).first()
      if sessions:
        return  workout_schema.jsonify(sessions)
      else:
          return jsonify({"message": "No sessions found for that member."})


@app.route('/workouts', methods=['GET'])

# route to view all workout sessions

def get_all_sessions():

      workouts = WorkoutSession.query.all()
      return  workouts_schema.jsonify(workouts)

### route for scheduling a workout session

@app.route('/workouts', methods=['POST'])
def schedule_workout():
   try:
     workout_data = workout_schema.load(request.json)
   except ValidationError as e:
     print(f'Validation Error: {e}')
     return jsonify(e.messages), 400

   new_workout = WorkoutSession(session_id= workout_data["session_id"], 
                                member_id= workout_data["member_id"],
                                session_date= workout_data["session_date"], 
                                duration_minutes= workout_data["duration_minutes"], 
                                activity= workout_data["activity"], 
                                calories_burned= workout_data["calories_burned"])
   db.session.add(new_workout)
   db.session.commit()
       
   return jsonify({"message": "New workout session added successfully"}), 201



# route to update a workout

@app.route('/workouts/<int:id>', methods=['PUT'])
def update_workout(id):
    workout = WorkoutSession.query.one_or_404(id)
    try:
    
      workout_data = workout_schema.load(request.json)
     #catch errors in input during update

    except ValidationError as e:
      print(f'Validation Error: {e}')
      return jsonify(e.messages), 400

    workout.session_id  = workout_data['session_id']
    workout.member_id  = workout_data['member_id']
    workout.duration_minutes = workout_data['duration_minutes']
    workout.activity = workout_data['activity']
    workout.calories_burned = workout_data['calories_burned']

    db.session.commit()

    return jsonify({"message": "Workout session updated successfully"}), 201

with app.app_context():
    db.create_all()