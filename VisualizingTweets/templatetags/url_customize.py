from urllib import parse
from django import template
from django.shortcuts import resolve_url

register = template.Library()


@register.filter(is_safe=True)
def url_target_blank(text):
    return text.replace('<a ', '<a target="_blank" rel="nofollow" ')


@register.simple_tag
def get_return_link(request):
    top_page = resolve_url('VisualizingTweets:index')  # Index
    referer = request.environ.get('HTTP_REFERER')  # これが、前ページのURL

    # URL直接入力やお気に入りアクセスのときはリファラがないので、トップぺージに戻す
    if referer:
        # リファラがある場合、前回ページが自分のサイト内であれば、そこに戻す。
        parse_result = parse.urlparse(referer)
        if request.get_host() == parse_result.netloc:
            return referer

    return top_page
