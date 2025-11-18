#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, List, Optional, Any
from datetime import datetime


class LinkedInPostParser:
    """Parser for LinkedIn GraphQL API responses."""

    @staticmethod
    def parse_response(response: Dict) -> List[Dict]:
        """
        Parse the LinkedIn API response and extract post information.

        Args:
            response: Raw API response dictionary

        Returns:
            List of parsed post dictionaries
        """
        posts = []

        try:
            # Try both possible response structures
            # Structure 1: data -> data -> searchDashClustersByAll
            # Structure 2: data -> searchDashClustersByAll
            data = response.get('data', {})
            if 'searchDashClustersByAll' in data:
                # Direct structure (data -> searchDashClustersByAll)
                search_results = data.get('searchDashClustersByAll', {})
            else:
                # Nested structure (data -> data -> searchDashClustersByAll)
                search_results = data.get('data', {}).get('searchDashClustersByAll', {})

            elements = search_results.get('elements', [])

            included = response.get('included', [])

            for element in elements:
                if not element.get('items'):
                    continue

                for item in element['items']:
                    post_item = item.get('item', {})

                    # Try searchFeedUpdate first (full post format)
                    feed_update = post_item.get('searchFeedUpdate')
                    if feed_update and feed_update.get('update'):
                        update_urn = feed_update['update']
                        post_data = LinkedInPostParser._extract_post_data(
                            update_urn, included
                        )
                        if post_data:
                            posts.append(post_data)

                    # Otherwise try entityResult (simplified format)
                    elif post_item.get('entityResult'):
                        entity_data = LinkedInPostParser._extract_entity_data(post_item['entityResult'])
                        if entity_data:
                            posts.append(entity_data)

        except Exception as e:
            print(f"Error parsing response: {str(e)}")

        return posts

    @staticmethod
    def _extract_post_data(update_urn: str, included: List[Dict]) -> Optional[Dict]:
        """
        Extract post data from the included array.

        Args:
            update_urn: URN of the update to find
            included: List of included entities

        Returns:
            Dictionary with parsed post data or None
        """
        # Find the update in the included array
        update = None
        for item in included:
            if item.get('entityUrn') == update_urn:
                update = item
                break

        if not update:
            return None

        try:
            # Extract full data first
            author_data = LinkedInPostParser._extract_author(update, included)
            content_data = LinkedInPostParser._extract_content(update)
            metadata = LinkedInPostParser._extract_metadata(update)
            engagement_data = LinkedInPostParser._extract_engagement(update, included)
            article_data = LinkedInPostParser._extract_article(update)

            # Convert timestamp
            import time
            import re
            posted_str = metadata.get('posted', '')
            timestamp_ms = None
            if posted_str:
                current_time_ms = int(time.time() * 1000)
                match = re.search(r'(\d+)\s*(h|hour|hours|d|day|days|w|week|weeks|m|month|months|y|year|years)', posted_str.lower())
                if match:
                    value = int(match.group(1))
                    unit = match.group(2)
                    if unit in ['h', 'hour', 'hours']:
                        offset_ms = value * 60 * 60 * 1000
                    elif unit in ['d', 'day', 'days']:
                        offset_ms = value * 24 * 60 * 60 * 1000
                    elif unit in ['w', 'week', 'weeks']:
                        offset_ms = value * 7 * 24 * 60 * 60 * 1000
                    elif unit in ['m', 'month', 'months']:
                        offset_ms = value * 30 * 24 * 60 * 60 * 1000
                    elif unit in ['y', 'year', 'years']:
                        offset_ms = value * 365 * 24 * 60 * 60 * 1000
                    else:
                        offset_ms = 0
                    timestamp_ms = current_time_ms - offset_ms

            # Build simplified post data
            post_data = {
                'urn': update_urn,  # Keep for deduplication
                'author': author_data.get('name', 'Unknown'),
                'timestamp': timestamp_ms,
                'content': content_data.get('text', ''),
                'engagement': {
                    'likes': engagement_data.get('likes', 0),
                    'comments': engagement_data.get('comments', 0),
                    'shares': engagement_data.get('shares', 0),
                },
                'title': article_data.get('title') if article_data else None,
                'link': LinkedInPostParser._build_post_url(update),
            }
            return post_data
        except Exception as e:
            print(f"Error extracting post data: {str(e)}")
            return None

    @staticmethod
    def _extract_entity_data(entity: Dict) -> Optional[Dict]:
        """
        Extract post data from entityResult format (search results).

        Args:
            entity: Entity result dictionary

        Returns:
            Dictionary with parsed post data or None
        """
        try:
            # Extract text content - try to find the actual post content
            content_text = ''

            # Priority order for content extraction
            # 1. Try summary (most likely to contain post content)
            summary = entity.get('summary', {})
            if isinstance(summary, dict) and 'text' in summary:
                content_text = summary['text']

            # 2. Try snippet
            if not content_text:
                snippet = entity.get('snippet', {})
                if isinstance(snippet, dict) and 'text' in snippet:
                    content_text = snippet['text']

            # 3. Try caption
            if not content_text:
                caption = entity.get('caption', {})
                if isinstance(caption, dict) and 'text' in caption:
                    content_text = caption['text']

            # 4. Try navigationText
            if not content_text:
                nav_text = entity.get('navigationText', {})
                if isinstance(nav_text, dict) and 'text' in nav_text:
                    content_text = nav_text['text']

            # Extract author info
            title = entity.get('title', {})
            author_name = title.get('text', 'Unknown')

            # Extract other metadata
            tracking_urn = entity.get('trackingUrn', '')
            badges = entity.get('badges', {})

            # Extract URLs - post URL vs profile URL
            post_url = (
                entity.get('bserpEntityNavigationalUrl') or
                entity.get('navigationUrl') or
                entity.get('url') or
                ''
            )
            # Clean up URL - remove query parameters
            if post_url and '?' in post_url:
                post_url = post_url.split('?')[0]
            # Convert timestamp for entity data (from secondarySubtitle which has time info)
            import time
            import re
            secondary_subtitle = entity.get('secondarySubtitle', {}).get('text', '')
            timestamp_ms = None
            if secondary_subtitle:
                current_time_ms = int(time.time() * 1000)
                match = re.search(r'(\d+)\s*(h|hour|hours|d|day|days|w|week|weeks|m|month|months|y|year|years)', secondary_subtitle.lower())
                if match:
                    value = int(match.group(1))
                    unit = match.group(2)
                    if unit in ['h', 'hour', 'hours']:
                        offset_ms = value * 60 * 60 * 1000
                    elif unit in ['d', 'day', 'days']:
                        offset_ms = value * 24 * 60 * 60 * 1000
                    elif unit in ['w', 'week', 'weeks']:
                        offset_ms = value * 7 * 24 * 60 * 60 * 1000
                    elif unit in ['m', 'month', 'months']:
                        offset_ms = value * 30 * 24 * 60 * 60 * 1000
                    elif unit in ['y', 'year', 'years']:
                        offset_ms = value * 365 * 24 * 60 * 60 * 1000
                    else:
                        offset_ms = 0
                    timestamp_ms = current_time_ms - offset_ms

            # Build simplified post data
            post_data = {
                'urn': tracking_urn,  # Keep for deduplication
                'author': author_name,
                'timestamp': timestamp_ms,
                'content': content_text,
                'engagement': {
                    'likes': 0,
                    'comments': 0,
                    'shares': 0,
                },
                'title': None,
                'link': post_url,
            }

            return post_data

        except Exception as e:
            print(f"Error extracting entity data: {str(e)}")
            return None

    @staticmethod
    def _build_post_url(update: Dict) -> str:
        """Build the post URL from update data."""
        share_url = update.get('socialContent', {}).get('shareUrl', '')
        # Clean up URL - remove query parameters
        if share_url and '?' in share_url:
            share_url = share_url.split('?')[0]
        return share_url

    @staticmethod
    def _extract_author(update: Dict, included: List[Dict]) -> Dict:
        """Extract author information."""
        actor = update.get('actor', {})

        author_data = {
            'name': actor.get('name', {}).get('text', ''),
            'description': actor.get('description', {}).get('text', ''),
            'profile_url': actor.get('navigationContext', {}).get('actionTarget', ''),
            'backend_urn': actor.get('backendUrn', ''),
        }

        # Extract profile information from included
        backend_urn = actor.get('backendUrn', '')
        for item in included:
            if item.get('entityUrn') == backend_urn or item.get('entityUrn', '').endswith(backend_urn.split(':')[-1]):
                if item.get('$type') == 'com.linkedin.voyager.dash.identity.profile.Profile':
                    author_data['public_identifier'] = item.get('publicIdentifier', '')
                elif item.get('$type') == 'com.linkedin.voyager.dash.organization.Company':
                    author_data['company_name'] = item.get('name', '')

        return author_data

    @staticmethod
    def _extract_content(update: Dict) -> Dict:
        """Extract post content/commentary."""
        commentary = update.get('commentary', {})

        return {
            'text': commentary.get('text', {}).get('text', ''),
            'num_lines': commentary.get('numLines', 0),
        }

    @staticmethod
    def _extract_metadata(update: Dict) -> Dict:
        """Extract post metadata."""
        metadata = update.get('metadata', {})
        actor = update.get('actor', {})
        sub_description = actor.get('subDescription', {}).get('text', '')

        return {
            'backend_urn': metadata.get('backendUrn', ''),
            'share_urn': metadata.get('shareUrn', ''),
            'share_audience': metadata.get('shareAudience', ''),
            'posted': sub_description,  # Contains posting time info
        }

    @staticmethod
    def _extract_engagement(update: Dict, included: List[Dict]) -> Dict:
        """Extract engagement metrics (likes, comments, shares)."""
        social_detail_urn = update.get('socialDetail', '')

        # Find social activity counts
        for item in included:
            if item.get('$type') == 'com.linkedin.voyager.dash.feed.SocialActivityCounts':
                item_urn = item.get('entityUrn', '')
                # Match based on activity URN
                if social_detail_urn and social_detail_urn in item_urn or update.get('metadata', {}).get('backendUrn', '') in item_urn:
                    return {
                        'likes': item.get('numLikes', 0),
                        'comments': item.get('numComments', 0),
                        'shares': item.get('numShares', 0),
                        'impressions': item.get('numImpressions'),
                        'liked': item.get('liked', False),
                        'reaction_types': [
                            {
                                'type': r.get('reactionType'),
                                'count': r.get('count')
                            }
                            for r in item.get('reactionTypeCounts', [])
                        ]
                    }

        return {
            'likes': 0,
            'comments': 0,
            'shares': 0,
            'impressions': None,
            'liked': False,
            'reaction_types': []
        }

    @staticmethod
    def _extract_hashtags(update: Dict) -> List[str]:
        """Extract hashtags from the post."""
        hashtags = []
        commentary = update.get('commentary', {})
        text_data = commentary.get('text', {})
        attributes = text_data.get('attributesV2', [])

        for attr in attributes:
            detail_data = attr.get('detailData', {})
            if 'hashtag' in detail_data and detail_data.get('hashtag'):
                # Extract hashtag URN and get the hashtag text
                hashtag_urn = detail_data['hashtag']
                if isinstance(hashtag_urn, str):
                    # URN format: urn:li:fsd_hashtag:(hashtagtext,...)
                    parts = hashtag_urn.split(':(')
                    if len(parts) > 1:
                        hashtag_text = parts[1].split(',')[0]
                        hashtags.append(f"#{hashtag_text}")

        return list(set(hashtags))  # Remove duplicates

    @staticmethod
    def _extract_links(update: Dict) -> List[str]:
        """Extract URLs from the post."""
        links = []
        commentary = update.get('commentary', {})
        text_data = commentary.get('text', {})
        attributes = text_data.get('attributesV2', [])

        for attr in attributes:
            detail_data = attr.get('detailData', {})
            text_link = detail_data.get('textLink', {})
            if text_link and text_link.get('url'):
                links.append(text_link['url'])

        # Also check for article links
        article = update.get('content', {}).get('articleComponent')
        if article:
            nav_context = article.get('navigationContext', {})
            if nav_context.get('actionTarget'):
                links.append(nav_context['actionTarget'])

        return links

    @staticmethod
    def _extract_images(update: Dict) -> List[Dict]:
        """Extract image information from the post."""
        images = []
        image_component = update.get('content', {}).get('imageComponent')

        if image_component and image_component.get('images'):
            for img in image_component['images']:
                attributes = img.get('attributes', [])
                if attributes:
                    attr = attributes[0]
                    detail_data = attr.get('detailData', {})
                    vector_image = detail_data.get('vectorImage', {})

                    if vector_image:
                        images.append({
                            'root_url': vector_image.get('rootUrl', ''),
                            'artifacts': [
                                {
                                    'width': a.get('width'),
                                    'height': a.get('height'),
                                    'url': vector_image.get('rootUrl', '') + a.get('fileIdentifyingUrlPathSegment', '')
                                }
                                for a in vector_image.get('artifacts', [])
                            ]
                        })

        return images

    @staticmethod
    def _extract_article(update: Dict) -> Optional[Dict]:
        """Extract article information if the post contains an article."""
        article_component = update.get('content', {}).get('articleComponent')

        if not article_component:
            return None

        return {
            'title': article_component.get('title', {}).get('text', ''),
            'subtitle': article_component.get('subtitle', {}).get('text', ''),
            'description': article_component.get('description', {}).get('text', ''),
            'url': article_component.get('navigationContext', {}).get('actionTarget', ''),
            'type': article_component.get('type', ''),
        }

    @staticmethod
    def export_to_simple_format(posts: List[Dict]) -> List[Dict]:
        """
        Convert parsed posts to a simpler, more readable format.

        Args:
            posts: List of parsed posts

        Returns:
            List of simplified post dictionaries
        """
        simplified = []

        for post in posts:
            simplified.append({
                'author': post['author']['name'],
                'author_profile': post['author']['profile_url'],
                'content': post['content']['text'],
                'post_url': post['post_url'],
                'posted': post['metadata']['posted'],
                'likes': post['engagement']['likes'],
                'comments': post['engagement']['comments'],
                'shares': post['engagement']['shares'],
                'hashtags': post['hashtags'],
                'links': post['links'],
                'has_images': len(post['images']) > 0,
                'article_title': post['article']['title'] if post['article'] else None,
            })

        return simplified
