# Slack Data Import Tool

The slack import tool has been shifted to the WyzePal server repository.
The data can be converted from slack data format to wyzepal data format
using the command `./manage.py convert_slack_data`.

The procedure to use this would be:

1. `./manage.py convert_slack_data <slack_zip_file> <realm_name> --output <output_dir>`.
2. To import this converted data into a new WyzePal instance, use
    `./manage.py import --destory-rebuild-database <output_dir>`.
3. To import this converted data into an existing WyzePal instance (with multiple realms)
   use `./manage.py import --import-into-nonempty <output_dir>`.
