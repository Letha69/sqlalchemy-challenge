import numpy as np
import pandas as pd
import datetime as dt


# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

from flask import Flask, jsonify


################################################################################
# Database setup
################################################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement=Base.classes.measurement
Station = Base.classes.station

##################################################################################
# flask setup
##################################################################################
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )
# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

        # Find the most recent date in the data set.
    recent_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    #  Calculate the date one year from the last date in data set.
    query_date = dt.datetime(2017,8,23) - dt.timedelta(days=365)

    """ Return a list of measurement date and prcp information from the last year """
    rainfall_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>= query_date).order_by(Measurement.date)
    
    session.close()
    
  # Create a dictionary from the row data and append to a list
    rainfall_values = []
    for p in rainfall_results:
        rain_dict = {}
        rain_dict["date"] = p.date
        rain_dict["prcp"] = p.prcp
        rainfall_values.append(rain_dict)

    return jsonify(rainfall_values)


    # list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """Return a list of all stations"""

    stations = session.query(Station.station).all()
    session.close()

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for station in stations:
        station_dict = {}
        station_dict["station"] = station
        all_stations.append(station_dict)

    return jsonify(all_stations)

    #Query the dates and temperature observations of the most active station for the last year of data.
    #Return a JSON list of temperature observations (TOBS) for the previous year

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Calculate the date 1 year ago from last date in database
    year_ago = dt.datetime(2017,8,23) - dt.timedelta(days=365)
    sel= [Measurement.date, Measurement.tobs]
    """Return the temperature observations (tobs) for previous year."""    

    #Return a JSON list of temperature observations (TOBS) for the previous year
    # Query  the primary station for all tobs from the last year
    results = session.query(*sel).\
        filter(Measurement.station =='USC00519281').\
        filter(Measurement.date >=year_ago).all()


    session = Session(engine)

    """ Return the result of most active station"""
    
    temps = list(np.ravel(results))

    # Return the results
    return jsonify(temps)
   
# list of the minimum temperature, the average temperature, and the max temperature for a given start

@app.route('/api/v1.0/<start>')
def temps(start):
    session = Session(engine)

    start = dt.datetime(2017,8,23) - dt.timedelta(days=365)
    end=  dt.datetime(2017, 8, 23) 

    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()
    temp = list(np.ravel(temp_data))

    return jsonify(temp) 

@app.route('/api/v1.0/<start>/<end>')
def temp(start, end):
    session = Session(engine)

    start = dt.datetime(2017,8,23) - dt.timedelta(days=365)
    end=  dt.datetime(2017, 8, 23) 

    end_temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <=end).all()
    session.close()
    temp = list(np.ravel(end_temp_data))

    return jsonify(temp)    

if __name__ == "__main__":
    app.run(debug=True)








