#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='venue', lazy=True)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='artist', lazy=True)

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'),nullable=False)
    start_time = db.Column(db.DateTime(), nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
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

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  query = request.form.get('search_term')
  query = "%{}%".format(query)
  venues = Venue.query.filter(Venue.name.ilike('%' + query + '%')).all()
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

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
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

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
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

@app.route('/venues/<venue_id>', methods=['DELETE'])
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
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.order_by('id').all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    query = request.form.get('search_term')
    query = "%{}%".format(query)
    artists = Artist.query.filter(Artist.name.ilike('%' + query + '%')).all()
    data = []
    for artist in artists:
        data.append({
            "id":artist.id,
            "name":artist.name,
            "num_upcoming_shows":len(artist.shows)
        })
    
    response={
        "count": len(data),
        "data": data
    }

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

    artist = Artist.query.get(artist_id)
    past_shows = []
    upcoming_shows = []
    for show in artist.shows:
        show_data = {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        if datetime.now() > show.start_time:
            past_shows.append(show_data)
        else:
            upcoming_shows.append(show_data)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "image_link": artist.image_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "past_shows": past_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows": upcoming_shows,
        "upcoming_shows_count": len(upcoming_shows)
    }  

    print(data)
    return render_template('pages/show_artist.html', artist=data)

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  # endpoint for taking a venue_id, and using SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
        artist = Artist.query.get(artist_id)
        for show in artist.shows:
            db.session.delete(show)
            db.session.commit()

        db.session.delete(artist)
        db.session.commit()
    except:
       error = True
       db.session.rollback()
    finally:
       db.session.close()
    
    if (not error):
    # on successful delete, flash success
        flash('Artist was successfully deleted!')
    else:
        flash('An error occurred. Artist could not be deleted.')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for('index'))

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    form.seeking_venue.default = artist.seeking_venue
    form.process()

    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.genres.data = artist.genres
    form.phone.data = artist.phone
    form.website_link.data = artist.website
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.seeking_description.data = artist.seeking_description
  # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.get(artist_id)
    error = False
    try:
        artist.name = request.form.get('name')
        artist.city = request.form.get('city')
        artist.state = request.form.get('state')
        artist.genres = request.form.getlist('genres')
        artist.phone = request.form.get('phone')
        artist.image_link = request.form.get('image_link')
        artist.facebook_link = request.form.get('facebook_link')
        artist.website = request.form.get('website_link')
        artist.seeking_venue = bool(request.form.get('seeking_venue'))
        artist.seeking_description = request.form.get('seeking_description')

        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    # on successful db insert, flash success
    if error:
        flash('An error occurred.')
    if not error:
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
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

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
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

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
    error = False
    try:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        genres = request.form.getlist('genres')
        phone = request.form.get('phone')
        image_link = request.form.get('image_link')
        facebook_link = request.form.get('facebook_link')
        website = request.form.get('website_link')
        seeking_venue = bool(request.form.get('seeking_venue'))
        seeking_description = request.form.get('seeking_description')

        artist = Artist(name=name, city=city, state=state, genres=genres, phone=phone, image_link=image_link, facebook_link=facebook_link,
                        website=website, seeking_venue=seeking_venue, seeking_description=seeking_description)
        db.session.add(artist)
        db.session.commit()
    except:
       error = True
       db.session.rollback()
       print(sys.exc_info())
    finally:
       db.session.close()
       
    
  # on successful db insert, flash success
    if not error:
       flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
       flash('Artist ' + request.form['name'] + ' could not be listed.!')

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  shows = Show.query.all()
  data = []
  for show in shows:
    data.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time":show.start_time.strftime('%Y-%m-%d %H:%M:%S')
     })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
    error = False
    try:
        artist_id = request.form.get('artist_id')
        venue_id = request.form.get('venue_id')
        start_time = request.form.get('start_time')
        show = Show(venue_id=venue_id, artist_id=artist_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

  # on successful db insert, flash success
    if not error:
        flash('Show was successfully listed!')
  # on unsuccessful db insert, flash an error instead.
    else:
        flash('An error occurred. Show could not be listed.')
    return render_template('pages/home.html')

@app.route('/shows/search', methods=['POST'])
def search_shows():
  # search for artist and venue
  query = request.form.get('search_term')
  query = "%{}%".format(query)
  shows = Show.query.join(Artist).join(Venue).filter((Artist.name.ilike('%' + query + '%')) | (Venue.name.ilike('%' + query + '%'))).all()
  data = []
  for show in shows:
    data.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time":show.start_time.strftime('%Y-%m-%d %H:%M:%S')
     })
    
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/show.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/shows/<show_id>', methods=['DELETE'])
def delete_show(show_id):
  try:
    show = Show.query.get(id=show_id)
    db.session.delete(show)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''