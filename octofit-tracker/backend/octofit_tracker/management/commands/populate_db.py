from django.core.management.base import BaseCommand
from django.utils import timezone
from octofit_tracker.models import User, Team, Activity, Workout, Leaderboard
from django.db import transaction
from django.conf import settings
import pymongo


class Command(BaseCommand):
    help = 'Populate the octofit_db database with test data'

    def handle(self, *args, **options):
        self.stdout.write('Starting database population...')

        # Use pymongo to drop collections first to avoid Djongo ORM deletion issues
        try:
            client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
            db = client[settings.DATABASES['default']['NAME']]
            for col in ['leaderboard', 'activities', 'workouts', 'users', 'teams']:
                if col in db.list_collection_names():
                    db[col].drop()
                    self.stdout.write(f'Dropped collection: {col}')
        except Exception as e:
            self.stderr.write(f'Warning: could not drop collections via pymongo: {e}')

        # Clear any remaining data using Django ORM
        with transaction.atomic():
            Leaderboard.objects.all().delete()
            Activity.objects.all().delete()
            Workout.objects.all().delete()
            User.objects.all().delete()
            Team.objects.all().delete()

        self.stdout.write('Cleared existing data')

        # Create teams
        marvel = Team.objects.create(name='Marvel', description='Marvel team')
        dc = Team.objects.create(name='DC', description='DC team')

        # Create users (superheroes)
        users = []
        users.append(User.objects.create(name='Tony Stark', email='tony@stark.com', team=marvel, is_superhero=True))
        users.append(User.objects.create(name='Peter Parker', email='peter@parker.com', team=marvel, is_superhero=True))
        users.append(User.objects.create(name='Bruce Wayne', email='bruce@wayne.com', team=dc, is_superhero=True))
        users.append(User.objects.create(name='Clark Kent', email='clark@kent.com', team=dc, is_superhero=True))

        self.stdout.write(f'Created {len(users)} users')

        # Create workouts
        w1 = Workout.objects.create(name='Super Strength', description='Strength routine', difficulty='Hard')
        w2 = Workout.objects.create(name='Speed Run', description='Interval sprints', difficulty='Medium')

        self.stdout.write('Created workouts')

        # Create activities for users
        today = timezone.now().date()
        activities = []
        activities.append(Activity.objects.create(user=users[0], type='fly', duration=60, date=today))
        activities.append(Activity.objects.create(user=users[1], type='run', duration=30, date=today))
        activities.append(Activity.objects.create(user=users[2], type='train', duration=45, date=today))
        activities.append(Activity.objects.create(user=users[3], type='rescue', duration=50, date=today))

        self.stdout.write(f'Created {len(activities)} activities')

        # Create leaderboard entries
        lb_entries = []
        lb_entries.append(Leaderboard.objects.create(user=users[0], score=980, rank=1))
        lb_entries.append(Leaderboard.objects.create(user=users[1], score=870, rank=2))
        lb_entries.append(Leaderboard.objects.create(user=users[2], score=920, rank=1))
        lb_entries.append(Leaderboard.objects.create(user=users[3], score=900, rank=2))

        self.stdout.write('Created leaderboard entries')

        # Ensure unique index on users.email using direct pymongo client
        try:
            client = pymongo.MongoClient(settings.DATABASES['default']['CLIENT']['host'])
            db = client[settings.DATABASES['default']['NAME']]
            db.users.create_index([('email', pymongo.ASCENDING)], unique=True)
            self.stdout.write('Ensured unique index on users.email')
        except Exception as e:
            self.stderr.write(f'Warning: could not create unique index via pymongo: {e}')

        self.stdout.write(self.style.SUCCESS('Database population completed successfully'))
