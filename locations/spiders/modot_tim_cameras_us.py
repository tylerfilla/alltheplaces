import re

from locations.categories import Categories, apply_category
from locations.json_blob_spider import JSONBlobSpider

_REGEX_URL_MODOT = re.compile(
    r"^https?://sfs[0-9][0-9]-traveler\.modot\.mo\.gov(?::443)?/rtplive/MODOT_CAM_([0-9]+)/playlist\.m3u8$"
)
_REGEX_URL_KC_SCOUT = re.compile(
    r"^https?://5fca316e7c40f\.streamlock\.net/live-secure/([A-Z0-9-]+)-LQ\.stream/playlist\.m3u8$"
)
_REGEX_URL_OZARKS_TRAFFIC = re.compile(r"^https?://s2\.ozarkstrafficoneview\.com/rtplive/CAM([0-9]+)/playlist\.m3u8$")


class ModotTimCamerasUSSpider(JSONBlobSpider):
    name = "modot_tim_cameras_us"
    no_refs = True  # Don't dedupe refs, as multiple owners/operators are involved
    start_urls = ["https://traveler.modot.org/timconfig/feed/desktop/StreamingCams2.json"]

    def post_process_item(self, item, response, feature):
        apply_category(Categories.SURVEILLANCE_CAMERA, item)

        item["extras"]["surveillance:zone"] = "traffic"
        item["lon"] = feature["x"]
        item["lat"] = feature["y"]
        item["name"] = feature["location"]

        url = feature["html"]

        # These cameras are owned and operated by MoDOT alone (including Gateway Guide cameras)
        match_modot = _REGEX_URL_MODOT.search(url)
        if match_modot:
            item["extras"]["operator"] = "Missouri Department of Transportation"
            item["extras"]["operator:short"] = "MoDOT"
            item["extras"]["operator:type"] = "government"
            item["extras"]["operator:wikidata"] = "Q5557977"
            item["extras"]["owner"] = "Missouri Department of Transportation"
            item["extras"]["owner:short"] = "MoDOT"
            item["extras"]["owner:type"] = "government"
            item["extras"]["owner:wikidata"] = "Q5557977"
            item["ref"] = match_modot.group(1)

        # These cameras are owned either by KDOT or MoDOT (unclear and possibly varies by camera)
        # They are jointly operated at MoDOT's TMC in Lee's Summit, MO, under the KC Scout partnership program
        match_kc_scout = _REGEX_URL_KC_SCOUT.search(url)
        if match_kc_scout:
            item["extras"]["operator"] = "Kansas City Scout"
            item["extras"]["operator:short"] = "KC Scout"
            item["extras"]["operator:type"] = "partnership"
            item["extras"]["operator:wikidata"] = "Q16851572"
            item["ref"] = match_kc_scout.group(1)

        # These cameras are owned either by the City of Springfield or MoDOT (unclear and possibly varies by camera)
        # They are jointly operated at MoDOT's TMC in Springfield, MO, under the TMC of the Ozarks partnership program
        match_ozarks_traffic = _REGEX_URL_OZARKS_TRAFFIC.search(url)
        if match_ozarks_traffic:
            item["extras"]["operator"] = "Transportation Management Center of the Ozarks"
            item["extras"]["operator:short"] = "TMC of the Ozarks"
            item["extras"]["operator:type"] = "partnership"
            item["extras"]["operator:wikidata"] = "Q130397579"
            item["ref"] = match_ozarks_traffic.group(1)

        yield item
