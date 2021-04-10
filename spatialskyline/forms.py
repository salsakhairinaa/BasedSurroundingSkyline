from django import forms

POI_CHOICES = (
    (None, None),
    ('restaurant', 'Restaurant'), ('lodging', 'Hotel'), ('cafe', 'Cafe'), ('supermarket', 'Supermarket'), ('parking', 'Parking'), ('shopping_mall', 'Shopping Mall'),
    ('accounting', 'Accounting'), ('airport', 'Airport'), ('amusement_park', 'Amusement Park'), ('aquarium', 'Aquarium'), ('art_gallery', 'Art Gallery'), ('atm', 'ATM'),
    ('bakery', 'Bakery'), ('bank', 'Bank'), ('bar', 'Bar'), ('beauty_salon', 'Beauty Salon'), ('bicycle_store', 'Bicycle Store'), ('book_store', 'Book Store'),
    ('bowling_alley', 'Bowling Alley'), ('bus_station', 'Bus Station'), ('campground', 'Campground'), ('car_dealer', 'Car Dealer'), ('car_rental', 'Car Rental'),
    ('car_repair', 'Car Repair'), ('car_wash', 'Car Wash'), ('casino', 'Casino'), ('cemetery', 'Cemetery'), ('church', 'Church'), ('city_hall', 'City Hall'),
    ('clothing_store', 'Clothing Store'), ('convenience_store', 'Convenience Store'), ('courthouse', 'Courthouse'), ('dentist', 'Dentist'), ('department_store', 'Department Store'),
    ('doctor', 'Doctor'), ('drugstore', 'Drugstore'), ('electrician', 'Electrician'), ('electronics_store', 'Electronics Store'), ('embassy', 'Embassy'), ('fire_station', 'Fire Station'),
    # ('florist', 'Florist'), ('funeral_home', 'Funeral Home'), ('furniture_store', 'Furniture Store'), ('gas_station', 'Gas Station'), ('gym', 'Gym'), ('hair_care', 'Hair Care'),
    # ('hardware_store', 'Hardware Store'), ('hindu_temple, Hindu Temple'), ('home_goods_store', 'Home Goods Store'), ('hospital', 'Hospital'), ('insurance_agency', 'Insurance Agency'),
    # ('jewelry_store', 'Jewelry Store'), ('laundry', 'Laundry'), ('lawyer', 'Lawyer'), ('library',  'Library'), ('light_rail_station', 'Light Rail Station'), ('liquor_store', 'Liquor Store'),
    # ('local_government_office', 'Local Government Office'), ('locksmith', 'Locksmith'), ('meal_delivery', 'Meal Delivery'), ('meal_takeaway', 'Meal Takeaway'), ('mosque', 'Mosque'),
    # ('movie_rental', 'Movie Rental'), ('movie_theater', 'Movie Theater'), ('moving_company', 'Moving Company'), ('museum', 'Museum'), ('night_club', 'Night Club'), ('painter', 'Painter'),
    # ('park', 'Park'), ('pet_store', 'Pet Store'), ('pharmacy', 'Pharmacy'), ('physiotherapist', 'Physiotherapist'), ('plumber', 'Plumber'), ('police', 'Police'),
    # ('post_office', 'Post Office'), ('primary_school', 'Primary School'), ('real_estate_agency', 'Real Estate Agency'), ('roofing_contractor', 'Roofing Contractor'), ('rv_park', 'RV Park'),
    # ('school', 'School'), ('secondary_school', 'Secondary School'), ('shoe_store', 'Shoe Store'), ('spa', 'Spa'), ('stadium', 'Stadium'), ('storage', 'Storage'), ('store', 'Store'),
    # ('subway_station', 'Subway Station'), ('synagogue', 'Synagogue'), ('taxi_stand', 'Taxi Stand'), ('tourist_attraction', 'Tourist Attraction'), ('train_station', 'Train Station'),
    # ('transit_station', 'Transit Station'), ('travel_agency', 'Travel Agency'), ('university', 'University'), ('veterinary_care', 'Veterinary Care'), ('zoo', 'Zoo'),
)

RATING_CHOICES = (
    (0, 'Tidak ada'),
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
)

class SpatialForm(forms.Form):
    tipe_poi = forms.ChoiceField(choices=POI_CHOICES)
    min_rating = forms.ChoiceField(choices=RATING_CHOICES, required=False)

class QueryForm(forms.Form):
    lokasi = forms.CharField(max_length=200)
