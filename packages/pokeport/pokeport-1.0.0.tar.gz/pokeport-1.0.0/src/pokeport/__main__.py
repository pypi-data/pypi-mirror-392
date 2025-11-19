import logging

from pokeport.pokeport import main


def cli():
    try:
        main()
    except Exception as e:
        logging.error(e)


if __name__ == "__main__":
    main()
