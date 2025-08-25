from analytics.models import PageView, PopularPage

print(f"Total page views: {PageView.objects.count()}")
print("\nRecent views:")
for view in PageView.objects.all()[:5]:
    print(f"  {view.path} - {view.ip_address} - {view.timestamp}")

print("\nPopular pages:")
for page in PopularPage.objects.all()[:5]:
    print(f"  {page.path}: {page.total_views} views")
