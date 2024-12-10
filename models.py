"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *
import csv #csv reading and writing

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
db.commit()

