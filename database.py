from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    symbol = db.Column(db.String(20))
    type = db.Column(db.String(10))  # BUY / SELL

    entry_price = db.Column(db.Float)
    exit_price = db.Column(db.Float)

    quantity = db.Column(db.Float)
    profit = db.Column(db.Float)

    status = db.Column(db.String(10))  # OPEN / CLOSED

    timestamp = db.Column(db.DateTime)
    
    