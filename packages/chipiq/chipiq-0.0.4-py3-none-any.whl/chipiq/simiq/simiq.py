
def simiq(
    uri_or_filepath: str = "", 
    report_type: str = "user_manual",
    from_timestamp: int = 0, 
    signal_names: list = [".*"],
) -> str:
    """ Analyze a VCD-file. """
    return f"SimIQ analysis of {uri_or_filepath} with report type {report_type}, from timestamp {from_timestamp}, signals {signal_names}."
