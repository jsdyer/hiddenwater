"""Build the documented Fraser Valley case from its independently dated PSCIS rows."""
from html import escape

REPORT = "https://www2.gov.bc.ca/assets/gov/environment/plants-animals-and-ecosystems/fish-fish-habitat/fish-passage/fish-passage/fish_passage_program_2008-2017.pdf#page=16"


def render_case(data):
    stages = data["stages"]

    def text(value):
        return escape(str(value)) if value is not None else "Unreported"

    def measurement(value, unit):
        return f"{value:,.0f}{unit}" if value is not None else "Unreported"

    habitat = measurement(stages["habitat"]["HABCONF_VERIFIED_HABITAT_LEN"], " m")
    dollars = stages["completion"]["REMEDIATION_COST"]
    cost = f"${dollars:,.0f}" if dollars is not None else "Unreported"
    descriptions = {
        "design": ("Design proposal", text(stages["design"]["CROSSING_FIX_DESC"])),
        "assessment": ("Barrier assessment", text(stages["assessment"]["BARRIER_RESULT_DESCRIPTION"])),
        "habitat": ("Habitat confirmation", f"{habitat} of verified habitat in the provincial database."),
        "completion": ("Completed work", f'{text(stages["completion"]["CROSSING_FIX_DESC"])}. The recorded cost was {cost} CAD.'),
    }
    timeline = []
    for key, row in sorted(stages.items(), key=lambda item: item[1]["date"] or "9999"):
        title, note = descriptions[key]
        timeline.append(f'<details><summary>{text(row["date"])} · {title}</summary><p>{note} '
                        f'<a href="{escape(row["source"], quote=True)}">Open the provincial record ↗</a></p></details>')
    return f'''<section class="about" id="crossing-1474" aria-labelledby="crossing-title"><div>
<p class="eyebrow">Fraser Valley case study · Provincial crossing 1474</p>
<h2 id="crossing-title">Chilliwack Bench fish passage</h2>
<p>A separate provincial record follows the work at kilometre four of Bench Forest Service Road in the Chilliwack River drainage.</p>
<strong class="case-cost">{cost}</strong><span>Recorded remediation cost · CAD</span>
<p class="hint">Provincial records retrieved {text(data["retrieved"])} UTC.</p>
</div><div><h3>How much habitat?</h3><p>The provincial habitat confirmation lists <strong>{habitat}</strong> of verified habitat. The project report credits the replacement arch with restoring access to <strong>1,000 m of high-value habitat</strong>. One figure describes the habitat documented at assessment, the other the access improvement the project reported.</p>
<p><a href="{REPORT}">Read project 21 in the provincial report, PDF p. 16 ↗</a></p>
<h3>Follow the records</h3>{''.join(timeline)}
<p>The report names cutthroat trout and lists coho among the possible beneficiaries. The DFO Chilliwack River coho series provides historical watershed context. Its surveys cover a different geographic unit from this crossing.</p>
<p><a href="https://coolcode.ca/salmonlines/#series=46982-62&amp;measure=legacy">Explore Chilliwack River coho in Salmon Lines ↗</a> · <a href="https://smnorris.github.io/bcfishpass/">Stream-network connectivity methods in bcfishpass ↗</a></p>
<p class="hint">Contains information licensed under the <a href="https://www2.gov.bc.ca/gov/content/data/open-data/open-government-licence-bc">Open Government Licence – British Columbia</a>.</p>
</div></section>'''
