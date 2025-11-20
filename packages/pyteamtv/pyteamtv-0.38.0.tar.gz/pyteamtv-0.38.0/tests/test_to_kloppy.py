from datetime import timedelta
from pyteamtv.models.observation import Observation
from pyteamtv.models.observation_log import ObservationLog
from pyteamtv.models.sporting_event import SportingEvent


def test_to_kloppy(requester, requests_mock):
    """Test that to_kloppy converts observations to kloppy CodeDataset with period parsing."""
    sporting_event = SportingEvent(
        requester,
        {
            "sportingEventId": "event-1",
            "type": "match",
            "name": "Team A - Team B",
            "scheduledAt": "2025-01-01T10:00:00Z",
            "homeTeamId": "team-1",
            "awayTeamId": "team-2",
            "lineUpId": "lineup-1",
            "clocks": {},
            "outcome": {"score": {"home": 1, "away": 10}},
        },
    )

    requests_mock.get(
        "https://fake-url/sportingEvents/event-1/observations/U1",
        json=[
            {
                "observationId": "1",
                "code": "CUSTOM",
                "description": "start",
                "startTime": 100.0,
                "endTime": 101.0,
                "triggerTime": 100.0,
                "clockId": "clock-1",
                "attributes": {"code": "start", "labels": [{"text": "start"}]},
            },
            {
                "observationId": "1-duplicate",
                "code": "CUSTOM",
                "description": "start",
                "startTime": 100.0,
                "endTime": 101.0,
                "triggerTime": 100.0,
                "clockId": "clock-1",
                "attributes": {"code": "start", "labels": [{"text": "start"}]},
            },
            {
                "observationId": "2",
                "code": "CUSTOM",
                "description": "BS2 TEAM1",
                "startTime": 110.0,
                "endTime": 115.0,
                "triggerTime": 110.0,
                "clockId": "clock-1",
                "attributes": {"code": "BS2 TEAM1", "labels": [{"text": "BS2 TEAM1"}]},
            },
            {
                "observationId": "3",
                "code": "CUSTOM",
                "description": "eind",
                "startTime": 900.0,
                "endTime": 901.0,
                "triggerTime": 900.0,
                "clockId": "clock-1",
                "attributes": {"code": "eind", "labels": [{"text": "eind"}]},
            },
            {
                "observationId": "3-duplicate",
                "code": "CUSTOM",
                "description": "eind",
                "startTime": 900.0,
                "endTime": 901.0,
                "triggerTime": 900.0,
                "clockId": "clock-1",
                "attributes": {"code": "eind", "labels": [{"text": "eind"}]},
            },
            {
                "observationId": "4",
                "code": "CUSTOM",
                "description": "start",
                "startTime": 1000.0,
                "endTime": 1001.0,
                "triggerTime": 1000.0,
                "clockId": "clock-1",
                "attributes": {"code": "start", "labels": [{"text": "start"}]},
            },
            {
                "observationId": "5",
                "code": "CUSTOM",
                "description": "GOAL TEAM1",
                "startTime": 1150.0,
                "endTime": 1155.0,
                "triggerTime": 1150.0,
                "clockId": "clock-1",
                "attributes": {
                    "code": "GOAL TEAM1",
                    "labels": [{"text": "GOAL TEAM1"}],
                },
            },
            {
                "observationId": "6",
                "code": "CUSTOM",
                "description": "eind",
                "startTime": 1900.0,
                "endTime": 1901.0,
                "triggerTime": 1900.0,
                "clockId": "clock-1",
                "attributes": {"code": "eind", "labels": [{"text": "eind"}]},
            },
        ],
    )

    observation_log = ObservationLog(
        Observation,
        requester,
        "GET",
        "/sportingEvents/event-1/observations/U1",
        "clock-1",
        sporting_event,
    )

    # Call to_kloppy
    dataset = sporting_event.to_kloppy()

    # Assertions
    assert len(dataset.metadata.periods) == 2
    assert dataset.metadata.periods[0].id == 1
    assert dataset.metadata.periods[1].id == 2

    # Check that records have periods assigned and timestamps are normalized
    # We have 8 observations in the dataset
    assert len(dataset.records) == 8

    # Find the BS2 TEAM1 record (should be after the 2 start codes)
    bs2_record = [r for r in dataset.records if r.code == "BS2 TEAM1"][0]
    assert bs2_record.period.id == 1
    assert bs2_record.timestamp == timedelta(seconds=10.0)  # 110 - 100 = 10

    # Find the GOAL TEAM1 record
    goal_record = [r for r in dataset.records if r.code == "GOAL TEAM1"][0]
    assert goal_record.period.id == 2
    assert goal_record.timestamp == timedelta(seconds=150.0)  # 1150 - 1000 = 150

    assert dataset.metadata.score.home == 1
    assert dataset.metadata.score.away == 10
