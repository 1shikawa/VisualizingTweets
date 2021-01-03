from re import search
from django import forms
from django.forms import ValidationError
from .models import Stock
import re


class SearchForm(forms.Form):
    """Twitterユーザータイムライン検索フォーム"""
    screen_name = forms.CharField(label='スクリーン名', required=True,)
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
        initial=300,
        required=True,
        widget=forms.widgets.Select
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

class KeyWordSearchForm(forms.Form):
    """Twitterキーワード検索フォーム"""
    keyword = forms.CharField(label='キーワード', required=True,)
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
        initial=300,
        required=True,
        widget=forms.widgets.Select
    )
    lang = forms.ChoiceField(label='言語',
        choices=(
            ('ja', '日本'),
            ('en', '英語'),
        ),
        initial='ja',
        required=True,
        widget=forms.widgets.RadioSelect()
    )
    # locale = forms.MultipleChoiceField(label='対象範囲',
    #     choices=(('ja', '日本のみ'),),
    #     widget=forms.CheckboxSelectMultiple(),
    #     initial='ja'
    #     )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['keyword'].widget.attrs['class'] = 'form-control'
        self.fields['keyword'].widget.attrs['placeholder'] = 'キーワード'
        self.fields['display_number'].widget.attrs['class'] = 'form-control'
        self.fields['display_number'].widget.attrs['placeholder'] = '取得件数'


class FollowUsersForm(forms.Form):
    """Twitterキーワード検索フォーム"""
    keyword = forms.CharField(label='キーワード', required=True,)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['keyword'].widget.attrs['class'] = 'form-control'
        self.fields['keyword'].widget.attrs['placeholder'] = 'キーワード'


class StockCreateForm(forms.ModelForm):
    """ツイートストック用フォーム"""
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
    """ツイートストック更新フォーム"""
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


class SpecifiedUrlForm(forms.Form):
    """URL指定からのTweet取得フォーム"""
    tweet_url = forms.CharField(label='URL', required=True,)

    def clean_tweet_url(self):
        tweet_url = str(self.cleaned_data['tweet_url'])
        RE_URL = re.compile('https://twitter.com/[\w]+/status/[\d]+')
        if not(RE_URL.fullmatch(tweet_url)):
            raise forms.ValidationError(
                'TwitterのURLを入力して下さい。\n 例：https://twitter.com/user_name/status/9999999999999999999')
        return tweet_url


