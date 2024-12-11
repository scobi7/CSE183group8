"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *
import os
import csv

def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
db.define_table(
    'checklist',
    Field('SAMPLING_EVENT_IDENTIFIER', 'string'),
    Field('LATITUDE', 'double'),
    Field('LONGITUDE', 'double'),
    Field('OBSERVATION_DATE', 'date'),
    Field('TIME_OBSERVATIONS_STARTED', 'time'),
    Field('OBSERVER_ID', 'string'),
    Field('DURATION_MINUTES', 'double')
)

db.define_table(
    'species',
    Field('COMMON_NAME', 'string')
)

db.define_table(
    'sightings',
    Field('SAMPLING_EVENT_IDENTIFIER', 'string'),
    Field('COMMON_NAME', 'string'),
    Field('OBSERVATION_COUNT', 'string')
)

db.define_table(
    'checklist_table',
    Field('user_email', default=get_user_email),
    Field('date', 'datetime', default=get_time),
    Field('species_name', 'string'),
    Field('numSeen', 'integer')
)

CSV_DIR = os.path.join(os.getcwd(), 'csvfiles')
#prime data from csv files
def load_species():
    species_file = os.path.join(CSV_DIR, 'species.csv')
    if db(db.species).isempty():
        with open(species_file, 'r') as f:
            reader = csv.reader(f)
            next(reader) 
            for row in reader:
                db.species.insert(
                    id=int(row[0]),
                    common_name=row[1],
                    scientific_name=row[2] if len(row) > 2 else None,
                    habitat=row[3] if len(row) > 3 else None
                )
        db.commit()

def load_checklists():
    checklist_file = os.path.join(CSV_DIR, 'checklists.csv')
    if db(db.checklist).isempty():
        with open(checklist_file, 'r') as f:
            reader = csv.reader(f)
            next(reader)  
            for row in reader:
                db.checklist.insert(
                    sampling_event_id=row[0],
                    latitude=float(row[1]),
                    longitude=float(row[2]),
                    observer_email=row[3],
                    observation_date=row[4]
                )
        db.commit()

def load_sightings():
    sightings_file = os.path.join(CSV_DIR, 'sightings.csv')
    if db(db.sightings).isempty():
        with open(sightings_file, 'r') as f:
            reader = csv.reader(f)
            next(reader) 
            for row in reader:
                db.sightings.insert(
                    sampling_event_id=row[0],
                    species_id=int(row[1]),
                    observation_count=int(row[2]) if row[2].isdigit() else 0,
                    notes=row[3] if len(row) > 3 else None
                )
        db.commit()

def load_data():
    """Call all loaders to populate the database."""
    load_species()
    load_checklists()
    load_sightings()

# Run the loader
load_data()
