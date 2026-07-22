from pystac_client import Client
import planetary_computer


CATALOG = Client.open(

    "https://planetarycomputer.microsoft.com/api/stac/v1",

    modifier=planetary_computer.sign_inplace,

)