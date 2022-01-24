from .models import Post, Pictures, PropertyPlan
from django import forms



class PropertyForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'body', 'main_image', 'address', 'city', 'postcode', 'number_of_beds',
                  'number_of_baths', 'rent', 'property_type']


class PicturesForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    class Meta:
        model = Pictures
        fields = ('image',)


# Add something for contact
class ContactForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField(required=False)
    head = forms.CharField(required=False)
    body = forms.CharField(widget=forms.Textarea())


class PropertyPlanForm(forms.ModelForm):
    property_plan = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = PropertyPlan
        fields = ('property_plan',)
