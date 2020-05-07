from django.test import TestCase
from django.urls import reverse_lazy
from ..models import Stock


class TestIndex(TestCase):
    """Index用のテストクラス"""

    def test_1_Index_access_success(self):
        # Indexアクセスが成功することを検証
        response = self.client.get(reverse_lazy('VisualizingTweets:Index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Visualizing Tweets')
        self.assertTemplateUsed(template_name='index.html')

    def test_2_Index_get_access_success(self):
        # Indexのgetメソッドが成功することを検証
        response = self.client.get(reverse_lazy('VisualizingTweets:Index'), {'user_id':'neet_se', 'display_number':10})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Visualizing Tweets')
        self.assertTemplateUsed(template_name='index.html')
        # self.assertTrue('user_id' in response.context)

class StockList(TestCase):
    """StockList用のテストクラス"""

    def test_3_stock_list_success(self):
        """stock一覧処理が成功することを検証"""
        response = self.client.get(reverse_lazy('VisualizingTweets:stock_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(template_name='stock_list.html')


class StockUpdate(TestCase):
    """StockUpdate用のテストクラス"""

    # テストデータ準備
    @classmethod
    def setUpTestData(cls):
        stock = Stock.objects.create(
            tweet_id = '123456',
            created_at = '2020-04-21',
            updated_at = '2020-04-21',
            tweet_created_at='2020-04-21 00:00:00'
            )

    def test_4_stock_update_success(self):
        """stock更新処理が成功することを検証"""
        data = {
            'tweet_created_at': '2020-05-21 00:00:00'
        }
        response = self.client.post('/StockUpdate/2', data)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed(template_name='stock_update.html')

    def test_5_stock_update_failure(self):
        """stock更新処理が失敗することを検証"""
        data = {
            'tweet_created_at': '2020-05-21 00:00:00'
        }
        response = self.client.post('/StockUpdate/3', data)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(template_name='stock_update.html')


class StockDelete(TestCase):
    """StockDelete用のテストクラス"""

    @classmethod
    def setUpTestData(cls):
        """テストデータ準備"""
        stock = Stock.objects.create(
            tweet_id='123456',
            created_at='2020-04-21',
            updated_at='2020-04-21',
            tweet_created_at='2020-04-21 00:00:00'
        )

    def test_6_stock_delete_success(self):
        """stock削除処理が成功することを検証"""
        data = {
            'tweet_created_at': '2020-05-21 00:00:00'
        }
        response = self.client.post('/StockDelete/1')
        self.assertEqual(response.status_code, 302)

    def test_7_stock_delete_failure(self):
        """stock削除処理が失敗することを検証"""
        data = {
            'tweet_created_at': '2020-05-21 00:00:00'
        }
        response = self.client.post('/StockDelete/2')
        self.assertEqual(response.status_code, 404)


# class StockAdd(TestCase):
#     """StockAdd用のテストクラス"""

#     def test_stock_add_success(self):
#         """stock作成処理が成功することを検証"""

#         params = {'tweet_created_at': '2020-04-21'}

#         response = self.client.post('Stock/testuser/11111')

#         # self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(template_name='stock_add.html')
#         self.assertEqual(Stock.objects.filter(tweet_id=11111).count(), 1)
