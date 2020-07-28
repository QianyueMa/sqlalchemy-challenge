import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

from flask import Flask, jsonify

import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Collect the names of tables within the database
inspector = inspect(engine)
inspector.get_table_names()


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes listed in the Instructions."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of your dictionary."""

    print("Precipitation API:")

    last_data = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    # the lastest date point
    last_date = last_data[0][0]

    # 1 year before from the lastest date point
    start_date = last_date - dt.timedelta(365)
    
    # Perform a query to retrieve the data and precipitation scores
    # Convert the query results to a dictionary using date as the key and prcp as the value.
    precipitation_last_yr = session.query(func.strftime("%Y-%m-%d", Measurement.date), Measurement.prcp).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= start_date).all()
    
    session.close()

    precipitation_data = list(np.ravel(precipitation_last_yr))

    # Return the JSON representation of your dictionary.
    return jsonify(precipitation_data)


@app.route("/api/v1.0/stations")
def stations():
    stations = session.query(Station.station).all()
    stations_data = list(np.ravel(stations))
    return jsonify(stations_data)


@app.route("/api/v1.0/tobs")
def tobs():
    last_data = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    last_date = last_data[0][0]

    start_date = last_date - dt.timedelta(365)
    
    temperature_last_yr = session.query(Measurement.date, Measurement.tobs).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= dt.date(2016, 8, 23)).all()
    
    # Create a dictionary from the row data and append to the list
    tobs = []
    for result in temperature_last_yr:
        tobs_dict = {}
        tobs_dict["date"] = result.date
        tobs_dict["station"] = result.station
        tobs_dict["tobs"] = result.tobs
        tobs_list.append(tobs_dict)
    
    return jsonify(tobs)


@app.route("/api/v1.0/<start>")
def start(start):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    start_date = session.query(*sel)\
            .filter(func.strftime("%Y-%m-%d", Measurement.date) >= dt.date(2016, 8, 23))\
            .group_by(Measurement.date)\
            .all()

    dates = []                       
    for result in start_date:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    
    return jsonify(dates)


@app.route("/api/v1.0/<start>/<end>")
def startend(start, end):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                .filter(func.strftime("%Y-%m-%d", Measurement.date) >= dt.date(2016, 8, 23))
                .filter(func.strftime("%Y-%m-%d", Measurement.date) <= dt.date(2017, 8, 23))
                .group_by(Measurement.date)
                .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)


if __name__ == '__main__':
    app.run(debug=True)
