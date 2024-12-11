"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email

url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', db, auth, url_signer)
def index():
    return dict(
        # COMPLETE: return here any signed URLs you need.
        my_callback_url = URL('my_callback', signer=url_signer),
    )


@action('my_callback')
@action.uses() # Add here things like db, auth, etc.
def my_callback():
    # The return value should be a dictionary that will be sent as JSON.
    return dict(my_value=3)

@action('location')
@action.uses('location.html', db, auth, url_signer)
def location():
    return dict(
        get_location_data_url = URL('get_location_data'),
    )

@action('get_location_data')
@action.uses(db, auth, url_signer)
def get_location_data():
    #sightings = db(db.sightings).select().as_list() #all sightings
    # = [{"SAMPLING_EVENT_IDENTIFIER": "S80376372" ,"COMMON_NAME": "White-crowned Sparrow", "OBSERVATION_COUNT": 2}]
    # {'id': 1, 'SAMPLING_EVENT_IDENTIFIER': None, 'COMMON_NAME': None, 'OBSERVATION_COUNT': None}
    
    #checklist = db(db.checklist).select().as_list() 
    # = [{"SAMPLING_EVENT_IDENTIFIER": "S80681260", "LATITUDE": 37.06096445677006, "LONGITUDE": -84.63335595604734, 
    #       "OBSERVATION_DATE": "2021-02-03", "TIME_OBSERVATIONS_STARTED": "10:55:00", "OBSERVER_ID": "obs1644106", "DURATION_MINUTES": 90.0}]
    # {'id': 8506, 'SAMPLING_EVENT_IDENTIFIER': None, 'LATITUDE': 37.432195056770055, 'LONGITUDE': -121.97998405604734, 'OBSERVATION_DATE': None, 'TIME_OBSERVATIONS_STARTED': None, 'OBSERVER_ID': None, 'DURATION_MINUTES': None}
    # get region coordinates


    #HOW IT WORKS
    # sampling event in checklist = LOCATION and DAY on map
    # sampling event IN SIGHTINGS = detailed BIRDS and COUNT for each point in checklist

    #print(sightings)
    #print(checklist)
    total_sightings = 0
    total_checklists = 0
    contributor_list = []
    location_data = [] # [{'species': 'bird', 'day': ['2021-02-03'], 'count': [2]}]

    checklist = db(db.checklist).select().as_list() #whole checklist for now while waiting for index page to catch up
    sightings = db(db.sightings).select().as_list()

    print(checklist)
    
    for sight in sightings: 
        checklist_data = db(db.checklist.SAMPLING_EVENT_IDENTIFIER == sight.SAMPLING_EVENT_IDENTIFIER).select().first() # all Sightings match to a single sampling event in Checklists
        if not location_data: # if empty, populate with first item
            location_data.append({
                'species': sight.COMMON_NAME,
                'day': [checklist_data.DATE], #list of dates
                'count': [sight.OBSERVATION_COUNT] #list of counts, index aligned with the dates
            })
        else:
            for check_location_data in location_data:
                if check_location_data['species'] == sight.COMMON_NAME: # have seen the bird before
                    # 
                    if checklist_data.DATE in check_location_data['day']: 
                        # add up count for this day
                        get_index = check_location_data['day'].index(checklist_data.DATE) # index of the existing day
                        check_location_data['count'][get_index] += sight.OBSERVATION_COUNT
                        break
                    else:
                        # append day and count
                        check_location_data['day'].append(checklist_data.DATE)
                        check_location_data['count'].append(sight.OBSERVATION_COUNT)
                        break

    return dict(location_data=location_data)