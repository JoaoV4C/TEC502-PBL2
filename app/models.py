from app.server import db 

class Passager(db.Model):
    __tablename__ = 'passager'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    ticket_ids = db.Column(db.PickleType, nullable=False, default=[])

    def __init__(self, name, cpf, email):
        self.name = name
        self.cpf = cpf
        self.ticket_ids = []

    def __repr__(self):
        return f'<Passager {self.name}>'

class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    origin = db.Column(db.String(80), nullable=False)
    destination = db.Column(db.String(80), nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Flight {self.id}>'