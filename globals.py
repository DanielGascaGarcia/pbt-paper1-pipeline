#Code: globals.py
#Description: Central configuration for the experiment 1 pipeline.
#             Every script imports this module, so all paths, IDs and
#             constants live here and nowhere else. Do not hardcode any
#             of these values inside individual scripts.
#Author: mbaxdg6

import os
import matplotlib

# Non-interactive backend. Set here, at import time, so no script opens a
# window and blocks the orchestrator. Comment out to see figures while
# working locally.
matplotlib.use("Agg")

# -----------------------------------------------------------#
# Paths
# -----------------------------------------------------------#
# Resolved relative to this file, so the repository runs as cloned and a
# script can also be run on its own from any working directory.
#
#   path1  raw        input data as downloaded / parsed from OhioT1DM
#   path2  processed  intermediate CSVs passed between pipeline steps
#   path3  figures    final figures for the manuscript
#   path4  tables     final tables for the manuscript
#
# NOTE: several steps collect their inputs by listing whatever per-day
# files are present in path2, rather than regenerating a known list. A
# leftover file from an earlier run is therefore picked up as if it
# belonged to the current one. Clear path2 and re-run from the parser for
# any run intended to reproduce the reported values.
HERE = os.path.dirname(os.path.abspath(__file__))

path1 = os.path.join(HERE, 'raw') + '/'
path2 = os.path.join(HERE, 'processed') + '/'
path3 = os.path.join(HERE, 'results', 'figures') + '/'
path4 = os.path.join(HERE, 'results', 'tables') + '/'

# -----------------------------------------------------------#
# Participant selection
# -----------------------------------------------------------#
# Current participant. Read from the PATIENT_ID environment variable so
# the orchestrator can loop over participants without editing this file
# (it sets PATIENT_ID per subprocess). The default only applies when a
# script is run on its own from the editor.
# NOTE: the name shadows Python's built-in id(). A script that forgets to
# assign it will therefore NOT raise NameError -- it silently picks up the
# built-in function instead. Rename to patient_id if this ever bites.
id = int(os.environ.get("PATIENT_ID", 559))

# Participants included in this experiment: the six OhioT1DM subjects that
# report self-reported activity. Used by the aggregation scripts that plot
# all participants at once (G.GraphResults.py, G.GraphBoxPlots.py).
ids = [559, 563, 570, 575, 588, 591]

# Participant shown as the worked example in the manuscript. Scripts that
# produce a single-subject illustrative figure check `id == idG` before
# saving, so the figure is only written once per full run.
idG = 588

# -----------------------------------------------------------#
# Figure formatting
# -----------------------------------------------------------#
# Journals put the figure title in the caption, not inside the image.
# Keep this False for the figures that go into the manuscript; set it to
# True when reviewing plots locally and you want them self-labelled.
FIGURE_TITLES = False

# Shared z-axis range for the three panels of Figure 3, in mg/dL, so the
# panels are directly comparable.
FIG3_ZLIM_MGDL = (0, 400)

# -----------------------------------------------------------#
# Unit conversion
# -----------------------------------------------------------#
# All blood glucose values in the pipeline are stored in mg/dL. This is the
# single factor used to add mmol/L to tables and secondary axes. Kept here
# so the axes, the tolerance bands and the tables can never drift apart.
# 18 is the conventional rounding of the exact factor (18.0182); at the
# precision reported in the manuscripts the two are indistinguishable.
MGDL_TO_MMOL = 1/18