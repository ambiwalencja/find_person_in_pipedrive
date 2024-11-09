from pydantic import BaseModel, Field
from typing import Union

class FindPersonInPipedrive(BaseModel):
    Name: str
    Email: str
    Phone: str
    Webhook: str
    utm0: Union[str, None] = None # allows parameter to be optional; latest python: | None = None
    utm1: Union[str, None] = None
    Etap: int
    Kontakt_z_doradca: str = Field(alias="Kontakt z doradcą")
    Deal_Owner: str = Field(alias="Deal Owner", default=None) # default=None - also allows to be optional
    Zrodlo_szczegolowe: str = Field(alias="Źródło szczegółowe")
    Zrodlo_Deal: str = Field(alias="Źródło (Deal)")
    Zrodlo_Person: str = Field(alias="Źródło (Person)")
    Uwagi: Union[str, None] = None
    Wynik_testu: str = Field(alias="Wynik testu", default=None) 
    url: Union[str, None] = None
    Kraj_rynek: str = Field(alias="Kraj/rynek")
    Termin_kursu_Amazon: str = Field(alias="Termin kursu (Amazon)", default=None) # optional
