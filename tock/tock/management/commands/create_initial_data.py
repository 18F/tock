import random
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from employees.models import EmployeeGrade, UserData
from organizations.models import Unit
from faker import Faker
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        self.create_unit()

        self.stdout.write(self.style.SUCCESS('Successfully create_unit'))

    def create_users(self, unit, num_users):
        fake = Faker()
        user_user_data_pair = []
        for _ in range(num_users):
            while True:
                first = fake.first_name()
                self.stdout.write(first)
                last = fake.last_name()
                self.stdout.write(last)
                username = f'{first.lower()}.{last.lower()}'
                if User.objects.filter(username=username).exists():
                    continue
                # self.stdout.write(User.objects.all())
                user = User.objects.create_user(first_name=first,last_name=last,username=username,email=f'{username}@gsa.gov',password='',is_staff=False,is_active=True)
                # self.stdout.write(user)
                user.save()
                userdata = UserData.objects.create(user=user,is_18f_employee=True,current_employee=True,organization=unit.org,unit=unit)
                userdata.save()
                user_user_data_pair.append((user, userdata))
                break

            print("*This is user_user_data_pair in create_users*")
            print(user_user_data_pair)
        return user_user_data_pair

    def find_sundays(self, num_users):
        self.stdout.write(f'find_sundays: num_users: {num_users}')
        today = datetime.today() 
        self.stdout.write(f'today: {today}')
        delta = timedelta(days=today.weekday() + 1)
        last_sunday = today - delta
        self.stdout.write(f'last_sunday:{last_sunday}')
        # Find a few Sundays within the 4 years term, there's 52 weeks in a year, and 4 years means 208 weeks
        four_years_ago_sunday = last_sunday - timedelta(weeks=52*4)
        self.stdout.write(f'four_years_ago_sunday:{four_years_ago_sunday}')
        # If bi-weekly, there's 208/2 = 104 Sundays between the four years period
        # get a list of num_user / 2 dates
        # num_users randint(1, 104)
        random_start_week_list = [four_years_ago_sunday + timedelta(weeks=random.randint(1, 104)*2) for i in range(int(num_users/2))]
        return random_start_week_list

    def add_start_date(self, user_user_data_pair):
        num_user = len(user_user_data_pair)
        self.stdout.write(f'num_user: {num_user}')
        start_date_list = self.find_sundays(num_user)
        for pair in user_user_data_pair:
            pair[1].start_date = random.choice(start_date_list)
            pair[1].save()


    def create_unit(self):
        count = Unit.objects.count()
        units = Unit.objects.all()
        user_user_data_pair = []
        for unit in units:
            user_user_data_pair.extend(self.create_users(unit, random.randint(5,10)))
        # self.stdout.write(user_user_data_pair)
        self.add_start_date(user_user_data_pair)

