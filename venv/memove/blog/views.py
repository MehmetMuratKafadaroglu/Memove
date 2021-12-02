from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from .models import Post, Pictures, PropertyPlan, NearestSchools, SavedProperties
from django.core.paginator import Paginator, EmptyPage,\
                                    PageNotAnInteger
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import PicturesForm, PropertyForm, PropertyPlanForm
from django.http import HttpResponseRedirect, HttpResponse
from .maps import get_cordinates, get_details
import folium,math, json

def home_view(request):
    return render(request, 'blog/post/home.html')

User = get_user_model()
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

class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    paginate_by = 20
    template_name = 'blog/post/list.html'
    
    def min_max(self, low, high, x, y):
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
        query = Post.objects
        
        location = self.request.GET.get('location') or "undefined"
        if query.filter(city=location).exists():
            query = query.filter(city=location)
        elif query.filter(postcode_district=location).exists():
            query = query.filter(postcode_district=location)
        elif query.filter(postcode_area=location).exists():
            query = query.filter(postcode_district=location)
        elif query.filter(postcode=location).exists():
            query = query.filter(postcode=location)
        else:
            return query.none()

        ad_type = self.request.GET.get('ad_type') or "undefined"
        query = query.filter(type_of_ad__iexact = ad_type)

        min_beds = self.request.GET.get('min_beds') or "undefined"
        max_beds = self.request.GET.get('max_beds') or "undefined"
        replacer = self.min_max(min_beds, max_beds,1,10)
        query = query.filter(number_of_beds__lte = replacer[1],number_of_beds__gte = replacer[0])
    
        min_price = self.request.GET.get('min_price') or "undefined"
        max_price = self.request.GET.get('max_price') or "undefined"
        replacer = self.min_max(min_price, max_price,10000,10000000)
        query = query.filter(price__lte = replacer[1], price__gte = replacer[0])
        
        min_baths = self.request.GET.get('min_baths') or "undefined"
        max_baths = self.request.GET.get('max_baths') or "undefined"
        replacer = self.min_max(min_baths, max_baths,1, 2)
        query = query.filter(number_of_baths__lte = replacer[1], price__gte = replacer[0])
        
        property_type = []
        x = self.request.GET.get('house')
        y = self.request.GET.get('flat')
        z = self.request.GET.get('boat')
        
        if x != "false":
            property_type.append('house') 
        
        if y != "false":
            property_type.append('flat')
        
        if z != "false":
            property_type.append('boat')

        if len(property_type)==0:
            property_type = ['house','flat','boat']
        query = query.filter(property_type__in = property_type)
        
        price_sort = self.request.GET.get('sort') or "undefined"
        if price_sort == "high_to_low_price":
            query = query.order_by('-price')
        elif price_sort == "most_recent" :
            query = query.order_by('-created')   
        else:
            query = query.order_by('price')
            
        return query



def map_view_list(request):
    #page = request.GET.get('postcodes')
    cordinates = Post.objects

    location = request.GET.get('location') or "undefined"
    if cordinates.filter(city__iexact = location).exists():
        cordinates = cordinates.filter(city__iexact = location) 
    elif cordinates.filter(postcode_district__iexact = location).exists():
        cordinates = cordinates.filter(postcode_district__iexact = location)
    elif cordinates.filter(postcode_area__iexact = location).exists():
        cordinates = cordinates.filter(postcode_district__iexact = location)
    elif cordinates.filter(postcode__iexact = location).exists():
        cordinates = cordinates.filter(postcode__iexact = location)
    
    ad_type = request.GET.get('ad_type') or "undefined"
    cordinates = cordinates.filter(type_of_ad__iexact = ad_type)

    min_beds = request.GET.get('min_beds') or "undefined"
    max_beds = request.GET.get('max_beds') or "undefined"
    replacer = min_max(min_beds, max_beds,1,10)
    cordinates = cordinates.filter(number_of_beds__lte = replacer[1],number_of_beds__gte = replacer[0])
    
    min_baths = request.GET.get('min_baths') or "undefined"
    max_baths = request.GET.get('max_baths') or "undefined"
    replacer = min_max(min_baths, max_baths,1, 2)
    cordinates = cordinates.filter(number_of_baths__lte = replacer[1], price__gte = replacer[0])

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

    if len(property_type)==0:
        property_type = ['house','flat','boat']
    #execution of the query
    cordinates = cordinates.filter(property_type__in = property_type).values('latitude', 'longitude','slug' ,'id', 'number_of_beds', 'main_image', 'price')
    #execute the query 
    
    i = 0
    coords = []
    while i < len(cordinates):
        coords.append(get_cordinates(cordinates,i))
        i += 1
    
    details = []
    i = 0
    while i < len(cordinates):
        details.append(get_details(cordinates, i))
        i +=1

    #All this below is for where the first the map starts
    
    latitudes = []
    longitudes = []
    
    for i in coords:
        latitudes.append(i[0])
        longitudes.append(i[1])
    
    average_latitude = (max(latitudes) + min(latitudes)) / 2
    average_longitude = (max(longitudes) + min(longitudes)) / 2
    zoom = max((max(latitudes) - min(latitudes)) , (max(longitudes) - min(longitudes)))

