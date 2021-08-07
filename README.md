# Hundred-Nights

A simple Django application used to manage data for the Hundred Nights shelter in Keene, NH.

Provides functionality to:
  - Manage visitors, volunteers, and donors
  - Administer per-visit or single-time questionaires
  - Report on and export record sets


## Modifying the database schema

 - In development environment:
     - Update `models.py` as appropriate
     - Run `manage.py schemamigration HundredNights --auto <migration_name>`
 - Apply the migration in production:
      - Push updated files to production environment (e.g. via `git pull` or `rsync`)
      - Run `manage.py migrate HundredNights`