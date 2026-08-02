from extensions import db

class Province(db.Model):
  __tablename__ = 'provinces'
  ProvinceID = db.Column(db.Integer, primary_key=True)
  Code = db.Column(db.String(50), unique=True, nullable=False)
  Name = db.Column(db.String(100), nullable=False)

  # Relationship
  districts = db.relationship(
      'District', backref='province', lazy=True, cascade='all, delete-orphan'
  )

class District(db.Model):
  __tablename__ = 'districts'
  DistrictID = db.Column(db.Integer, primary_key=True)
  ProvinceID = db.Column(
      db.Integer, db.ForeignKey('provinces.ProvinceID'), nullable=False
  )
  Code = db.Column(db.String(50), unique=True, nullable=False)
  Name = db.Column(db.String(100), nullable=False)

  # Relationship
  communes = db.relationship(
      'Commune', backref='district', lazy=True, cascade='all, delete-orphan'
  )

class Commune(db.Model):
  __tablename__ = 'communes'
  CommuneID = db.Column(db.Integer, primary_key=True)
  DistrictID = db.Column(
      db.Integer, db.ForeignKey('districts.DistrictID'), nullable=False
  )
  Code = db.Column(db.String(50), unique=True, nullable=False)
  Name = db.Column(db.String(100), nullable=False)

  # Relationship
  villages = db.relationship(
      'Village', backref='commune', lazy=True, cascade='all, delete-orphan'
  )

class Village(db.Model):
  __tablename__ = 'villages'
  VillageID = db.Column(db.Integer, primary_key=True)
  CommuneID = db.Column(
      db.Integer, db.ForeignKey('communes.CommuneID'), nullable=False
  )
  Code = db.Column(db.String(50), unique=True, nullable=False)
  Name = db.Column(db.String(100), nullable=False)

class Address(db.Model):
  __tablename__ = 'addresses'
  AddressID = db.Column(db.Integer, primary_key=True)
  Home = db.Column(db.String(50))
  Street = db.Column(db.String(100))
  ProvinceID = db.Column(db.Integer, db.ForeignKey('provinces.ProvinceID'))
  DistrictID = db.Column(db.Integer, db.ForeignKey('districts.DistrictID'))
  CommuneID = db.Column(db.Integer, db.ForeignKey('communes.CommuneID'))
  VillageID = db.Column(db.Integer, db.ForeignKey('villages.VillageID'))

  # Relationships
  province = db.relationship('Province')
  district = db.relationship('District')
  commune = db.relationship('Commune')
  village = db.relationship('Village')