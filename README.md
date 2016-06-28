# armada-version
Simple service for keeping armada’s clients up to date.

### usage
sample request:

    curl http://version.armada.sh/version_check?version=0.19.2

sample response:

    {
        "latest_version": "0.19.4",    # latest version number found in the dockyard
        "is_newer": true               # boolean value that indicates if the "latest_version" is newer than the version provided in the request
    }
