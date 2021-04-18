"""Module for tests related to parsing."""
import pytest

from beetsplug.bandcamp._metaguru import NEW_BEETS, Metaguru, urlify

pytestmark = pytest.mark.parsing


def check(actual, expected) -> None:
    if NEW_BEETS:
        assert actual == expected
    else:
        assert vars(actual) == vars(expected)


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("2 x Vinyl LP - MTY003", 2),
        ('3 x 12" Vinyl LP - MTY003', 3),
        ("Double Vinyl LP - MTY003", 2),
        ('12" Vinyl - MTY003', 1),
        ('EP 12"Green Vinyl', 1),
        ("2LP Vinyl", 2),
    ],
)
def test_mediums_count(name, expected):
    assert Metaguru.get_vinyl_count(name) == expected


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("LI$INGLE010 - cyberflex - LEVEL X", "li-ingle010-cyberflex-level-x"),
        ("LI$INGLE007 - Re:drum - Movin'", "li-ingle007-re-drum-movin"),
        ("X23 & Høbie - Exhibit A", "x23-h-bie-exhibit-a"),
    ],
)
def test_convert_title(title, expected):
    assert urlify(title) == expected


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("released 06 November 2019", "06 November 2019"),
        ("released on Some Records", ""),
    ],
)
def test_parse_release_date(string, expected):
    assert Metaguru.parse_release_date(string) == expected


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        (
            "Title",
            {"track_alt": None, "artist": None, "title": "Title"},
        ),
        (
            "Artist - Title",
            {"track_alt": None, "artist": "Artist", "title": "Title"},
        ),
        (
            "A1. Artist - Title",
            {"track_alt": "A1", "artist": "Artist", "title": "Title"},
        ),
        (
            "A1- Artist - Title",
            {"track_alt": "A1", "artist": "Artist", "title": "Title"},
        ),
        (
            "A1.- Artist - Title",
            {"track_alt": "A1", "artist": "Artist", "title": "Title"},
        ),
        (
            "1.Artist - Title",
            {"track_alt": "1", "artist": "Artist", "title": "Title"},
        ),
        (
            "DJ BEVERLY HILL$ - Raw Steeze",
            {"track_alt": None, "artist": "DJ BEVERLY HILL$", "title": "Raw Steeze"},
        ),
        (
            "LI$INGLE010 - cyberflex - LEVEL X",
            {"track_alt": None, "artist": "cyberflex", "title": "LEVEL X"},
        ),
        (
            "Fifty-Third ft. SYH",
            {"track_alt": None, "artist": None, "title": "Fifty-Third ft. SYH"},
        ),
        (
            "I'll Become Pure N-R-G",
            {"track_alt": None, "artist": None, "title": "I'll Become Pure N-R-G"},
        ),
        (
            "&$%@#!",
            {"track_alt": None, "artist": None, "title": "&$%@#!"},
        ),
        (
            "24 Hours",
            {"track_alt": None, "artist": None, "title": "24 Hours"},
        ),
        (
            "Some tune (Someone's Remix)",
            {"track_alt": None, "artist": None, "title": "Some tune (Someone's Remix)"},
        ),
    ],
)
def test_parse_track_name(name, expected):
    assert Metaguru.parse_track_name(name) == expected


