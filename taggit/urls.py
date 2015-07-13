from django.conf.urls import patterns, url

urlpatterns = patterns('',
	url(r'^ajax/$', 'taggit.views.ajax', name='taggit-ajax'),
	url(r'^generate-tags/$', 'taggit.views.generate_tags', name='taggit-generate-tags'),
)
