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

@action('checklist')
@action.uses('checklist.html', db, auth.user, url_signer)
def checklist():
    if not auth.curren_user:
        redirect(URL('auth/login'))
    return dict(
        checklist_data_url = URL('checklist_data'),
        my_checklist_url = URL('my_checklist'),
        update_sightings_url = URL('update_sightings')
    )

@action('checklist_data', method="GET")
@action.uses(db,auth)
def checklist_data():
    species_sightings = db(db.sightings).select(
        db.sightings.COMMON_NAME,
        db.sightings.OBSERVATION_COUNT.sum(),
        groupby=db.sightings.COMMON_NAME
    ).as_list()
    return dict(checklist_data=species_sightings)

@action('my_checklists')
@action.uses('my_checklists.html', db, auth.user, session)
def my_checklists():
    drawn_cordinates = session.get('drawn_coordinates', [])
    return dict(
        load_checklists_url=URL('load_checklists'),
        delete_checklists_url=URL('delete_checklists'),
        edit_checklists_url=URL('edit_checklists'),
        drawn_cordinates = json.dumps(drawn_cordinates),
    )

@action('load_checklists')
@action.uses(db,auth.user)
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
        drawn_coordinates = json.dumps(drawn_coordinates)
    )

@action('submit_checklist', method = 'POST')
@action.uses(db, auth.user, url_signer)
def submit_checklist():
    if not auth.current_user:
        redirect(URL('auth/login)'))
    species_name = request.forms.get('species_name')
    latitude = float(request.forms.get('latitude'))
    longitude = float(request.forms.get('longitude'))
    observation_date = request.form.get('observation_date')
    time_observations_started = request.forms.get('time_observations_started')
    duration_minutes = float(request.forms.get('duration_minutes'))

    observer_id = get_user_email()

    sighting = db(db.sightings.COMMON_NAME == species_name).select().first()
    if not sighting:
        return dict(message="Sighting for the given species not found")
    
    sampling_event_identifier = sighting.SAMPLING_EVENT_IDENTIFIER

    db.checklist.inser(
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

@action('edit_checklist/<checklist_id:int>', method=['GET','POST'])
@action.uses(db,auth.user,url_signer)
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
            SAMPLING_EVENT_IDENTIFIER = request.forms.get('sampling_event_identifier'),
            LATITUDE=float(request.forms.get('latitude')),
            LONGITUDE=float(request.forms.get('longitude')),
            OBSERVATION_DATE=request.forms.get('observation_date'),
            TIME_OBSERVATIONS_STARTED=request.gorms.get('time_observations_started'),
            OBSERVER_ID=get_user_email(),
            DURATION_MINUTES=float(request.forms.get('duration_minutes'))
        )
        redirect(URL('my_checklists'))