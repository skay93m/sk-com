
from django.test import TestCase, Client
from home.models import Hero

class HomePageIntegrationTest(TestCase):
	def setUp(self):
		self.client = Client()
		# Create a Hero object for the test
		self.hero = Hero.objects.create(
			header='Welcome!',
			tagline='Test tagline',
			cta='Test CTA'
		)

	def test_home_page_renders_correctly(self):
		response = self.client.get('/', follow=True)
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, 'index.html')
		self.assertIn('title', response.context)
		self.assertEqual(response.context['title'], 'Home')
		self.assertIn('header', response.context)
		self.assertEqual(response.context['header'], 'Welcome!')
