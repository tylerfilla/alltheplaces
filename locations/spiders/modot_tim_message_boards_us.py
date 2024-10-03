import re

from locations.json_blob_spider import JSONBlobSpider


class ModotTimMessageBoardsUSSpider(JSONBlobSpider):
    name = "modot_tim_message_boards_us"
    start_urls = ["https://traveler.modot.org/timconfig/feed/desktop/MsgBrdV1.json"]

    def post_process_item(self, item, response, feature):
        item["extras"]["traffic_sign"] = "variable_message"
        item["lon"] = feature["x"]
        item["lat"] = feature["y"]
        item["ref"] = feature["dev"]

        # If sign location refers to an interstate, US, or state route, it's safe to assume MoDOT owns and operates it
        # We can't really make that assumption about other signs, as regional TMC partners might be involved
        if re.match(r"(?:i|us|mo|rte?)\s*[a-z0-9]{1,3}", feature["dev"], re.IGNORECASE):
            item["extras"]["operator"] = "Missouri Department of Transportation"
            item["extras"]["operator:short"] = "MoDOT"
            item["extras"]["operator:type"] = "government"
            item["extras"]["operator:wikidata"] = "Q5557977"
            item["extras"]["owner"] = "Missouri Department of Transportation"
            item["extras"]["owner:short"] = "MoDOT"
            item["extras"]["owner:type"] = "government"
            item["extras"]["owner:wikidata"] = "Q5557977"

        yield item
