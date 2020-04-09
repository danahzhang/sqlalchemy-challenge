import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt

#Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
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
        f"/api/v1.0/startdate<br/>"
        f"/api/v1.0/startdate/enddate<br/>"
        "*the last two routes, please format start and end dates as YYYYMMDD between the last '/'"
        "*dates between 20200101-20170823(1/1/2010-8/23/2017)"
        "examples for the last two"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    # Query date and prcp
    results = session.query(Measurement.date, Measurement.prcp).all()
    all_results = list(np.ravel(results))

    session.close()

    # Convert to dictionary
    prcp_dict = {}
    total = len(all_results)+1

    for n in range(int(total/2)-1):
        prcp_dict[all_results[n*2]]=all_results[n*2+1]
    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    # Query
    results = session.query(Station.name).all()

    session.close()

    # Convert to list
    stations = list(np.ravel(results))

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    # Query date and data
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last = str(last_date[0])
    first_date = (dt.date.fromisoformat(last) - dt.timedelta(days=365)).isoformat()

    results = session.query(Measurement.tobs).\
        filter(Measurement.date >= first_date).\
        order_by(Measurement.date).all()

    session.close()

    # Convert to list
    tobs = list(np.ravel(results))

    return jsonify(tobs)
 
@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)

    # Query date and data
    year = int(start[0:4])
    if start[5]=="0":
        month = int(start[6])
    else: 
        month = int(start[5:6])
    if start[7]=="0":
        month = int(start[8])
    else:    
        day = int(start[7:8])
    date = dt.date(year,month,day).isoformat()
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= date).all()

    session.close()

    # Convert to list
    start = list(np.ravel(results))

    return jsonify(start)

@app.route("/api/v1.0/<start>/<end>")
def time(start,end):
    session = Session(engine)
    timestamp = [start,end]
    date_range = []
    # Query date and data
    for times in timestamp:
        year = int(times[0:4])
        if start[5]=="0":
            month = int(start[6])
        else: 
            month = int(start[5:6])
        if start[7]=="0":
            month = int(start[8])
        else:    
            day = int(start[7:8])
        date_range.append(dt.date(year,month,day).isoformat())
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= date_range[0]).\
        filter(Measurement.date <= date_range[1]).all()

    session.close()

    # Convert to list
    time = list(np.ravel(results))

    return jsonify(time)


if __name__ == '__main__':
    app.run(debug=True)

