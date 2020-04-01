from django.test import TestCase
from django.urls import reverse_lazy


class TestIndex(TestCase):
    """Index用のテストクラス"""

    def test_Index_access_success(self):

        response = self.client.get(reverse_lazy('VisualizingTweets:Index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Visualizing Tweets')
        self.assertTemplateUsed(template_name='index.html')

        response2 = self.client.get(reverse_lazy('VisualizingTweets:Index'), {'user_id':'neet_se', 'display_number':10})
        self.assertEqual(response2.status_code, 200)
        self.assertContains(response2, 'Visualizing Tweets')