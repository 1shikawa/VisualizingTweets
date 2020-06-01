# from django import forms


# class LiveSearchForm(forms.Form):
#     """Twitterユーザータイムライン検索フォーム"""
#     screen_name = forms.CharField(label='スクリーンネーム', required=True,)

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for field in self.fields.values():
#             field.widget.attrs['class'] = 'form-control'
#             field.widget.attrs['placeholder'] = field.label
