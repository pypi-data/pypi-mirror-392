#!/usr/bin/env python3
"""Tells which VTRx correspods to the package serial number scanned."""

import re

__valid_sn__ = re.compile("J-(SD|MT)[0-9]+")

def is_vtrx(SN):
    """Checks if the SN corresponds to a VTRx."""
    if __valid_sn__.match(SN) is None:
        return False
    return True

def find_vtrx(client, SN):
    """Searches VTRx."""
    if not is_vtrx(SN):
        return None
    
    payload = {
        "filterMap": {
            "project": "CE",
            "componentType": ["VTRX"],
            "propertyFilter": [{"code": "PACKAGE_SN", "operator": "=", "value": SN}],
        }
    }
    out = client.get("listComponentsByProperty", json=payload)
    vtrx = None
    nitem = 0
    for item in out:
        vtrx = item["serialNumber"]
        nitem += 1

    if nitem > 1:
        raise ValueError("Too many VTRx with same device SN.")

    return vtrx