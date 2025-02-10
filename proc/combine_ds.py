import unicodedata
from pathlib import Path

import beruf_proc
import pandas as pd

TOTAL_FREQ_DF = pd.read_csv("data/total_word_freq.csv")

slf = pd.read_csv("data/stadt_fluss_tmp.csv")

chat_gpt_df = pd.read_excel("data/words_chat_gpt.xlsx")


def remove_umlaut_from_char(char):
    normalized_char = unicodedata.normalize("NFD", char)
    return "".join([ch for ch in normalized_char if not unicodedata.combining(ch)])


def gen_category(name, src_series):
    category = TOTAL_FREQ_DF[TOTAL_FREQ_DF["Word"].isin(src_series)].copy()
    category["Category"] = name
    category["FirstLetter"] = category["Word"].str[0].apply(remove_umlaut_from_char)
    return category


def get_land():
    land_src = pd.read_excel("data/src/sds_laenderliste.xlsx")
    land_src.columns = land_src.columns.str.strip()
    land_src["Kurzform"] = land_src["Kurzform"].str.split(",").str[0]
    land_src["Kurzform"] = land_src["Kurzform"].str.strip()
    land = gen_category("Land", land_src["Kurzform"])
    return land


def get_beruf():
    beruf_src = pd.read_excel(
        "data/src/Alphabetisches-Verzeichnis-Berufsbenennungen.xlsx",
        sheet_name="alphabet_Verz_Berufsb",
        skiprows=4,
    )
    beruf_out_dir = Path("data/beruf")
    beruf_out_dir.mkdir(exist_ok=True)

    # Drop the last 2 rows
    beruf_src = beruf_src.drop(beruf_src.tail(2).index)

    beruf_src = beruf_src["Berufsbenennungen"]

    # Save the original professions
    beruf_orig = pd.DataFrame({"Word": beruf_src, "Index": beruf_src.index})
    beruf_orig.to_csv(beruf_out_dir / "beruf_orig.csv", index=False)

    # Get the derived professions
    beruf_derived = beruf_proc.get_derived_beruf(beruf_src)

    # Save the derived professions with index
    beruf_indexed = pd.DataFrame(
        {
            "Word": beruf_derived,
            "OriginalIndex": beruf_derived.index.get_level_values(0),
        }
    ).reset_index(drop=True)
    beruf_indexed.to_csv(beruf_out_dir / "beruf_indexed.csv", index=False)

    # Combine the original and the derived professions
    beruf_derived = pd.concat([beruf_src, beruf_derived], ignore_index=True)

    beruf = gen_category("Beruf", beruf_derived)

    return beruf


def get_pflanze():
    pflanze_src = pd.read_csv("data/src/de_species.txt", header=None)
    pflanze = gen_category("Pflanze", pflanze_src[0])
    return pflanze


def get_tier():
    tier_src = pd.read_csv("data/src/tier-dtn.csv")
    tier = gen_category("Tier", tier_src["vernacularName"])
    return tier


land = get_land()

beruf = get_beruf()
pflanze = get_pflanze()
tier = get_tier()

beruf_chat_gpt = gen_category(
    "Beruf", chat_gpt_df[chat_gpt_df["Category"] == "Beruf"]["lemma"]
)
pflanze_chat_gpt = gen_category(
    "Pflanze", chat_gpt_df[chat_gpt_df["Category"] == "Pflanzen"]["lemma"]
)
tier_chat_gpt = gen_category(
    "Tier", chat_gpt_df[chat_gpt_df["Category"] == "Tier"]["lemma"]
)

print(f"Land entries: {len(land)}")
print(f"Beruf entries: {len(beruf)}")
print(f"Pflanze entries: {len(pflanze)}")
print(f"Tier entries: {len(tier)}")
print(f"Beruf ChatGPT entries: {len(beruf_chat_gpt)}")
print(f"Pflanze ChatGPT entries: {len(pflanze_chat_gpt)}")
print(f"Tier ChatGPT entries: {len(tier_chat_gpt)}")

slf = pd.concat(
    [
        slf,
        land,
        beruf,
        pflanze,
        tier,
        beruf_chat_gpt,
        pflanze_chat_gpt,
        tier_chat_gpt,
    ],
    axis=0,
    ignore_index=True,
)

print(f"Total entries before dropping duplicates: {len(slf)}")

slf = slf.drop_duplicates()

print(f"Total entries after dropping duplicates: {len(slf)}")

slf = slf.sort_values(by=["Category", "Word"]).reset_index(drop=True)

slf.to_csv("data/stadt_land_fluss.csv")

print(f"Final dataset saved with {len(slf)} unique entries.")
