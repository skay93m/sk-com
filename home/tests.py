
from django.test import TestCase, Client

class HomePageIntegrationTest(TestCase):
	def setUp(self):
		self.client = Client()

	def test_home_page_renders_correctly(self):
		response = self.client.get('/')
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'index.html')
		self.assertIn('title', response.context)
		self.assertEqual(response.context['title'], 'Home')
		self.assertIn('header', response.context)
		self.assertEqual(response.context['header'], 'Welcome!')
		self.assertIn('image', response.context)
		self.assertTrue(response.context['image'].endswith('img001.jpg'))
