"""
Database seeding script for Souk'Jam application
Creates diverse sample data for testing with Tunisian locations and varied pricing
"""
from app import create_app
from app.extensions import db
from app.models import User, Instrument, JamRequest, Rental
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random
import os
import glob

def create_diverse_tunisian_data():
    """Create diverse sample data for testing with Tunisian locations and varied pricing"""

    app = create_app()
    with app.app_context():
        print("Creating diverse Tunisian sample data...")

        # Diverse Tunisian locations with coordinates
        tunisian_locations = [
            {'name': 'Tunis Centre', 'lat': 36.8065, 'lng': 10.1815},
            {'name': 'Sidi Bou Said', 'lat': 36.8708, 'lng': 10.3417},
            {'name': 'La Marsa', 'lat': 36.8762, 'lng': 10.3247},
            {'name': 'Carthage', 'lat': 36.8529, 'lng': 10.3233},
            {'name': 'Ariana', 'lat': 36.8625, 'lng': 10.1939},
            {'name': 'Manouba', 'lat': 36.8097, 'lng': 10.0967},
            {'name': 'Bizerte', 'lat': 37.2744, 'lng': 9.8739},
            {'name': 'Sfax', 'lat': 34.7398, 'lng': 10.7600},
            {'name': 'Sousse', 'lat': 35.8256, 'lng': 10.6369},
            {'name': 'Monastir', 'lat': 35.7780, 'lng': 10.8262},
            {'name': 'Nabeul', 'lat': 36.4513, 'lng': 10.7357},
            {'name': 'Hammamet', 'lat': 36.4000, 'lng': 10.6167},
            {'name': 'Gabès', 'lat': 33.8815, 'lng': 10.0982},
            {'name': 'Kairouan', 'lat': 35.6781, 'lng': 10.0963},
            {'name': 'Mahdia', 'lat': 35.5047, 'lng': 11.0622},
            {'name': 'Tozeur', 'lat': 33.9197, 'lng': 8.1335},
            {'name': 'Tataouine', 'lat': 32.9297, 'lng': 10.4518},
            {'name': 'Djerba', 'lat': 33.8075, 'lng': 10.8451},
            {'name': 'Zarzis', 'lat': 33.5033, 'lng': 11.1122},
            {'name': 'Gafsa', 'lat': 34.4250, 'lng': 8.7842}
        ]

        # Diverse musical genres
        genres = [
            'rock', 'blues', 'jazz', 'pop', 'folk', 'traditional', 'classical',
            'electronic', 'metal', 'fusion', 'reggae', 'hip-hop', 'world', 'arabic'
        ]

        # Instrument types and their typical price ranges
        instrument_types = {
            'electric_guitar': {'min_price': 15, 'max_price': 50},
            'acoustic_guitar': {'min_price': 12, 'max_price': 40},
            'bass_guitar': {'min_price': 18, 'max_price': 45},
            'drums': {'min_price': 25, 'max_price': 60},
            'keyboard': {'min_price': 20, 'max_price': 55},
            'piano': {'min_price': 30, 'max_price': 80},
            'violin': {'min_price': 20, 'max_price': 70},
            'cello': {'min_price': 25, 'max_price': 75},
            'saxophone': {'min_price': 22, 'max_price': 65},
            'trumpet': {'min_price': 15, 'max_price': 40},
            'flute': {'min_price': 10, 'max_price': 35},
            'clarinet': {'min_price': 12, 'max_price': 38},
            'oud': {'min_price': 18, 'max_price': 55},
            'percussion': {'min_price': 8, 'max_price': 30},
            'accordion': {'min_price': 20, 'max_price': 50}
        }

        # Famous instrument brands
        brands = [
            'Fender', 'Gibson', 'Yamaha', 'Ibanez', 'Pearl', 'Roland', 'Korg',
            'Stradivarius', 'Selmer', 'Steinway', 'Casio', 'Boss', 'Marshall',
            'Behringer', 'AKG', 'Shure', 'Taylor', 'Martin', 'PRS', 'ESP'
        ]

        # Sample user data with diverse Tunisian representation
        users_data = []

        # Generate 15 diverse users
        first_names = ['Ahmed', 'Sara', 'Karim', 'Leila', 'Mehdi', 'Amina', 'Houssem',
                      'Rim', 'Youssef', 'Nour', 'Fatma', 'Mohamed', 'Sonia', 'Ali', 'Hana']
        last_names = ['Ben Ali', 'Trabelsi', 'Jelassi', 'Mansour', 'Khemiri', 'Cherif',
                     'Ben Amor', 'Gharbi', 'Saad', 'Hamdi', 'Bouzid', 'Miled', 'Chahed',
                     'Zouari', 'Ben Salem']

        roles = ['jammer', 'owner', 'renter']

        for i in range(15):
            location = random.choice(tunisian_locations)
            role = random.choice(roles)

            # Adjust role distribution (more jammers)
            if random.random() < 0.6:
                role = 'jammer'

            # Select 2-4 random genres
            user_genres = random.sample(genres, random.randint(2, 4))

            # Generate instruments played based on role
            instruments_played = []
            if role == 'jammer':
                # Jammers play 1-3 instruments
                num_instruments = random.randint(1, 3)
                available_types = list(instrument_types.keys())
                selected_types = random.sample(available_types, num_instruments)
                for inst_type in selected_types:
                    instruments_played.append({
                        'instrument_type': inst_type,
                        'skill_level': random.choice(['beginner', 'intermediate', 'advanced', 'expert'])
                    })

            user = {
                'email': f"{first_names[i % len(first_names)].lower()}.{last_names[i % len(last_names)].lower()}{i+1}@example.com",
                'password': 'password123',
                'name': f"{first_names[i % len(first_names)]} {last_names[i % len(last_names)]}",
                'location_name': location['name'],
                'location_lat': location['lat'],
                'location_lng': location['lng'],
                'role': role,
                'genres_enjoyed': user_genres,
                'instruments_played': instruments_played,
                'is_active_for_jam': role == 'jammer' and random.random() < 0.8  # 80% of jammers are active
            }
            users_data.append(user)

        # Create users
        users = []
        for user_data in users_data:
            user = User(
                email=user_data['email'],
                password_hash=generate_password_hash(user_data['password']),
                name=user_data['name'],
                location_name=user_data['location_name'],
                location_lat=user_data['location_lat'],
                location_lng=user_data['location_lng'],
                role=user_data['role'],
                genres_enjoyed=user_data['genres_enjoyed'],
                instruments_played=user_data['instruments_played'],
                is_active_for_jam=user_data['is_active_for_jam']
            )
            db.session.add(user)
            users.append(user)

        db.session.commit()
        print(f"Created {len(users)} diverse users across Tunisia")

        # Generate 12 diverse instruments with varied pricing
        instruments_data = []
        instrument_names = [
            'Electric Guitar', 'Acoustic Guitar', 'Bass Guitar', 'Drum Kit', 'Digital Keyboard',
            'Grand Piano', 'Violin', 'Cello', 'Alto Saxophone', 'Trumpet', 'Flute', 'Clarinet',
            'Traditional Oud', 'Percussion Set', 'Accordion', 'Electric Piano', 'Classical Guitar'
        ]

        # Get owners (users with role 'owner' or some jammers who also own instruments)
        owners = [u for u in users if u.role == 'owner'] + random.sample([u for u in users if u.role == 'jammer'], 3)

        # Get available images from uploads folder
        uploads_path = os.path.join(os.path.dirname(__file__), 'uploads')
        available_images = []
        if os.path.exists(uploads_path):
            # Get all image files and create paths relative to uploads
            for img_file in glob.glob(os.path.join(uploads_path, '*.*')):
                if img_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    filename = os.path.basename(img_file)
                    available_images.append(f"/uploads/{filename}")
        
        # Fallback if no images found - use a default
        if not available_images:
            available_images = ['/uploads/guitar1.jpeg']  # Fallback default

        for i in range(12):
            owner = random.choice(owners)
            inst_type = random.choice(list(instrument_types.keys()))
            price_range = instrument_types[inst_type]
            price = round(random.uniform(price_range['min_price'], price_range['max_price']), 2)

            # Use owner's location or nearby location
            if random.random() < 0.7:  # 70% chance to use owner's location
                location = {'name': owner.location_name, 'lat': owner.location_lat, 'lng': owner.location_lng}
            else:
                location = random.choice(tunisian_locations)

            instrument = {
                'owner_id': owner.id,
                'name': f"{random.choice(brands)} {random.choice(instrument_names)}",
                'brand': random.choice(brands),
                'type': inst_type,
                'description': f"High-quality {inst_type.replace('_', ' ')} in excellent condition, perfect for {random.choice(['professional performances', 'studio recording', 'practice sessions', 'live concerts', 'teaching', 'home use'])}",
                'price_per_day': price,
                'photo_url': random.choice(available_images),
                'location_name': location['name'],
                'location_lat': location['lat'],
                'location_lng': location['lng'],
                'tags': random.sample(['professional', 'vintage', 'new', 'portable', 'acoustic', 'electric', 'handmade'], random.randint(1, 3))
            }
            instruments_data.append(instrument)

        # Create instruments
        instruments = []
        for instrument_data in instruments_data:
            instrument = Instrument(**instrument_data)
            db.session.add(instrument)
            instruments.append(instrument)

        db.session.commit()
        print(f"Created {len(instruments)} instruments with diverse pricing (TND {min([i.price_per_day for i in instruments]):.2f} - {max([i.price_per_day for i in instruments]):.2f} per day)")

        # Generate 10 jam requests between compatible users
        jam_requests_data = []
        jammers = [u for u in users if u.role == 'jammer' and u.is_active_for_jam]

        for i in range(10):
            sender = random.choice(jammers)
            # Find a receiver who is not the sender and shares at least one genre
            potential_receivers = [u for u in jammers if u.id != sender.id and
                                 any(g in u.genres_enjoyed for g in sender.genres_enjoyed)]
            if potential_receivers:
                receiver = random.choice(potential_receivers)
                status = random.choice(['pending', 'accepted', 'accepted', 'pending', 'skipped'])  # More accepted/pending

                jam_request = {
                    'sender_id': sender.id,
                    'receiver_id': receiver.id,
                    'status': status
                }
                jam_requests_data.append(jam_request)

        # Create jam requests
        jam_requests = []
        for request_data in jam_requests_data:
            jam_request = JamRequest(**request_data)
            db.session.add(jam_request)
            jam_requests.append(jam_request)

        db.session.commit()
        print(f"Created {len(jam_requests)} jam requests between compatible musicians")

        # Generate 8 sample rentals
        rentals_data = []
        renters = [u for u in users if u.role == 'renter']

        for i in range(8):
            renter = random.choice(renters)
            # Find an available instrument
            available_instruments = [inst for inst in instruments if inst.status == 'available']
            if available_instruments:
                instrument = random.choice(available_instruments)

                # Generate rental dates (some past, some future)
                if random.random() < 0.6:  # 60% past rentals
                    start_date = datetime.now() - timedelta(days=random.randint(1, 30))
                    end_date = start_date + timedelta(days=random.randint(1, 7))
                    status = random.choice(['completed', 'completed', 'cancelled'])
                else:  # 40% future rentals
                    start_date = datetime.now() + timedelta(days=random.randint(1, 14))
                    end_date = start_date + timedelta(days=random.randint(1, 7))
                    status = 'confirmed'

                total_price = instrument.price_per_day * (end_date - start_date).days

                rental = {
                    'instrument_id': instrument.id,
                    'renter_id': renter.id,
                    'start_date': start_date.date(),
                    'end_date': end_date.date(),
                    'total_price': round(total_price, 2),
                    'status': status
                }
                rentals_data.append(rental)

        # Create rentals
        rentals = []
        for rental_data in rentals_data:
            rental = Rental(**rental_data)
            db.session.add(rental)
            rentals.append(rental)

        db.session.commit()
        print(f"Created {len(rentals)} rental records with diverse dates and statuses")

        print("\n🎵 Diverse Tunisian Music Community Created!")
        print("=" * 50)

        # Statistics
        print(f"📍 Locations covered: {len(set([u.location_name for u in users]))} cities across Tunisia")
        print(f"🎸 Instruments available: {len(instruments)} (priced TND {min([i.price_per_day for i in instruments]):.2f} - {max([i.price_per_day for i in instruments]):.2f}/day)")
        print(f"👥 Active musicians: {len([u for u in users if u.role == 'jammer' and u.is_active_for_jam])}")
        print(f"🏪 Instrument owners: {len([u for u in users if u.role == 'owner'])}")
        print(f"🎵 Music genres represented: {len(set([g for u in users for g in u.genres_enjoyed]))}")

        print("\n📧 Test Accounts (password: password123):")
        for user in random.sample(users, min(5, len(users))):
            print(f"  • {user.name} ({user.email}) - {user.role} from {user.location_name}")

        print("\n🎼 Ready for testing jam discovery, instrument rental, and user matching!")
        print("💡 Try searching for instruments by location, price range, or type!")

if __name__ == '__main__':
    create_diverse_tunisian_data()