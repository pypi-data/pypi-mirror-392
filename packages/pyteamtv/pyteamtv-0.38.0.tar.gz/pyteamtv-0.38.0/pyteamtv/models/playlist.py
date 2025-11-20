from typing import Optional, List
from pyteamtv.infra.requester import Requester
from pyteamtv.models.teamtv_object import TeamTVObject


class VideoFragment:
    """Represents a video fragment (clip) in a playlist."""

    def __init__(
        self,
        video_id: str,
        start_time: float,
        end_time: float,
        description: str,
        video_fragment_id: Optional[str] = None,
        event_time: Optional[float] = None,
        creator_user_id: Optional[str] = None,
        creator_role_name: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        created: Optional[str] = None,
    ):
        self.video_fragment_id = video_fragment_id
        self.video_id = video_id
        self.start_time = start_time
        self.end_time = end_time
        self.description = description
        self.event_time = (
            event_time if event_time is not None else (end_time - start_time) / 2
        )
        self.creator_user_id = creator_user_id
        self.creator_role_name = creator_role_name
        self.thumbnail_url = thumbnail_url
        self.created = created

    def to_dict(self):
        """Convert to dict for API requests."""
        result = {
            "videoId": self.video_id,
            "startTime": self.start_time,
            "endTime": self.end_time,
            "eventTime": self.event_time,
            "description": self.description,
        }

        # Only include videoFragmentId for existing fragments (updates)
        if self.video_fragment_id is not None:
            result["videoFragmentId"] = self.video_fragment_id

        # Only include creator fields if they're not None
        if self.creator_user_id is not None:
            result["creatorUserId"] = self.creator_user_id
        if self.creator_role_name is not None:
            result["creatorRoleName"] = self.creator_role_name

        return result

    @classmethod
    def from_dict(cls, data: dict) -> "VideoFragment":
        """Create VideoFragment from API response."""
        return cls(
            video_fragment_id=data["videoFragmentId"],
            video_id=data["videoId"],
            start_time=data["startTime"],
            end_time=data["endTime"],
            description=data.get("description", ""),
            event_time=data.get("eventTime"),
            creator_user_id=data.get("creatorUserId"),
            creator_role_name=data.get("creatorRoleName"),
            thumbnail_url=data.get("thumbnailUrl"),
            created=data.get("created"),
        )

    def __repr__(self):
        return f"<VideoFragment id={self.video_fragment_id} video={self.video_id} {self.start_time}-{self.end_time}>"


class Playlist(TeamTVObject):
    """Represents a TeamTV playlist containing video fragments."""

    @property
    def playlist_id(self) -> str:
        return self._playlist_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def created(self) -> str:
        return self._created

    @property
    def creator(self) -> dict:
        return self._creator

    @property
    def permissions(self) -> list:
        return self._permissions

    @property
    def poster(self) -> Optional[str]:
        return self._poster

    @property
    def video_fragments(self) -> List[VideoFragment]:
        return self._video_fragments

    @property
    def group_id(self) -> Optional[str]:
        return self._group_id

    def add_video_fragment(
        self,
        video_id: str,
        start_time: float,
        end_time: float,
        description: str = "",
    ) -> str:
        """
        Add a video fragment to the playlist.

        Args:
            video_id: The ID of the video
            start_time: Start time in seconds
            end_time: End time in seconds
            description: Optional description of the fragment

        Returns:
            The ID of the created video fragment
        """
        response = self._requester.request(
            "POST",
            f"/playlists/{self.playlist_id}/addVideoFragment",
            {
                "videoId": video_id,
                "startTime": int(start_time),
                "endTime": int(end_time),
                "description": description,
            },
        )

        return response

    def set_video_fragments(self, video_fragments: List[VideoFragment]) -> str:
        """
        Set all video fragments at once (replaces existing fragments).

        Args:
            video_fragments: List of VideoFragment objects

        Returns:
            Status message
        """
        fragments_data = [fragment.to_dict() for fragment in video_fragments]

        response = self._requester.request(
            "POST",
            f"/playlists/{self.playlist_id}/setVideoFragments",
            {"videoFragments": fragments_data},
        )

        # Refresh the playlist data
        self._refresh()

        return response

    def remove_video_fragment(self, video_fragment_id: str) -> str:
        """
        Remove a video fragment from the playlist.

        Args:
            video_fragment_id: The ID of the video fragment to remove

        Returns:
            Status message
        """
        response = self._requester.request(
            "POST",
            f"/playlists/{self.playlist_id}/removeVideoFragment",
            {"videoFragmentId": video_fragment_id},
        )

        # Refresh the playlist data
        self._refresh()

        return response

    def change_name_and_description(self, name: str, description: str) -> str:
        """
        Update the playlist name and description.

        Args:
            name: New name
            description: New description

        Returns:
            Status message
        """
        response = self._requester.request(
            "POST",
            f"/playlists/{self.playlist_id}/changeNameAndDescription",
            {"name": name, "description": description},
        )

        # Update local cache
        self._name = name
        self._description = description

        return response

    def delete(self) -> str:
        """
        Delete this playlist.

        Returns:
            Status message
        """
        return self._requester.request(
            "DELETE",
            f"/playlists/{self.playlist_id}",
        )

    def _refresh(self):
        """Refresh the playlist data from the server."""
        data = self._requester.request("GET", f"/playlists/{self.playlist_id}")
        self._use_attributes(data)

    def _use_attributes(self, attributes: dict):
        self._playlist_id = attributes["playlistId"]
        self._name = attributes["name"]
        self._description = attributes.get("description", "")
        self._created = attributes.get("created")
        self._creator = attributes.get("creator")
        self._permissions = attributes.get("permissions", [])
        self._poster = attributes.get("poster")
        self._group_id = attributes.get("groupId")

        # Parse video fragments
        self._video_fragments = [
            VideoFragment.from_dict(fragment)
            for fragment in attributes.get("videoFragments", [])
        ]

        super()._use_attributes(attributes)

    def __repr__(self):
        return f"<Playlist id={self.playlist_id} name='{self.name}' fragments={len(self.video_fragments)}>"
