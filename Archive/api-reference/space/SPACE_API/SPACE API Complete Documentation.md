# SPACE API Complete Documentation

## Overview

The SPACE project provides access to a RESTful API. This will allow partners to integrate their systems with SPACE and allow them to create, update and delete frames. The API will return all output in JSON format and where input is required the HTTP request body should contain JSON.

[Download the Quick Start Guide](https://oohspace.co.uk/content/api_quickstart.pdf)

### Definitions, Acronyms and Abbreviations

| Term | Description |
| --- | --- |
| SPACE | The outdoor industry code allocation system |
| OISC | Outdoor Industry Standards Committee |
| IMS | Inventory Mapping System |
| REST | Representational State Transfer |
| API | Application Programming Interface |
| JSON | JavaScript Object Notation |
| XML | Extensible Markup Language |
| UI | User Interface |

### Security

Access to the production API must be done via HTTPS and you will be required to supply a username (company_id) and password via HTTP Basic Authentication.

Please note that IP restriction is in place for all methods and requests not coming from an authorised IP address for the company will be rejected.

[Click here](https://oohspace.co.uk/content/api-security-requirements.pdf) to see the security protocols and ciphers that SPACE supports.

### Headers

The API honours the Accept header returning data in the requested format. At the moment only JSON is supported so ensure that all requests have a Accept header set to application/json.

The Content-Type header is required for POST/PUT requests and, when sending a JSON body, must be set to application/json for all requests.

### Errors

Should the system detect a problem with your API request, such as invalid or missing data, the response code will be set to HTTP 400 and JSON returned explaining the errors. Within the errors object you'll find a message providing a general summary of issues. A list of all issues will be returned as well.

```json
{
    "errors": [
        "Sales code must be a three-digit alphanumeric code",
        "The surface area doesn't seem to be equal to the width x height"
    ]
}
```

All returned elements are strings.

### Rate Limiting

Rate limits will be applied per company on GET /frame calls.

After the first request, every other request will be refused until the end of the last request or 1 minute (whichever is shortest). This will result in a 429 HTTP error status code. Any other call types will be allowed in the meantime.

---

## API Endpoints

### GET /agency

A lookup call to retrieve all approved agencies; use https://oohspace.co.uk/api/agency.

There is no INPUT for this method.

**Response:**
```json
{
    "data": {
        "datetime_last_update": "2021-12-01 16:16:15",
        "approved": [
            {
                "agency_id": 15320,
                "agency_name": "Carat",
                "organisation_id": 4,
                "organisation_name": "Media Agency"
            },
            {
                "agency_id": 15321,
                "agency_name": "Goodstuff",
                "organisation_id": 4,
                "organisation_name": "Media Agency"
            },
            {
                "agency_id": 15322,
                "agency_name": "Astus",
                "organisation_id": 2,
                "organisation_name": "Barter Agency"
            }
        ],
        "approval_intervention_history": [
            {
                "agency_id": 15365,
                "agency_name": "Agency Name YX",
                "organisation_id": 3,
                "organisation_name": "DSP",
                "date": "2021-11-10 10:00:09",
                "status": "approved"
            },
            {
                "agency_id": 15360,
                "agency_name": "Agency Name YY",
                "organisation_id": 3,
                "organisation_name": "DSP",
                "date": "2021-11-10 09:59:52",
                "status": "approved"
            },
            {
                "agency_id": 15352,
                "agency_name": "Agency Name YZ",
                "organisation_id": 2,
                "organisation_name": "Barter Agency",
                "date": "2021-11-09 23:57:57",
                "status": "approved"
            }
        ]
    }
}
```

**Organisation types:**

| Organisation ID | Organisation Name |
| --- | --- |
| 2 | Barter Agency |
| 3 | DSP |
| 4 | Media Agency |
| 5 | Specialist Agency |

---

### GET /agency/bcr-validation

A lookup call to retrieve all Buyer Campaign Reference formats; use https://oohspace.co.uk/api/agency/bcr-validation.

**Parameters:**

| parameter | type | description |
| --- | --- | --- |
| changed_since | string | A datetime string to filter Buyer Campaign Reference formats changed after this date. e.g. 2024-11-05 14:16:39 |

**Response:**
```json
{
    "data": [
        {
            "space_buyer_id": 15887,
            "agency_name": "BambOOH Ltd",
            "valid_formats": [
                "[0-9]{5}"
            ],
            "last_updated": "2024-11-05 14:07:06"
        },
        {
            "space_buyer_id": 15890,
            "agency_name": "Billups Worldwide Inc",
            "valid_formats": [
                "BU[0-9]{6}"
            ],
            "last_updated": "2024-11-05 14:15:41"
        },
        {
            "space_buyer_id": 17040,
            "agency_name": "BITPOSTER LTD T/A MEDIABRIDGE",
            "valid_formats": [
                "[A-Z]{3}-[0-9]{4}"
            ],
            "last_updated": "2024-11-05 14:15:41"
        },
        {
            "space_buyer_id": 17035,
            "agency_name": "KINETIC INTERNATIONAL UK LTD",
            "valid_formats": [
                "AVUK[0-9]{4}"
            ],
            "last_updated": "2024-11-05 14:15:41"
        },
        {
            "space_buyer_id": 15776,
            "agency_name": "Kinetic Worldwide Limited",
            "valid_formats": [
                "(K|k)[0-9]{5}",
                "AVUK[0-9]{4}"
            ],
            "last_updated": "2024-11-05 14:16:39"
        }
    ],
    "last_updated": "2024-11-05 14:16:39"
}
```

---

### GET /client-brand

A lookup call to retrieve all approved advertiser/brand pairs; use https://oohspace.co.uk/api/client-brand.

**Parameters:**

| parameter | type | description |
| --- | --- | --- |
| changed_date | string (optional) | restricts results to only client-brands that have been changed since this date, date must be formatted as 2015-04-01T08:00:00 |

**Response:**
```json
{
    "data": {
        "datetime_last_update": "2020-12-01 16:16:15",
        "approved": [
            {
                "client_id": 4997,
                "client_name": "El Al Israel Airlines Ltd",
                "brand_id": 14215,
                "brand_name": "El Al Israel Airlines",
                "brand_date_added": "2021-02-18 17:25:12",
                "categories": [
                    {
                        "category_id": 30666,
                        "category_name": "Airlines"
                    }
                ]
            },
            {
                "client_id": 4998,
                "client_name": "Hashtag Merky Records Limited",
                "brand_id": 2737,
                "brand_name": "Stormzy",
                "brand_date_added": "2021-02-18 17:25:12",
                "categories": [
                    {
                        "category_id": 20027,
                        "category_name": "Entertainment"
                    }
                ]
            },
            {
                "client_id": 4999,
                "client_name": "[PIAS] UK Ltd",
                "brand_id": 16927,
                "brand_name": "[PIAS]",
                "brand_date_added": "2019-04-11 17:25:54",
                "categories": []
            }
        ],
        "approval_intervention_history": [
            {
                "client_id": 5446,
                "client_name": "Art 15",
                "brand_id": null,
                "brand_name": null,
                "status": "removed",
                "date": "2018-08-16 10:05:18"
            },
            {
                "client_id": 6824,
                "client_name": "Converse",
                "brand_id": 4091,
                "brand_name": "One Star",
                "status": "removed",
                "date": "2018-08-22 14:47:04"
            },
            {
                "client_id": 13856,
                "client_name": "Refresco Drinks UK Limited",
                "brand_id": 4485,
                "brand_name": "Emerge",
                "matched_client_id": 10311,
                "matched_brand_id": 4485,
                "status": "matched",
                "date": "2018-10-23 17:13:44"
            }
        ]
    }
}
```

If an advertiser doesn't have any associated brands/categories then the brand/category fields will be returned as NULL.

---

### GET /conurbation

A lookup call to get all available conurbations, including their ID and description. The call will allow a single ID to be given in order to limit results to the specific conurbation.

**Parameters:**

| parameter | type | description |
| --- | --- | --- |
| id | int (optional) | a conurbation id to restrict results to |

**Response example** (GET /api/conurbation?id=1):
```json
{
    "data": [
        {
            "conurbation_id": "1",
            "conurbation_name": "Birkenhead"
        }
    ]
}
```

---

### GET /dimension

A lookup call to get all available dimensions, including their code, description, width, height and surface area. The call will allow a single code to be supplied in order to return the dimension. If no code is supplied, all dimensions are returned.

The Dimension is a Route standard, these map generally in a one to many relationship to the new SPACE standard formats. The mapping can be shown [here](https://oohspace.co.uk/format_mapping.pdf). There are more SPACE formats than there are Route dimensions.

**Parameters:**

| parameter | type | description |
| --- | --- | --- |
| id | int (optional) | a dimension code to restrict results to |

**Response example** (GET /api/dimension?id=12):
```json
{
    "data": [
        {
            "code": "12",
            "description": "12 sheet size",
            "width": 3.05,
            "height": 1.52,
            "surface_area": 4.64
        }
    ]
}
```

**Response fields:**
- **code** - string - the unique identifier used within SPACE to reference the dimension
- **description** - string - a description of the dimension suitable for display to a user
- **width** - float - the width in meters
- **height** - float - the height in meters
- **surface_area** - float - the surface area in square meters

---

### GET /environment-group

A lookup call to get all available environment groups, including their ID and description. The call will allow a single ID to be given in order to limit results to the specific environment group.

**Parameters:**

| parameter | type | description |
| --- | --- | --- |
| id | int (optional) | a environment id to restrict results to |

**Response example** (GET /api/environment-group?id=1):
```json
{
    "data": [
        {
            "id": 1,
            "description": "Airport"
        }
    ]
}
```

---

### GET /environment

A lookup call to get all available environments, including their ID and description. The call will allow a single ID to be given in order to return the description. If no ID is supplied, all environments are returned.

Included in the response will be a list of required and optional attributes for the environment. This data can be used as the basis for generating the attribute listing when creating or updating frames.

**Parameters:**

| parameter | type | description |
| --- | --- | --- |
| id | string (optional) | a environment code to restrict results to |

**Response example** (GET /api/environment?id=AirportEnclosed):
```json
{
    "data": [
        {
            "environment_code": "AirportEnclosed",
            "route_environment_description": "Airport enclosed - 15",
            "on_route": 1,
            "space_environment_description": "Airport Enclosed",
            "attributes": {
                "required": [
                    "Address",
                    "FramePositionID",
                    "MapID",
                    "PostCode",
                    "WorldGeodeticCoordinate"
                ],
                "optional": [
                    "BreakLength",
                    "MGEIndoorCoordinate",
                    "ShareOfTime",
                    "SpotLength"
                ]
            }
        }
    ]
}
```

**Response fields:**
- **environment_code** - string - the unique identifier used within SPACE to reference the environment
- **route_environment_description** - string - a description of the environment suitable for display to a user
- **on_route** - int - whether the frame is to be submitted to Route or not, by 1 or 0 respectively
- **space_environment_description** - string - SPACE description of the environment suitable for display to a user
- **attributes** - array - an array containing required and optional keys
  - **required** - array - an array of strings listing required attributes for this environment
  - **optional** - array - an array of strings listing optional attributes for this environment

---

### GET /format-group

A lookup call to get all available format groups, including their ID and description. The call will allow a single ID to be given in order to limit results to the specific format group.

**Parameters:**

| parameter | type | description |
| --- | --- | --- |
| id | int (optional) | a format group id to restrict results to |

**Response example** (GET /api/format-group?id=1):
```json
{
    "data": [
        {
            "id": 1,
            "description": "6 Sheets"
        }
    ]
}
```

---

### GET /format

A lookup call to get all available formats, including their ID and description. The call will allow a single ID to be given in order to limit results to the specific format.

The format is a SPACE standard.

**Parameters:**

| parameter | type | description |
| --- | --- | --- |
| id | int (optional) | a format id to restrict results to |

**Response example** (GET /api/format?id=1):
```json
{
    "data": [
        {
            "id": 1,
            "description": "12 Sheets",
            "width": 3.05,
            "height": 1.52,
            "surface_area": 4.64,
            "on_route": true
        }
    ]
}
```

---

### GET /frame-type

A lookup call to get all available frame types, including their ID and description. The call will allow a single ID to be given in order to return the description.

**Parameters:**

| parameter | type | description |
| --- | --- | --- |
| id | string (optional) | a frame type code to restrict results to |

**Response example** (GET /api/frame-type?id=4):
```json
{
    "data": [
        {
            "id": 4,
            "description": "Digital (moving image)",
            "on_route": true
        }
    ]
}
```

**Response fields:**
- **id** - string - the unique identifier used within SPACE to reference the frame type
- **description** - string - a description of the frame type suitable for display to a user
- **on_route** - boolean - true if the frame type is on route or false if not

---

### GET /frame

Used to retrieve/view a frame.

When accessed via a GET request this API method will return a list of all frames. By specifying an id parameter you can retrieve details about a specific frame. The result will contain a paging object with details on the total pages and records within the resultset. You'll need to move through the pages via the page parameter in the URL.

Some parameters accept more than one value, these currently include: space_format_id, frame_type, environment_type, and conurbation_id. These values should be presented as a comma separated list (i.e. /api/frame?frame_type=1,2,3).

**Parameters:**

| parameter | type | description |
| --- | --- | --- |
| id | int64 (optional) | a frame identifier to restrict results to |
| previous_frame_id | int64 (optional) | a previous frame identifier to restrict results to |
| media_owner | int (optional) | restrict results to frames from this media owner |
| sales_code | string (optional) | restrict results to frames with this sales code |
| space_format_id | int (optional) | restrict results to frames with this SPACE format identifier |
| frame_type | int (optional) | restrict results to frames with this frame type |
| faces | int (optional) | restrict results to frames with this number of faces |
| illumination | int (optional) | restrict results to frames with this illumination type |
| environment_type | string (optional) | restrict results to frames with this environment type |
| spot_length | int (optional) | restrict results to frames with a spot length value greater than or equal to the parameter value |
| break_length | int (optional) | restrict results to frames with a break length value greater than or equal to the parameter value |
| share_time | int (optional) | restrict results to frames with a share of time value greater than or equal to the parameter value |
| closed | int (optional) | restrict results to open, closed or open & closed frames by setting the value to 0, 1 or 2 respectively |
| on_route | int (optional) | restrict results to frames not to be submitted to Route, to be submitted to Route, or both by setting the value to 0, 1 or 2 respectively |
| address | string (optional) | complete address to search on, partial matches are not supported |
| location | string (optional) | complete location to search on, partial matches are not supported |
| changed_date | string (optional) | restricts results to only frames that have been changed since this date, registered changes do not include changes to IMSWorldGeodeticCoordinates or IMSMapID, the date of any changes to these fields are recorded separately, date must be formatted as 2015-04-01T08:00:00 |
| ims_changed_date | string (optional) | restricts results to only frames that have had the IMSWorldGeodeticCoordinates or IMSMapID data changed since this date, date must be formatted as 2015-04-01T08:00:00 |
| town_id | int (optional) | restricts results to only frames that are within a specific town, see GET town for available options |
| tv_region_id | int (optional) | restricts results to only frames that are within a TV region, see GET tv-region for available options |
| conurbation_id | int (optional) | restricts results to only frames that are within a specific conurbation, see GET conurbation for available options |
| locality_id | int (optional) | restricts results to only frames that are associated with a specific locality, see GET locality for available options |
| environment_group_id | int (optional) | restricts results to only frames with this environment group, see GET environment-group for available options |
| format_group_id | int (optional) | restricts results to only frames with this format group, see GET format-group for available options |
| future_start_date | int (optional) | restrict results to exclude future frames or only include future frames by setting the value to 0 or 1 respectively |
| (*) proximity_distance | int (optional) | restricts results to only frames that are greater than or equal to this distance (in metres) from any proximity_location, if proximity_distance is specified without an accompanying proximity_location then this distance will apply to all sensitive locations |
| (*) proximity_location | string (optional) | goes hand in hand with proximity_distance to restrict the proximity_distance to the supplied sensitive locations, this is a comma separated list which can include values of school, playground and place_of_worship, if an empty string is submitted for this value then it'll be assumed that it applies to all sensitive locations (i.e same as setting to school,playground,place_of_worship) |
| page | int (optional) | move through a resultset to the requested page |
| page_size | int (optional) | the maximum number of frame records per page |

(*) Available for Proximity data subscribers. For further information contact space@uk.adwanted.com.

**Response example** (GET /api/frame?space_format_id=1):
```json
{
    "data": [{
        "FrameID": 2000000051,
        "LocationDescription": "Some place2",
        "SalesCode": "19C",
        "Format": {
            "Code": "12",
            "SpaceFormatID": 1,
            "Width": 3.05,
            "Height": 1.52,
            "SurfaceArea": 4.64
        },
        "FrameType": 3,
        "Faces": 2,
        "Illumination": 1,
        "Environment": {
            "Type": "Roadside",
            "Description": "Roadside",
            "Attributes": [
                 {
                     "Type": "IMSWorldGeodeticCoordinate",
                     "Value": "51.37705546,-0.27882552"
                },
                {
                    "Type": "Address",
                    "Value": "address value"
                },
                {
                    "Type": "PostCode",
                    "Value": "SM12EA"
                },
                {
                    "Type": "WorldGeodeticCoordinate",
                    "Value": "51.37705546,-0.27882552"
                },
                {
                    "Type": "SpotLength",
                    "Value": "10"
                },
                {
                    "Type": "BreakLength",
                    "Value": "6"
                },
                {
                    "Type": "ShareOfTime",
                    "Value": "62.5"
                }
            ]
        },
        "Distance": {
            "PrimarySchool": 404,
            "PrimarySchoolName": "Hallfield Primary School",
            "SecondarySchool": 848,
            "SecondarySchoolName": "Ashbourne Independent Sixth Form College",
            "SpecialNeedsSchool": 559,
            "SpecialNeedsSchoolName": "College Park School",
            "FurtherSchool": 6238,
            "FurtherSchoolName": "Putney High School",
            "UpdateDateTime": "2016-02-29 23:41:46"
        },
        "UpdateDateTime": "2015-02-25 14:00:34",
        "IMSUpdatedDateTime": "2017-05-10 09:05:34",
        "ClosedDate": null,
        "PreviousMediaOwner": null,
        "PreviousMediaOwnerID": null,
        "MediaOwner": "Mediatel",
        "MediaOwnerID": 1,
        "MediaOwnerStartDate": "2018-01-11",
        "MediaOwnerEndDate": null,
        "NewMediaOwner": null,
        "NewMediaOwnerID": null,
        "TransferDate": null,
        "LegacySiteNumber": "SITE123456",
        "OnRoute": 1,
        "Tags": [1,8],
        "Localities": [1],
        "ComparableLocalities": [2],
        "Prohibitions": {
            "MediaOwnerCategories": [1, 2, 3]
         },
        "TownName": "Sutton",
        "TvRegionName": "London",
        "ConurbationName": "Greater London",
        "EnvironmentGroup": "Roadside",
        "EnvironmentGroupID": 4,
        "FormatGroup": "12 Sheets",
        "FormatGroupID": 3,
        "LinkedAssetID": 3000000004,
        "LinkedAssetReference": "Reference text",
        "LinkedAssetDescription": "Description of Linked Asset ID 3000000004",
        "RestrictedAssets": [],
        "MediaOwnerAttributes": null,
        "MediaOwnerFrameReference": "BSY03B",
        "CurrentStatus": 33,
        "NumberOfClassificationPhotos": 5,
        "GreenStarExported": 55,
        "MinRouteRelease": "R49",
        "MaxRouteRelease": "R50",
        "CurrentStatusDate": "2023-11-27 00:00:00",
        "LastStatusOneDate": "2023-11-23 00:00:00",
        "AngleToMapNorth": 66,
        "VisibilitySectorRadius": 45.11,
        "StatusEditor": "14",
        "PolygonBoundaryAreacode": "abc",
        "ProductionSpecificationID": 11,
        "ProductionSpecification": "Production/Creative specification name",
        "PreviousFrameID": "2004605892"
    }],
    "paging": {
        "page": 723,
        "page_size": 100,
        "total_pages": 723,
        "total_records": 72204
    }
}
```

**Response fields:**

- **FrameID** - int64 - the unique identifier used within SPACE to reference the frame
- **LocationDescription** - string - a description of the location of the frame
- **SalesCode** - string - the sales code as set for the frame
- **Format** - array - an array of format data defined as follows:
  - **Code** - string - the unique dimension identifier
  - **SpaceFormatID** - int - the unique identifier for this format
  - **Width** - float - width in meters
  - **Height** - float - height in meters
  - **SurfaceArea** - float - surface area in square meters
- **FrameType** - int - the type of frame (see relevant GET API method)
- **Faces** - int - the number of faces for the frame
- **Illumination** - int - the type of illumination (see relevant GET API method)
- **Environment** - array - an array of environment data
  - **Type** - string - the environment type
  - **Description** - string - the environment description
  - **Attributes** - array - an array of attributes specifically for this environment
    - **Type** - string - attribute type
    - **Value** - string- attribute value
- **MediaOwnerAttributes** - object - media owner attribute data
  - **AttributeName:AttributeValue** - key:value - paired media owner attributes and their associated values
- **(*) Distance** - array - an array of distance data calculated as the crow flies
  - **PrimarySchool** - int - distance in metres to the nearest primary school
  - **PrimarySchoolName** - string - name of the nearest primary school
  - **SecondarySchool** - int - distance in metres to the nearest secondary school
  - **SecondarySchoolName** - string - name of the nearest secondary school
  - **SpecialNeedsSchool** - int - distance in metres to the nearest special needs school
  - **SpecialNeedsSchoolName** - string - name of the nearest special needs school
  - **FurtherSchool** - int - distance in metres to the nearest further education school
  - **FurtherSchoolName** - string - name of the nearest further education school
  - **UpdateDateTime** - float - date/time that distances were last updated (YYYY-MM-DD HH:ii:ss)
- **UpdateDateTime** - string - date/time that the frame was last updated (YYYY-MM-DD HH:ii:ss)
- **IMSUpdatedDateTime** - string - date/time that the IMS fields were last updated (YYYY-MM-DD HH:ii:ss)
- **ClosedDate** - string - date that the frame was closed, can be null
- **PreviousMediaOwner** - string - previous media owner company name
- **PreviousMediaOwnerID** - int - previous media owner company identifier
- **MediaOwner** - string - media owner company name
- **MediaOwnerID** - int - media owner company identifier
- **MediaOwnerStartDate** - string - date from which the media owner owned the frame
- **MediaOwnerEndDate** - string - date from which the media owner no longer owned the frame
- **NewMediaOwner** - string - media owner company name that frame is transferring to
- **NewMediaOwnerID** - int - media owner company identifier that frame is transferring to
- **TransferDate** - string - date from which new media owner will own frame
- **LegacySiteNumber** - string - legacy site number
- **OnRoute** - int - whether the frame is to be submitted to Route or not, specified by 1 or 0 respectively
- **PreviousFrameID** - int - previous frame identifier that was associated with this frame
- **Tags** - array - an array of tags associated with the frame
- **Localities** - array - an array of localities associated with the frame
- **ComparableLocalities** - array - an array of comparable localities associated with the attached locality
- **Prohibitions** - object - a collection of arrays representing different types of prohibitions associated with this frame, including MediaOwnerCategories
- **TownName** - string - town
- **TvRegionName** - string - TV region name
- **ConurbationName** - string - Conurbation name
- **EnvironmentGroup** - string - Environment group
- **EnvironmentGroupID** - int - Environment group identifier
- **FormatGroup** - string - Format group
- **FormatGroupID** - int - Format group identifier
- **LinkedAssetID** - int - Linked Asset identifier
- **LinkedAssetDescription** - string - Linked Asset description
- **MediaOwnerFrameReference** - string - media owner frame reference
- **CurrentStatus** – int – Last status (MID) in IMS
- **NumberOfClassificationPhotos** – int - Classification photos define max. visibility of a frame from a particular link ID (traffic flow). This is their number per frame.
- **GreenStarExported** - int - The green star is assigned to a specific frame status (MID) that is in the current Release.
- **MinRouteRelease** – int - Earliest Route release a frame has appeared in.
- **MaxRouteRelease** – int - Latest Route release a frame has appeared in.
- **CurrentStatusDate** - string - Date of last status (MID) in IMS
- **LastStatusOneDate** - string -Date of last status 1 (MID) in IMS
- **AngleToMapNorth** - int - Angle to map North
- **VisibilitySectorRadius** - double – Visibility sector radius
- **StatusEditor** - string - IMS user who saved a particular status (MID)
- **PolygonBoundaryAreacode** - string – Polygon boundary area code
- **ProductionSpecificationID** - int - the unique identifier ot the frame's linked Production/Creative Specification
- **ProductionSpecification** - string - the name of the linked specification
- **ReasonUnableToProvideProductionSpecification** - string - the reason a specification cannot be provided
- **paging** - array - an array of paging date for the resultset data defined as follows:
  - **page** - int - the current page for this request
  - **page_size** - int - the maximum number of frame records per page
  - **total_pages** - int - the total number of pages this request generated
  - **total_records** - int - the total number of frame records this request generated

MediaOwnerFrameReference will only be returned in requests for frames where the user is the media owner.

PreviousFrameID will only be returned in requests for frames where a previous frame identifier has been assigned.

(*) Available for Proximity data subscribers. For further information contact space@uk.adwanted.com.

---

### GET /frame/mge-status

A lookup call to get the MGE upload status of frames that have been amended in the last 12-month period.

There is no INPUT for this method.

**Response example** (GET /api/frame/mge-status):
```json
{
    "data": [
        {
            "frame_id": 1234930685,
            "media_owner_id": 3,
            "media_owner_description": "JCDecaux",
            "date_of_last_change": "2022-01-23 14:00:34",
            "date_submitted_to_ims": "2022-01-24 21:00:00",
            "status": "Rejected - Error Code XX"
        },
        {
            "frame_id": 1234930685,
            "media_owner_id": 3,
            "media_owner_description": "JCDecaux",
            "date_of_last_change": "2022-01-25 14:00:34",
            "date_submitted_to_ims": "2022-01-26 21:00:00",
            "status": "Successful"
        },
        {
            "frame_id": 1234930685,
            "media_owner_id": 3,
            "media_owner_description": "JCDecaux",
            "date_of_last_change": "2022-02-25 14:00:34",
            "date_submitted_to_ims": null,
            "status": "Pending"
        }
    ]
}
```

**Response fields:**
- **frame_id** - int64 - the unique identifier used within SPACE to reference the frame
- **media_owner_id** - integer - the unique identifier used within SPACE to reference the media owner
- **media_owner_description** - string - a description of the media owner suitable for display to a user
- **date_of_last_change** - string - the date/time the frame was changed and added to the queue
- **date_submitted_to_ims** - string|null - the date/time the frame was submitted for processing, or NULL if still in the queue
- **status** - string - one of the following values "Pending", "Successful" or "Rejected" with some error code if "Rejected"

---

### GET /illumination

A lookup call to get all available illumination types, including their ID and description. The call will allow a single ID to be supplied in order to return the description. If no ID is supplied, all illumination types are returned.

**Parameters:**

| parameter | type | description |
| --- | --- | --- |
| id | string (optional) | a illumination code to restrict results to |

**Response example** (GET /api/illumination?id=2):
```json
{
    "data": [
        {
            "id": "2",
            "description": "Illuminated (front)"
        }
    ]
}
```

**Response fields:**
- **id** - string - the unique identifier used within SPACE to reference the illumination
- **description** - string - a description of the illumination suitable for display to a user

---

### GET /locality

A lookup call to get all available localities and comparable localities, including their ID and description. The call will allow a single ID to be given in order to limit results to the specific locality.

**Parameters:**

| parameter | type | description |
| --- | --- | --- |
| id | int (optional) | a locality id to restrict results to |

**Response example** (GET /api/locality?id=28):
```json
{
    "data": [
        {
            "locality_id": "28",
            "locality_code": "Aintree Rail Station",
            "comparable_locality_id": "4805",
            "comparable_locality_code": "Manchester Airport Rail Station"
        }
    ]
}
```

---

### GET /map-id

A lookup call to get all available Map IDs.

There is no INPUT for this method.

**Response example** (GET /api/map-id):
```json
{
    "data": [
        {
            "map_id": "8OUTDOOR_SHOPPING_CENTRE_EXTERIOR_DERBYRIVERLIGHTS_01OF01_01_20180822",
            "media_owner": "8 Outdoor"
        },
        {
            "map_id": "8OUTDOOR_SHOPPING_CENTRE_EXTERIOR_LEEDSPINNACLE_01OF01_01_20180822",
            "media_owner": "8 Outdoor"
        },
        {
            "map_id": "ADM_RETAIL _ABINGTON_01of01_01_20110117",
            "media_owner": "i-media"
        },
        {
            "map_id": "ADM_RETAIL _ALFRETON_01of01_01_20110117",
            "media_owner": "i-media"
        }
    ]
}
```

---

### GET /media-owner

A lookup call to get all available Media Owners, including their Media Owner ID and description. The call will allow a single ID to be given in order to return the description.

**Parameters:**

| parameter | type | description |
| --- | --- | --- |
| id | string (optional) | a media owner identifier to restrict results to |

**Response example** (GET /api/media-owner?id=3):
```json
{
    "data": [
        {
            "media_owner_id": 3,
            "media_owner_description": "JCDecaux"
        }
    ]
}
```

**Response fields:**
- **media_owner_id** - string - the unique identifier used within SPACE to reference the media owner
- **media_owner_description** - string - a description of the media owner suitable for display to a user

---

### GET /route-releases

A lookup call to get all available Route release dates.

**Response example** (GET /api/route-releases):
```json
{
    "data": [
        {
            "route_release_id": 51,
            "route_release_revision": 1,
            "space_deadline": "* Some message may be displayed in lieu of SPACE deadline.",
            "ims_deadline": "2024-01-18",
            "map_submission_deadline": "2023-11-13",
            "published_date": "2024-07-23",
            "notes": null,
            "trading_period_commences": "2024-08-05"
        },
        {
            "route_release_id": 52,
            "route_release_revision": 1,
            "space_deadline": "2024-05-08",
            "ims_deadline": "2024-05-09",
            "map_submission_deadline": "2024-03-11",
            "published_date": "2024-09-26",
            "notes": null,
            "trading_period_commences": "2024-10-14"
        },
        {
            "route_release_id": 53.01,
            "route_release_revision": 1,
            "space_deadline": "2024-08-07",
            "ims_deadline": "2024-08-08",
            "map_submission_deadline": "2024-06-10",
            "published_date": "2024-12-19",
            "notes": null,
            "trading_period_commences": "2025-01-05"
        },
        {
            "route_release_id": 54,
            "route_release_revision": 1,
            "space_deadline": "2024-11-06",
            "ims_deadline": "2024-11-07",
            "map_submission_deadline": "2024-09-09",
            "published_date": "2025-03-20",
            "notes": null,
            "trading_period_commences": "2025-04-07"
        },
        {
            "route_release_id": 55,
            "route_release_revision": 1,
            "space_deadline": "2025-01-08",
            "ims_deadline": "2025-01-09",
            "map_submission_deadline": "2024-11-11",
            "published_date": "2025-06-19",
            "notes": null,
            "trading_period_commences": "2025-07-07"
        },
        {
            "route_release_id": 56,
            "route_release_revision": 1,
            "space_deadline": "2025-05-07",
            "ims_deadline": "2025-05-08",
            "map_submission_deadline": "2025-03-10",
            "published_date": "2025-09-18",
            "notes": null,
            "trading_period_commences": "2025-10-06"
        },
        {
            "route_release_id": 57,
            "route_release_revision": 1,
            "space_deadline": "2025-08-13",
            "ims_deadline": "2025-08-14",
            "map_submission_deadline": "2025-06-09",
            "published_date": "2025-12-18",
            "notes": null,
            "trading_period_commences": "2026-01-05"
        }
    ]
}
```

---

### GET /tag

A lookup call to get all available tags, including their ID and description. The call will allow a single ID to be given in order to limit results to the specific tag.

**Parameters:**

| parameter | type | description |
| --- | --- | --- |
| id | int (optional) | a tag id to restrict results to |

**Response example** (GET /api/tag?id=1):
```json
{
    "data": [
        {
            "tag_id": 1,
            "tag_code": "HD",
            "tag_group_id": 1
        }
    ]
}
```

---

### GET /town

A lookup call to get all available towns, including their ID and description. The call will allow a single ID to be given in order to limit results to the specific town.

**Parameters:**

| parameter | type | description |
| --- | --- | --- |
| id | int (optional) | a town id to restrict results to |

**Response example** (GET /api/town?id=1):
```json
{
    "data": [
        {
            "town_id": "1",
            "town_name": "Aberdeen"
        }
    ]
}
```

---

### GET /train-operating-company

A lookup call to get a list of all available train operating companies.

This method has no input parameters.

**Response example** (GET /api/train-operating-company):
```json
{
    "data": [
        "Arriva Trains Wales",
        "c2c",
        "Chiltern Railways",
        "CrossCountry",
        "East Coast",
        "East Midlands Trains",
        "Eurostar",
        "First Capital Connect",
        "First Great Western",
        "First Hull Trains",
        "First TransPennine Express",
        "Gatwick Express",
        "Grand Central",
        "Heathrow Connect",
        "Heathrow Express",
        "Island Line Trains",
        "London Midland",
        "London Overground",
        "Merseyrail",
        "Greater Anglia",
        "Northern Rail",
        "ScotRail",
        "South West Trains",
        "Southeastern",
        "Southern",
        "Stansted Express",
        "Virgin Trains",
        "Wrexham and Shropshire"
    ]
}
```

---

### GET /tv-region

A lookup call to get all available TV regions, including their ID and description. The call will allow a single ID to be given in order to limit results to the specific TV region.

**Parameters:**

| parameter | type | description |
| --- | --- | --- |
| id | int (optional) | a TV region id to restrict results to |

**Response example** (GET /api/tv-region?id=1):
```json
{
    "data": [
        {
            "tv_region_id": "1",
            "tv_region_name": "Border"
        }
    ]
}
```

---

### GET /underground-line

A lookup call to get a list of all available underground lines.

This method has no input parameters.

**Response example** (GET /api/underground-line):
```json
{
    "data": [
        "Bakerloo",
        "Central",
        "Circle or Hammersmith and City",
        "District",
        "Glasgow Subway",
        "Jubilee",
        "Metropolitan",
        "Northern",
        "Piccadilly",
        "Victoria",
        "Waterloo and City"
    ]
}
```

---

### GET /vehicle-creative-position

A lookup call to get all available vehicle creative positions, including their ID and description.

This method has no input parameters.

**Response example** (GET /api/vehicle-creative-position):
```json
{
    "data": [
        {
            "id": 1,
            "on_route": true,
            "description": "Front"
        },
        {
            "id": 6,
            "on_route": false,
            "description": "Internal"
        },
        {
            "id": 3,
            "on_route": true,
            "description": "Nearside"
        },
        {
            "id": 4,
            "on_route": true,
            "description": "Offside"
        },
        {
            "id": 2,
            "on_route": true,
            "description": "Rear"
        },
        {
            "id": 5,
            "on_route": true,
            "description": "Wrap"
        }
    ]
}
```