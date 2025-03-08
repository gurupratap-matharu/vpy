# Generated by Django 5.1.6 on 2025-03-06 17:40

import django.core.validators
import django.db.models.deletion
import wagtail.contrib.routable_page.models
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("wagtailcore", "0094_alter_page_locale"),
        ("wagtailimages", "0027_image_description"),
    ]

    operations = [
        migrations.CreateModel(
            name="CityIndexPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                ("social_text", models.CharField(blank=True, max_length=255)),
                (
                    "listing_title",
                    models.CharField(
                        blank=True,
                        help_text="Override the page title when this page appears on listings",
                        max_length=255,
                    ),
                ),
                (
                    "listing_summary",
                    models.CharField(
                        blank=True,
                        help_text="The text description used when this page appears on listings. It's also used if meta description is absent",
                        max_length=255,
                    ),
                ),
                (
                    "appear_in_search_results",
                    models.BooleanField(
                        default=True,
                        help_text="Make this page indexable by search engines.If unchecked this page will no longer be indexed by search engines.",
                    ),
                ),
                (
                    "intro",
                    models.TextField(blank=True, help_text="Text to describe the page"),
                ),
                (
                    "listing_image",
                    models.ForeignKey(
                        blank=True,
                        help_text="Choose an image you wish to be displayed when this page appears on listings",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
                (
                    "social_image",
                    models.ForeignKey(
                        blank=True,
                        help_text="Choose an image you wish to display when this page appears on social media",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
            ],
            options={
                "verbose_name": "City Index Page",
                "verbose_name_plural": "City Index Pages",
            },
            bases=("wagtailcore.page", models.Model),
        ),
        migrations.CreateModel(
            name="CityPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                ("social_text", models.CharField(blank=True, max_length=255)),
                (
                    "listing_title",
                    models.CharField(
                        blank=True,
                        help_text="Override the page title when this page appears on listings",
                        max_length=255,
                    ),
                ),
                (
                    "listing_summary",
                    models.CharField(
                        blank=True,
                        help_text="The text description used when this page appears on listings. It's also used if meta description is absent",
                        max_length=255,
                    ),
                ),
                (
                    "appear_in_search_results",
                    models.BooleanField(
                        default=True,
                        help_text="Make this page indexable by search engines.If unchecked this page will no longer be indexed by search engines.",
                    ),
                ),
                (
                    "intro",
                    models.TextField(blank=True, help_text="Text to describe the page"),
                ),
                (
                    "lat_long",
                    models.CharField(
                        blank=True,
                        help_text="Comma separated lat/long. (Ex. 64.144367, -21.939182)                    Right click Google Maps and select 'What's Here'",
                        max_length=36,
                        validators=[
                            django.core.validators.RegexValidator(
                                code="invalid_lat_long",
                                message="Lat Long must be a comma-separated numeric lat and long",
                                regex="^(\\-?\\d+(\\.\\d+)?),\\s*(\\-?\\d+(\\.\\d+)?)$",
                            )
                        ],
                    ),
                ),
                (
                    "body",
                    wagtail.fields.StreamField(
                        [
                            ("block_quote", 2),
                            ("document", 3),
                            ("embed_block", 4),
                            ("faq", 10),
                            ("further_reading", 17),
                            ("gallery", 21),
                            ("heading_block", 23),
                            ("image_block", 20),
                            ("link", 17),
                            ("nav_tab", 27),
                            ("paragraph_block", 28),
                        ],
                        blank=True,
                        block_lookup={
                            0: ("wagtail.blocks.TextBlock", (), {}),
                            1: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {
                                    "blank": True,
                                    "label": "e.g. Mary Berry",
                                    "required": False,
                                },
                            ),
                            2: (
                                "wagtail.blocks.StructBlock",
                                [[("text", 0), ("attribute_name", 1)]],
                                {},
                            ),
                            3: (
                                "wagtail.documents.blocks.DocumentChooserBlock",
                                (),
                                {"template": "blocks/document_block.html"},
                            ),
                            4: (
                                "wagtail.embeds.blocks.EmbedBlock",
                                (),
                                {
                                    "help_text": "Insert an embed URL e.g https://www.youtube.com/watch?v=SGJFWirQ3ks",
                                    "icon": "media",
                                    "template": "blocks/embed_block.html",
                                },
                            ),
                            5: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {"default": "Frequently asked questions"},
                            ),
                            6: ("wagtail.blocks.CharBlock", (), {"required": True}),
                            7: ("wagtail.blocks.RichTextBlock", (), {"required": True}),
                            8: (
                                "wagtail.blocks.StructBlock",
                                [[("question", 6), ("answer", 7)]],
                                {},
                            ),
                            9: ("wagtail.blocks.ListBlock", (8,), {}),
                            10: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 5), ("item", 9)]],
                                {},
                            ),
                            11: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {
                                    "help_text": "Leave blank to use page's listing title.",
                                    "required": False,
                                },
                            ),
                            12: ("wagtail.blocks.PageChooserBlock", (), {}),
                            13: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 11), ("page", 12)]],
                                {},
                            ),
                            14: ("wagtail.blocks.CharBlock", (), {}),
                            15: ("wagtail.blocks.URLBlock", (), {}),
                            16: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 14), ("link", 15)]],
                                {},
                            ),
                            17: (
                                "wagtail.blocks.StreamBlock",
                                [[("internal_link", 13), ("external_link", 16)]],
                                {},
                            ),
                            18: (
                                "wagtail.images.blocks.ImageChooserBlock",
                                (),
                                {"required": True},
                            ),
                            19: ("wagtail.blocks.CharBlock", (), {"required": False}),
                            20: (
                                "wagtail.blocks.StructBlock",
                                [[("image", 18), ("caption", 19), ("attribution", 19)]],
                                {},
                            ),
                            21: (
                                "wagtail.blocks.ListBlock",
                                (20,),
                                {"template": "blocks/gallery_block.html"},
                            ),
                            22: (
                                "wagtail.blocks.ChoiceBlock",
                                [],
                                {
                                    "blank": True,
                                    "choices": [
                                        ("", "Select a header size"),
                                        ("h2", "H2"),
                                        ("h3", "H3"),
                                        ("h4", "H4"),
                                    ],
                                    "required": False,
                                },
                            ),
                            23: (
                                "wagtail.blocks.StructBlock",
                                [[("heading_text", 6), ("size", 22)]],
                                {},
                            ),
                            24: (
                                "wagtail.blocks.RichTextBlock",
                                (),
                                {
                                    "icon": "pilcrow",
                                    "required": True,
                                    "template": "blocks/paragraph_block.html",
                                },
                            ),
                            25: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 6), ("content", 24)]],
                                {},
                            ),
                            26: ("wagtail.blocks.ListBlock", (25,), {}),
                            27: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 6), ("item", 26)]],
                                {},
                            ),
                            28: (
                                "wagtail.blocks.RichTextBlock",
                                (),
                                {
                                    "icon": "pilcrow",
                                    "template": "blocks/paragraph_block.html",
                                },
                            ),
                        },
                        verbose_name="Page body",
                    ),
                ),
                (
                    "faq",
                    wagtail.fields.StreamField(
                        [("faq", 5)],
                        blank=True,
                        block_lookup={
                            0: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {"default": "Frequently asked questions"},
                            ),
                            1: ("wagtail.blocks.CharBlock", (), {"required": True}),
                            2: ("wagtail.blocks.RichTextBlock", (), {"required": True}),
                            3: (
                                "wagtail.blocks.StructBlock",
                                [[("question", 1), ("answer", 2)]],
                                {},
                            ),
                            4: ("wagtail.blocks.ListBlock", (3,), {}),
                            5: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 0), ("item", 4)]],
                                {},
                            ),
                        },
                        verbose_name="FAQ Section",
                    ),
                ),
                (
                    "links",
                    wagtail.fields.StreamField(
                        [("Links", 7)],
                        blank=True,
                        block_lookup={
                            0: ("wagtail.blocks.CharBlock", (), {"required": True}),
                            1: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {
                                    "help_text": "Leave blank to use page's listing title.",
                                    "required": False,
                                },
                            ),
                            2: ("wagtail.blocks.PageChooserBlock", (), {}),
                            3: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 1), ("page", 2)]],
                                {},
                            ),
                            4: ("wagtail.blocks.ListBlock", (3,), {}),
                            5: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 0), ("item", 4)]],
                                {},
                            ),
                            6: ("wagtail.blocks.ListBlock", (5,), {}),
                            7: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 0), ("item", 6)]],
                                {},
                            ),
                        },
                        verbose_name="Links Section",
                    ),
                ),
                (
                    "companies",
                    wagtail.fields.StreamField(
                        [("Links", 5)],
                        blank=True,
                        block_lookup={
                            0: ("wagtail.blocks.CharBlock", (), {"required": True}),
                            1: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {
                                    "help_text": "Leave blank to use page's listing title.",
                                    "required": False,
                                },
                            ),
                            2: ("wagtail.blocks.PageChooserBlock", (), {}),
                            3: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 1), ("page", 2)]],
                                {},
                            ),
                            4: ("wagtail.blocks.ListBlock", (3,), {}),
                            5: (
                                "wagtail.blocks.StructBlock",
                                [[("heading_text", 0), ("item", 4)]],
                                {},
                            ),
                        },
                        verbose_name="Companies Section",
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        blank=True,
                        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
                (
                    "listing_image",
                    models.ForeignKey(
                        blank=True,
                        help_text="Choose an image you wish to be displayed when this page appears on listings",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
                (
                    "social_image",
                    models.ForeignKey(
                        blank=True,
                        help_text="Choose an image you wish to display when this page appears on social media",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
            ],
            options={
                "verbose_name": "CityPage",
                "verbose_name_plural": "CityPages",
            },
            bases=("wagtailcore.page", models.Model),
        ),
        migrations.CreateModel(
            name="StationPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                ("social_text", models.CharField(blank=True, max_length=255)),
                (
                    "listing_title",
                    models.CharField(
                        blank=True,
                        help_text="Override the page title when this page appears on listings",
                        max_length=255,
                    ),
                ),
                (
                    "listing_summary",
                    models.CharField(
                        blank=True,
                        help_text="The text description used when this page appears on listings. It's also used if meta description is absent",
                        max_length=255,
                    ),
                ),
                (
                    "appear_in_search_results",
                    models.BooleanField(
                        default=True,
                        help_text="Make this page indexable by search engines.If unchecked this page will no longer be indexed by search engines.",
                    ),
                ),
                (
                    "intro",
                    models.TextField(blank=True, help_text="Text to describe the page"),
                ),
                (
                    "body",
                    wagtail.fields.StreamField(
                        [
                            ("block_quote", 2),
                            ("document", 3),
                            ("embed_block", 4),
                            ("faq", 10),
                            ("further_reading", 17),
                            ("gallery", 21),
                            ("heading_block", 23),
                            ("image_block", 20),
                            ("link", 17),
                            ("nav_tab", 27),
                            ("paragraph_block", 28),
                        ],
                        blank=True,
                        block_lookup={
                            0: ("wagtail.blocks.TextBlock", (), {}),
                            1: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {
                                    "blank": True,
                                    "label": "e.g. Mary Berry",
                                    "required": False,
                                },
                            ),
                            2: (
                                "wagtail.blocks.StructBlock",
                                [[("text", 0), ("attribute_name", 1)]],
                                {},
                            ),
                            3: (
                                "wagtail.documents.blocks.DocumentChooserBlock",
                                (),
                                {"template": "blocks/document_block.html"},
                            ),
                            4: (
                                "wagtail.embeds.blocks.EmbedBlock",
                                (),
                                {
                                    "help_text": "Insert an embed URL e.g https://www.youtube.com/watch?v=SGJFWirQ3ks",
                                    "icon": "media",
                                    "template": "blocks/embed_block.html",
                                },
                            ),
                            5: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {"default": "Frequently asked questions"},
                            ),
                            6: ("wagtail.blocks.CharBlock", (), {"required": True}),
                            7: ("wagtail.blocks.RichTextBlock", (), {"required": True}),
                            8: (
                                "wagtail.blocks.StructBlock",
                                [[("question", 6), ("answer", 7)]],
                                {},
                            ),
                            9: ("wagtail.blocks.ListBlock", (8,), {}),
                            10: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 5), ("item", 9)]],
                                {},
                            ),
                            11: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {
                                    "help_text": "Leave blank to use page's listing title.",
                                    "required": False,
                                },
                            ),
                            12: ("wagtail.blocks.PageChooserBlock", (), {}),
                            13: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 11), ("page", 12)]],
                                {},
                            ),
                            14: ("wagtail.blocks.CharBlock", (), {}),
                            15: ("wagtail.blocks.URLBlock", (), {}),
                            16: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 14), ("link", 15)]],
                                {},
                            ),
                            17: (
                                "wagtail.blocks.StreamBlock",
                                [[("internal_link", 13), ("external_link", 16)]],
                                {},
                            ),
                            18: (
                                "wagtail.images.blocks.ImageChooserBlock",
                                (),
                                {"required": True},
                            ),
                            19: ("wagtail.blocks.CharBlock", (), {"required": False}),
                            20: (
                                "wagtail.blocks.StructBlock",
                                [[("image", 18), ("caption", 19), ("attribution", 19)]],
                                {},
                            ),
                            21: (
                                "wagtail.blocks.ListBlock",
                                (20,),
                                {"template": "blocks/gallery_block.html"},
                            ),
                            22: (
                                "wagtail.blocks.ChoiceBlock",
                                [],
                                {
                                    "blank": True,
                                    "choices": [
                                        ("", "Select a header size"),
                                        ("h2", "H2"),
                                        ("h3", "H3"),
                                        ("h4", "H4"),
                                    ],
                                    "required": False,
                                },
                            ),
                            23: (
                                "wagtail.blocks.StructBlock",
                                [[("heading_text", 6), ("size", 22)]],
                                {},
                            ),
                            24: (
                                "wagtail.blocks.RichTextBlock",
                                (),
                                {
                                    "icon": "pilcrow",
                                    "required": True,
                                    "template": "blocks/paragraph_block.html",
                                },
                            ),
                            25: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 6), ("content", 24)]],
                                {},
                            ),
                            26: ("wagtail.blocks.ListBlock", (25,), {}),
                            27: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 6), ("item", 26)]],
                                {},
                            ),
                            28: (
                                "wagtail.blocks.RichTextBlock",
                                (),
                                {
                                    "icon": "pilcrow",
                                    "template": "blocks/paragraph_block.html",
                                },
                            ),
                        },
                        verbose_name="Page body",
                    ),
                ),
                ("address", models.TextField()),
                (
                    "lat_long",
                    models.CharField(
                        blank=True,
                        help_text="Comma separated lat/long. (Ex. 64.144367, -21.939182)                    Right click Google Maps and select 'What's Here'",
                        max_length=36,
                        validators=[
                            django.core.validators.RegexValidator(
                                code="invalid_lat_long",
                                message="Lat Long must be a comma-separated numeric lat and long",
                                regex="^(\\-?\\d+(\\.\\d+)?),\\s*(\\-?\\d+(\\.\\d+)?)$",
                            )
                        ],
                    ),
                ),
                (
                    "faq",
                    wagtail.fields.StreamField(
                        [("faq", 5)],
                        blank=True,
                        block_lookup={
                            0: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {"default": "Frequently asked questions"},
                            ),
                            1: ("wagtail.blocks.CharBlock", (), {"required": True}),
                            2: ("wagtail.blocks.RichTextBlock", (), {"required": True}),
                            3: (
                                "wagtail.blocks.StructBlock",
                                [[("question", 1), ("answer", 2)]],
                                {},
                            ),
                            4: ("wagtail.blocks.ListBlock", (3,), {}),
                            5: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 0), ("item", 4)]],
                                {},
                            ),
                        },
                        verbose_name="FAQ Section",
                    ),
                ),
                (
                    "links",
                    wagtail.fields.StreamField(
                        [("Links", 5)],
                        blank=True,
                        block_lookup={
                            0: ("wagtail.blocks.CharBlock", (), {"required": True}),
                            1: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {
                                    "help_text": "Leave blank to use page's listing title.",
                                    "required": False,
                                },
                            ),
                            2: ("wagtail.blocks.PageChooserBlock", (), {}),
                            3: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 1), ("page", 2)]],
                                {},
                            ),
                            4: ("wagtail.blocks.ListBlock", (3,), {}),
                            5: (
                                "wagtail.blocks.StructBlock",
                                [[("heading_text", 0), ("item", 4)]],
                                {},
                            ),
                        },
                        verbose_name="Links Section",
                    ),
                ),
                (
                    "companies",
                    wagtail.fields.StreamField(
                        [("Links", 5)],
                        blank=True,
                        block_lookup={
                            0: ("wagtail.blocks.CharBlock", (), {"required": True}),
                            1: (
                                "wagtail.blocks.CharBlock",
                                (),
                                {
                                    "help_text": "Leave blank to use page's listing title.",
                                    "required": False,
                                },
                            ),
                            2: ("wagtail.blocks.PageChooserBlock", (), {}),
                            3: (
                                "wagtail.blocks.StructBlock",
                                [[("title", 1), ("page", 2)]],
                                {},
                            ),
                            4: ("wagtail.blocks.ListBlock", (3,), {}),
                            5: (
                                "wagtail.blocks.StructBlock",
                                [[("heading_text", 0), ("item", 4)]],
                                {},
                            ),
                        },
                        verbose_name="Companies Section",
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        blank=True,
                        help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
                (
                    "listing_image",
                    models.ForeignKey(
                        blank=True,
                        help_text="Choose an image you wish to be displayed when this page appears on listings",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
                (
                    "social_image",
                    models.ForeignKey(
                        blank=True,
                        help_text="Choose an image you wish to display when this page appears on social media",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
            ],
            options={
                "verbose_name": "Station Page",
                "verbose_name_plural": "Station Pages",
            },
            bases=(
                wagtail.contrib.routable_page.models.RoutablePageMixin,
                "wagtailcore.page",
                models.Model,
            ),
        ),
    ]
