from models import Artist, Venue, Show, db
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
from forms import ShowForm
import sys
import json

shows_route = Blueprint('show', __name__)

#  Routes
#  ----------------------------------------------------------------

@shows_route.route('')
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


@shows_route.route('/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


@shows_route.route('/create', methods=['POST'])
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
    if (not error):
        flash('Show was successfully listed!')
  # on unsuccessful db insert, flash an error instead.
    else:
        flash('An error occurred. Show could not be listed.')
    return render_template('pages/home.html')


@shows_route.route('/search', methods=['POST'])
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


@shows_route.route('/<show_id>', methods=['DELETE'])
def delete_show(show_id):
  error = False
  try:
    show = Show.query.get(id=show_id)
    db.session.delete(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if (not error):
    # on successful delete, flash success
    flash('Show was successfully deleted!')
  else:
    flash('An error occurred. Show could not be deleted.')
  return redirect(url_for('index'))