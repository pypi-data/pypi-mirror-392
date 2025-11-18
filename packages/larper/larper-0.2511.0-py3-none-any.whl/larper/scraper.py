#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import time
from typing import Dict, List, Optional, Union, Generator, Any, Set
from urllib.parse import quote

DEFAULT_SLEEP_TIME = 1.0
DEFAULT_BATCH_SIZE = 10


class Larper:
    """
    LinkedIn posts scraper using the GraphQL API.
    Requires authentication cookies to work properly.
    """

    BASE_URL = "https://www.linkedin.com/voyager/api/graphql"
    QUERY_ID = "voyagerSearchDashClusters.ef3d0937fb65bd7812e32e5a85028e79"

    def __init__(self, cookies: Dict[str, str], headers: Optional[Dict[str, str]] = None):
        """
        Initialize the scraper with authentication cookies.

        Args:
            cookies: Dictionary with LinkedIn session cookies
            headers: Optional additional headers
        """
        self.cookies = cookies
        self.additional_headers = headers or {}

    def _build_headers(self) -> Dict[str, str]:
        """Build request headers."""
        # Build cookie string from cookies dict
        cookie_parts = []
        for key, value in self.cookies.items():
            cookie_parts.append(f'{key}={value}')
        cookie_string = ';'.join(cookie_parts)

        # Headers exactly as in working example
        # NOTE: csrf-token needs the full JSESSIONID value INCLUDING "ajax:" prefix
        headers = {
            'Cookie': cookie_string,
            'csrf-token': self.cookies.get('JSESSIONID', ''),
        }

        # Add any additional headers
        if self.additional_headers:
            headers.update(self.additional_headers)

        return headers

    def _build_query_params(
        self,
        keywords: str,
        start: int = 0,
        count: int = 10,
        sort_by: str = "date_posted"
    ) -> str:
        """
        Build the GraphQL query parameters in LinkedIn's format.

        Args:
            keywords: Search keywords
            start: Pagination start index
            count: Number of results to fetch
            sort_by: Sort criterion (date_posted or relevance)

        Returns:
            Encoded query string
        """
        # URL encode the keywords
        encoded_keywords = quote(keywords)

        # Build the variables string in LinkedIn's format (parentheses and colons)
        # Using GLOBAL_SEARCH_HEADER as origin for better results
        variables = (
            f"(start:{start},"
            f"origin:GLOBAL_SEARCH_HEADER,"
            f"query:(keywords:{encoded_keywords},"
            f"flagshipSearchIntent:SEARCH_SRP,"
            f"queryParameters:List("
            f"(key:resultType,value:List(CONTENT)),"
            f"(key:sortBy,value:List({sort_by}))"
            f"),"
            f"includeFiltersInResponse:false),"
            f"count:{count})"
        )

        return f"variables={variables}&queryId={self.QUERY_ID}"

    def _normalize_query(self, query: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Normalize query to dictionary format.

        Args:
            query: Raw string or dictionary query

        Returns:
            Normalized query dictionary
        """
        if isinstance(query, str):
            return {
                'keywords': query,
                'sort_by': 'date_posted'
            }
        return query

    def _fetch_page(
        self,
        keywords: str,
        start: int = 0,
        count: int = DEFAULT_BATCH_SIZE,
        sort_by: str = "date_posted"
    ) -> Dict:
        """
        Fetch a single page of results.

        Args:
            keywords: Search keywords
            start: Pagination start index
            count: Number of results to fetch
            sort_by: Sort by 'date_posted' or 'relevance'

        Returns:
            Dictionary with the API response

        Raises:
            Exception: If the request fails
        """
        query_params = self._build_query_params(keywords, start, count, sort_by)
        url = f"{self.BASE_URL}?{query_params}"

        # Build headers for this request
        headers = self._build_headers()

        try:
            # Use requests directly, not session - exactly as in working example
            response = requests.request("GET", url, headers=headers, data="")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching posts: {str(e)}")

    def search(
        self,
        query: Union[Dict[str, Any], List[Dict[str, Any]], str, List[str]],
        deep: bool = False,
        fast: bool = False,
        limit: Optional[int] = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
        sort_by: str = "date_posted",
        sleep_time: float = DEFAULT_SLEEP_TIME,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Search posts matching the given query.

        Args:
            query: Query definition or list of queries. Each query can be a
                raw string or a dictionary with 'keywords' and optional 'sort_by'.
            deep: If True, paginate through all results until no more are left.
            fast: When combined with deep, stop searching as soon as a cursor
                (pagination offset) repeats or no new results appear.
            limit: Maximum number of posts to yield. None means unlimited.
            batch_size: Number of posts to fetch per request.
            sort_by: Default sort criterion ('date_posted' or 'relevance').
            sleep_time: Delay between requests to avoid rate limits.

        Yields:
            Dictionaries representing posts. Each post includes a 'raw_query'
            field with the query string used to fetch it, and 'query_info'
            with full query details.
        """
        # Normalize queries to list
        if not isinstance(query, list):
            queries = [query]
        else:
            queries = query

        yielded_count = 0
        seen_urns: Set[str] = set()  # Track seen posts to avoid duplicates

        for q in queries:
            # Normalize query
            normalized = self._normalize_query(q)
            keywords = normalized.get('keywords', '')
            query_sort_by = normalized.get('sort_by', sort_by)

            if not keywords:
                continue

            # Track pagination
            start = 0
            seen_cursors: Set[int] = set()
            no_new_results_count = 0

            while True:
                # Check limit
                if limit is not None and yielded_count >= limit:
                    return

                # Check for cursor repeat (fast mode)
                if fast and start in seen_cursors:
                    break
                seen_cursors.add(start)

                # Fetch page
                try:
                    response = self._fetch_page(
                        keywords=keywords,
                        start=start,
                        count=batch_size,
                        sort_by=query_sort_by
                    )

                    # Parse response
                    from .parser import LinkedInPostParser
                    posts = LinkedInPostParser.parse_response(response)

                    if not posts:
                        no_new_results_count += 1
                        if not deep or no_new_results_count >= 2:
                            break
                    else:
                        no_new_results_count = 0

                    # Yield posts
                    new_posts_found = False
                    for post in posts:
                        # Check for duplicates
                        post_urn = post.get('urn', '')
                        if post_urn in seen_urns:
                            continue

                        seen_urns.add(post_urn)
                        new_posts_found = True

                        # Add query information
                        post['raw_query'] = keywords
                        post['query_info'] = {
                            'keywords': keywords,
                            'sort_by': query_sort_by,
                            'offset': start
                        }

                        yield post

                        yielded_count += 1
                        if limit is not None and yielded_count >= limit:
                            return

                    # Check if we should continue pagination
                    if not deep:
                        break

                    if fast and not new_posts_found:
                        break

                    # If no posts were returned, stop pagination
                    if not posts:
                        break

                    # Move to next page
                    start += batch_size

                    # Sleep to avoid rate limits
                    if sleep_time > 0:
                        time.sleep(sleep_time)

                except Exception as e:
                    print(f"Error fetching posts at offset {start}: {str(e)}")
                    break
