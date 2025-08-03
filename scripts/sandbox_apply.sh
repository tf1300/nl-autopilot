
#!/bin/bash
set -e
id=$(python /home/tom/nl-autopilot/bots/greenhouse_apply.py --demo)
grep -q "CONFIRM_ID=" <<< "$id"
