# TAW

Slips, pairings &amp; standings generator from AetherHub

"TAW" is a recursive acronym for "TAW Ain't WLTR".

## Motivations behind this project

As a Magic: The Gathering judge, the options I know of when it comes to scorekeeping are:

- Using the official WotC software, EventLink. EventLink is notoriously limited, and I feel is not well suited to run 65+ people tournament. You also need to be a WPN store to access it
- Paying for a service like MTG Melee. I've only heard good things from the service, but it is far from cheap. Good for them if they can it work, but it makes this option less appealing for smaller scale tournaments, without barely any money to spare
- Using WLTR. This would be great, if we had access to it 👼
- Using AetherHub to generate pairings and compute standings. AetherHub's great, but it doesn't generate pairings, standings or match slips

A few fellow judges have developed custom ways to generate the papers from AetherHub. These work great, but they often have hard requirements (eg. using Microsoft Excel and / or Windows) and are not available online. These solutions are also not widely shared or available.

The goals of these projects are two-folds:
- Having an easy way to generate the papers from an AetherHub tournament
- Sharing this solution with everyone

## Where is this service available?

TODO

# Contributing

TODO

## Installation

Create a virtual environment, then run `pip install -r requirements.txt`

Run the local server with `flask --app taw run`

### Development installation

In the same virtual environment, run `pip install -r requirements-dev.txt`

Install the pre-commit hooks with `pre-commit install`

Run the local tests with `pytest`

## TODO

- Table number offset
- Match slips template
- Pairings by table
- Tournament logo / branding
- How to deploy :clown: -> pythonanywhere? Vercel?
- Move these TODOs into Github issues :eyes:
- Create issue template (in particular, unexpected input)
- Add a documentation page, and a FAQ page (same one?)
- Sentry?
