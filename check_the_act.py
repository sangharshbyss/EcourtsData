"""
if CrPC 438 and PoA present then
check - if order is uploaded.
if yes click.
download pdf
"""

from ecourts_logging import logger


def act_check(some_browser_session):
    table = some_browser_session.find_element_by_id('act_table')
    cells = table.find_elements_by_tag_name('td')
    all_acts = ""
    for cell in cells:
        text = cell.text
        all_acts = f'{all_acts} \n {text}'

    if "Scheduled Castes and the Scheduled Tribes (" \
       "Prevention of Atrocities) Act" in all_acts:
        logger.info("download this")
        return True
    else:
        logger.info("no")
        return False

