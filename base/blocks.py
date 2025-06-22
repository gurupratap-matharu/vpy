from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
    EmailBlock,
    IntegerBlock,
    ListBlock,
    PageChooserBlock,
    RichTextBlock,
    StreamBlock,
    StructBlock,
    TextBlock,
    URLBlock,
)
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

from .struct_values import LinkStructValue, RatingsStructValue


class HeadingBlock(StructBlock):
    """
    Custom `StructBlock` that allows the user to select h2 - h4 sizes for headers.
    """

    heading_text = CharBlock(required=True)
    size = ChoiceBlock(
        choices=[
            ("", "Select a header size"),
            ("h2", "H2"),
            ("h3", "H3"),
            ("h4", "H4"),
        ],
        blank=True,
        required=False,
    )

    class Meta:
        icon = "title"
        template = "blocks/heading_block.html"


class ImageBlock(StructBlock):
    """
    Custom `StructBlock` for utilizing images with associated caption and attribution data.
    """

    image = ImageChooserBlock(required=True)
    caption = CharBlock(required=False)
    attribution = CharBlock(required=False)

    class Meta:
        icon = "image"
        template = "blocks/image_block.html"


class InternalLinkBlock(StructBlock):
    title = CharBlock(
        required=False,
        help_text="Leave blank to use page's listing title.",
    )
    page = PageChooserBlock()

    class Meta:
        icon = "link"
        value_class = LinkStructValue


class ExternalLinkBlock(StructBlock):
    title = CharBlock()
    link = URLBlock()

    class Meta:
        icon = "link"
        value_class = LinkStructValue


class LinkStreamBlock(StreamBlock):
    """
    Allow editors to an internal page link or an external web link.
    """

    internal_link = InternalLinkBlock()
    external_link = ExternalLinkBlock()

    class Meta:
        template = "blocks/link_stream_block.html"
        label = "Link"
        icon = "link"
        min_num = 1
        max_num = 1


class FurtherReadingBlock(StreamBlock):
    """
    Used to show a list of internal | external links for further perusal.
    """

    internal_link = InternalLinkBlock()
    external_link = ExternalLinkBlock()

    class Meta:
        template = "blocks/further_reading_block.html"
        label = "Further Reading"
        icon = "tasks"
        min_num = 1
        max_num = 5


class ImageLinkItemBlock(StructBlock):
    """
    A single image that can be used as a link to another page on our site.
    """

    title = CharBlock(required=False, help_text="Keep it to one word only")
    image = ImageChooserBlock(required=True)
    page = PageChooserBlock()

    class Meta:
        icon = "image"


class ImageLinkBlock(StructBlock):
    """
    A collection of multiple ImageLinks.
    """

    heading_text = CharBlock(required=True)
    item = ListBlock(ImageLinkItemBlock())

    class Meta:
        icon = "list-ol"
        template = "blocks/image_link_block.html"


class PromotionsBlock(ImageLinkBlock):
    """
    Same as Image link block but renders a different template.
    """

    class Meta:
        template = "blocks/promotions_block.html"


class BlockQuote(StructBlock):
    """
    Custom `StructBlock` that allows the user to attribute a quote to the author.
    """

    text = TextBlock()
    attribute_name = CharBlock(blank=True, required=False, label="e.g. Mary Berry")

    class Meta:
        icon = "openquote"
        template = "blocks/blockquote.html"


class FAQItemBlock(StructBlock):
    question = CharBlock(required=True)
    answer = RichTextBlock(required=True)

    class Meta:
        label = "Section"
        icon = "title"


class FAQBlock(StructBlock):
    title = CharBlock(default="Frequently asked questions")
    item = ListBlock(FAQItemBlock())

    class Meta:
        icon = "list-ol"
        template = "blocks/faq_block.html"


class LinkBlock(StructBlock):
    """
    Used to show a collection of internal links typically for seo purposes.
    """

    heading_text = CharBlock(required=True)
    item = ListBlock(InternalLinkBlock())

    class Meta:
        icon = "list-ol"
        template = "blocks/link_block.html"


class NavTabItemBlock(StructBlock):
    title = CharBlock(required=True)
    content = RichTextBlock(
        required=True, icon="pilcrow", template="blocks/paragraph_block.html"
    )

    class Meta:
        label = "Section"
        icon = "title"


class NavTabBlock(StructBlock):
    title = CharBlock(required=True)
    item = ListBlock(NavTabItemBlock())

    class Meta:
        icon = "list-ol"
        template = "blocks/nav_tab_block.html"


class NavTabLinksItemBlock(StructBlock):
    title = CharBlock(required=True)
    item = ListBlock(InternalLinkBlock())

    class Meta:
        label = "Tab"
        icon = "title"


class NavTabLinksBlock(StructBlock):
    """Similar to Nav Tab block but purely used to show SEO links"""

    title = CharBlock(required=True)
    item = ListBlock(NavTabLinksItemBlock())

    class Meta:
        icon = "list-ol"
        template = "blocks/nav_tab_links_block.html"


class ContactBlock(StructBlock):
    phone = CharBlock()
    whatsapp = CharBlock()
    email = EmailBlock()
    address = TextBlock()
    website = URLBlock()

    class Meta:
        template = "blocks/contact_block.html"


class RatingsBlock(StructBlock):
    """
    Stores responses for ratings from 1 to 5 stars.
    """

    five = IntegerBlock(default=0, help_text="How many 5 stars?")
    four = IntegerBlock(default=0, help_text="How many 4 stars?")
    three = IntegerBlock(default=0, help_text="How many 3 stars?")
    two = IntegerBlock(default=0, help_text="How many 2 stars?")
    one = IntegerBlock(default=0, help_text="How many 1 star?")

    class Meta:
        icon = "pick"
        template = "blocks/ratings.html"
        label_format = "Five:{five} Four:{four} Three:{three} Two:{two} One:{one}"
        search_index = False
        value_class = RatingsStructValue


class BaseStreamBlock(StreamBlock):
    """
    Define a custom block that `StreamField` will utilize.
    """

    block_quote = BlockQuote()
    document = DocumentChooserBlock(template="blocks/document_block.html")
    embed_block = EmbedBlock(
        help_text="Insert an embed URL e.g https://www.youtube.com/watch?v=SGJFWirQ3ks",
        icon="media",
        template="blocks/embed_block.html",
    )
    faq = FAQBlock()
    further_reading = FurtherReadingBlock()
    gallery = ListBlock(ImageBlock(), template="blocks/gallery_block.html")
    heading_block = HeadingBlock()
    image_block = ImageBlock()
    link = LinkStreamBlock()
    nav_tab = NavTabBlock()
    paragraph_block = RichTextBlock(
        icon="pilcrow", template="blocks/paragraph_block.html"
    )
