import datetime
import os
import csv
from .common import db, Field, auth
from pydal.validators import *

def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()

# Define tables
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

# Path to the csvfiles directory
#CSV_DIR = os.path.join(os.path.dirname(__file__), 'csvfiles')
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # Two levels up from models.py
UPLOADS_DIR = os.path.join(BASE_DIR, 'cse183group8', 'csvfiles')
CSV_DIR = os.path.join(BASE_DIR, 'csvfiles')

# Prime data from csv files
# Load data from species.csv
if db(db.species).isempty():
    species_file = os.path.join(UPLOADS_DIR, 'species.csv')
    with open(species_file, 'r') as dumpfile:
        db.species.import_from_csv_file(dumpfile)
        db.commit()

# Load data from sightings.csv
if db(db.sightings).isempty():
    sightings_file = os.path.join(UPLOADS_DIR, 'sightings.csv')
    with open(sightings_file, 'r') as dumpfile:
        db.sightings.import_from_csv_file(dumpfile)
        db.commit()

# Load data from checklists.csv
if db(db.checklist).isempty():
    checklist_file = os.path.join(UPLOADS_DIR, 'checklists.csv')
    with open(checklist_file, 'r') as dumpfile:
        db.checklist.import_from_csv_file(dumpfile)
        db.commit()

# Additional function to load sightings from the csvfiles directory
def load_sightings():
    if db(db.sightings).isempty():
        sightings_file = os.path.join(CSV_DIR, 'sightings.csv')
        with open(sightings_file, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip the header row
            for row in reader:
                db.sightings.insert(
                    SAMPLING_EVENT_IDENTIFIER=row[0],
                    COMMON_NAME=row[1],
                    OBSERVATION_COUNT=int(row[2]) if row[2].isdigit() else 0
                )
        db.commit()