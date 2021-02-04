import random
import bcrypt

from django_seed import Seed
from faker       import Faker
from django.core.management.base import BaseCommand

from users.models import User, Gender

fake_kr = Faker('ko_KR')
fake    = Faker()

class Command(BaseCommand):

        help = 'This Command Creates Users'

        def add_arguments(self, parser):
            parser.add_argument(
                "-number", default=1, type=int, help = "How many users do you want to create?"
            )

        def handle(self, *args, **options):
            number = options.get("number")
            seeder = Seed.seeder()
            seeder.add_entity(
                User, 
                number,
                {    
                    "name"         : lambda x: fake_kr.name(),
                    "email"        : lambda x: fake.email(),
                    "password"     : bcrypt.hashpw("q1w2e3r4".encode(), bcrypt.gensalt()).decode(),
                    "phone_number" : lambda x: f"010{random.randint(11111111, 99999999)}",
                    "gender"       : None,
                    "is_master"    : True,
                }
            )
            seed_user = seeder.execute()
            self.stdout.write(self.style.SUCCESS(f'{number} users created!'))
