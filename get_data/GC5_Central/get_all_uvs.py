#!/usr/bin/env python

# Extract the uwnd, vwnd, and rh for all years for all three runs

import os


# Function to check if the job is already done for this timepoint
def is_done(run, year, variable):
    op_file_name = ("%s/GC5-Central/Historical/monthly/%s/%s_%04d.pp") % (
        os.getenv("PDIR"),
        run,
        variable,
        year,
    )
    if os.path.isfile(op_file_name):
        return True
    return False


for run in ("dl339", "dl340", "dl341"):
    for year in range(1850, 2015):
        if not is_done(run, year, "uwnd"):
            print("./get_uwnd_for_year.py --year=%d --run=%s" % (year, run))
        if not is_done(run, year, "vwnd"):
            print("./get_vwnd_for_year.py --year=%d --run=%s" % (year, run))
        if not is_done(run, year, "sh"):
            print("./get_sh_for_year.py --year=%d --run=%s" % (year, run))
        if not is_done(run, year, "pr"):
            print("./get_pr_for_year.py --year=%d --run=%s" % (year, run))
