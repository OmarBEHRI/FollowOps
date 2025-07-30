from django import forms
from .models import Project
from ressources.models import Ressource

class ProjectForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=Ressource.objects.all(),
        widget=forms.MultipleHiddenInput,  # ← SOLUTION
        required=False
    )
    project_manager = forms.ModelChoiceField(
        queryset=Ressource.objects.filter(appRole__in=['ADMIN', 'MANAGER']),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label="Chef de projet"
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Project._meta.get_field('tags').related_model.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control hidden', 'id': 'id_tags_select'}),
        required=False,
        label="Tags ou categories"
    )
    
    class Meta:
        model = Project
        fields = ['title', 'description', 'type', 'status', 'priority', 
                 'project_manager', 'expected_start_date', 'expected_end_date',
                 'estimated_charges', 'progress']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control h-32'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'project_manager': forms.Select(attrs={'class': 'form-control'}),
            'expected_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expected_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'estimated_charges': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1',
                'placeholder': 'Ex: 10 jours ou 80 heures'
            }),
            'progress': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'step': '1'
            }),
        }