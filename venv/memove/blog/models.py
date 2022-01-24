from django.contrib.gis.db import models
from django.utils import timezone
from django.urls import reverse
from django.template.defaultfilters import slugify
from django.contrib.auth import get_user_model
from .maps import map_maker

User = get_user_model()


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')


class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    """AD_TYPE = (
        ('rent', 'Rent'),
        ('sale', 'Sale'),
    )"""
    """PRICING = (
        ('auction', 'Auction'),
        ('fixed_price', ' Fixed Price'),
        ('guide_price', 'Guide Price'),
    )"""
    PROPERTY_CHOICES = (
        ('house', 'House'),
        ('flat', 'Flat'),
        ('boat', 'Boat'),
    )
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, null=False, unique_for_date='publish')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='published')
    objects = models.Manager()
    published = PublishedManager()
    main_image = models.ImageField(null=True, upload_to="property_photos")
    address = models.CharField(max_length=250, default='8 Grovebury Road')
    city = models.CharField(max_length=50, default='London', db_index=True)
    postcode = models.CharField(max_length=50, default='SE2 9YA', db_index=True)
    rent = models.IntegerField(default=200)
    property_type = models.CharField(max_length=20, choices=PROPERTY_CHOICES, default='Flat')
    number_of_beds = models.IntegerField(default=2)
    number_of_baths = models.IntegerField(default=0)
    #type_of_ad = models.CharField(max_length=20, choices=AD_TYPE, default='rent')
    #pricing = models.CharField(max_length=20, choices=PRICING, default='fixed_price')
    latitude = models.DecimalField(max_digits=15, decimal_places=10, null=True, db_index=True, )
    longitude = models.DecimalField(max_digits=15, decimal_places=10, null=True, db_index=True, )
    postcode_area = models.CharField(max_length=3, blank=True, null=True, db_index=True)
    postcode_district = models.CharField(max_length=4, blank=True, null=True, db_index=True)

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.id, 'slug': self.slug})

    def post_update_url(self):
        return reverse('blog:post_update', kwargs={'pk': self.id, 'slug': self.slug})

    def property_picture_form(self):
        return reverse('blog:property_picture_form', kwargs={'pk': self.id, 'slug': self.slug})

    def property_plan_form(self):
        return reverse('blog:property_plan_form', kwargs={'pk': self.id, 'slug': self.slug})

    def get_pictures(self):
        return Pictures.objects.filter(property_id=self.id)

    def get_cordinates(self):
        cordinates = [self.latitude, self.longitude]
        return cordinates

    def get_plan(self):
        return PropertyPlan.objects.filter(property_id=self.id)

    def plan_exists(self):
        return PropertyPlan.objects.filter(property_id=self.id).exists()

    def post_delete(self):
        return reverse('blog:post_delete', kwargs={'pk': self.id, 'slug': self.slug})

    def save(self, *args, **kwargs, ):
        if not self.slug:
            self.slug = slugify(self.title)
        pc = Postcodes.objects.get(postcode=self.postcode)
        if not self.author.is_agent:
            self.author.make_agent()

        self.latitude = pc.latitude
        self.longitude = pc.longitude

        self.postcode_area = pc.postcode_area
        self.postcode_district = pc.postcode_district
        x = super().save(*args, **kwargs)

        #!!This is expensive
        #delete_maps()
        map_maker(self.id, pc.latitude, pc.longitude)
        return x


