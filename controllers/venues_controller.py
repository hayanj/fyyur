from models import Artist, Venue, db
from sqlalchemy import asc
from flask import (
   render_template,
   request,
   flash,
   redirect,
   url_for,
   Blueprint
)
from datetime import datetime
from forms import VenueForm
import sys
import json

# Flask uses a concept of blueprints for making application components and supporting common patterns within an application or across applications.
venues_route = Blueprint('venues', __name__)

#  Routes
#  ----------------------------------------------------------------

@venues_route.route('')
def venues():
  cities=Venue.query.with_entities(Venue.city, Venue.state).distinct().all() #with entites used here to get a tuple of city and state
  all_venues = []
  for city in cities:
    data= Venue.query.filter_by(city=city.city).filter_by(state=city.state).all()
    venues_list = [] # a list to store all venues per city with formatted json
    for d in data:
        venues_list.append({
            "id": d.id,
            "name": d.name,
            "num_upcoming_shows": len(d.shows)
        })
    all_venues.append({
                "city": city.city,
                "state": city.state,
                "venues": venues_list
            })
  print (all_venues)
  return render_template('pages/venues.html', areas=all_venues)


@venues_route.route('/search', methods=['POST'])
def search_venues():
  query = request.form.get('search_term')
  query = "%{}%".format(query)
  venues = Venue.query.filter(Venue.name.ilike('%' + query + '%') | Venue.city.ilike('%' + query + '%') | Venue.state.ilike('%' + query + '%')).all()
  data = []
  for venue in venues:
     data.append({
        "id":venue.id,
        "name":venue.name,
        "num_upcoming_shows":len(venue.shows)
     })
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@venues_route.route('/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.get(venue_id)
  past_shows = []
  upcoming_shows = []
  for show in venue.shows:
     data={
        "id": show.id,
        "artist_id":show.artist_id,
        "artist_name": show.artist.name,
        "venue_id":show.venue_id,
        "artist_image_link": show.artist.image_link,
        "venue_image_link": show.venue.image_link,
        "start_time":show.start_time.strftime('%Y-%m-%d %H:%M:%S')
     }
     if datetime.now() > show.start_time:
            past_shows.append(data)
     else:
            upcoming_shows.append(data)
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows": upcoming_shows,
    "upcoming_shows_count": len(upcoming_shows)
    }
  return render_template('pages/show_venue.html', venue=data)


@venues_route.route('/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@venues_route.route('/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    genres = request.form.getlist('genres')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    facebook_link = request.form.get('facebook_link')
    website = request.form.get('website_link')
    seeking_talent = bool(request.form.get('seeking_talent'))
    seeking_description = request.form.get('seeking_description')
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone,
                    genres=genres,facebook_link=facebook_link, image_link=image_link,
                    website=website, seeking_talent=seeking_talent, seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
  except:
     error = True
     db.session.rollback()
     print(sys.exc_info())
  finally:
     db.session.close()
  if (not error):
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  return render_template('pages/home.html')


@venues_route.route('/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # endpoint for taking a venue_id, and using SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
        venue = Venue.query.get(venue_id)
        for show in venue.shows:
            db.session.delete(show)
            db.session.commit()
        db.session.delete(venue)
        db.session.commit()
    except:
       error = True
       db.session.rollback()
    finally:
       db.session.close()
    if (not error):
    # on successful delete, flash success
        flash('Venue was successfully deleted!')
    else:
        flash('An error occurred. Venue could not be deleted.')
    return redirect(url_for('index'))


@venues_route.route('/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter_by(id=venue_id).first()
  form.seeking_talent.default = venue.seeking_talent
  form.process()
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.website_link.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.seeking_description.data = venue.seeking_description
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@venues_route.route('/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  venue = Venue.query.get(venue_id)
  try:
    venue.name = request.form.get('name')        
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.genres = request.form.getlist('genres')
    venue.phone = request.form.get('phone')
    venue.image_link = request.form.get('image_link')
    venue.facebook_link = request.form.get('facebook_link')
    venue.website = request.form.get('website_link')
    venue.seeking_talent = bool(request.form.get('seeking_talent'))
    venue.seeking_description = request.form.get('seeking_description')
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close() 
  if error:
    flash('An error occurred.')
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return redirect(url_for('venues.show_venue', venue_id=venue_id))
