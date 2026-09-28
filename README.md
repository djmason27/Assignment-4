# Assignment 4: Pandas — Iris measurements

This project combines the petal and sepal measurements of iris samples from two Canvas CSV files. It reports all six correlations between the four measurements, then the mean, median, and sample standard deviation for each species. Finally, it compares the species using their mean measurements.

## Run it

1. Download `Petal_Data.csv` and `Sepal_Data.csv` from Canvas. Put both beside `iris_analysis.py`. Keep their original filenames.
2. Install Pandas if needed (`python -m pip install pandas`). Pandas is the only third-party package used; it is required by this assignment.
3. From this folder, run `python iris_analysis.py` (or `python3 iris_analysis.py`). The results print in the terminal.

Expected columns are a sample ID (`sample id`, `sample_id`, `sampleid`, or `id`), `species` in at least one file, and length and width for the corresponding flower part (spaces or underscores in measurement headers are accepted). Check the actual Canvas headers before submitting. If they differ, adjust the header names in `read_measurements`.

## Design and implementation

There are no custom classes: Pandas DataFrames already represent the tabular data, and functions keep the project simple.

- `FOLDER` locates the CSVs beside the script; `MEASUREMENTS` lists the four numerical columns and their display order.
- `read_measurements(filename, prefix)` loads one CSV, standardizes header spelling, selects the needed columns, and rejects missing IDs, duplicate IDs, and invalid measurements.
- `combine_data()` merges on the **sample ID**, checks that every ID exists in both files, and checks that species labels agree when both files include them. Merging by ID avoids pairing unrelated rows when files are sorted differently.
- `compare_species(means, overall_standard_deviations)` prints the distance between each pair of species' mean measurements. Each trait difference is divided by that trait's overall standard deviation before the four squared differences are added and square rooted. Smaller distances mean more similar *average measurements*.
- `main()` prints the combined DataFrame, the six distinct Pearson correlations across all samples, and species level averages, medians, and sample standard deviations (`ddof=1`, the Pandas default). It then prints the closest and farthest species by standardized mean distance.

## Interpretation and limitations

The six correlations are calculated on all samples pooled together, **not** separately for each species. Correlation measures linear association, not cause. The similarity ranking compares average trait values; it does not account for overlap between individual flowers, measurement error, or classification accuracy. Small species groups may have undefined sample standard deviations. The program needs matching sample IDs, valid numeric measurements, and a species column in at least one CSV. It does not silently fill in bad measurements or mismatched samples.

Use the printed **Mean by species** table to write a short conclusion in your own words, identifying which petal and sepal averages support the most and least similar pairs. Do not submit a conclusion based on a different iris dataset until you have run the supplied Canvas files.

## Submission

Upload this script, README, **both Canvas CSVs**, and the complete AI conversation transcript to a public GitHub repository, then submit the repository link. See `AI_USE.md` for the disclosure. Check whether your class permits public redistribution of its CSVs; if not, ask your instructor how to include them for grading.
