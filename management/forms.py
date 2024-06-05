from django import forms

class CSVUploadForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            ext = file.name.split('.')[-1]
            if ext.lower() != 'csv':
                raise forms.ValidationError('This file type is not supported. Please upload a CSV file.')
        return file