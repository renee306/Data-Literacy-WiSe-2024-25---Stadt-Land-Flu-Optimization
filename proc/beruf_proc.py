import re

import pandas as pd


def get_compound_beruf(profession_str, beruf_derived):
    if profession_str.count("/-") == 1:
        split_char = "/-"
    elif profession_str.count("-/") == 1:
        split_char = "-/"
    elif len(re.findall(r"/[a-zäöüß]", profession_str)) == 1:
        split_char = "/"
    else:
        return profession_str

    part_1, part_2 = profession_str.split(split_char)

    for word in beruf_derived:
        # Replace the gender specific profession suffix
        if split_char != "-/":
            if part_1.endswith(word.lower()):
                part_2_updated = part_1.replace(word.lower(), part_2)
                return part_1, part_2_updated
        # Derive a profession using the describing prefix
        else:
            if part_2.endswith(word.lower()):
                part_1_updated = part_1 + word.lower()
                return part_1_updated, part_2

    if split_char != "-/":
        return part_1
    else:
        return part_2


def split_profession_string(profession_str):
    # Split using the fact that nouns start with an uppercase letter
    pattern = r"(?<=[a-zäöüß])/+(?=[A-ZÄÖÜ])"
    parts = re.split(pattern, profession_str)
    return parts if len(parts) == 2 else [profession_str]


def get_gender_beruf(beruf_str):
    male_str, female_str = beruf_str, beruf_str

    gender_suffixes = {
        "(er/in)": ("er", "in"),
        "(e/r)": ("er", "e"),
        "(e/in)": ("e", "in"),
        "er/In": ("er", "in"),
        "/e/in": ("e", "in"),
        "er/r": ("er", "e"),
        "/in": ("", "in"),
        "e/r": ("er", "e"),
        "r/e": ("r", "e"),
        "r/n": ("r", "rin"),
        "mann/-frau": ("mann", "frau"),
        "mann-/frau": ("mann", "frau"),
        "mann/frau": ("mann", "frau"),
    }

    # Derive male and female professions using the suffix mapping
    male_str, female_str = beruf_str, beruf_str
    for key, (male, female) in gender_suffixes.items():
        if key in male_str:
            male_str = male_str.replace(key, male)
            female_str = female_str.replace(key, female)

    return male_str, female_str


def remove_parentheses_content(text):
    result = []
    i = 0
    length = len(text)

    while i < length:
        # Remove parentheses and their content if preceded by a whitespace
        if text[i] == "(" and i > 0 and text[i - 1] == " ":
            result.pop()
            depth = 1
            i += 1

            # Keep track of nested parentheses
            while i < length and depth > 0:
                if text[i] == "(":
                    depth += 1
                elif text[i] == ")":
                    depth -= 1
                i += 1

            continue

        result.append(text[i])
        i += 1

    return "".join(result)


def get_derived_beruf(beruf_src: pd.Series):
    # Remove parentheses content taking nesting into account
    beruf_derived = beruf_src.apply(remove_parentheses_content)

    # Remove categories
    beruf_derived = beruf_derived.str.split(" - ").str[0]

    # Remove duplicates
    beruf_derived = beruf_derived.drop_duplicates()

    # Remove everything with " in *"
    beruf_derived = beruf_derived.str.replace(r" in .*", "", regex=True)

    # Remove everything with " für *"
    beruf_derived = beruf_derived.str.replace(r" für .*", "", regex=True)

    # Split professions by slash
    beruf_derived = beruf_derived.str.split(" / ").explode()

    # Get gender specific professions based on suffix
    beruf_derived = beruf_derived.apply(get_gender_beruf).explode()

    # Split professions by a/A pattern
    beruf_derived = beruf_derived.apply(split_profession_string).explode()

    # Get specific versions of compound words with non-standard suffix or prefix
    beruf_derived = (
        beruf_derived.apply(get_compound_beruf, args=(beruf_derived,))
        .explode()
        .drop_duplicates()
    )

    # Assert that no word starts with lowercase
    assert not beruf_derived.str[0].str.islower().any()

    return beruf_derived
