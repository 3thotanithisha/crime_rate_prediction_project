# init_db.py
from app import db, CrimeData

# ... (sample data)
def initialize_data():
    for data in sample_data:
        crime_data = CrimeData(**data)
        db.session.add(crime_data)
    db.session.commit()

if __name__ == '__main__':
    initialize_data()
