# # Getting Started
#
# The LFSIR package provides easy access to Iran's Labor Force Survey data.
# We can load the survey tables and enrich them with additional informations.

import lfsir

# ## Loading Survey Data
#
# The `load_table` function loads survey data for a given year.
# Let's load the data from 1401.

df = lfsir.load_table(years=1401)
df.head()

# We now have the raw survey data for 1401.
#
# Next we can enrich this by adding attributes about each household.

# ## Adding Attributes
#
# The `add_attribute` function can append additional attribute columns based on a household ID.

# This allows easy segmentation and analysis by attributes like province and urban/rural status.

df = lfsir.add_attribute(df, "Province")

# We added the province name for each household.

df = lfsir.add_attribute(df, "Urban_Rural")

# Now we also have the urban/rural status.

# Let's confirm that worked by peeking at the data.

df[["ID", "Province", "Urban_Rural"]].sample(20)

# ## Adding Classification
#
# The `add_classification` function can decode classification codes like industry and occupation.
#
# It takes columns containing codes like ISIC and ISCO, and decodes them into descriptive
# categories across multiple levels of hierarchy.
#
# For example with ISIC industry codes:

df = lfsir.add_classification(df, target="Main_Job_Workplace_ISIC_Code")

# This will add a new column with name "Industry" that contains
# human-readable titles derived from the ISIC classification system.
#
# Let's confirm the new column were added:

df[["Main_Job_Workplace_ISIC_Code", "Industry"]].dropna().sample(20)

# So with a single line we have effectively joined a mapping table to
# decode the original numeric codes into descriptive categories.
#
# We now have a enriched dataset ready for further analysis and visualization!
