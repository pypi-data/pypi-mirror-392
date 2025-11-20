import datetime
import time


def create_timestamp() -> str:
    now = datetime.datetime.utcnow()
    return datetime.datetime.isoformat(now).replace("+00:00", "Z")


class TestEventStream:
    def test_get_all_events(self, requests_mock, current_team):
        sporting_event_id = "sporting-event-id-123"
        event_stream_id = "event-stream-id-123"

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

        requests_mock.get(
            f"https://fake-url/sportingEvents/{sporting_event_id}/eventStreams",
            json=[
                {
                    "eventStreamId": event_stream_id,
                    "endpointUrls": {
                        "sse": f"https://fake-eventstream/streams/{event_stream_id}/subscribe/sse",
                        "polling": f"https://fake-eventstream/streams/{event_stream_id}/list",
                    },
                    "streamType": "all",
                }
            ],
        )

        streams = sporting_event.get_event_streams()

        requests_mock.get(
            f"https://fake-eventstream/streams/{event_stream_id}/list",
            json=[
                {
                    "event_attributes": {
                        "name": "Bla 1 - Hoi 1",
                        "awayTeam": {
                            "teamId": "d78b85ea-f0c4-11ed-a89a-254ed3a3b07d",
                            "appearance": {
                                "secondaryColor": None,
                                "primaryColor": None,
                                "logoUrl": None,
                            },
                            "name": "Bla 1",
                            "shortCode": "BLA",
                        },
                        "homeTeam": {
                            "teamId": "bd30a351-8527-4dcb-a6ff-57b92138fe03",
                            "appearance": {
                                "secondaryColor": None,
                                "primaryColor": None,
                                "logoUrl": None,
                            },
                            "name": "Hoi 1",
                            "shortCode": "HOI",
                        },
                        "scheduledAt": "2023-08-29T18:15:26.527000Z",
                    },
                    "event_name": "SportingEventCreated",
                    "event_id": "642270db37fdd48cb30572e26b2cfc50",
                    "occurred_on": create_timestamp(),
                },
            ],
        )

        time.sleep(0.001)
        with streams[0].open(seek_to_start=True) as stream:
            time.sleep(
                0.001
            )  # Make sure event timestamp below is after start of stream.open

            requests_mock.get(
                f"https://fake-eventstream/streams/{event_stream_id}/list?last-event-id=642270db37fdd48cb30572e26b2cfc50",
                json=[
                    {
                        "event_attributes": {
                            "period": "1",
                            "time": "1693333394.77399993",
                        },
                        "event_name": "StartPeriod",
                        "event_id": "ddfa76d51a72889c0d9f94f3da269199",
                        "occurred_on": create_timestamp(),
                    },
                ],
            )

            config, state, event = next(stream)
            assert event.event_type == "SportingEventCreated"
            assert not state.period_active

            config, state, event = next(stream)
            assert event.event_type == "StartPeriod"
            assert state.period_active

    def test_get_from_start(self, requests_mock, current_team):
        sporting_event_id = "sporting-event-id-123"
        event_stream_id = "event-stream-id-123"

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

        requests_mock.get(
            f"https://fake-url/sportingEvents/{sporting_event_id}/eventStreams",
            json=[
                {
                    "eventStreamId": event_stream_id,
                    "endpointUrls": {
                        "sse": f"https://fake-eventstream/streams/{event_stream_id}/subscribe/sse",
                        "polling": f"https://fake-eventstream/streams/{event_stream_id}/list",
                    },
                    "streamType": "all",
                }
            ],
        )

        streams = sporting_event.get_event_streams()

        requests_mock.get(
            f"https://fake-eventstream/streams/{event_stream_id}/list",
            json=[
                {
                    "event_attributes": {
                        "name": "Bla 1 - Hoi 1",
                        "awayTeam": {
                            "teamId": "d78b85ea-f0c4-11ed-a89a-254ed3a3b07d",
                            "appearance": {
                                "secondaryColor": None,
                                "primaryColor": None,
                                "logoUrl": None,
                            },
                            "name": "Bla 1",
                            "shortCode": "BLA",
                        },
                        "homeTeam": {
                            "teamId": "bd30a351-8527-4dcb-a6ff-57b92138fe03",
                            "appearance": {
                                "secondaryColor": None,
                                "primaryColor": None,
                                "logoUrl": None,
                            },
                            "name": "Hoi 1",
                            "shortCode": "HOI",
                        },
                        "scheduledAt": "2023-08-29T18:15:26.527000Z",
                    },
                    "event_name": "SportingEventCreated",
                    "event_id": "642270db37fdd48cb30572e26b2cfc50",
                    "occurred_on": create_timestamp(),
                },
            ],
        )

        time.sleep(0.001)

        with streams[0].open(seek_to_start=False) as stream:
            time.sleep(
                0.001
            )  # Make sure event timestamp below is after start of stream.open
            requests_mock.get(
                f"https://fake-eventstream/streams/{event_stream_id}/list?last-event-id=642270db37fdd48cb30572e26b2cfc50",
                json=[
                    {
                        "event_attributes": {
                            "period": "1",
                            "time": "1693333394.77399993",
                            "startPeriodAttributes": [],
                        },
                        "event_name": "StartPeriod",
                        "event_id": "ddfa76d51a72889c0d9f94f3da269199",
                        "occurred_on": create_timestamp(),
                    },
                    {
                        "event_attributes": {
                            "startPossessionAttributes": {"teamId": "team-id-123"}
                        },
                        "event_name": "StartPossession",
                        "event_id": "ddfa76d51a72889c0d9f94f3da269191",
                        "occurred_on": create_timestamp(),
                    },
                    {
                        "event_attributes": {
                            "startPossessionAttributes": {"teamId": "team-id-567"}
                        },
                        "event_name": "StartPossession",
                        "event_id": "ddfa76d51a72889c0d9f94f3da269191",
                        "occurred_on": create_timestamp(),
                    },
                    {
                        "event_attributes": {"periodCount": 3},
                        "event_name": "MatchConfigChanged",
                        "occurred_on": create_timestamp(),
                        "event_id": "7e59f7264fbc079fb4359a6f568f8bb7",
                    },
                ],
            )

            config, state, event = next(stream)
            assert event.event_type == "StartPeriod"
            assert state.period_active
            assert state.current_period == 1
            assert config.period_count == 2
            assert event.attributes["startPeriodAttributes"] == {}

            config, state, event = next(stream)
            assert state.current_possession_team_id == "team-id-123"

            config, state, event = next(stream)
            assert state.current_possession_team_id == "team-id-567"
            assert config.period_count == 2

            config, state, event = next(stream)
            assert event.event_type == "MatchConfigChanged"
            assert state.current_possession_team_id == "team-id-567"
            assert config.period_count == 3

    def test_get_last_event(self, requests_mock, current_team):
        sporting_event_id = "sporting-event-id-123"
        event_stream_id = "event-stream-id-123"

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

        requests_mock.get(
            f"https://fake-url/sportingEvents/{sporting_event_id}/eventStreams",
            json=[
                {
                    "eventStreamId": event_stream_id,
                    "endpointUrls": {
                        "sse": f"https://fake-eventstream/streams/{event_stream_id}/subscribe/sse",
                        "polling": f"https://fake-eventstream/streams/{event_stream_id}/list",
                    },
                    "streamType": "all",
                }
            ],
        )

        streams = sporting_event.get_event_streams()

        requests_mock.get(
            f"https://fake-eventstream/streams/{event_stream_id}/list",
            json=[
                {
                    "event_attributes": {
                        "name": "Bla 1 - Hoi 1",
                        "awayTeam": {
                            "teamId": "d78b85ea-f0c4-11ed-a89a-254ed3a3b07d",
                            "appearance": {
                                "secondaryColor": None,
                                "primaryColor": None,
                                "logoUrl": None,
                            },
                            "name": "Bla 1",
                            "shortCode": "BLA",
                        },
                        "homeTeam": {
                            "teamId": "bd30a351-8527-4dcb-a6ff-57b92138fe03",
                            "appearance": {
                                "secondaryColor": None,
                                "primaryColor": None,
                                "logoUrl": None,
                            },
                            "name": "Hoi 1",
                            "shortCode": "HOI",
                        },
                        "scheduledAt": "2023-08-29T18:15:26.527000Z",
                    },
                    "event_name": "SportingEventCreated",
                    "event_id": "642270db37fdd48cb30572e26b2cfc50",
                    "occurred_on": create_timestamp(),
                },
            ],
        )

        time.sleep(0.001)

        with streams[0].open(seek_to_start=False) as stream:
            time.sleep(
                0.001
            )  # Make sure event timestamp below is after start of stream.open
            requests_mock.get(
                f"https://fake-eventstream/streams/{event_stream_id}/list?last-event-id=642270db37fdd48cb30572e26b2cfc50",
                json=[
                    {
                        "event_attributes": {
                            "period": "1",
                            "time": "1693333394.77399993",
                            "startPeriodAttributes": [],
                        },
                        "event_name": "StartPeriod",
                        "event_id": "ddfa76d51a72889c0d9f94f3da269199",
                        "occurred_on": create_timestamp(),
                    },
                    {
                        "event_attributes": {
                            "startPossessionAttributes": {"teamId": "team-id-123"}
                        },
                        "event_name": "StartPossession",
                        "event_id": "ddfa76d51a72889c0d9f94f3da269191",
                        "occurred_on": create_timestamp(),
                    },
                    {
                        "event_attributes": {
                            "startPossessionAttributes": {"teamId": "team-id-567"}
                        },
                        "event_name": "StartPossession",
                        "event_id": "ddfa76d51a72889c0d9f94f3da269191",
                        "occurred_on": create_timestamp(),
                    },
                    {
                        "event_attributes": {"periodCount": 3},
                        "event_name": "MatchConfigChanged",
                        "occurred_on": create_timestamp(),
                        "event_id": "7e59f7264fbc079fb4359a6f568f8bb7",
                    },
                ],
            )

            # Make sure data is fetched
            time.sleep(1.5)

            config, state, event = stream.get_last_event()
            assert event.event_type == "StartPeriod"
            assert state.period_active
            assert state.current_period == 1
            assert config.period_count == 2

            config, state, event = stream.get_last_event()
            assert state.current_possession_team_id == "team-id-123"

            config, state, event = stream.get_last_event()
            assert state.current_possession_team_id == "team-id-567"
            assert config.period_count == 2

            config, state, event = stream.get_last_event()
            assert event.event_type == "MatchConfigChanged"
            assert state.current_possession_team_id == "team-id-567"
            assert config.period_count == 3

            assert stream.get_last_event() is None
