from database import db

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
    # albums = db.relationship('Album', backref='artist', lazy=True)

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'),nullable=False)
    start_time = db.Column(db.DateTime(), nullable=False)

#TODO add album to artist
# class Album(db.Model):
#     __tablename__ = 'Album'

#     id = db.Column(db.Integer, primary_key=True)
#     artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),nullable=False)
#     name = db.Column(db.String)
#     published_date = db.Column(db.DateTime(), nullable=False)
#     songs = db.Column(db.ARRAY(db.String))