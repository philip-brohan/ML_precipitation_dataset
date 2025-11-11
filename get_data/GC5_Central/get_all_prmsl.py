#!/usr/bin/env python

# Extract the PRMSL for all years for all three runs

import os


# Function to check if the job is already done for this timepoint
def is_done(run, year):
    op_file_name = ("%s/GC5-Central/Historical/monthly/%s/prmsl_%04d.pp") % (
        os.getenv("PDIR"),
        run,
        year,
    )
    if os.path.isfile(op_file_name):
        return True
    return False


for run in ("dl339", "dl340", "dl341"):
    for year in range(1850, 2015):
        if is_done(run, year):
            continue
        print("./get_prmsl_for_year.py --year=%d --run=%s" % (year, run))
