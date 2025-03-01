"""
On loading, Wagtail will search for any app with the file `wagtail_hooks.py`
and execute the contents. This provides a way to register our own functions to execute
at certain points in Wagtail’s execution, such as when a page is saved or when the
main menu is constructed.
"""

from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from base.models import Person


class PersonViewSet(SnippetViewSet):
    """
    Add the person model to snippets section.
    """

    model = Person
    icon = "group"
    list_display = ("first_name", "last_name", "job_title", "thumb_image")


class MiscSnippetViewSetGroup(SnippetViewSetGroup):
    menu_label = "Misc"
    menu_icon = "list-ul"
    menu_order = 300
    items = (PersonViewSet,)


register_snippet(MiscSnippetViewSetGroup)
