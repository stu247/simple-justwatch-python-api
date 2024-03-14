from pytest import mark, raises

from simplejustwatchapi.query import prepare_search_request, prepare_details_request

GRAPHQL_DETAILS_QUERY = """
query GetTitleNode(
  $nodeId: ID!,
  $language: Language!,
  $country: Country!,
  $formatPoster: ImageFormat,
  $formatOfferIcon: ImageFormat,
  $profile: PosterProfile,
  $backdropProfile: BackdropProfile,
  $filter: OfferFilter!,
) {
  node(id: $nodeId) {
    ...TitleDetails
    __typename
  }
  __typename
}
"""


GRAPHQL_SEARCH_QUERY = """
query GetSearchTitles(
  $searchTitlesFilter: TitleFilter!,
  $country: Country!,
  $language: Language!,
  $first: Int!,
  $formatPoster: ImageFormat,
  $formatOfferIcon: ImageFormat,
  $profile: PosterProfile,
  $backdropProfile: BackdropProfile,
  $filter: OfferFilter!,
) {
  popularTitles(
    country: $country
    filter: $searchTitlesFilter
    first: $first
    sortBy: POPULAR
    sortRandomSeed: 0
  ) {
    edges {
      node {
        ...TitleDetails
        __typename
      }
      __typename
    }
    __typename
  }
}
"""

GRAPHQL_DETAILS_FRAGMENT = """
fragment TitleDetails on MovieOrShow {
  id
  objectId
  objectType
  content(country: $country, language: $language) {
    title
    fullPath
    originalReleaseYear
    originalReleaseDate
    runtime
    shortDescription
    genres {
      shortName
      __typename
    }
    externalIds {
      imdbId
      __typename
    }
    posterUrl(profile: $profile, format: $formatPoster)
    backdrops(profile: $backdropProfile, format: $formatPoster) {
      backdropUrl
      __typename
    }
    __typename
  }
  offers(country: $country, platform: WEB, filter: $filter) {
    ...TitleOffer
  }
  __typename
}
"""


GRAPHQL_OFFER_FRAGMENT = """
fragment TitleOffer on Offer {
  id
  monetizationType
  presentationType
  retailPrice(language: $language)
  retailPriceValue
  currency
  lastChangeRetailPriceValue
  type
  package {
    id
    packageId
    clearName
    technicalName
    icon(profile: S100, format: $formatOfferIcon)
    __typename
  }
  standardWebURL
  elementCount
  availableTo
  deeplinkRoku: deeplinkURL(platform: ROKU_OS)
  subtitleLanguages
  videoTechnology
  audioTechnology
  audioLanguages
  __typename
}
"""


@mark.parametrize(
    argnames=["title", "country", "language", "count", "best_only"],
    argvalues=[
        ("TITLE 1", "US", "language 1", 5, True),
        ("TITLE 2", "gb", "language 2", 10, False),
    ],
)
def test_prepare_search_request(
    title: str, country: str, language: str, count: int, best_only: bool
) -> None:
    expected_request = {
        "operationName": "GetSearchTitles",
        "variables": {
            "first": count,
            "searchTitlesFilter": {"searchQuery": title},
            "language": language,
            "country": country.upper(),
            "formatPoster": "JPG",
            "formatOfferIcon": "PNG",
            "profile": "S718",
            "backdropProfile": "S1920",
            "filter": {"bestOnly": best_only},
        },
        "query": GRAPHQL_SEARCH_QUERY + GRAPHQL_DETAILS_FRAGMENT + GRAPHQL_OFFER_FRAGMENT,
    }
    request = prepare_search_request(title, country, language, count, best_only)
    assert expected_request == request


@mark.parametrize(
    argnames=["invalid_code"],
    argvalues=[
        ("United Stated of America",),  # too long
        ("usa",),  # too long
        ("u",),  # too short
    ],
)
def test_prepare_search_request_asserts_on_invalid_country_code(invalid_code: str) -> None:
    expected_error_message = f"Invalid country code: {invalid_code}, code must be 2 characters long"
    with raises(AssertionError) as error:
        prepare_search_request("", invalid_code, "", 1, True)
        assert str(error.value) == expected_error_message


@mark.parametrize(
    argnames=["node_id", "country", "language", "best_only"],
    argvalues=[
        ("NODE ID 1", "US", "language 1", True),
        ("NODE ID 1", "gb", "language 2", False),
    ],
)
def test_prepare_details_request(
    node_id: str, country: str, language: str, best_only: bool
) -> None:
    expected_request = {
        "operationName": "GetTitleNode",
        "variables": {
            "nodeId": node_id,
            "language": language,
            "country": country.upper(),
            "formatPoster": "JPG",
            "formatOfferIcon": "PNG",
            "profile": "S718",
            "backdropProfile": "S1920",
            "filter": {"bestOnly": best_only},
        },
        "query": GRAPHQL_DETAILS_QUERY + GRAPHQL_DETAILS_FRAGMENT + GRAPHQL_OFFER_FRAGMENT,
    }
    request = prepare_details_request(node_id, country, language, best_only)
    assert expected_request == request


@mark.parametrize(
    argnames=["invalid_code"],
    argvalues=[
        ("United Stated of America",),  # too long
        ("usa",),  # too long
        ("u",),  # too short
    ],
)
def test_prepare_details_request_asserts_on_invalid_country_code(invalid_code: str) -> None:
    expected_error_message = f"Invalid country code: {invalid_code}, code must be 2 characters long"
    with raises(AssertionError) as error:
        prepare_details_request("", invalid_code, "", True)
        assert str(error.value) == expected_error_message
