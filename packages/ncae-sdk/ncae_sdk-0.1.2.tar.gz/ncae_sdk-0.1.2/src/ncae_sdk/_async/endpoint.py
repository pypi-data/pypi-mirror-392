from typing import IO, Any, AsyncIterator, Callable, Final, Mapping, Optional, Union

from pydantic import TypeAdapter
from typing_extensions import TypeAlias, Unpack

from ncae_sdk._async.session import AsyncSession
from ncae_sdk._error import NcaeHttpError
from ncae_sdk._http import RequestArgs, Response
from ncae_sdk._resource import ResourceId
from ncae_sdk._util import next_async

PreProcessor: TypeAlias = Callable[[dict[str, Any]], dict[str, Any]]
PostProcessor: TypeAlias = Callable[[Response], Any]


class AsyncEndpoint:
    __slots__ = ("_session",)

    DEFAULT_PAGE_SIZE: int = 250

    def __init__(self, *, session: AsyncSession) -> None:
        self._session: Final[AsyncSession] = session

    async def _refetch(self, url: str, response: Response) -> Any:
        if response.status_code == 204 or (response.status_code == 200 and len(response.content) == 0):
            return None

        response_json = response.json()
        if isinstance(response_json, dict) and "id" in response_json:
            return await self._get_by_id(url, response_json["id"])

        return response_json

    async def _create(
        self,
        url: str,
        create_model: TypeAdapter[Any],
        payload: Any,
        *,
        preprocessor: Optional[PreProcessor] = None,
    ) -> Any:
        payload_data = self._transform_data(create_model, payload)
        payload_data = preprocessor(payload_data) if preprocessor else payload_data
        response = await self._session.post(url, json=payload_data)
        return await self._refetch(url, response)

    async def _create_multipart(
        self,
        url: str,
        create_model: TypeAdapter[Any],
        payload: Any,
        files: Mapping[str, IO[bytes]],
        *,
        preprocessor: Optional[PreProcessor] = None,
    ) -> Any:
        payload_data = self._transform_data(create_model, payload)
        payload_data = preprocessor(payload_data) if preprocessor else payload_data
        response = await self._session.post(url, data=payload_data, files=files)
        return await self._refetch(url, response)

    async def _update(
        self,
        url: str,
        rid: ResourceId,
        update_model: TypeAdapter[Any],
        payload: Any,
        *,
        preprocessor: Optional[PreProcessor] = None,
    ) -> Any:
        payload_data = self._transform_data(update_model, payload)
        payload_data = preprocessor(payload_data) if preprocessor else payload_data
        response = await self._session.patch(f"{url}/{rid}", json=payload_data)
        return await self._refetch(url, response)

    async def _delete(self, url: str, rid: ResourceId) -> bool:
        try:
            await self._session.delete(f"{url}/{rid}")
            return True
        except NcaeHttpError as exc:
            if exc.status_code == 404:
                return False

            raise

    async def _list(
        self,
        url: str,
        filter_model: TypeAdapter[Any],
        filters: Any,
        paginate: bool = True,
        page_size: Optional[int] = None,
        postprocessor: Optional[PostProcessor] = None,
    ) -> AsyncIterator[Any]:
        filter_data = self._transform_data(filter_model, filters)
        query = self._encode_query_values(filter_data)

        if paginate:
            results = self._paginate(url, query=query, page_size=page_size)
            async for result in results:
                yield result
        else:
            response = await self._session.get(url, query=query)
            response_data = postprocessor(response) if postprocessor else response.json()
            if not isinstance(response_data, list):
                raise ValueError(f"Unexpected response format: {response_data}")

            for result in response_data:
                yield result

    async def _get_by_id(self, url: str, rid: ResourceId) -> Optional[Any]:
        try:
            response = await self._session.get(f"{url}/{rid}")
            return response.json()
        except NcaeHttpError as exc:
            if exc.status_code == 404:
                return None

            raise

    async def _get_by_filters(self, url: str, filter_model: TypeAdapter[Any], filters: Any) -> Optional[Any]:
        results = self._list(url, filter_model, filters, page_size=2)

        # Return early if there are no results, indicating a lack of existence
        first = await next_async(results, None)
        if first is None:
            return None

        # Ensure uniqueness by raising if there is a second result
        second = await next_async(results, None)
        if second is not None:
            raise ValueError(f"Received more than one result for [{url}] with filters: {filters}")

        return first

    async def _paginate(
        self,
        url: str,
        *,
        page_size: Optional[int] = None,
        postprocessor: Optional[PostProcessor] = None,
        **kwargs: Unpack[RequestArgs],
    ) -> AsyncIterator[Any]:
        offset: int = 0
        limit: int = page_size or self.DEFAULT_PAGE_SIZE

        # Iterate over all available pages
        while True:
            # Update query parameters with pagination details
            kwargs["query"].update({"offset": str(offset), "limit": str(limit)})

            # Fetch current page and extract content as JSON
            response = await self._session.get(url, **kwargs)
            response_data = postprocessor(response) if postprocessor else response.json()

            # Ensure page matches expected structure
            if not isinstance(response_data, dict):
                raise ValueError(f"Unexpected response format: {response_data}")
            if not all(key in response_data for key in {"count", "next", "results"}):
                raise ValueError(f"Missing expected keys in response: {response_data}")

            # Yield current results and break if no further pages are available
            for result in response_data["results"]:
                yield result
            if not response_data["count"] or not response_data["results"] or not response_data["next"]:
                break

            # Update query parameters for next page
            offset += limit

    @classmethod
    def _transform_data(cls, filter_model: TypeAdapter[Any], data: Any) -> Any:
        instance = filter_model.validate_python(data)
        return filter_model.dump_python(instance, by_alias=True, mode="json")

    @classmethod
    def _encode_query_values(cls, values: dict[str, Any]) -> dict[str, Union[str, list[str]]]:
        query: dict[str, Union[str, list[str]]] = {}
        for key, value in values.items():
            encoded_key = str(key)
            encoded_value = cls._encode_query_value(value)
            if isinstance(encoded_value, list):
                query[f"{encoded_key}[]"] = encoded_value
            else:
                query[encoded_key] = encoded_value

        return query

    @classmethod
    def _encode_query_value(cls, value: Any) -> Union[str, list[str]]:
        if isinstance(value, str):
            return value
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, list):
            return [str(v) for v in value]
        elif value is None:
            return "null"
        else:
            raise TypeError(f"Unsupported query value type: {type(value)}")
