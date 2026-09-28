"""Combine the Canvas iris CSVs and summarize the four measurements."""

from itertools import combinations
from pathlib import Path

import pandas as pd


FOLDER = Path(__file__).resolve().parent
MEASUREMENTS = ["petal length", "petal width", "sepal length", "sepal width"]


def read_measurements(filename, prefix):
    """Read a Canvas CSV, standardize its headers, and check its contents."""
    path = FOLDER / filename
    if not path.is_file():
        raise FileNotFoundError(f"Missing {filename}. Put it beside iris_analysis.py.")

    frame = pd.read_csv(path)
    # Spaces, underscores, and capitalization may differ between CSVs.
    frame.columns = [str(name).strip().lower().replace("_", " ") for name in frame.columns]
    frame = frame.rename(columns={"sample id": "sample id", "sampleid": "sample id",
                                  "id": "sample id", "species name": "species"})
    required = ["sample id", f"{prefix} length", f"{prefix} width"]
    missing = [name for name in required if name not in frame.columns]
    if missing:
        raise ValueError(f"{filename} is missing columns: {', '.join(missing)}. "
                         f"Found: {', '.join(frame.columns)}")
    if frame["sample id"].isna().any() or frame["sample id"].duplicated().any():
        raise ValueError(f"{filename} has missing or repeated sample IDs.")
    if "species" in frame.columns and frame["species"].isna().any():
        raise ValueError(f"{filename} has missing species.")
    for column in (f"{prefix} length", f"{prefix} width"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
        if frame[column].isna().any():
            raise ValueError(f"{filename}: {column} contains missing or nonnumeric values.")
    columns = ["sample id"] + (["species"] if "species" in frame else [])
    return frame[columns + [f"{prefix} length", f"{prefix} width"]]


def combine_data():
    """Match measurements by sample ID; verify matching species when present."""
    petals = read_measurements("Petal_Data.csv", "petal")
    sepals = read_measurements("Sepal_Data.csv", "sepal")
    if "species" not in petals and "species" not in sepals:
        raise ValueError("At least one CSV must contain a species column.")
    combined = petals.merge(sepals, on="sample id", how="outer", validate="one_to_one",
                            indicator=True, suffixes=("_petal", "_sepal"))
    if (combined["_merge"] != "both").any():
        raise ValueError("The two CSVs have different sample IDs; check the input files.")
    combined = combined.drop(columns="_merge")
    if "species_petal" in combined and "species_sepal" in combined:
        if not combined["species_petal"].astype(str).str.strip().str.lower().equals(
                combined["species_sepal"].astype(str).str.strip().str.lower()):
            raise ValueError("The species labels disagree for at least one sample ID.")
        combined = combined.rename(columns={"species_petal": "species"}).drop(columns="species_sepal")
    return combined[["sample id", "species"] + MEASUREMENTS]


def compare_species(means, overall_standard_deviations):
    """Compare species means after scaling each measurement by its overall SD."""
    if len(means) < 2:
        print("At least two species are needed for a species comparison.")
        return
    distances = {}
    for first, second in combinations(means.index, 2):
        scaled_differences = (means.loc[first] - means.loc[second]) / overall_standard_deviations
        distance = (scaled_differences.pow(2).sum()) ** 0.5
        distances[(first, second)] = distance
        print(f"{first} vs. {second}: standardized distance = {distance:.3f}")
    closest = min(distances, key=distances.get)
    farthest = max(distances, key=distances.get)
    print(f"Most similar: {closest[0]} and {closest[1]} ({distances[closest]:.3f}).")
    print(f"Least similar: {farthest[0]} and {farthest[1]} ({distances[farthest]:.3f}).")
    print("Use the species means above to explain which petal and sepal traits differ.")


def main():
    data = combine_data()
    print(f"\nCombined data: {len(data)} samples across {data['species'].nunique()} species")
    print(data.to_string(index=False))

    # Four measurements make six distinct pairwise Pearson correlations.
    correlations = data[MEASUREMENTS].corr()
    print("\nSix correlations across all samples:")
    for first, second in combinations(MEASUREMENTS, 2):
        print(f"{first} vs. {second}: {correlations.loc[first, second]:.3f}")

    grouped = data.groupby("species")[MEASUREMENTS]
    means = grouped.mean()
    print("\nMean by species:\n", means.round(3).to_string())
    print("\nMedian by species:\n", grouped.median().round(3).to_string())
    print("\nSample standard deviation by species:\n", grouped.std().round(3).to_string())

    # Scaling stops a wide-range measurement from dominating the comparison.
    overall_sd = data[MEASUREMENTS].std()
    if (overall_sd == 0).any():
        raise ValueError("A measurement has zero overall variation; cannot scale species means.")
    print("\nComparison of species mean measurements:")
    compare_species(means, overall_sd)


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
        print(f"Error: {error}")
