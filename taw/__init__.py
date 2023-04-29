from flask import Flask, render_template

from taw.forms import PairingsForm

app = Flask(
    __name__,
    static_url_path="",
    static_folder="static",
    template_folder="templates",
)


@app.route("/", methods=["GET", "POST"])
def home():
    # We don't handle sensitive data, I can't be bothered to set up a secret key properly
    form = PairingsForm(meta={"csrf": False})
    if form.validate_on_submit():
        return "GG"
    return render_template("index.html", form=form)
