import logging
import re

from locations.json_blob_spider import JSONBlobSpider


def _clean_office_name(name):
    # There's one special case where parentheses are important
    # Don't know why this office puts part of its official name in parentheses
    if name == "DOWNTOWN (ST LOUIS)":
        name = "Downtown Saint Louis"

    # Remove hyphenated comments in name field
    if "-" in name:
        name = name[: name.find("-")]

    # Remove parenthesized comments in name field
    if "(" in name:
        name = name[: name.find("(")]

    # Official name ends with suffix "License Office"
    name = name.title().strip() + " License Office"

    return name


def _clean_office_facebook(x):
    if not isinstance(x, str):
        return None

    # Yes, sometimes the TLD is missing...
    if "://www.facebook/" in x:
        x = x.replace("://www.facebook/", "://www.facebook.com/")
    if "://m.facebook/" in x:
        x = x.replace("://m.facebook/", "://m.facebook.com/")

    # If we're dealing with a profile ID instead of a username
    # Just give a normalized URL to the Facebook page using the ID number
    if "/profile.php" in x:
        # Example: https://www.facebook.com/profile.php?id=100095153615010
        uid = re.search(r"facebook\.com/profile\.php\?id=([0-9]+)", x).group(1)
        return f"https://www.facebook.com/profile.php?id={uid}"
    if "/pages/" in x:
        # Example: https://www.facebook.com/pages/Bowling-Green-License-Office/952352194843286
        uid = re.search(r"facebook\.com/pages/[A-Za-z0-9-]+/([0-9]+)", x).group(1)
        return f"https://www.facebook.com/profile.php?id={uid}"

    # Extract username from clean URL
    match = re.search(r"facebook\.com/([^/?]+)", x)
    return match.group(1) if match else None


def _clean_office_twitter(x):
    if not isinstance(x, str):
        return None

    # If the "URL" is actually a handle
    if x.startswith("@"):
        return x[1:]

    # Be ready for missing TLD on the apex or its mobile subdomain
    if "://www.twitter/" in x:
        x = x.replace("://www.twitter/", "://www.twitter.com/")
    if "://www.x/" in x:
        x = x.replace("://www.x/", "://www.x.com/")
    if "://mobile.twitter/" in x:
        x = x.replace("://mobile.twitter/", "://mobile.twitter.com/")
    if "://mobile.x" in x:
        x = x.replace("://mobile.x", "://mobile.x.com/")

    # We'll just normalize the apex domain...
    x = x.replace("x.com/", "twitter.com/")

    # Extract username from the clean URL
    match = re.search(r"twitter.com/@?([^/?]+)", x)
    return match.group(1) if match else None


class MissouriLicenseOfficesUSSpider(JSONBlobSpider):
    name = "missouri_license_offices_us"
    start_urls = ["https://data.mo.gov/resource/835g-7keg.json"]

    def pre_process_data(self, feature):
        feature["lat"] = feature["latlng"]["latitude"]
        feature["lon"] = feature["latlng"]["longitude"]
        feature["name"] = _clean_office_name(feature["name"])
        feature["ref"] = feature["number"]

    def post_process_item(self, item, response, feature):
        # Some entries use the name field to indicate permanent or temporary closure
        if "closed" in feature["name"].lower() or "closing" in feature["name"].lower():
            logging.log(logging.INFO, f"Considering office {item['ref']} closed based on name: {feature['name']}")
            return

        item["facebook"] = _clean_office_facebook(feature.get("facebook_url"))
        item["twitter"] = _clean_office_twitter(feature.get("twitter_url"))

        yield item
