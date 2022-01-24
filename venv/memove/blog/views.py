import folium
import json
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import PicturesForm, PropertyForm, PropertyPlanForm, ContactForm
from .maps import get_cordinates, get_details
from .models import Post, Pictures, PropertyPlan, SavedProperties, NearestRailwayStations, Contact, Times

LONDON_LOCATION = (51.503454, -0.139011)


def home_view(request):
    return render(request, 'blog/post/home.html')


User = get_user_model()


class PostListView(ListView):
    model = Post
    context_object_name = 'properties'
    paginate_by = 20
    template_name = 'blog/post/list.html'

    @staticmethod
    def min_max(low, high, x, y):
        if low == "undefined":
            low = x

        else:
            low = int(low)

        if high == "undefined":
            high = y

        else:
            high = int(high)

        if high < low:
            high2 = high

            high = low
            low = high2

        return [low, high]

    def get_queryset(self):
        query = list_view_query(self.request)
        uni = self.request.GET.get('uni') or "undefined"
        return query


def list_view_query(request):
    query = Post.objects
    location = request.GET.get('location') or "undefined"
    if query.filter(city__iexact=location).exists():
        query = query.filter(city__iexact=location)
    elif query.filter(postcode_district__iexact=location).exists():
        query = query.filter(postcode_district__iexact=location)
    elif query.filter(postcode_area__iexact=location).exists():
        query = query.filter(postcode_district__iexact=location)
    elif query.filter(postcode__iexact=location).exists():
        query = query.filter(postcode__iexact=location)

    min_baths = request.GET.get('min_baths') or "undefined"
    max_baths = request.GET.get('max_baths') or "undefined"
    replacer = PostListView.min_max(min_baths, max_baths, 1, 2)
    query = query.filter(number_of_baths__lte=replacer[1], number_of_baths__gte=replacer[0])

    min_beds = request.GET.get('min_beds') or "undefined"
    max_beds = request.GET.get('max_beds') or "undefined"
    replacer = PostListView.min_max(min_beds, max_beds, 1, 10)
    query = query.filter(number_of_beds__lte=replacer[1], number_of_beds__gte=replacer[0])

    min_price = request.GET.get('min_price') or "undefined"
    max_price = request.GET.get('max_price') or "undefined"
    replacer = PostListView.min_max(min_price, max_price, 10000, 10000000)
    query = query.filter(rent__lte=replacer[1], rent__gte=replacer[0])

    property_type = []
    x = request.GET.get('house')
    y = request.GET.get('flat')
    z = request.GET.get('boat')

    if x != "false":
        property_type.append('house')

    if y != "false":
        property_type.append('flat')

    if z != "false":
        property_type.append('boat')

    if len(property_type) == 0:
        property_type = ['house', 'flat', 'boat']
    query = query.filter(property_type__in=property_type)
    return query


def list_view(request):
    query = list_view_query(request)
    properties = query.values('postcode', 'id')
    uni = request.GET.get('uni') or "undefined"
    duration = {}
    for property in properties:
        pc = property['postcode']
        times = Times.objects.raw("""SELECT id, duration FROM blog_times WHERE origin=
        (SELECT  blog_stations.id
        FROM blog_nearestrailwaystations, blog_postcodes,blog_stations
        WHERE blog_postcodes.id = blog_nearestrailwaystations.postcode_id
        AND blog_stations.boundary_id=blog_nearestrailwaystations.boundary_id
        AND blog_nearestrailwaystations.type='Railway Station' AND postcode = %s
        ORDER BY blog_nearestrailwaystations.distance LIMIT 1
        ) 
        AND destination=(SELECT 
              blog_stations.id
              FROM blog_boundaries,blog_nearestrailwaystations, blog_stations
              WHERE blog_boundaries.search_name=%s
              AND blog_nearestrailwaystations.postcode_id = blog_boundaries.postcode_id
              AND blog_nearestrailwaystations.type='Railway Station'
              AND blog_stations.boundary_id=blog_nearestrailwaystations.boundary_id
              ORDER BY blog_nearestrailwaystations.distance LIMIT 1
            )
        ORDER BY duration LIMIT 1""", [pc, uni])

        for time in times:
            university_station = NearestRailwayStations.objects.raw("""
                   (SELECT id,distance FROM blog_nearestrailwaystations WHERE postcode_id=
                   (SELECT postcode_id FROM blog_boundaries WHERE search_name= %s LIMIT 1)
                   AND type='Railway Station'
                   ORDER BY distance LIMIT 1)
                    """, [uni])
            nearest_station = NearestRailwayStations.objects.raw("""
                    (SELECT id, distance FROM blog_nearestrailwaystations WHERE postcode_id=
                    (SELECT id FROM blog_postcodes WHERE postcode = %s)
                    AND type='Railway Station'
                    ORDER BY distance LIMIT 1)
                    """, [property['postcode']])
            university_station = int(university_station[0].distance /60)
            nearest_station = int(nearest_station[0].distance /60)
            duration[property['id']] = time.duration + university_station + nearest_station
    return render(request, "blog/post/list.html", {'properties' : query, 'duration': duration, 'uni': uni})


