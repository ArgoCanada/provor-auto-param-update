# PROVOR Automatic Surface Time Updates

Python code to automatically update the target surface timing of NKE PROVOR floats after they report a profile.

Script `update-params.py` is the workhorse of this function, and runs daily via cron job github workflow (`.github/workflows/check-floats.yaml`). 

Basic steps of the workflow: 

- log into RUDICS ftp server
- loop through float directories, and for each float:
    - get latest profile time, and check the following conditions:
        - was there a profile withing the last 1 day?
        - ensure a RUDICS_cmd.txt file does not already exist
        - is there a command respone associated with the last profile?
    - if all the above conditions are met, then: 
        - select a new surfacing time, either based on previous command file, or a user defined list
        - create a RUDICS_cmd.txt file and upload to the ftp
        - log the change and save the command file with date and imei information
