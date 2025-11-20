from pyteamtv.dataframe_builder import DataframeBuilder
from pyteamtv.models.observation import Observation
from pyteamtv.models.observation_log import ObservationLog
from pyteamtv.models.sporting_event import SportingEvent


def test_build_records_with_dynamic_person_ids(requester, current_team, requests_mock):
    """Test that DataframeBuilder expands all *PersonId fields dynamically"""
    requests_mock.get("https://fake-url/teams", json=[])
    requests_mock.get(
        "https://fake-url/persons",
        json=[
            {
                "personId": "person-1",
                "firstName": "John",
                "lastName": "Doe",
                "number": 10,
                "gender": "male",
            },
            {
                "personId": "person-2",
                "firstName": "Jane",
                "lastName": "Smith",
                "number": 7,
                "gender": "female",
            },
            {
                "personId": "person-3",
                "firstName": "Bob",
                "lastName": "Keeper",
                "number": 1,
                "gender": "male",
            },
        ],
    )

    builder = DataframeBuilder(current_team)

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
        },
    )

    requests_mock.get(
        "https://fake-url/observations",
        json=[
            {
                "observationId": "obs-1",
                "code": "START-POSSESSION",
                "startTime": 0.0,
                "triggerTime": 0.0,
                "endTime": 1.0,
                "clockId": "clock-1",
                "description": "Start",
                "attributes": {"teamId": "team-1"},
            },
            {
                "observationId": "obs-2",
                "code": "SHOT",
                "startTime": 1.0,
                "triggerTime": 1.5,
                "endTime": 2.0,
                "clockId": "clock-1",
                "description": "Shot",
                "attributes": {
                    "personId": "person-1",
                    "assistPersonId": "person-2",
                    "keeperPersonId": "person-3",
                    "position": None,
                },
            },
        ],
    )

    observation_log = ObservationLog(
        Observation, requester, "GET", "/observations", "clock-1", sporting_event
    )

    records = builder.build_records([observation_log])

    assert len(records) == 2
    shot_record = records[1]

    # Check that all person fields are expanded correctly
    assert shot_record["code"] == "SHOT"
    assert shot_record["person_id"] == "person-1"
    assert shot_record["first_name"] == "John"
    assert shot_record["last_name"] == "Doe"
    assert shot_record["full_name"] == "John Doe"

    # Check assist person fields
    assert shot_record["assist_person_id"] == "person-2"
    assert shot_record["assist_first_name"] == "Jane"
    assert shot_record["assist_last_name"] == "Smith"
    assert shot_record["assist_full_name"] == "Jane Smith"

    # Check keeper person fields (dynamically detected)
    assert shot_record["keeper_person_id"] == "person-3"
    assert shot_record["keeper_first_name"] == "Bob"
    assert shot_record["keeper_last_name"] == "Keeper"
    assert shot_record["keeper_full_name"] == "Bob Keeper"

    # Check that position=None doesn't break
    assert shot_record.get("position") is None

    # The raw personId fields should NOT be in the record
    assert "personId" not in shot_record
    assert "assistPersonId" not in shot_record
    assert "keeperPersonId" not in shot_record
