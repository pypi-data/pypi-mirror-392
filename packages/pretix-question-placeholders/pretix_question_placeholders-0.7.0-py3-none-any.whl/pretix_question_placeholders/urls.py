from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r"^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/question-placeholders/$",
        views.QuestionPlaceholderList.as_view(),
        name="list",
    ),
    url(
        r"^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/question-placeholders/new/$",
        views.QuestionPlaceholderCreate.as_view(),
        name="add",
    ),
    url(
        r"^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/question-placeholders/(?P<pk>[0-9]+)/$",
        views.QuestionPlaceholderEdit.as_view(),
        name="show",
    ),
    url(
        r"^control/event/(?P<organizer>[^/]+)/(?P<event>[^/]+)/question-placeholders/(?P<pk>[0-9]+)/delete/",
        views.QuestionPlaceholderDelete.as_view(),
        name="delete",
    ),
]
