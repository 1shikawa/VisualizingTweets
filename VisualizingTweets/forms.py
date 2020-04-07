from django import forms
from .models import Stock


class SearchForm(forms.Form):
    user_id = forms.CharField(label='ユーザーID', required=True,)
    display_number = forms.ChoiceField(label='取得件数',
        choices=(
            ('10', 10),
            ('30', 30),
            ('50', 50),
            ('100', 100),
            ('300', 300),
            ('500', 500),
            ('800', 800),
            ('1000', 1000),
        ),
        required=True,
        widget=forms.widgets.Select
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['tweet_id', 'user_id', 'user_name', 'tweet_text',
                  'tweet_url', 'tweet_created_at', 'favorite_count', 'retweet_count', 'expanded_url',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label
            field.widget.attrs['readonly'] = 'readonly'
