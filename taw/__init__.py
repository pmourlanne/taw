from flask import Flask, render_template, request

from taw.forms import PairingsForm, StandingsForm
from taw.utils import get_pairings_by_name, sort_pairings_for_paper_cutter


app = Flask(
    __name__,
    static_url_path="",
    static_folder="static",
    template_folder="templates",
)


NB_SLIPS_PER_PAGE = 5


@app.route("/", methods=["GET", "POST"])
def home():
    # If we're asked to handle standings, we use the dedicated form
    if getattr(request, "form") and request.form["action"] == "standings":
        form = StandingsForm()
    # We default to the pairings form otherwise
    else:
        form = PairingsForm()

    if form.validate_on_submit():
        ctx = {
            "tournament_name": form.tournament_name.data,
            "round_number": form.round_number.data,
        }

        if request.form["action"] == "pairings":
            pairings_by_name = get_pairings_by_name(form.parsed_pairings)

            rows = []
            for pairing in pairings_by_name:
                # We don't want to show the bye as player 1
                # TODO: Do better than checking against a string
                if pairing.player_1.name != "BYE":
                    rows.append(
                        {
                            "table_number": pairing.number,
                            "player_1": pairing.player_1.name,
                            "player_1_points": pairing.player_1.points,
                            "player_2": pairing.player_2.name,
                            "player_2_points": pairing.player_2.points,
                        },
                    )

            return render_template("pairings.html", rows=rows, **ctx)

        if request.form["action"] == "match_slips":
            pairings = form.parsed_pairings
            # We want to print five match slips per page, and we want
            # them to in the "correct" order when we use the paper cutter
            pairings = sort_pairings_for_paper_cutter(
                pairings,
                nb_slips_per_page=NB_SLIPS_PER_PAGE,
            )

            rows = []
            for pairing in pairings:
                rows.append(
                    {
                        "table_number": pairing.number,
                        "player_1": pairing.player_1.name,
                        "player_1_points": pairing.player_1.points,
                        "player_2": pairing.player_2.name,
                        "player_2_points": pairing.player_2.points,
                    },
                )

            return render_template(
                "match_slips.html",
                rows=rows,
                nb_slips_per_page=NB_SLIPS_PER_PAGE,
                **ctx,
            )

        if request.form["action"] == "standings":
            standings = form.parsed_standings
            return render_template("standings.html", standings=standings, **ctx)

    return render_template("index.html", form=form)


@app.route("/help/")
def help_page():
    return render_template("help.html")


@app.route("/faq/")
def faq():
    return render_template("faq.html")
