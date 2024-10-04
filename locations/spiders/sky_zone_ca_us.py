from scrapy import Request

from locations.hours import DAYS_EN
from locations.linked_data_parser import LinkedDataParser
from locations.storefinders.wp_store_locator import WPStoreLocatorSpider


class SkyZoneCAUSSpider(WPStoreLocatorSpider):
    name = "sky_zone_ca_us"
    item_attributes = {"brand": "Sky Zone", "brand_wikidata": "Q7537557"}
    allowed_domains = ["skyzone.com"]
    days = DAYS_EN

    def post_process_item(self, item, response, feature):
        # Their WP Store Locator entries lack opening hours, but their individual store pages lack store numbers 🥲
        # A hybrid method is used that queries the store locator for ref codes but fetches structured data for the rest
        # Only the items derived from WP Store Locator contain the "park_id" key, so this selectively deals with those
        if "park_id" in feature:
            # Drop the item derived from the WP Store Locator...
            yield Request(
                url=feature["park_url"],
                meta={
                    # ...but make sure we keep the park ID around for later
                    "park_id": feature["park_id"]
                },
                callback=self.parse_park_page,
            )
        else:
            yield item

    def parse_park_page(self, response):
        # Use JSON5 parser because sometimes they use trailing commas
        ld = LinkedDataParser.find_linked_data(response, "LocalBusiness", "json5")

        # They also use a custom time format...
        item = LinkedDataParser.parse_ld(ld, "%I:%M%p")

        # Drop image as it's just their logo
        item["image"] = None

        # Recall the park ID from the store locator
        item["ref"] = response.meta["park_id"]

        yield item