class Postcodes(models.Model):
    id = models.BigAutoField(primary_key=True)
    postcode = models.CharField(max_length=10, db_index=True)
    latitude = models.DecimalField(max_digits=15, decimal_places=10, blank=True, null=True, db_index=True, )
    longitude = models.DecimalField(max_digits=15, decimal_places=10, blank=True, null=True, db_index=True, )
    easting = models.IntegerField(blank=True, null=True)
    northing = models.IntegerField(blank=True, null=True)
    grid_ref = models.CharField(max_length=8, blank=True, null=True)
    county = models.CharField(max_length=25, blank=True, null=True)
    district = models.CharField(max_length=40, blank=True, null=True)
    ward = models.CharField(max_length=55, blank=True, null=True)
    district_code = models.CharField(max_length=10, blank=True, null=True)
    ward_code = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=20, blank=True, null=True)
    county_code = models.CharField(max_length=10, blank=True, null=True)
    constituency = models.CharField(max_length=50, blank=True, null=True)
    rural_urban = models.CharField(max_length=60, blank=True, null=True)
    region = models.CharField(max_length=25, blank=True, null=True)
    london_zone = models.CharField(max_length=2, blank=True, null=True)
    nearest_station = models.CharField(max_length=55, blank=True, null=True)
    distance_to_station = models.DecimalField(max_digits=15, decimal_places=10, blank=True, null=True)
    postcode_area = models.CharField(max_length=3, blank=True, null=True)
    postcode_district = models.CharField(max_length=4, blank=True, null=True)
    plus_code = models.CharField(max_length=11, blank=True, null=True)
    objects = models.Manager()


class Pictures(models.Model):
    id = models.AutoField(primary_key=True)
    property_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    property_pic = models.ImageField(null=False, upload_to='property_photos')
    objects = models.Manager()

    def picture_delete(self):
        return reverse('blog:picture_delete', kwargs={'pk': self.id})


class PropertyPlan(models.Model):
    id = models.AutoField(primary_key=True)
    property_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    property_plan = models.FileField(upload_to='property_plans')
    objects = models.Manager()

    def plan_delete(self):
        return reverse('blog:plan_delete', kwargs={'pk': self.id})


class Meta:
    ordering = ('-publish',)

    def __str__(self):
        return self.title


class Boundaries(models.Model):
    id = models.AutoField(primary_key=True)
    search_name = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    borough = models.CharField(max_length=80, null=True)
    county = models.CharField(max_length=80, null=True)
    geom = models.GeometryField()
    type = models.CharField(max_length=25)
    postcode = models.ForeignKey(Postcodes, on_delete=models.CASCADE, null=True)
    objects = models.Manager()


class Distances(models.Model):
    id = models.AutoField(primary_key=True)
    km_or_mile = models.CharField(max_length=4)
    distance = models.SmallIntegerField()


class BufferZones(models.Model):
    id = models.AutoField(primary_key=True)
    distance = models.ForeignKey(Distances, on_delete=models.CASCADE)
    boundary = models.ForeignKey(Boundaries, on_delete=models.CASCADE)
    geom = models.GeometryField(null=True)

    class Meta:
        unique_together = ('distance_id', 'boundary_id',)


class NearestRailwayStations(models.Model):
    id = models.AutoField(primary_key=True)
    boundary = models.ForeignKey(Boundaries, on_delete=models.CASCADE)
    postcode = models.ForeignKey(Postcodes, on_delete=models.CASCADE)
    distance = models.FloatField()
    type = models.CharField(max_length=50)
    objects = models.Manager()

    class Meta:
        db_table = "blog_nearestrailwaystations"

    def get_time_takes(self):
        return self.distance / 60

    def is_uni(self):
        return self.type == 'Railway Station'

    def get_destination(self):
        return Boundaries.objects.filter(id=self.boundary)


class Contact(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(null=True)
    head = models.CharField(max_length=200)
    body = models.TextField()
    date = models.DateField(auto_now_add=True)


class SavedProperties(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Post, on_delete=models.CASCADE)
    objects = models.Manager()

    class Meta:
        unique_together = ('user_id', 'property_id',)

    def is_saved(self, user_id, property_id):
        return self.objects.filter(property_id=property_id, user_id=user_id).exists()


class Lines(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)


class Stations(models.Model):
    id = models.AutoField(primary_key=True)
    line = models.ForeignKey(Lines, on_delete=models.CASCADE)
    station_name = models.CharField(max_length=100)
    boundary = models.ForeignKey(Boundaries, on_delete=models.CASCADE)


class Times(models.Model):
    id = models.AutoField(primary_key=True)
    origin = models.ForeignKey(Stations, on_delete=models.CASCADE, related_name='origin_station')
    destination = models.ForeignKey(Stations, on_delete=models.CASCADE, related_name='destination_station')
    duration = models.IntegerField(db_index=True)
    objects = models.Manager()