#   do not touch here TODO:
    if zoom <= 2:
        zoom = 2
    zoom = math.log(zoom, 2)
    #zoom = -2.57142857143 * zoom + 15
    zoom = -8 * zoom + 23
    zoom = int(round(zoom, 0))
    if zoom > 15:
        zoom = 15
    elif zoom < 6:
        zoom = 6
    
    # zoom range ---> 9-15
    start_location = (average_latitude, average_longitude)
    map = folium.Map(location=start_location, zoom_start=zoom)
    
    # these are for popup details
        
    for i in range(len(coords)):
        folium.Marker(coords[i], 
        popup='<p>Price:%d£</p><p>Number of Beds:%d</p><a href="../property/%d-%s" target=_blank>Touch here to see more details</a> <img src="../media/%s" class=map_view_photo>' %(details[i][3], details[i][2], details[i][1], details[i][0], details[i][4])).add_to(map)
    
    html_string = map.get_root().render() 
    return render(request, 'blog/post/map.html', {'html_string' : html_string})

def post_list(request):
        object_list = Post.published.all() 
        paginator = Paginator(object_list, 3) # 3 posts in each page
        page = request.GET.get('page')
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer deliver the first page
            posts = paginator.page(1)
        except EmptyPage:
            # If page is out of range deliver last page of results
            posts = paginator.page(paginator.num_pages)
        return render(request,
                    'blog/post/list.html',
                {'page': page, 'posts': posts})

class ProfileListView(LoginRequiredMixin, ListView):
    model = Post
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

    def get_queryset(self):
        post = Post.objects 
        return post.filter(author = self.request.user)
    
class PostCreateView( LoginRequiredMixin ,CreateView):
    form_class = PropertyForm
    template_name = 'blog/post/post_creation.html'
    login_url = 'login'
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
class PostUpdateView( LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'body', 'address', 'city', 'postcode','number_of_beds',
    'number_of_baths','price','property_type','main_image' ]
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
    post = get_object_or_404(Post, id=pk ,  status = 'published')
    railway_stations = NearestSchools.objects.raw("""SELECT blog_nearestrailwaystations.*,blog_nearestschools.*, search_name 
                                FROM blog_postcodes, blog_nearestschools, blog_nearestrailwaystations, blog_boundaries
                                WHERE blog_nearestschools.postcode_id = blog_postcodes.id 
				                AND blog_nearestrailwaystations.id = blog_postcodes.id 
                                AND blog_boundaries.id = blog_nearestschools.boundary_id
				                AND blog_boundaries.id = blog_nearestrailwaystations.boundary_id
                                AND blog_postcodes.postcode = '%s';"""%(post.postcode))
    return render(request, 'blog/post/detail.html', {'post':post, 'railway_stations': railway_stations})

def property_picture_form(request, pk ,slug):
    x = 1
    obj = Pictures.objects.filter(property_id=pk)
    if request.method == 'POST':
        form = PicturesForm(request.POST, request.FILES)
        images = request.FILES.getlist('image')
        for image in images:
            photo = Pictures.objects.create(property_pic = image, property_id_id = pk)
            photo.save()
        return HttpResponseRedirect('../../property/' + str(pk) + "-" + slug)
    else:
        form = PicturesForm()
    return render(request, 'blog/post/property_pictures.html', {'form': form, 'obj':obj, 'x' : x})

def property_plan_form(request, pk, slug):
    x = 1
    obj = PropertyPlan.objects.filter(property_id=pk)
    if request.method == 'POST':
        form = PropertyPlanForm(request.POST, request.FILES)
        plans = request.FILES.getlist('property_plan')
        for plan in plans:
            photo = PropertyPlan.objects.create(property_plan = plan, property_id_id = pk)
            photo.save()
        return HttpResponseRedirect('../../property/' + str(pk) + "-" + slug)
    else:
        form = PropertyPlanForm()
    return render(request, 'blog/post/property_plan_form.html', {'form': form, 'obj':obj, 'x' : x})

def filter_page(request):
    return render(request, 'blog/post/filter.html')
    
def property_save(request, pk):
    current_user = request.user
    some_data_to_dump = { 'code': 0,'message': 'save completed succesfully',}

    if current_user.is_anonymous :
        some_data_to_dump = { 'code': 1,'message': 'Go sign in first',}
    else:
        if not SavedProperties.objects.filter(property_id=pk, user_id=current_user.id).exists():
            p = SavedProperties(user_id= current_user.id, property_id= pk) 
            p.save()
        
    data = json.dumps(some_data_to_dump)
    return HttpResponse(data, content_type='application/json')

#publish__year = year,
#publish__month = month,
#publish__day = day
'''class PropertyUpdate(ListView):
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'
'''
    
    
