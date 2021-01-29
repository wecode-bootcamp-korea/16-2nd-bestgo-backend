from django_seed import Seed

from django.core.management.base import BaseCommand

from users.models import User

class Command(BaseCommand):

        help = 'This Command Creates Users'

        def add_arguments(self, parser):
            parser.add_argument(
                '-number', default=1, type=int, help = "How many users do you want to create?"
            )

        def handle(self, *args, **options):
            number = options.get('number')
            seeder = Seed.seeder()
            seeder.add_entity(User, number)
            seeder.excute()
            self.stdout.write(self,style,SUCCESS(f'{number} users created!'))
