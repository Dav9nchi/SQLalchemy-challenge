#---------------------------------------------------------------------------------------------------------------------------------------
#                                         Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#---------------------------------------------------------------------------------------------------------------------------------------
#                                         Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table (Measurement, Station)
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session=Session(engine)
#---------------------------------------------------------------------------------------------------------------------------------------
#                                         Flask Setup
app = Flask(__name__)
#---------------------------------------------------------------------------------------------------------------------------------------
#                                         Flask Routes
    # /
    # Start at the homepage.
    # List all the available routes.    
@app.route("/")
def welcome():
    return(''' <h2> Welcome to the Climate app, the API available are following: 
               <li><a href = "/api/v1.0/precipitation"> Precipitation</a>: /api/v1.0/precipitation<br/>
               <li><a href = "/api/v1.0/stations">      API Stations</a>:  /api/v1.0/stations<br/>
               <li><a href = "/api/v1.0/tobs">          API Tobs</a>:      /api/v1.0/tobs<br/>
               <li><a href = "/api/v1.0/<start>">       API Start</a>:     /api/v1.0/<start_date><br/>
               <li><a href = "/api/v1.0/<start>">       API Start & End</a>: /api/v1.0/<start_date>/<end_date><br/>''')
#---------------------------------------------------------------------------------------------------------------------------------------
#                                         Precipitation
# Instructions:
    # Convert the query results from your precipitation analysis
    # (i.e. retrieve only the last 12 months of data) to a dictionary
    # using date as the key and prcp as the value.
    # Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Session link from Python to the DB
    session = Session(engine)

    # Query the Precipitation retriving the last 12 months of data      
    last_12_months = dt.date(2017, 8, 23) - dt.timedelta(days=365) 
    prec_data = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date >= last_12_months).\
                order_by(Measurement.date).all()
    
    # close Session 
    session.close()

    # put query results into a dictionary and return it jsonified
    prec_data_dict = {date: prcp for date, prcp in prec_data}
    return jsonify(prec_data_dict)
#---------------------------------------------------------------------------------------------------------------------------------------
#                                         Stations
# Instructions:
    # /api/v1.0/stations
    # Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    # Session link from Python to the DB
    session = Session(engine)

    # Query the list of stations from the dataset.  
    most_active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
                           group_by(Measurement.station).\
                           order_by(func.count(Measurement.station).desc()).all()
    # close Session  
    session.close()

    # Convert list of tuples into normal list
    most_active_stations_list = list(np.ravel(most_active_stations))

    # Return a list of stations in jsonified form
    return jsonify(most_active_stations_list)
#---------------------------------------------------------------------------------------------------------------------------------------
#                                         Tobs
# Instructions:
    #/api/v1.0/tobs
    # Query the dates and temperature observations of the most-active station
    # for the previous year of data.
    # Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    # Session link from Python to the DB
    session = Session(engine)

    #the most-active station
    previuos_year_of_data = dt.date(2017, 8, 23) - dt.timedelta(days=365) 
    most_active_station= 'USC00519281'
    Dates_Temp_observacion= session.query(Measurement.date, Measurement.tobs).\
                            filter(Measurement.date >= previuos_year_of_data).\
                            filter(Measurement.date <= '2017-08-23').\
                            filter(Measurement.station == most_active_station).\
                            order_by(Measurement.date).all()
    
    # close Session 
    session.close()

    # Convert list of tuples into normal list
    Dates_Temp_obse_list = list(np.ravel(Dates_Temp_observacion))

    # Return a list of stations in jsonified form
    return jsonify(Dates_Temp_obse_list)

#---------------------------------------------------------------------------------------------------------------------------------------
#                                         Start Date              
# Instructions: 
# /api/v1.0/<start>
    # Return a JSON list of the MIN temperature, AVG temperature, MAX temperature
    # for a specified start or start-end range.
    # For a specified start, calculate TMIN, TAVG, and TMAX for all the dates
    # greater than or equal to the start date.
@app.route("/api/v1.0/<start_date>")
def start(start_date):
    # Session link from Python to the DB
    session = Session(engine)

    # Query the MIN, AVG, MAX Temperature start date
    temperature_stats = session.query(func.min(Measurement.tobs).label('TMIN'),
                                func.avg(Measurement.tobs).label('TAVG'),
                                func.max(Measurement.tobs).label('TMAX')).\
                                filter(Measurement.date >= start_date).all()
    # close Session 
    session.close()
  
    # Convert the result into a dictionary
    temperature_dict = {'TMIN': temperature_stats[0].TMIN,
                        'TAVG': temperature_stats[0].TAVG,
                        'TMAX': temperature_stats[0].TMAX}

    # Return the result in JSON format
    return jsonify(temperature_dict)
#---------------------------------------------------------------------------------------------------------------------------------------
#                                         Start & End date
# Instructions: 
# /api/v1.0/<start>/<end>
    # Return a JSON list of the MIN temperature, AVG temperature, MAX temperature
    # for a specified start or start-end range.
    # For a specified start date and end date, calculate TMIN, TAVG, and TMAX
    # for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date, end_date):
    # Session link from Python to the DB
    session = Session(engine)

    # Query the MIN, AVG, MAX Temperature for the specified date range
    temperature_stats = session.query(func.min(Measurement.tobs).label('TMIN'),
                                func.avg(Measurement.tobs).label('TAVG'),
                                func.max(Measurement.tobs).label('TMAX')).\
                                filter(Measurement.date >= start_date).\
                                filter(Measurement.date <= end_date).all()

    # Close Session
    session.close()

    # Convert the result into a dictionary
    temperature_dict = {'TMIN': temperature_stats[0].TMIN,
                        'TAVG': temperature_stats[0].TAVG,
                        'TMAX': temperature_stats[0].TMAX}

    # Return the result in JSON format
    return jsonify(temperature_dict)
#---------------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)