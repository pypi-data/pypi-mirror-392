from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any, Final, List, Optional

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import map_async
from ncae_sdk.resources._schema import (
    InfluxRepository,
    InfluxRepositoryCreate,
    InfluxRepositoryCreateModel,
    InfluxRepositoryFilter,
    InfluxRepositoryFilterModel,
    InfluxRepositoryUpdate,
    InfluxRepositoryUpdateModel,
)
from ncae_sdk.types._models import InfluxDataPoint, InfluxTagFilter


class AsyncInfluxRepositoryEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "observability/v1/influx-repository"

    async def list(self, **filters: Unpack[InfluxRepositoryFilter]) -> AsyncIterator[InfluxRepository]:
        results = self._list(self.BASE_PATH, InfluxRepositoryFilterModel, filters)
        return map_async(InfluxRepository.parse_api, results)

    async def find(self, **filters: Unpack[InfluxRepositoryFilter]) -> Optional[InfluxRepository]:
        result = await self._get_by_filters(self.BASE_PATH, InfluxRepositoryFilterModel, filters)
        return InfluxRepository.parse_api(result) if result else None

    async def get(self, rid: ResourceId) -> Optional[InfluxRepository]:
        result = await self._get_by_id(self.BASE_PATH, rid)
        return InfluxRepository.parse_api(result) if result else None

    async def create(self, **payload: Unpack[InfluxRepositoryCreate]) -> InfluxRepository:
        result = await self._create(self.BASE_PATH, InfluxRepositoryCreateModel, payload)
        return InfluxRepository.parse_api(result)

    async def update(self, rid: ResourceId, /, **payload: Unpack[InfluxRepositoryUpdate]) -> InfluxRepository:
        result = await self._update(self.BASE_PATH, rid, InfluxRepositoryUpdateModel, payload)
        return InfluxRepository.parse_api(result)

    async def delete(self, rid: ResourceId) -> bool:
        return await self._delete(self.BASE_PATH, rid)

    async def ingest_metrics(self, rid: ResourceId, points: List[InfluxDataPoint]) -> None:
        points_data = [point.model_dump(exclude_defaults=True, mode="json") for point in points]
        await self._session.post(
            f"{self.BASE_PATH}/{rid}/metrics/ingest",
            json={"points": points_data},
        )

    async def query_metrics(
        self,
        rid: ResourceId,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        tag_filters: Optional[List[InfluxTagFilter]] = None,
    ) -> Any:
        date_from_data = date_from.isoformat() if date_from else None
        date_to_data = date_to.isoformat() if date_to else None
        tag_filter_data = (
            [tag_filter.model_dump(exclude_defaults=True, mode="json") for tag_filter in tag_filters]
            if tag_filters
            else []
        )

        response = await self._session.post(
            f"{self.BASE_PATH}/{rid}/metrics/query",
            json={
                "date_from": date_from_data,
                "date_to": date_to_data,
                "tag_filters": tag_filter_data,
            },
        )
        return response.json()
