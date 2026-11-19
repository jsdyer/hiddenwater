"""Retrieve the four public PSCIS records for the Chilliwack Bench case study."""
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "web/data/crossing.json"
SERVICE = "https://delivery.maps.gov.bc.ca/arcgis/rest/services/whse/bcgw_pub_whse_fish/MapServer"
LAYERS = {
    "design": (11, "PROPOSAL_DATE", "CROSSING_FIX_DESC"),
    "assessment": (15, "ASSESSMENT_DATE", "BARRIER_RESULT_DESCRIPTION"),
    "habitat": (3, "ASSMT_DATE", "HABCONF_VERIFIED_HABITAT_LEN"),
    "completion": (1, "COMPLETION_DATE", "ROAD_NAME,STREAM_NAME,CROSSING_FIX_DESC,REMEDIATION_COST"),
}


def main():
    records = {}
    for stage, (layer, date_field, fields) in LAYERS.items():
        params = {"where": "STREAM_CROSSING_ID=1474", "outFields": f"STREAM_CROSSING_ID,{date_field},{fields}",
                  "f": "pjson", "returnGeometry": "false"}
        url = f"{SERVICE}/{layer}/query?{urlencode(params)}"
        with urlopen(url, timeout=45) as response:
            matches = json.load(response)["features"]
        if len(matches) != 1 or matches[0]["attributes"]["STREAM_CROSSING_ID"] != 1474:
            raise ValueError(f"Expected one PSCIS 1474 record in {stage}")
        attrs = matches[0]["attributes"]
        stamp = attrs[date_field]
        day = datetime.fromtimestamp(stamp / 1000, timezone.utc).date().isoformat() if stamp is not None else None
        records[stage] = {"date": day, "source": url, **{key: attrs[key] for key in fields.split(",")}}
    payload = {"retrieved": datetime.now(timezone.utc).date().isoformat(), "id": 1474, "stages": records}
    temp = TARGET.with_suffix(".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    temp.replace(TARGET)


if __name__ == "__main__":
    main()
