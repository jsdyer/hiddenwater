# Hidden Water

Explore Langley’s creeks, drainage channels and mapped culverts.

**[Open the live browser tool](https://coolcode.ca/hiddenwater/)** · [CoolCode catalogue](https://coolcode.ca/)

No installation or account is needed to use the tool. This repository contains its independent source, tests and GitHub Pages publishing workflow.

<!-- coolcode:guide -->
At Chilliwack Bench, compare the verified habitat length in the database with the length of habitat the project report says became accessible.
<!-- /coolcode:guide -->

## Chilliwack Bench crossing

The case study joins four provincial Fish Passage (PSCIS) layers on crossing ID 1474. Follow the design, barrier assessment, habitat confirmation and completed work in chronological order. Each stage opens its exact source record. The 2011 confirmation lists 2,500 m of verified habitat. The [provincial report, project 21, PDF p. 16](https://www2.gov.bc.ca/assets/gov/environment/plants-animals-and-ecosystems/fish-fish-habitat/fish-passage/fish-passage/fish_passage_program_2008-2017.pdf#page=16) credits the open-bottom arch with restoring access to 1,000 m of high-value habitat. The completion layer records a cost of $211,500 CAD. The report identifies cutthroat trout and possible coho use. A reciprocal link opens the related DFO Chilliwack River coho series in Salmon Lines.

The weekly refresh runs `python3 scripts/crossing.py` against the provincial layers. It checks each returned crossing ID before replacing the dated snapshot. The report excerpt describes a historical publication, while the database values follow the provincial records.

## What you can do

- Search waterways by name, municipality, type and published classification.
- Pan the map, use neighbourhood shortcuts, inspect source records, and share a segment.
- Follow named waterways to the [BC Place Names Explorer](https://coolcode.ca/bcplacenames/). A set of local names links directly to a reviewed provincial name record. Other named segments offer a general search link.
- Export matching records as CSV or GeoJSON with source IDs and retrieval time.

The first snapshot contains **28,921 segments**: 20,597 Township channels, 8,012 Township culverts and 312 City watercourses. Counts are segments, not separate rivers. Culverts are optional and off initially.

## Data and interpretation

- [Township drainage channels](https://services5.arcgis.com/frpHL0Fv8koQRVWY/arcgis/rest/services/Drainage_Channels/FeatureServer/0)
- [Township drainage culverts](https://services5.arcgis.com/frpHL0Fv8koQRVWY/arcgis/rest/services/Drainage_Culverts/FeatureServer/0)
- [City watercourse classifications](https://maps.langleycity.ca/server/rest/services/Maps/Open_Data/MapServer/185)

Township channel classifications are explicitly **unofficial** in the source. City classifications use their own code mapping. Neither classification establishes current fish occupancy. Missing features do not establish that water is absent; this is not a survey, setback assessment, flood model or access guide. The app does not infer buried streams or flow direction. Culverts are Township data only.

Contains municipal public mapping information, subject to the linked source terms. OpenStreetMap contributors supply the basemap; Leaflet's licence is included in `web/vendor/LICENSE`. Retrieval dates are shown in the app and do not represent survey dates.

## Development

```sh
node --test tests/*.test.mjs
python3 -m unittest discover -s tests -v
python3 scripts/build.py
```

The offline build expands the lossless `web/data/water.json.gz` snapshot to `dist/data/water.json`. It writes `dist/` and works at the project subpath `/hiddenwater/`. Do not commit `dist/` or add a `CNAME`; the account’s main Pages site supplies the coolcode.ca domain. Node is used for tests, not a frontend dependency bundle.

`web/` contains the application; `scripts/` contains the offline builder and data refresh; `tests/` contains model/source/build checks and Chromium user-flow tests. Browser checks cover project paths, controls, sharing, exports or layer selection, error handling, and mobile overflow. GitHub Actions installs their test-only dependencies from `tests/browser-requirements.txt`.

## Publishing and maintenance

`.github/workflows/pages.yml` checks pull requests and main commits. Only a successful main build deploys. Repository Settings → Pages must use **GitHub Actions**. The browser-checks artifact contains desktop/mobile screenshots. A failed build leaves the previous deployment in place.

`.github/dependabot.yml` enables **GitHub Dependabot**, which proposes updates to workflow actions and configured dependencies as pull requests. A proposal does not update main until merged. Review the diff and checks for the current PR commit before merging. Netlify is not used by this project.

`tool.json` describes this tool in the CoolCode catalogue. Its reviewed record belongs in `jsdyer/jsdyer.github.io/data/tools.json`; run that repository’s `scripts/sync_readme.py` to keep the hub README and polished homepage aligned. Changing this repository alone does not change the homepage listing.

## Data refreshes

`.github/workflows/refresh.yml` runs weekly (Tuesday 08:23 UTC) and can be started manually from Actions → Data snapshot · Refresh and publish. GitHub schedules can be delayed and may be paused for inactive public repositories; the visible retrieval date is the source of truth.

The workflow fetches and validates complete source responses, runs unit/browser checks, then commits the snapshot with GitHub’s Actions token and deploys the same tested build. Failed refreshes do not replace the last successful deployment. A normal non-force push protects concurrent edits; a rejected push stops deployment. This is the only workflow with `contents: write`; ordinary checks use read-only repository access.

Manual refresh:

```sh
python3 scripts/refresh.py
```

Review source/count changes before committing.

## Privacy

The app does not retain searches or location history. Searches run against a bundled public snapshot in your browser. OpenStreetMap receives tile requests for the viewed map area. There are no accounts or analytics. Sharing places the selected record or comparison view in the URL; it does not upload private files. External source links open the original provider.
