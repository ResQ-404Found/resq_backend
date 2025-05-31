from sqlmodel import Field, SQLModel


class DisasterRegion(SQLModel, table=True):
    disaster_id: int = Field(foreign_key="disasterinfo.id", primary_key=True)
    region_id: int = Field(foreign_key="region.id", primary_key=True)