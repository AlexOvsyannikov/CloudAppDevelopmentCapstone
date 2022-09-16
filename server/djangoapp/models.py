from django.db import models
from django.utils.timezone import now


# Create your models here.

# <HINT> Create a Car Make model `class CarMake(models.Model)`:
# - Name
# - Description
# - Any other fields you would like to include in car make model
# - __str__ method to print a car make object
class CarMake(models.Model):
    name = models.TextField()
    description = models.TextField()

    def __str__(self):
        return f'{self.name} {self.description}'

# <HINT> Create a Car Model model `class CarModel(models.Model):`:
# - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
# - Name
# - Dealer id, used to refer a dealer created in cloudant database
# - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
# - Year (DateField)
# - Any other fields you would like to include in car model
# - __str__ method to print a car make object


class CarModel(models.Model):
    options = [
        ('suv', 'SUV'),
        ('sedan', 'Sedan'),
        ('wagon', 'WAGON')
    ]
    name = models.TextField()
    dealer_id = models.IntegerField()
    type = models.CharField(choices=options,
                            default='suv',
                            max_length=10)
    year = models.DateField()
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} {self.dealer_id} {self.type} {self.year}'


# <HINT> Create a plain Python class `CarDealer` to hold dealer data
class CarDealer:

    def __init__(self, address, city, full_name, id, lat, long, short_name, st, zip):
        # Dealer address
        self.address = address
        # Dealer city
        self.city = city
        # Dealer Full Name
        self.full_name = full_name
        # Dealer id
        self.id = id
        # Location lat
        self.lat = lat
        # Location long
        self.long = long
        # Dealer short name
        self.short_name = short_name
        # Dealer state
        self.st = st
        # Dealer zip
        self.zip = zip

    def __str__(self):
        return "Dealer name: " + self.full_name

# <HINT> Create a plain Python class `DealerReview` to hold review data


class DealerReview:
    def __init__(self, name, review, dealership, id, purchase, purchase_date, car_make, car_model, car_year, sentiment):
        # Dealer address
        self.name = name
        # Dealer city
        self.review = review
        # Dealer Full Name
        self.dealership = dealership
        # Dealer id
        self.id = id
        # Location lat
        self.purchase = purchase
        # Location long
        self.purchase_date = purchase_date
        # Dealer short name
        self.car_make = car_make
        # Dealer state
        self.car_model = car_model
        # Dealer zip
        self.car_year = car_year

        self.sentiment = sentiment

    def __str__(self):
        return "Dealer name: " + self.name