def map_view_list(request):
    # page = request.GET.get('postcodes')
    cordinates = Post.objects

    location = request.GET.get('location') or "undefined"
    if cordinates.filter(city__iexact=location).exists():
        cordinates = cordinates.filter(city__iexact=location)
    elif cordinates.filter(postcode_district__iexact=location).exists():
        cordinates = cordinates.filter(postcode_district__iexact=location)
    elif cordinates.filter(postcode_area__iexact=location).exists():
        cordinates = cordinates.filter(postcode_district__iexact=location)
    elif cordinates.filter(postcode__iexact=location).exists():
        cordinates = cordinates.filter(postcode__iexact=location)

    min_beds = request.GET.get('min_beds') or "undefined"
    max_beds = request.GET.get('max_beds') or "undefined"
    replacer = PostListView.min_max(min_beds, max_beds, 1, 10)
    cordinates = cordinates.filter(number_of_beds__lte=replacer[1], number_of_beds__gte=replacer[0])

    min_baths = request.GET.get('min_baths') or "undefined"
    max_baths = request.GET.get('max_baths') or "undefined"
    replacer = PostListView.min_max(min_baths, max_baths, 1, 2)
    cordinates = cordinates.filter(number_of_baths__lte=replacer[1], rent__gte=replacer[0])

    property_type = []
    x = request.GET.get('house')
    y = request.GET.get('flat')
    z = request.GET.get('boat')

    if x != "false":
        property_type.append('house')

    if y != "false":
        property_type.append('flat')

    if z != "false":
        property_type.append('boat')

    if len(property_type) == 0:
        property_type = ['house', 'flat', 'boat']
    # execution of the query
    cordinates = cordinates.filter(property_type__in=property_type).values('latitude', 'longitude', 'slug', 'id',
                                                                           'number_of_beds', 'main_image', 'rent')
    # execute the query

    i = 0
    coords = []
    while i < len(cordinates):
        coords.append(get_cordinates(cordinates, i))
        i += 1

    details = []
    for crd in cordinates:
        details.append([crd.get('slug'), crd.get('id'), crd.get('number_of_beds'), crd.get('price'), crd.get('main_image')])

    # All this below is for where the first the map starts

    latitudes = []
    longitudes = []

    for i in coords:
        latitudes.append(i[0])
        longitudes.append(i[1])



    # zoom range ---> 9-15

    map = folium.Map(location=LONDON_LOCATION, zoom_start=11)

    # these are for popup details

    for i in range(len(coords)):
        folium.Marker(coords[i],
                      popup='<p>Rent:%s£</p><p>Number of Beds:%d</p><a href="../../property/%d-%s" target=_blank>Touch here to see more details</a> <img src="../../media/%s" class=map_view_photo>' % (
                      details[i][3], details[i][2], details[i][1], details[i][0], details[i][4])).add_to(map)

    # To see whether Post exist or not
    html_string = map.get_root().render()
    return render(request, 'blog/post/map.html', {'html_string': html_string})


class ProfileListView(LoginRequiredMixin, ListView):
    model = Post
    context_object_name = 'properties'
    paginate_by = 3
    template_name = 'blog/post/list.html'

    def get_queryset(self):
        post = Post.objects
        return post.filter(author=self.request.user)


