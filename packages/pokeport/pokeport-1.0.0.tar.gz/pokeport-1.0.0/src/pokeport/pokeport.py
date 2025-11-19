import argparse
import io
import os
import re
import sys

import climage
import requests
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from PIL import Image

# Paths

PROGRAM = os.path.realpath(__file__)

# Query function


def pokeport_query(name, emotion):
    ## Make Query using name and emotion string

    # Select your transport with a defined url endpoint
    transport = AIOHTTPTransport(
        url="https://spriteserver.pmdcollab.org/graphql", ssl=False
    )

    # Create a GraphQL client using the defined transport
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Provide a GraphQL query
    query = gql(
        """
        query MyQuery($emotion: String!, $monsterName: String!) {
            searchMonster(monsterName: $monsterName) {
                name
                forms {
                portraits {
                    creditPrimary {
                    name
                    }
                    creditSecondary {
                    name
                    }
                    emotion(emotion: $emotion) {
                    url
                    }
                }
                fullName
                isFemale
                isShiny
                }
            }
        }
        """
    )

    params = {"emotion": emotion, "monsterName": name}

    # Execute the query on the transport
    result = client.execute(query, variable_values=params)

    return result


# main function


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="pokeport",
        description="CLI utility that queries SpriteCollab, and prints a portrait from there in your shell",
        usage="pokeport [POKÉMON NAME] [OPTION]",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
    )

    # args
    parser.add_argument(
        "-h", "--help", action="help", help="Show this help message and exit"
    )
    parser.add_argument(
        "name",
        type=str,
        help="""Required. Name of desired Pokémon.""",
    )
    parser.add_argument(
        "-e",
        "--emotion",
        type=str,
        default="Normal",
        help="""Name of desired emotion. Defaults to "Normal".""",
    )
    parser.add_argument(
        "-f",
        "--form",
        type=str,
        help="Show the specified alternate form of a Pokémon.",
    )
    parser.add_argument(
        "--female",
        action="store_true",
        default=False,
        help="Show the female form of the Pokémon instead, if it exists.",
    )
    parser.add_argument(
        "--shiny",
        action="store_true",
        default=False,
        help="Show the shiny colors of the Pokémon instead, if it exists.",
    )
    parser.add_argument(
        "--truecolor",
        action="store_true",
        default=False,
        help="Returns result in true colors instead of 256 colors, if supported by your terminal.",
    )
    parser.add_argument(
        "--unicode",
        action="store_true",
        default=False,
        help="Returns result in unicode.",
    )

    if len(sys.argv) == 1:
        parser.print_help()
        # parser.print_usage() # for just the usage line
        parser.exit()

    args = parser.parse_args()

    # regex clean special characters and convert to title case

    args.name = re.sub("[^0-9a-zA-Z]+", "_", args.name.title())
    args.emotion = args.emotion.title()

    if args.form is not None:
        args.form = re.sub("[^0-9a-zA-Z]+", "_", args.form.title())

    result = pokeport_query(args.name, args.emotion)

    ## simpify dict structure
    simplified = []

    if args.form is None:
        args.form = result.get("searchMonster", {})[0].get("forms")[0].get("fullName")

    for monster in result.get("searchMonster", []):
        # name check
        name = monster.get("name")

        if name != args.name:
            continue

        for form in monster.get("forms", []):
            # Check and remove the substring " Shiny" from fullName
            full_name = form.get("fullName")
            if " Shiny" in full_name:
                full_name = full_name.replace(" Shiny", "")

            # filter terms
            credit_exists = form.get("portraits", {}).get("creditPrimary", {})
            is_shiny = form.get("isShiny")
            is_female = form.get("isFemale")

            # apply filters
            if credit_exists is None:
                continue
            if args.shiny is not None and is_shiny != args.shiny:
                continue
            if args.female is not None and is_female != args.female:
                continue
            if args.form is not None and full_name != args.form:
                continue

            # Combine primary and secondary credits into one list
            primary_credit = (
                form.get("portraits", {})
                .get("creditPrimary", {})
                .get(
                    "name",
                )
            )
            secondary_credits = [
                credit.get("name")
                for credit in form.get("portraits", {}).get("creditSecondary", [])
            ]
            combined_credits = [primary_credit] + secondary_credits

            simplified.append(
                {
                    "name": name,
                    "form": full_name,
                    "isFemale": form.get("isFemale"),
                    "isShiny": form.get("isShiny"),
                    "emotionURL": form.get("portraits", {})
                    .get("emotion", {})
                    .get("url"),
                    "credits": combined_credits,
                }
            )

    ## IFELSE;

    if not bool(simplified):
        raise Exception("No matching portraits found!")
    else:
        simplified = simplified[0]

    # format url
    r = requests.get(simplified["emotionURL"])
    if r.status_code == 200:
        img = Image.open(io.BytesIO(r.content))
    else:
        raise Exception("Bad status code returned when downloading image!")

    if args.unicode:
        width = 40
    else:
        width = 80

    # climage
    output = climage.convert_pil(
        img.convert("RGBA"),
        is_unicode=args.unicode,
        is_256color=not (args.truecolor),
        is_truecolor=args.truecolor,
        width=width,
    )

    print(output)
    print(f"Authors: {', '.join(simplified['credits'])}")
