from collections.abc import AsyncIterator
from typing import Any, Final

from typing_extensions import Unpack

from ncae_sdk._async.endpoint import AsyncEndpoint
from ncae_sdk._http import Response
from ncae_sdk._util import map_async, next_async
from ncae_sdk.resources._schema import (
    TagRelation,
    TagRelationCreate,
    TagRelationCreateModel,
    TagRelationFilter,
    TagRelationFilterModel,
)


class AsyncTagRelationEndpoint(AsyncEndpoint):
    BASE_PATH: Final[str] = "tag/v1/tag-relations"

    async def list(self, **filters: Unpack[TagRelationFilter]) -> AsyncIterator[TagRelation]:
        results = self._list(
            self.BASE_PATH,
            TagRelationFilterModel,
            filters,
            paginate=False,
            postprocessor=self._flatten_response,
        )
        return map_async(TagRelation.parse_api, results)

    async def set(self, **payload: Unpack[TagRelationCreate]) -> TagRelation:
        await self._create(self.BASE_PATH, TagRelationCreateModel, payload)
        results = await self.list(object_type=payload["object_type"], object_ids=[payload["object_id"]])
        relation = await next_async(results)
        if relation is None:
            raise ValueError("No relation found after creation")

        return relation

    @classmethod
    def _flatten_response(cls, response: Response) -> Any:
        """
        The API response for this endpoint is somewhat exotic, given it returns a dictionary of object id to tag ids.
        To match our overall expected data structure, flatten the response into a list of dictionaries.
        Additionally, include the object type in each dictionary for clarity, which can be extracted from the request.
        """

        object_type = response.request.query_params["model_name"]
        response_data = response.json()
        if not isinstance(response_data, dict):
            raise ValueError("Invalid response data format")

        results = []
        for object_id, tags in response_data.items():
            if not isinstance(tags, list):
                raise ValueError(f"Invalid tag IDs format for object ID {object_id}")

            tag_ids: list[int] = [int(tag["id"]) for tag in tags]
            results.append({"object_type": object_type, "object_id": object_id, "tag_ids": tag_ids})

        return results
