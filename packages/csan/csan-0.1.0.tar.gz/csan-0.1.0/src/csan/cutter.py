import logging

from .data import CUTTER_DATA
from .naming import compose_name, process_name

logger = logging.getLogger(__name__)


def cutter_number(
    first_name: str,
    last_name: str,
    composed_name: str | None = None,
    composed_name_abbr: str | None = None,
    *,
    verbose: bool = False,
) -> int:
    """
    Generate/Retrieve a cutter-sanborn number, given a first and last name.

    Args:
        first_name (str): a person's first name (e.g. "Jane");
        last_name (str): a person's last name (e.g. "Doe");
        composed_name (str|None): a composition in the format "Last, First";
        composed_name_abbr (str|None): an abbreviated compositon, format "Last, F."
        verbose (bool): show debug logs.

    Returns:
        An integer, retrieved from the Cutter-Sanborn table.

    Raises:
        ValueError: if no Cutter-Sanborn number is found.

    Examples:
        >>> cutter_number("First", "Last")
        349
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(message)s")

    first_name, last_name = process_name(first_name, last_name)

    if (composed_name is None) or (composed_name_abbr is None):
        composed_name, composed_name_abbr = compose_name(first_name, last_name)

    cutter_s = None

    obvious_attempts = [
        composed_name,
        last_name + f", {first_name[:3]}.",
        composed_name_abbr,
        last_name,
    ]

    if attempt := next((a for a in obvious_attempts if a in CUTTER_DATA), None):
        logger.debug(
            "Obvious attempts: %s\nReturning match '%s' from obvious attempts",
            obvious_attempts,
            attempt,
        )
        return CUTTER_DATA[attempt]

    sieved_data = [k for k in CUTTER_DATA if k.startswith(last_name[0:2])]

    composed_name_decrescent = [
        composed_name[: i + 1]
        for i in range(len(composed_name), 0, -1)
        if not composed_name[: i + 1].endswith((",", " "))
    ]

    logger.debug("\nDecrescent last name list: %s", composed_name_decrescent)

    for pos, name in enumerate(composed_name_decrescent[1:]):
        sub_sieved = [
            k
            for k in sieved_data
            if (k.startswith(name) and (len(k) <= len(composed_name)))
        ]

        if not sub_sieved:
            continue

        miss_lttrs = list(composed_name_decrescent[0][len(name) :])

        logger.debug("Name: %s\nPos: %s\nSieved List: %s", name, pos, sub_sieved)

        for candidate in sub_sieved:
            logger.debug("Candidate: %s", candidate)

            if candidate == name:
                cutter_s = candidate
            else:
                xtra_lttrs = list(candidate[len(name) :].replace(".", ""))
                logger.debug("Missing Letters: %s", miss_lttrs)
                logger.debug("Extra Letters: %s", xtra_lttrs)

                if not (pairs := list(zip(miss_lttrs, xtra_lttrs, strict=False))):
                    logger.debug("Pairs are empty. Continuing...")
                    continue

                logger.debug("Pairs: %s\nMatch: %s.", pairs, cutter_s)

                cutter_s = (
                    candidate
                    if all(x >= y and (x.isalpha() == y.isalpha()) for x, y in pairs)
                    else cutter_s
                )

            logger.debug("Match: %s\n", cutter_s)

        if cutter_s is not None:
            return CUTTER_DATA[cutter_s]

        logger.debug("\n")

    if cutter_s is None:
        raise RuntimeError("Unable to retrieve Cutter-Sanborn number.")

    return 0


# first_letters = last_name[0] if last_name[1] in "aeiou" else last_name[0:2].upper()
def cutter_identifier(
    last_name: str, cutter_number: int, title: str | None = None
) -> str:
    """
    Generate an identifier based on last name, cutter-sanborn number and a title.

    Args:
        last_name (str): a person's last name;
        cutter_number (int): the cutter-sanborn number;
        title (str): a work's title.

    Returns:
        A string identifier

    Examples:
        >>> cutter_identifier("Doe", 649, "Title")
        'D649t'
    """
    title = "" if title is None else title[0].lower()
    return last_name[0] + str(cutter_number) + title
