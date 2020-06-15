from django import forms


class VideoSearchForm(forms.Form):
    """Youtube動画検索フォーム"""
    keyword = forms.CharField(label='キーワード', required=True,)
    display_number = forms.ChoiceField(label='取得件数',
        choices=(
            ('5', 5),
            ('10', 10),
            ('20', 20),
        ),
        initial=10,
        required=True,
        widget=forms.widgets.Select
    )
    order = forms.ChoiceField(label='並び順',
        choices=(
            ('date', '作成日'),
            ('viewCount', '再生数'),
        ),
        initial='date',
        required=True,
        widget=forms.widgets.RadioSelect()
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['keyword'].widget.attrs['class'] = 'form-control'
        self.fields['keyword'].widget.attrs['placeholder'] = 'キーワード'
        self.fields['display_number'].widget.attrs['class'] = 'form-control'
        self.fields['display_number'].widget.attrs['placeholder'] = '取得件数'
