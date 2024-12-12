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
@action.uses('index.html', db, auth, url_signer)
def index():
    return dict(
        my_callback_url=URL('my_callback', signer=url_signer),
        get_bird_sightings_url=URL('get_bird_sightings'),
        save_coords_url=URL('save_coords'),
    )

@action('my_callback')
@action.uses(db, auth)
def my_callback():
    if db(db.checklist).isempty():
        with open('checklist.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                db.sightings.insert(COMMON_NAME=row[0])
    return dict(my_value=3)

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
@action.uses(db, auth, url_signer)
def get_location_data():

    total_sightings = 0
    total_checklists = 0
    contributor_list = [] # [{'name': name, 'contributions': 1}]
    location_data = [] # [{'species': 'bird', 'day': ['2021-02-03'], 'count': [2]}]

    #full lists. get coordinates somehow. create a new list of checklist
    checklist = db(db.checklist).select().as_list() 
    sightings = db(db.sightings).select().as_list() 

    for sight in sightings: 
        checklist_data = db(db.checklist.SAMPLING_EVENT_IDENTIFIER == sight.SAMPLING_EVENT_IDENTIFIER).select().first()
        #if sight.SAMPLING_EVENT_IDENTIFIER == checklist_data.SAMPLING_EVENT_IDENTIFIER: #

        if not location_data: # if empty, populate with first item
            location_data.append({
                'species': sight.COMMON_NAME,
                'day': [checklist_data.DATE], #list of dates
                'count': [sight.OBSERVATION_COUNT] #list of counts, index aligned with the dates
            })
            total_sightings += sight.OBSERVATION_COUNT
        else:
            for check_location_data in location_data:
                if check_location_data['species'] == sight.COMMON_NAME: # have seen the bird before
                    
                    if checklist_data.DATE in check_location_data['day']: 
                        # add up count for this day
                        get_index = check_location_data['day'].index(checklist_data.DATE) # index of the existing day
                        check_location_data['count'][get_index] += sight.OBSERVATION_COUNT
                        total_sightings += sight.OBSERVATION_COUNT
                        break
                    else:
                        # append day and count
                        check_location_data['day'].append(checklist_data.DATE)
                        check_location_data['count'].append(sight.OBSERVATION_COUNT)
                        total_sightings += sight.OBSERVATION_COUNT
                        break

    # get the observers from database and put into a list with number of contributions
    for check in checklist:
        if not contributor_list:
            contributor_list.append({'name': check.OBSERVER_ID, 'contributions': 1})
            total_checklists += 1
        else:
            contributor_found = False
            for contributor in contributor_list:
                if check.OBSERVER_ID in contributor['name']:
                    contributor_found = True
                    contributor['contributions'] += 1
                    total_checklists += 1
                    break
            if not contributor_found:
                contributor_list.append({'name': check.OBSERVER_ID, 'contributions': 1})
                total_checklists += 1
    if contributor_list:
        temp_list = sorted(contributor_list, key=lambda x: x['name'], reverse=True) #sort list so top contributors appear first
        contributor_list = temp_list

    return dict(location_data=location_data, contributor_list=contributor_list, total_sightings=total_sightings, total_checklists=total_checklists)

# Testing.