@pytest.mark.parametrize(
    ("name", "expected_digital_only", "expected_name"),
    [
        ("Artist - Track [Digital Bonus]", True, "Artist - Track"),
        ("DIGI 11. Track", True, "Track"),
        ("Digital Life", False, None),
        ("Messier 33 (Bandcamp Digital Exclusive)", True, "Messier 33"),
        ("33 (bandcamp exclusive)", True, "33"),
        ("Tune (Someone's Remix) [Digital Bonus]", True, "Tune (Someone's Remix)"),
    ],
)
def test_check_digital_only(name, expected_digital_only, expected_name):
    expected = dict(digital_only=expected_digital_only)
    if expected_name:
        expected.update(name=expected_name)
    assert Metaguru.check_digital_only(name) == expected


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Berlin, Germany", "DE"),
        ("Oslo, Norway", "NO"),
        ("London, UK", "GB"),
        ("Malmö, Sweden", "SE"),
        ("UK", "GB"),
        ("Seattle, Washington", "US"),
        ("Los Angeles, California", "US"),
        ("New York", "US"),
        ("No Ones, Land", "XW"),
        ("", "XW"),
        ("Utrecht, The Netherlands", "NL"),
        ("Russia", "RU"),
        ("Montreal, Québec", "CA"),
        ("St. Louis, Missouri", "US"),
    ],
)
def test_parse_country(name, expected):
    line = f'<span class="location secondaryText">{name}</span>'
    actual = Metaguru(line).country
    assert actual == expected


@pytest.mark.parametrize(
    ("album", "expected"),
    [
        ("Tracker-229 [PRH-002]", "PRH-002"),
        ("[PRH-002] Tracker-229", "PRH-002"),
        ("Tracker-229 PRH-002", "Tracker-229"),
        ("ISMVA003.2", "ISMVA003.2"),
        ("UTC003-CD", "UTC003"),
        ("UTC-003", "UTC-003"),
        ("EP [SINDEX008]", "SINDEX008"),
        ("2 x Vinyl LP - MTY003", "MTY003"),
        ("Kulør 001", "Kulør 001"),
        ("00M", ""),
        ("X-Coast - Dance Trax Vol.30", ""),
        ("Christmas 2020", ""),
        ("Various Artists 001", ""),
        ("C30 Cassette", ""),
        ("BC30 Hello", "BC30"),
        ("Blood 1/4", ""),
        ("Emotion 1 - Kulør 008", "Kulør 008"),
    ],
)
def test_parse_catalognum(album, expected):
    assert Metaguru.parse_catalognum(album, "") == expected


@pytest.mark.parametrize(
    ("album", "extras", "expected"),
    [
        ("Album - Various Artists", [], "Album"),
        ("Various Artists - Album", [], "Album"),
        ("Various Artists Album", [], "Various Artists Album"),
        ("Album EP", [], "Album"),
        ("[Label] Album EP", ["Label"], "Album"),
        ("Artist - Album EP", ["Artist"], "Album"),
        ("Label | Album", ["Label"], "Album"),
        (
            "Tweaker-229 - Tweaker-229 [PRH-002]",
            ["PRH-002", "Tweaker-229"],
            "Tweaker-229",
        ),
        ("Album (limited edition)", [], "Album"),
        ("Album - VARIOUS ARTISTS", [], "Album"),
        ("Drepa Mann", [], "Drepa Mann"),
        ("Some ft. Some ONE - Album", ["Some ft. Some ONE"], "Album"),
        ("Some feat. Some ONE - Album", ["Some feat. Some ONE"], "Album"),
    ],
)
def test_clean_up_album_name(album, extras, expected):
    assert Metaguru.clean_up_album_name(album, *extras) == expected


def test_parse_single_track_release(single_track_release):
    html, expected = single_track_release
    guru = Metaguru(html)

    check(guru.singleton, expected.singleton)


def test_parse_album_or_comp(multitracks):
    html, expected_release = multitracks
    guru = Metaguru(html, expected_release.media)
    include_all = False

    actual_album = guru.album(include_all)
    disctitle = actual_album.tracks[0].disctitle
    assert disctitle == expected_release.disctitle
    expected_album = expected_release.albuminfo

    assert hasattr(actual_album, "tracks")
    assert len(actual_album.tracks) == expected_release.track_count

    expected_album.tracks.sort(key=lambda t: t.index)
    actual_album.tracks.sort(key=lambda t: t.index)

    for actual_track, expected_track in zip(actual_album.tracks, expected_album.tracks):
        check(actual_track, expected_track)

    actual_album.tracks = None
    expected_album.tracks = None
    check(actual_album, expected_album)
