import os.path

import pytest

from pyteamtv.exceptions import InputError


class TestVideoUpload:
    def test_new_video(self, current_team, test_mp4, requests_mock):
        """
        Test upload of a new video
        """
        sporting_event_id = "sporting-event-id-123"
        video_id = "video-id-123"

        requests_mock.get(
            f"https://fake-url/sportingEvents/{sporting_event_id}",
            json={
                "type": "training",
                "name": "Test Training",
                "sportingEventId": sporting_event_id,
                "clocks": {},
                "scheduledAt": "2022-01-01T10:00:00.000Z",
            },
        )

        sporting_event = current_team.get_sporting_event(
            sporting_event_id=sporting_event_id
        )

        file_size = os.path.getsize(test_mp4)

        adapter = requests_mock.post(
            f"https://fake-url/sportingEvents/{sporting_event_id}/initVideoUpload",
            json=video_id,
        )
        requests_mock.get(
            f"https://fake-url/videos/{video_id}",
            json={
                "videoId": video_id,
                "state": "new",
                "parts": [
                    {
                        "fileSize": file_size,
                        "tusUploadUrl": "https://upload-url/random-url",
                    }
                ],
            },
        )
        requests_mock.head(
            "https://upload-url/random-url",
            headers={
                "Upload-Offset": "0",
                "Upload-Length": str(file_size),
                "Tus-Resumable": "1.0.0",
            },
        )
        patch_adapter = requests_mock.patch(
            "https://upload-url/random-url",
            headers={
                "upload-offset": str(file_size),
                "Upload-Length": str(file_size),
                "Tus-Resumable": "1.0.0",
            },
        )

        sporting_event.upload_video(test_mp4, description="Test Training")

        assert adapter.last_request.json() == {
            "description": "Test Training",
            "files": [{"name": "test.mp4", "size": 991017}],
            "skipTranscoding": False,
            "tags": {},
        }

        assert len(patch_adapter.last_request.body) == file_size

    def test_resume_video(self, current_team, test_mp4, requests_mock):
        """
        Test resume of upload of an existing video.

        This test includes:
        1. Test tags are set when resume_if_exists is set
        2. Remote and local files match size
        3. File upload is resumed at based on Upload-Offset header
        """
        sporting_event_id = "sporting-event-id-123"
        tags = {"output_key": "main"}
        video_id = "video-id-123"

        requests_mock.get(
            f"https://fake-url/sportingEvents/{sporting_event_id}",
            json={
                "type": "training",
                "name": "Test Training",
                "sportingEventId": sporting_event_id,
                "clocks": {},
                "videoIds": [video_id],
                "scheduledAt": "2022-01-01T10:00:00.000Z",
            },
        )

        sporting_event = current_team.get_sporting_event(
            sporting_event_id=sporting_event_id
        )

        file_size = os.path.getsize(test_mp4)
        upload_offset = file_size - 100  # Fake the upload offset

        requests_mock.get(
            f"https://fake-url/videos",
            json=[
                {
                    "videoId": video_id,
                    "state": "new",
                    "tags": tags,
                    "parts": [
                        {
                            "fileSize": file_size
                            - 1,  # Return an incorrect filesize. The resume code MUST check
                            # if the local and remote filesizes match.
                            "state": "new",
                            "tusUploadUrl": "https://upload-url/random-url",
                        }
                    ],
                }
            ],
        )
        requests_mock.head(
            "https://upload-url/random-url",
            headers={
                "Upload-Offset": str(upload_offset),
                "Upload-Length": str(file_size),
                "Tus-Resumable": "1.0.0",
            },
        )
        adapter = requests_mock.patch(
            "https://upload-url/random-url",
            headers={
                "Upload-Offset": str(file_size),
                "Upload-Length": str(file_size),
                "Tus-Resumable": "1.0.0",
            },
        )

        with pytest.raises(
            InputError,
            match="When `resume_if_exists` is specified you must pass `tags`",
        ):
            sporting_event.upload_video(
                test_mp4,
                description="Test Training",
                resume_if_exists=True,
            )

        requests_mock.get(
            f"https://fake-url/videos/{video_id}",
            json={
                "videoId": video_id,
                "state": "new",
                "tags": tags,
                "parts": [
                    {
                        "fileSize": file_size,
                        "state": "new",
                        "tusUploadUrl": "https://upload-url/random-url",
                    }
                ],
            },
        )

        with pytest.raises(
            InputError,
            match=r"File size of '.*test\.mp4' doesn't match existing video",
        ):
            sporting_event.upload_video(
                test_mp4,
                description="Test Training",
                resume_if_exists=True,
                tags=tags,
            )

        requests_mock.get(
            f"https://fake-url/videos",
            json=[
                {
                    "videoId": video_id,
                    "state": "new",
                    "tags": tags,
                    "parts": [
                        {
                            "fileSize": file_size,
                            "state": "new",
                            "tusUploadUrl": "https://upload-url/random-url",
                        }
                    ],
                }
            ],
        )
        sporting_event.upload_video(
            test_mp4,
            description="Test Training",
            resume_if_exists=True,
            tags=tags,
        )

        assert len(adapter.last_request.body) == 100

    def test_resume_completed_video(self, current_team, test_mp4, requests_mock):
        """
        Test calling upload to finished video.
        """
        sporting_event_id = "sporting-event-id-123"
        tags = {"output_key": "main"}
        video_id = "video-id-123"

        requests_mock.get(
            f"https://fake-url/sportingEvents/{sporting_event_id}",
            json={
                "type": "training",
                "name": "Test Training",
                "sportingEventId": sporting_event_id,
                "clocks": {},
                "videoIds": [video_id],
                "scheduledAt": "2022-01-01T10:00:00.000Z",
            },
        )

        sporting_event = current_team.get_sporting_event(
            sporting_event_id=sporting_event_id
        )

        file_size = os.path.getsize(test_mp4)

        requests_mock.get(
            f"https://fake-url/videos",
            json=[
                {
                    "videoId": video_id,
                    "state": "new",
                    "tags": tags,
                    "parts": [
                        {
                            "fileSize": file_size,
                            "state": "upload-success",
                            "tusUploadUrl": "https://upload-url/random-url",
                        }
                    ],
                }
            ],
        )

        video = sporting_event.upload_video(
            test_mp4,
            description="Test Training",
            resume_if_exists=True,
            tags=tags,
        )

        assert video.video_id == video_id

    def test_create_livestream(self, current_team, test_mp4, requests_mock):
        """
        Test calling upload to finished video.
        """
        sporting_event_id = "sporting-event-id-123"
        tags = {"output_key": "main"}
        video_id = "video-id-123"

        requests_mock.get(
            f"https://fake-url/sportingEvents/{sporting_event_id}",
            json={
                "type": "training",
                "name": "Test Training",
                "sportingEventId": sporting_event_id,
                "clocks": {},
                # This isn't correct but since the SportingEvent is cached in pyteamtv we need to pass
                # the video id already. Otherwise it will be filtered out in sportingEvent.get_videos()
                "videoIds": [video_id],
                "scheduledAt": "2022-01-01T10:00:00.000Z",
            },
        )

        sporting_event = current_team.get_sporting_event(
            sporting_event_id=sporting_event_id
        )

        adapter = requests_mock.post(
            f"https://fake-url/sportingEvents/{sporting_event_id}/initVideoUpload",
            json=video_id,
        )
        file_size = os.path.getsize(test_mp4)
        requests_mock.get(
            f"https://fake-url/videos",
            [
                # Before we create the livestream
                {"json": []},
                # When livestream is created but no part is added yet
                {
                    "json": [
                        {
                            "videoId": video_id,
                            "state": "new",
                            "tags": tags,
                            "parts": [],
                        }
                    ]
                },
                # When the video part is added
                {
                    "json": [
                        {
                            "videoId": video_id,
                            "state": "new",
                            "tags": tags,
                            "parts": [
                                {
                                    "fileSize": file_size,
                                    "state": "new",
                                    "tusUploadUrl": "https://upload-url/random-url",
                                }
                            ],
                        }
                    ]
                },
            ],
        )

        requests_mock.get(
            f"https://fake-url/videos/{video_id}",
            [
                # When only the livestream is created
                {
                    "json": {
                        "videoId": video_id,
                        "state": "new",
                        "livestream": {"url": "https://some-url/1231232/main.m3u8"},
                        "parts": [],
                    }
                },
                # When VideoPart is added
                {
                    "json": {
                        "videoId": video_id,
                        "state": "new",
                        "livestream": {"url": "https://some-url/1231232/main.m3u8"},
                        "parts": [
                            {
                                "fileSize": file_size,
                                "state": "new",
                                "tusUploadUrl": "https://upload-url/random-url",
                            }
                        ],
                    }
                },
            ],
        )

        video_livestream = sporting_event.create_livestream(
            livestream={"url": "https://some-url/1231232/main.m3u8"},
            description="Test Training",
            tags=tags,
        )
        assert video_livestream.video_id == video_id
        assert not video_livestream.is_upload_completed

        assert adapter.last_request.json() == {
            "description": "Test Training",
            "files": [],
            "livestream": {"url": "https://some-url/1231232/main.m3u8"},
            "skipTranscoding": False,
            "tags": {"output_key": "main"},
        }

        add_video_part_adapter = requests_mock.post(
            f"https://fake-url/videos/{video_id}/parts",
            json=video_id,
        )
        requests_mock.head(
            "https://upload-url/random-url",
            headers={
                "Upload-Offset": "0",
                "Upload-Length": str(file_size),
                "Tus-Resumable": "1.0.0",
            },
        )
        patch_adapter = requests_mock.patch(
            "https://upload-url/random-url",
            headers={
                "upload-offset": str(file_size),
                "Upload-Length": str(file_size),
                "Tus-Resumable": "1.0.0",
            },
        )

        video = sporting_event.upload_video(
            test_mp4,
            description="Test Training",
            resume_if_exists=True,
            tags=tags,
        )

        assert add_video_part_adapter.last_request.json() == {
            "name": "test.mp4",
            "size": 991017,
        }
        assert len(patch_adapter.last_request.body) == file_size

        assert video.video_id == video_id
        assert not video.is_upload_completed
