import chompjs
from scrapy.spiders import SitemapSpider

from locations.dict_parser import DictParser
from locations.hours import OpeningHours


class LongJohnSilversUSSpider(SitemapSpider):
    name = "long_john_silvers_us"
    item_attributes = {"brand": "Long John Silver's", "brand_wikidata": "Q1535221"}
    sitemap_urls = ["https://www.ljsilvers.com/sitemap.xml"]
    sitemap_rules = [("/locations/[a-z]{2}", "parse")]

    def parse(self, response, **kwargs):
        script = None
        for script in response.xpath("//script/text()"):
            if script.re(r"window\.__NUXT__"):
                break

        # LJS uses Nuxt.js with store metadata locked in an immediately-invoked function expression (IIFE)
        # Here we extract the IIFE's parameter declaration, code block, and invocation argument strings
        script_iife_params_str = script.re_first(r"window\.__NUXT__=function\((.*)\)\{.*\}\(.*\)")
        script_iife_body_str = script.re_first(r"window\.__NUXT__=function\(.*\)\{(.*)\}\(.*\)")
        script_iife_args_str = script.re_first(r"window\.__NUXT__=function\(.*\)\{.*\}\((.*)\)")

        # Handle arguments passed to IIFE function by pretending they're actually a JavaScript array
        # That way chompjs can be used to extract the arguments without needing to interpret the code
        params = {}
        param_values = chompjs.parse_js_object(f"[{script_iife_args_str}]")
        for i, key in enumerate(script_iife_params_str.split(",")):
            value = param_values[i]

            # Expand minified bools
            if value == "!0":
                value = True
            elif value == "!1":
                value = False

            params[key] = value

        # Extract the store data; parameters referenced by name have become strings
        # It depends on the context whether single-letter strings should be considered parameter references
        feature = chompjs.parse_js_object(script_iife_body_str[6:])["data"][0]["location"]
        item = DictParser.parse(feature)

        item["street_address"] = item["addr_full"]
        item["addr_full"] = None
        item["website"] = response.url

        name = feature["name"]
        if name in params:
            item["name"] = params[name]
        ref = feature["store_no"]
        if ref in params:
            item["ref"] = params[ref]

        item["opening_hours"] = OpeningHours()
        for hour in feature["hours"]:
            hour_day = hour.get("day")
            if hour_day in params:
                hour_day = params[hour_day]
            hour_open = hour.get("open")
            if hour_open in params:
                hour_open = params[hour_open]
            hour_close = hour.get("close")
            if hour_close in params:
                hour_close = params[hour_close]
            item["opening_hours"].add_range(hour_day, hour_open, hour_close)

        yield item
