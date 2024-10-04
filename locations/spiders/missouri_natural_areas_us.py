from locations.json_blob_spider import JSONBlobSpider


class MissouriNaturalAreasUSSpider(JSONBlobSpider):
    name = "missouri_natural_areas_us"
    locations_key = "features"
    start_urls = [
        "https://gisblue.mdc.mo.gov/arcgis/rest/services/Boundaries/MDC_Administrative_Boundaries/MapServer/4/query"
        "?where=1%3D1"
        "&timeRelation=esriTimeRelationOverlaps"
        "&geometryType=esriGeometryPoint"
        "&spatialRel=esriSpatialRelIntersects"
        "&units=esriSRUnit_Foot"
        "&outFields=*"
        "&returnGeometry=true"
        "&returnTrueCurves=false"
        "&outSR=4326"
        "&returnIdsOnly=false"
        "&returnCountOnly=false"
        "&returnZ=false"
        "&returnM=false"
        "&returnDistinctValues=false"
        "&returnExtentOnly=false"
        "&sqlFormat=none"
        "&featureEncoding=esriDefault"
        "&f=pjson"
    ]

    def pre_process_data(self, feature):
        feature["lat"] = feature["geometry"]["y"]
        feature["lon"] = feature["geometry"]["x"]
        feature["name"] = feature["attributes"]["NAME"].replace(" NA", " Natural Area")
        feature["ref"] = int(feature["attributes"]["DESIGORDER"])  # MDC ID
        feature["website"] = feature["attributes"]["SUMLINK"]
