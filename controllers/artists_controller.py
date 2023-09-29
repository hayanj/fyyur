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
from forms import ArtistForm
import sys
import json

# Flask uses a concept of blueprints for making application components and supporting common patterns within an application or across applications.
artists_route = Blueprint('artists', __name__)


#  Routes
#  ----------------------------------------------------------------

@artists_route.route('')
def artists():
  artists = Artist.query.order_by('id').all()
  return render_template('pages/artists.html', artists=artists)


@artists_route.route('/search', methods=['POST'])
def search_artists():
    #get the search term from the form
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


@artists_route.route('/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
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


@artists_route.route('/<artist_id>', methods=['DELETE'])
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
    return redirect(url_for('index'))


@artists_route.route('/<int:artist_id>/edit', methods=['GET'])
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
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@artists_route.route('/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # update existing artist record with ID <artist_id> using the new attributes
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
    if (not error):
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
    else:
        flash('Artist ' + request.form['name'] + ' could not be updated.')
    return redirect(url_for('artists.show_artist', artist_id=artist_id))


@artists_route.route('/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


@artists_route.route('/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
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
    if (not error):
       flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
       flash('Artist ' + request.form['name'] + ' could not be listed.')
    return render_template('pages/home.html')