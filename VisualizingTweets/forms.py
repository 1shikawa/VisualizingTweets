from django import forms
from .models import Stock


class SearchForm(forms.Form):
    screen_name = forms.CharField(label='ユーザー名', required=True,)
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


class StockCreateForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['tweet_id', 'user_id', 'screen_name', 'user_name','tweet_text',
                  'tweet_url', 'tweet_created_at', 'favorite_count', 'retweet_count', 'expanded_url',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label
            field.widget.attrs['readonly'] = 'readonly'


class StockUpdateForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['tweet_id', 'user_id', 'screen_name', 'user_name', 'tweet_text',
                  'tweet_url', 'tweet_created_at', 'favorite_count', 'retweet_count', 'expanded_url',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tweet_id'].widget.attrs['class'] = 'form-control'
        self.fields['tweet_id'].widget.attrs['readonly'] = 'readonly'
        self.fields['user_id'].widget.attrs['class'] = 'form-control'
        self.fields['user_id'].widget.attrs['readonly'] = 'readonly'
        self.fields['screen_name'].widget.attrs['class'] = 'form-control'
        self.fields['screen_name'].widget.attrs['readonly'] = 'readonly'
        self.fields['user_name'].widget.attrs['class'] = 'form-control'
        self.fields['user_name'].widget.attrs['readonly'] = 'readonly'
        self.fields['tweet_text'].widget.attrs['class'] = 'form-control'
        # self.fields['tweet_url'].widget.attrs['readonly'] = 'readonly'
        self.fields['tweet_url'].widget.attrs['class'] = 'form-control'
        self.fields['tweet_url'].widget.attrs['readonly'] = 'readonly'
        self.fields['tweet_created_at'].widget.attrs['class'] = 'form-control'
        self.fields['tweet_created_at'].widget.attrs['readonly'] = 'readonly'
        self.fields['favorite_count'].widget.attrs['class'] = 'form-control'
        self.fields['favorite_count'].widget.attrs['readonly'] = 'readonly'
        self.fields['retweet_count'].widget.attrs['class'] = 'form-control'
        self.fields['retweet_count'].widget.attrs['readonly'] = 'readonly'
        self.fields['expanded_url'].widget.attrs['class'] = 'form-control'
        self.fields['expanded_url'].widget.attrs['readonly'] = 'readonly'