class PostCreateView(LoginRequiredMixin, CreateView):
    form_class = PropertyForm
    template_name = 'blog/post/post_creation.html'
    login_url = 'login'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'body', 'address', 'city', 'postcode', 'number_of_beds',
              'number_of_baths', 'rent', 'property_type', 'main_image']
    template_name = 'blog/post/update.html'
    login_url = 'login'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post/delete.html'
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PictureDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Pictures
    template_name = 'blog/post/picture_delete.html'
    success_url = '/'

    def test_func(self):
        picture = self.get_object()
        if self.request.user == picture.property_id.author:
            return True
        return False


def post_detail(request, pk, slug):
    post = get_object_or_404(Post, id=pk, status='published')
    is_saved = SavedProperties.objects.filter(property_id=pk, user_id=post.author).exists()

    railway_stations = NearestRailwayStations.objects.raw("""
                                SELECT blog_nearestrailwaystations.*, search_name
                                FROM blog_postcodes,  blog_nearestrailwaystations, blog_boundaries
                                WHERE blog_nearestrailwaystations.postcode_id = blog_postcodes.id 
				                AND blog_boundaries.id = blog_nearestrailwaystations.boundary_id
                                AND blog_postcodes.postcode = %s;""" , [post.postcode])

    return render(request, 'blog/post/detail.html', {'post': post, 'is_saved': is_saved, 'railway_stations': railway_stations})


def property_picture_form(request, pk, slug):
    x = 1
    obj = Pictures.objects.filter(property_id=pk)
    if request.method == 'POST':
        form = PicturesForm(request.POST, request.FILES)
        images = request.FILES.getlist('image')
        for image in images:
            photo = Pictures.objects.create(property_pic=image, property_id_id=pk)
            photo.save()
        return HttpResponseRedirect('../../property/' + str(pk) + "-" + slug)
    else:
        form = PicturesForm()
    return render(request, 'blog/post/property_pictures.html', {'form': form, 'obj': obj, 'x': x})


def contact_form(request):
    if request.method == 'POST':
        form = ContactForm(data=request.POST)
        if form.is_valid():
            name = request.POST['name']
            email = request.POST['email']
            head = request.POST['head']
            body = request.POST['body']
            contact = Contact(name=name, email=email, head=head, body=body)
            contact.save()
            return HttpResponseRedirect('../')
    else:
        form = ContactForm()
    return render(request, 'blog/post/contact_form.html',{'form' : form})


def error(request):
    return render(request, "blog/error.html")


def property_plan_form(request, pk, slug):
    x = 1
    obj = PropertyPlan.objects.filter(property_id=pk)
    if request.method == 'POST':
        form = PropertyPlanForm(request.POST, request.FILES)
        plans = request.FILES.getlist('property_plan')
        for plan in plans:
            photo = PropertyPlan.objects.create(property_plan=plan, property_id_id=pk)
            photo.save()
        return HttpResponseRedirect('../../property/' + str(pk) + "-" + slug)
    else:
        form = PropertyPlanForm()
    return render(request, 'blog/post/property_plan_form.html', {'form': form, 'obj': obj, 'x': x})


def filter_page(request):
    return render(request, 'blog/post/filter.html')


def property_save(request, pk):
    current_user = request.user
    some_data_to_dump = {'code': 0, 'message': 'save completed successfully', }

    if current_user.is_anonymous:
        some_data_to_dump = {'code': 1, 'message': 'To save a property you must sign in', }
    else:
        if SavedProperties.objects.filter(property_id=pk, user_id=current_user.id).exists():
            p = SavedProperties(user_id=current_user.id, property_id=pk)
            p.delete()
            some_data_to_dump[1] = 'Property is unsaved'
        else:
            p = SavedProperties(user_id=current_user.id, property_id=pk)
            p.save()

    data = json.dumps(some_data_to_dump)
    return HttpResponse(data, content_type='application/json')


# publish__year = year,
# publish__month = month,
# publish__day = day
'''class PropertyUpdate(ListView):
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'
'''
