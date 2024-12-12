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
import json
import csv

url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', db, auth.user, url_signer)
def index():
    return dict(
        my_callback_url = URL('my_callback', signer=url_signer),
        get_user_statistics_url = URL('get_user_statistics'),
        load_user_statistics_url = URL('load_user_statistics'),
        search_url = URL('search'),
        get_bird_sightings_url = URL('get_bird_sightings'),
        save_coords_url = URL('save_coords'),
    )

@action('my_callback')
    
@action.uses(db, auth)
def my_callback():
    if db(db.species).isempty():
        with open('species.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                db.species.insert(COMMON_NAME=row[0])
    return dict(my_value=1)

@action('user_statistics')
@action.uses('user_statistics.html', db, auth.user, url_signer)
def user_statistics():
    return dict(
        load_user_statistics_url = URL('load_user_statistics'),
        search_url = URL('search'),
        observation_dates_url = URL('observation_dates')
    )
    
@action('load_user_statistics')
@action.uses(db, auth.user, url_signer)
def get_user_statistics():
    common_names = db(db.sightings).select(db.sightings.COMMON_NAME, distinct=True).as_list()
    return dict(common_names=common_names)

@action('my_birds')
@action.uses('my_birds.html', db, auth.user, url_signer)
def my_birds():
    user_email = get_user_email()
    if not user_email:
        abort(403, "User not logged in")

    # Fetch checklist data for the logged-in user
    checklists = db(db.checklist.OBSERVER_ID == user_email).select().as_list()

    return dict(
        checklists=checklists,  # Pass the checklist data to the frontend
    )

@action('get_bird_sightings', method=['POST'])
@action.uses(db, auth, url_signer)
def get_bird_sightings():
    north = request.json.get('north')
    south = request.json.get('south')
    east = request.json.get('east')
    west = request.json.get('west')

    events_in_bounds = db(
        (db.checklist.LATITUDE <= north) & 
        (db.checklist.LATITUDE >= south) &
        (db.checklist.LONGITUDE <= east) &
        (db.checklist.LONGITUDE >= west)
    ).select(db.checklist.SAMPLING_EVENT_IDENTIFIER)

    event_ids = [event.SAMPLING_EVENT_IDENTIFIER for event in events_in_bounds]
    sightings = db(db.sightings.SAMPLING_EVENT_IDENTIFIER.belongs(event_ids)).select()

    sightings_list = []
    for sighting in sightings:
        event_location = db(db.checklist.SAMPLING_EVENT_IDENTIFIER == sighting.SAMPLING_EVENT_IDENTIFIER).select().first()
        if event_location:
            try:
                intensity = int(sighting.OBSERVATION_COUNT)
            except ValueError:
                intensity = 0
            sightings_list.append({
                'species': sighting.COMMON_NAME,
                'lat': event_location.LATITUDE,
                'lon': event_location.LONGITUDE,
                'obs_id': event_location.OBSERVER_ID,
                'date': event_location.OBSERVATION_DATE,
                'intensity': intensity
            })
    return dict(sightings=sightings_list)

@action('save_coords', method='POST')
@action.uses(db, auth, url_signer, session)
def save_coords():
    data = request.json
    drawing_coords = data.get('drawing_coords', [])
    if not drawing_coords:
        session['drawn_coordinates'] = []
    else:
        session['drawn_coordinates'] = drawing_coords
    return 'Coordinates saved successfully.'

@action('update_sightings', method=["POST"])
@action.uses(db, auth, url_signer)
def update_sightings():
    common_name = request.json.get('common_name')
    new_sightings = request.json.get('new_sightings')

    if common_name is None or new_sightings is None:
        abort(400, "Invalid request")

    sightings = db(db.sightings.COMMON_NAME == common_name).select().first()

    if sightings:
        sightings.update_record(OBSERVATION_COUNT=str(int(sightings.OBSERVATION_COUNT) + new_sightings))
        total_sightings = sightings.OBSERVATION_COUNT
    else:
        total_sightings = new_sightings
        db.sightings.insert(COMMON_NAME=common_name, OBSERVATION_COUNT=total_sightings)

    return dict(total_sightings=total_sightings)

@action('search', method=["POST"])
@action.uses(db, auth.user, url_signer)
def search():
    data = request.json
    q = data.get("params", {}).get("q")
    option = data.get("params", {}).get("option")

    query = (db.sightings.OBSERVATION_COUNT > 0)

    # This is the search condition
    if q:
        query &= (db.sightings.COMMON_NAME.contains(q))

    if option in ["recent", "old"]:
        query &= (db.sightings.SAMPLING_EVENT_IDENTIFIER == db.checklist.SAMPLING_EVENT_IDENTIFIER)
        if option == "recent":
            common_names = db(query).select(db.sightings.COMMON_NAME, orderby=~db.checklist.OBSERVATION_DATE, distinct=True).as_list()
        else:
            common_names = db(query).select(db.sightings.COMMON_NAME, orderby=db.checklist.OBSERVATION_DATE, distinct=True).as_list()
    else:
        common_names = db(query).select(db.sightings.COMMON_NAME, distinct=True).as_list()

    return dict(common_names=common_names)

@action('observation_dates', method=["POST"])
@action.uses(db, auth.user, url_signer)
def observation_date():
    data = request.json
    common_name = data.get("common_name")
    observation_date = data.get("observation_date")
    if not common_name:
        return dict(observation_dates=[], most_recent_sighting=None)

    query = (db.sightings.COMMON_NAME == common_name) & \
            (db.sightings.SAMPLING_EVENT_IDENTIFIER == db.checklist.SAMPLING_EVENT_IDENTIFIER)

    if observation_date:
        query &= (db.checklist.OBSERVATION_DATE == observation_date)
        most_recent_sighting = db(query).select(
            db.checklist.LATITUDE,
            db.checklist.LONGITUDE,
            orderby=~db.checklist.OBSERVATION_DATE,
            limitby=(0, 1)
        ).first()
    else:
        most_recent_sighting = db(query).select(
            db.checklist.LATITUDE,
            db.checklist.LONGITUDE,
            orderby=~db.checklist.OBSERVATION_DATE,
            limitby=(0, 1)
        ).first()

    if most_recent_sighting:
        most_recent_sighting = dict(
            LATITUDE=most_recent_sighting.LATITUDE,
            LONGITUDE=most_recent_sighting.LONGITUDE
        )

    observation_dates = db(query).select(db.checklist.OBSERVATION_DATE, distinct=True).as_list()

    return dict(observation_dates=observation_dates, most_recent_sighting=most_recent_sighting)

@action('checklist')
@action.uses('checklist.html', db, auth.user, url_signer)
def checklist():
    if not auth.current_user:
        redirect(URL('auth/login'))
    return dict(
        checklist_data_url=URL('checklist_data'),
        my_checklist_url=URL('my_checklists'),
        update_sightings_url=URL('update_sightings')
    )

@action('checklist_data', method="GET")
@action.uses(db, auth)
def checklist_data():
    species_sightings = db(db.sightings).select(
        db.sightings.COMMON_NAME.with_alias('common_name'),
        db.sightings.OBSERVATION_COUNT.sum().with_alias('total_sightings'),
        groupby=db.sightings.COMMON_NAME
    ).as_list()
    return dict(checklist_data=species_sightings)

@action('my_checklists')
@action.uses('my_checklists.html', db, auth.user, session)
def my_checklists():
    drawn_coordinates = session.get('drawn_coordinates', [])
    return dict(
        load_checklists_url=URL('load_checklists'),
        delete_checklists_url=URL('delete_checklists'),
        edit_checklists_url=URL('edit_checklists'),
        drawn_coordinates=json.dumps(drawn_coordinates),
    )

@action('load_checklists')
@action.uses(db, auth.user)
def load_checklists():
    user_email = get_user_email()
    checklists = db(db.checklist.OBSERVER_ID == user_email).select().as_list()
    return dict(checklists=checklists)

@action('add_checklist')
@action.uses('add_checklist.html', db, auth.user, url_signer, session)
def add_checklist():
    drawn_coordinates = session.get('drawn_coordinates')
    if not auth.current_user:
        redirect(URL('auth/login'))
    return dict(
        submit_checklist_url=URL('submit_checklist'),
        drawn_coordinates=json.dumps(drawn_coordinates)
    )

@action('submit_checklist', method='POST')
@action.uses(db, auth.user, url_signer)
def submit_checklist():
    if not auth.current_user:
        redirect(URL('auth/login'))
    species_name = request.forms.get('species_name')
    latitude = float(request.forms.get('latitude'))
    longitude = float(request.forms.get('longitude'))
    observation_date = request.forms.get('observation_date')
    time_observations_started = request.forms.get('time_observations_started')
    duration_minutes = float(request.forms.get('duration_minutes'))

    observer_id = get_user_email()

    sighting = db(db.sightings.COMMON_NAME == species_name).select().first()
    if not sighting:
        return dict(message="Sighting for the given species not found")
    
    sampling_event_identifier = sighting.SAMPLING_EVENT_IDENTIFIER

    db.checklist.insert(
        SAMPLING_EVENT_IDENTIFIER=sampling_event_identifier,
        LATITUDE=latitude,
        LONGITUDE=longitude,
        OBSERVATION_DATE=observation_date,
        TIME_OBSERVATIONS_STARTED=time_observations_started,
        OBSERVER_ID=observer_id,
        DURATION_MINUTES=duration_minutes
    )
    
    redirect(URL('my_checklists'))

@action('delete_checklist/<checklist_id:int>', method='DELETE')
@action.uses(db, auth.user, url_signer)
def delete_checklist(checklist_id):
    user_email = get_user_email()
    checklist = db(db.checklist.id == checklist_id).select().first()

    if not checklist:
        return dict(message="Checklist not found")
    if checklist.OBSERVER_ID != user_email:
        return dict(message="User not authorized to delete checklist")
    
    db(db.checklist.id == checklist_id).delete()

    return dict(message="Checklist Deleted")

@action('edit_checklist/<checklist_id:int>', method=['GET', 'POST'])
@action.uses(db, auth.user, url_signer)
def edit_checklist(checklist_id):
    checklist = db.checklist[checklist_id]
    if not checklist:
        redirect(URL('my_checklists'))
    if request.method == 'GET':
        return dict(
            checklist=checklist,
            checklist_id=checklist_id
        )
    if request.method == 'POST':
        checklist.update_record(
            SAMPLING_EVENT_IDENTIFIER=request.forms.get('sampling_event_identifier'),
            LATITUDE=float(request.forms.get('latitude')),
            LONGITUDE=float(request.forms.get('longitude')),
            OBSERVATION_DATE=request.forms.get('observation_date'),
            TIME_OBSERVATIONS_STARTED=request.forms.get('time_observations_started'),
            OBSERVER_ID=get_user_email(),
            DURATION_MINUTES=float(request.forms.get('duration_minutes'))
        )
        redirect(URL('my_checklists'))


@action('location')
@action.uses('location.html', db, auth, url_signer)
def location():
    return dict(
        get_location_data_url = URL('get_location_data'),
    )

@action('get_location_data')
@action.uses(db, auth, url_signer, session)
def get_location_data():

    total_sightings = 0
    total_checklists = 0
    contributor_list = [] # [{'name': name, 'contributions': 1}]
    location_data = [] # [{'species': 'bird', 'day': ['2021-02-03'], 'count': [2]}]

    # full lists
    checklist = db(db.checklist).select().as_list() 
    sightings = db(db.sightings).select().as_list() 

    # want to cut down full lists to within a region. LATITUDE and LONGITUDE in checklist.
    #drawn_coordinates = session.get('drawn_coordinates')
    #print(drawn_coordinates)

    for sight in sightings: 
        checklist_data = db(db.checklist.SAMPLING_EVENT_IDENTIFIER == sight['SAMPLING_EVENT_IDENTIFIER']).select().first()
        if sight['SAMPLING_EVENT_IDENTIFIER'] == checklist_data.SAMPLING_EVENT_IDENTIFIER: # this sighting has location and time data in checklists
            if not location_data: # if empty, populate with first item
                if sight['OBSERVATION_COUNT'] != 'X': # WHEN THE CSV FILE READ IN DATA "X", SKIP
                    location_data.append({
                        'species': sight['COMMON_NAME'],
                        'day': [checklist_data.OBSERVATION_DATE], #list of dates
                        'count': [int(sight['OBSERVATION_COUNT'])] #list of counts, index aligned with the dates
                    })
                    total_sightings += int(sight['OBSERVATION_COUNT'])
            else: # second item or later
                bird_found = False
                for check_location_data in location_data: #loop to search if bird already is accounted for
                    if check_location_data['species'] == sight['COMMON_NAME']: # have seen the bird before  
                        if checklist_data.OBSERVATION_DATE in check_location_data['day']: 
                            # add up count (bird already exists, day already exists)
                            if sight['OBSERVATION_COUNT'] != 'X': # WHEN THE CSV FILE READ IN DATA "X", SKIP
                                get_index = check_location_data['day'].index(checklist_data.OBSERVATION_DATE) # index of the existing day
                                check_location_data['count'][get_index] += int(sight['OBSERVATION_COUNT'])
                                total_sightings += int(sight['OBSERVATION_COUNT'])
                                bird_found = True
                            break
                        else:
                            # append day and count (bird already exists, new day)
                            if sight['OBSERVATION_COUNT'] != 'X': # WHEN THE CSV FILE READ IN DATA "X", SKIP
                                check_location_data['day'].append(checklist_data.OBSERVATION_DATE)
                                check_location_data['count'].append(int(sight['OBSERVATION_COUNT']))
                                total_sightings += int(sight['OBSERVATION_COUNT'])
                                bird_found = True
                            break
                if not bird_found: # add a new bird entry
                    if sight['OBSERVATION_COUNT'] != 'X': # WHEN THE CSV FILE READ IN DATA "X", SKIP
                        location_data.append({
                            'species': sight['COMMON_NAME'],
                            'day': [checklist_data.OBSERVATION_DATE], #list of dates
                            'count': [int(sight['OBSERVATION_COUNT'])] #list of counts, index aligned with the dates
                        })
                        total_sightings += int(sight['OBSERVATION_COUNT'])
            
    # get the observers from database and put into a list with number of contributions
    for check in checklist:
        if not contributor_list:
            contributor_list.append({'name': check['OBSERVER_ID'], 'contributions': 1})
            total_checklists += 1
        else:
            contributor_found = False
            for contributor in contributor_list:
                if check['OBSERVER_ID'] in contributor['name']:
                    contributor_found = True
                    contributor['contributions'] += 1
                    total_checklists += 1
                    break
            if not contributor_found:
                contributor_list.append({'name': check['OBSERVER_ID'], 'contributions': 1})
                total_checklists += 1
    if contributor_list: #sort the list by number
        temp_list = sorted(contributor_list, key=lambda x: x['contributions'], reverse=True) #sort list so top contributors appear first
        contributor_list = temp_list            

    return dict(location_data=location_data, contributor_list=contributor_list, total_sightings=total_sightings, total_checklists=total_checklists)

