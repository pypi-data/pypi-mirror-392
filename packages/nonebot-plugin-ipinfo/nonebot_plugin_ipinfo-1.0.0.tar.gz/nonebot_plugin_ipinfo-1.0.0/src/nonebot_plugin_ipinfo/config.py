from pydantic import BaseModel

class Config(BaseModel):
    ipinfo_access_token: str | None = None
    ipinfo_use_ip2location: bool = False
    ipinfo_ip2location_api_key: str | None = None
    ipinfo_verbose_use_reference: bool = True
