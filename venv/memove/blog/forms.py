from django.forms import ModelForm
from .models import Post, Pictures, PropertyPlan
from django import forms

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'body','main_image', 'address', 'city', 'postcode','number_of_beds',
        'number_of_baths','price','property_type', 'type_of_ad', 'pricing',]  

class PicturesForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True})) 
    class Meta:
        model = Pictures
        fields = ('image', )

class PropertyPlanForm(forms.ModelForm):
    property_plan = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    class Meta:
        model = PropertyPlan
        fields = ('property_plan', )
    

#def __init__(self,*args,**kwargs):
    # self.prop_id = kwargs.pop('prop_id')
    #super(StylesForm,self).__init__(*args,**kwargs)
