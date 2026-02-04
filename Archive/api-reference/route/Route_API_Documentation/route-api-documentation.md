# Route API - Adwanted - API Documentation

## Overview

[Route](https://route.org.uk/) 's out-of-home advertising research data is available via this REST-like API, operated by [Adwanted UK](https://uk.adwanted.com/).

All references to API methods assume use of this base URL: **https://route.mediatelapi.co.uk/rest**

The API returns all output in JSON format and, where input is required, the HTTP request body also contains JSON.

### Security: HTTPS, login and API key

Access to the production API must be done via HTTPS.

As a client, you will be issued with a username and password which should be used to authenticate using HTTP Basic Authentication. If you are using a REST client (e.g. [Insomnia](https://insomnia.rest/), [Postman](https://www.getpostman.com/) or [Paw](https://paw.cloud/)), you can enter the username and password as part of your connection settings.

If you are developing a bespoke solution, it may be necessary instead to generate an 'Authorization' HTTP header to be sent with requests:

```
Authorization: Basic XXXX
```

where **XXXX** is a base64 encoding of the username and password separated by a colon character. See these [code examples for generating an HTTP Basic Auth header](https://gist.github.com/brandonmwest/a2632d0a65088a20c00a). Alternatively, use a [web tool to generate this header](https://www.blitter.se/utils/basic-authentication-header-generator/).

Additionally, an API Key will be issued to you which must be specified using the 'X-Api-Key' HTTP Header.

### HTTP headers

| Header | Description |
|----|----|
| Authorization | Used to supply your username and password. See the discussion in the previous section. |
| Accept | Must be set to **application/json** for all requests. |
| Content-Type | Must be set to **application/json** for all requests. |
| Accept-Encoding | Optional header which can be set to **gzip** to compress the response. |
| X-Api-Key | Required for all requests and must be set to the API key issues to your company. |

### Errors

Should the system detect a problem with your API request, such as invalid or missing data, the response code will be set to HTTP 400 (Bad Request) and JSON returned explaining the errors. Within the error response you'll find an error code and message further describing the error.

```
{
    "error_code": 225,
    "error_message": "JSON data error: Invalid or incomplete date-time: \"2016/10/03 10:30\""
}
```

The API includes the following error codes:

| Code | Description |
|----|----|
| 201 | Internal exception |
| 210 | API access not allowed |
| 215 | Invalid or incomplete HTTP request |
| 220 | Invalid or missing JSON property |
| 221 | Invalid or missing JSON property value |
| 225 | JSON date error |
| 230 | Demographic error |
| 240 | Grouping not accepted if API request have more then 100000 frames! |

### Limitations

To ensure the Route API accords with rules provided by Route and the Benchmarking Reach algorithm and to ensure optimum performance is maintained, the following limitations are in place:

* The Route API will not calculate reach based figures (reach, cover and average frequency) where schedules have a gap of a week or more (i.e. a week-on/week-off schedule) based on Mon–Sun as whole weeks.
* Grouping by frame_id cannot be used for more than 10,000 frames in a single call
* Grouping cannot be used for more than 100,000 frames in a single call.
* Where campaign schedules contain duplicate frames the dates/dayparts cannot overlap.
* The demographic array is limited to allowing a maximum of 30 demographics in a single call.
* The maximum number of resulting items/nodes cannot exceed 20,000 e.g. for a call with 10,000 frames using "grouping" by frame_id results in 10,000 output items. If applying more than 2 demographics at a time this will exceed 20,000 output nodes.
* The maximum size for an API request is 10Mb.

## POST version

A lookup call to get version information about data held in the system including route releases and algorithms.

When accessed via a POST request this API method will return a list of all version information.

Although this method is accessed via a POST request there is no HTTP body.

If accessing **POST https://route.mediatelapi.co.uk/rest/version** the following JSON would be returned:

```
{
    "api_version": "1.0",
    "default_route_release_id": 21,
    "route_releases": [
        {
            "route_release_id": 20,
            "route_release_revision": 2,
            "date_first_release": "2016-07-28",
            "date_last_revision": "2016-10-24",
            "total_respondents": 27948,
            "total_frames": 387898,
            "total_contacts": 212734522,
            "total_population": "51619.8007335308",
            "release_notes": ""
        },
        {
            "route_release_id": 21,
            "route_release_revision": 1,
            "date_first_release": "2016-10-27",
            "date_last_revision": "2016-11-01",
            "total_respondents": 27948,
            "total_frames": 391530,
            "total_contacts": 218217967,
            "total_population": "51619.8007335308",
            "release_notes": ""
        }
    ],
    "route_algorithms": [
        {
            "route_algorithm_version": 7.02,
            "supported_release_ids": [
                20,
                21
            ]
        }
    ],
    "processed_datetime": "2016-11-16 09:41:00"
}
```

* **api_version** - string - version identifier of the API
* A "route_releases" array containing release elements defined as follows:
* **route_release_id** - int - the route release ID
  * **default_route_release_id** - int - default route release /demographics will return where no release is specified.
  * **route_release_revision** - int - the latest available revision
  * **date_first_release** - string - date of first release
  * **date_last_revision** - string - date of last revision
  * **total_respondents** - int - total number of respondents
  * **total_contacts** - int - total number of contacts
  * **total_population** - int - total population
  * **release_notes** - string - release notes
* A "route_algorithms" array containing algorithm elements defined as follows:
* **route_algorithm_version** - float - the algorithm version
  * A "supported_release_ids" element that contains an array of Route release IDs
* **processed_datetime** - string - date and time of processing

## POST validate/demographic

Used to validate a custom audience build against a given release.

When accessed via a POST request this API method will validate a custom audience build returning information such as population and sample size. Your HTTP body should consist of JSON similar to the following sample.

Each attribute type/value will be validated to ensure that the data is valid. See the section on errors for how errors are represented.

As this method is accessed via a POST request the raw body must be set to JSON as described below.

```
{
    "route_release_id": 21,
    "demographic_custom": "sex=1 and social_grade<4",
    "option_respondent_data": false
}
```

The table below details the fields used in this example.

| parameter | type | description |
|----|----|----|
| route_release_id | int (required) | Specify Route release data |
| demographic_custom | string (required) | Custom audience build |
| option_respondent_data | boolean (optional) | Option (only available to Route Underwriting Companies) to have Respondent IDs returned in the output |

If accessing **POST https://route.mediatelapi.co.uk/rest/validate/demographic** with the body set to the sample JSON above then the following JSON would be returned:

```
{
    "route_release_id": 21,
    "demographic_valid": true,
    "expression": "sex=1 and social_grade<4",
    "population": 13532.94417019603,
    "sample_size": 7497,
    "processed_datetime": "2018-08-06 17:55:56"
}
```

* **route_release_id** - int - route release identifier
* **demographic_valid** - boolean - whether the audience is valid nor not
* **expression** - string - custom audience build
* **population** - float - population for this audience
* **sample_size** - int - sample size for this audience
* **processed_datetime** - string - date and time of processing

## POST process/custom

Used to retrieve figures and metrics.

When accessed via a POST request this API method will retrieve figures and metrics. Your HTTP body should consist of JSON similar to the following sample.

Each attribute type/value will be validated to ensure that the data is valid. See the section on errors for how errors are represented.

As this method is accessed via a POST request the raw body must be set to JSON as described below.

```
{
    "route_release_id": 47,
    "route_algorithm_version": 10.2,
    "option_split_reach": true,
    "algorithm_figures": [
        "grp",
        "impacts",
        "reach",
        "population"
    ],
    "demographics": [
        {
            "demographic_id": 1,
            "granular_audience_id": 10
        },
        {
            "demographic_custom": "sex=1 AND social_grade<=3"
        }
    ],
    "default_spot_length": 10,
    "default_spot_break_length": 50,
    "grouping": "environment",
    "campaign": [
        {
            "schedule": [
                {
                    "datetime_from": "2016-10-03 10:30",
                    "datetime_until": "2016-10-20 20:00"
                }
            ],
            "spot_length": 10,
            "spot_break_length": 50,
            "frames": [
                1234923947
            ]
        },
        {
            "schedule": [
                {
                    "date": "2016-10-10"
                },
                {
                    "date": "2016-10-11",
                    "daypart_from": "08:45",
                    "daypart_until": "12:15"
                },
                {
                    "date_from": "2016-10-15",
                    "date_until": "2016-10-25",
                    "daypart_from": "16:30",
                    "daypart_until": "22:00"
                }
            ],
            "spot_length": 10,
            "spot_break_length": 50,
            "frames": [
                1234923978
            ]
        }
    ],
    "target_month": 10,
    "option_respondent_data": false
}
```

The table below details the fields used in this example.

| parameter | type | description |
|----|----|----|
| route_release_id | int (required) | Specify Route release data |
| route_algorithm_version | float (required) | Specify Route algorithm version |
| option_split_reach | boolean (optional) | Option to include reach figures split by pedestrian/vehicular. Will only be included where "reach" or "all" are requested and will default to false. Unlike impacts, the sum of split reach figures will be higher than the total reach due to respondents having both pedestrian & vehicular contacts counted. |
| algorithm_figures | array of strings (required) | Custom set of desired figures to be processed including: - cover - average_frequency - reach - impacts - grp - population - sample_size - all  In addition, impacts_quarter_hour can be included, and impacts split by quarter hour will be provided.  "frequency_distribution" can also be included, and data values (prob., cumulative prob., n+) for each frequency 0-100 will be provided. |
| demographics | array (optional) | Allows defining of multiple demographic and granular audience definitions. Each demographic definitions will have separate results. If no demographic supplied the system will default to "All Adults". If no granular audience is supplied the system will default to "All Adults".  Each item in the array could either be a key/value pair set to:  - **demographic_id** as obtained from [POST /demographics](https://docs-route.mediatelapi.co.uk/api/documentation/demographics-post) - **demographic_custom** allows for fine-grained demographic definition - **granular_audience_id** as obtained from [POST /demographics](https://docs-route.mediatelapi.co.uk/api/documentation/demographics-post)  Syntax for the demographic_custom:  **Operators:**  "AND" conjunction   "OR" disjunction    **Logical Operators:**  "=" equal   ">" greater   ">="greater and equal   "<"lower   "<="lower or equal    Use of parentheses should be done to logically separate AND OR operators.  An example demographic scenario "males with a social_grade<=3 and females with a social_grade<=2" will have following API expression: (sex=1 AND social_grade<=3) OR (sex=2 AND social_grade<=2)  The expression is evaluated for each respondent, so expressions like "social_grade=1 AND social_grade=2" would match no respondents. You would need to specify "social_grade=1 OR social_grade=2" if you wanted a group made up of As and Bs.  Non-integer values are also accepted e.g. we're able to query a postcode district using "pdist='E 1'". |
| target_month | int (optional) | The target month is used to calculate the Illumination Effect to be applied to the campaign, values range from 01 - January to 12 - December.  If no target month is provided the IE will be calculated based on the earliest start date provided. |
| option_respondent_data | boolean (optional) | Option (only available to Route Underwriting Companies) to have Respondent IDs returned in the output  Please note: this option cannot be used in conjunction with "grouping". |
| default_spot_length | int (optional) | Length of the spot in seconds to be applied where spot_length not specified within the campaign array. If not populated 10 will be used.  *To be used in conjunction with default_spot_break_length.* |
| default_spot_break_length | int (optional) | Length of the break in seconds to be applied where spot_break_length not specified within the campaign array. If not populated 50 will be used.  *To be used in conjunction with default_spot_length.* |
| grouping | string (optional) | Returns additional result break downs grouped by frame attribute criteria and can be one of: - day - daypart - day_daypart - environment - mediaowner - dimension - frame_id (limited to 10,000 frames in a single call) - frame_type - illumination - region - postal_sector - tv_area - town - conurbation  Please note: this option cannot be used in conjunction with "option_respondent_data" or "impacts_quarter_hour". |
| option_include_totals | boolean (optional) | Option to exclude totals being returned in the output. Will only be applied where grouping is used. |
| campaign | array (required) | This will contain one or more campaigns which can be defined as follows. |
| campaign | element | A campaign element can contain one or more schedules each with their own unique set of frames.  - **schedule** array of schedule elements as defined below - **spot_length** - int - optional. Length of the spot in seconds. If not populated 10 will be used. 	*To be used in conjunction with spot_break_length.* - **spot_break_length** - int - optional. Length of the break in seconds. If not populated 50 will be used. 	*To be used in conjunction with spot_length.* - **frames** - array - required. Array of frame identifiers |
| schedule | element | A schedule element can contain options such as:  1. Coverage period where time part is optional  - **datetime_from** formatted as "2016-10-03 10:30" - **datetime_until** formatted as "2016-10-03 10:30"  2. Specific day (all time)  - **date** formatted as "2016-10-03"  3. Daypart set for a specific day  - **date** formatted as "2016-10-03" - **daypart_from** formatted as "08:45" - **daypart_until** formatted as "12:15"  4. Daypart set for a date range  - **date_from** formatted as "2016-10-15" - **date_until** formatted as "2016-10-25" - **daypart_from** formatted as "08:45" - **daypart_until** formatted as "12:15"  When supplying times please ensure they are in 24 hour format. Times reflect the current UK time zone.  Times are measured in "dayparts" and will be rounded to the nearest quarter of an hour daypart (e.g. 10:07 will be handled as 10:00, 10:08 as 10:15).  Please note a **datetime_until** "00:00" will include the given day in full (in effect acting as 24:00). As an example the following will return data for both days  `"datetime_from" : "2017-01-01 00:00", "datetime_until": "2017-01-02 00:00"`  Please also note if a campaign covers multiple months only the earliest start month is used to calculate the Illumination Effect to be applied to the campaign. If a target_month is supplied this will override the start month. |
| option_fd_steps | boolean (optional) | Optional parameter to set custom number of frequency distributions steps, default value is 11. |

If accessing **POST https://route.mediatelapi.co.uk/rest/process/custom** with the body set to the sample JSON above then the following JSON would be returned:

```
{
  "route_release_id": 47,
  "route_release_revision": 1,
  "route_algorithm_version": 10.2,
  "results": [{
      "description": "total",
      "demographic": "All Adults 15+ (1)",
      "granular_audience": "Males (10)",
      "target_month": 10,
      "figures": {
        "population": "53045.3510597589",
        "impacts": "71.1635723408",
        "impacts_pedestrian": "66.12747321",
        "impacts_vehicular": "5.0360991308",
        "gross_rating_points": "0.1341560965",
        "reach": "58.0329302138",
        "reach_pedestrian": "53.1346070275",
        "reach_vehicular": "5.449553136",
        "rag_status": "green"
      },
      "metrics": {
        "total_frames": 2,
        "total_dynamic_frames": 1,
        "total_contacts": 2897,
        "total_actual_contacts": 107,
        "total_respondents": 698,
        "total_actual_respondents": 48
      }
    },
    {
      "description": "total",
      "demographic": "Custom (sex=1 AND social_grade<=3)",
      "granular_audience": "All Adults (1)",
      "target_month": 10,
      "figures": {
        "population": "14385.941746469",
        "impacts": "53.4831453262",
        "impacts_pedestrian": "49.8704570973",
        "impacts_vehicular": "3.6126882288",
        "gross_rating_points": "0.371773682",
        "reach": "20.6793547177",
        "reach_pedestrian": "18.876310193",
        "reach_vehicular": "1.8660491926",
        "rag_status": "amber"
      },
      "metrics": {
        "total_frames": 2,
        "total_dynamic_frames": 1,
        "total_contacts": 1147,
        "total_actual_contacts": 53,
        "total_respondents": 238,
        "total_actual_respondents": 23
      }
    },
    {
      "description": "grouping",
      "demographic": "All Adults 15+ (1)",
      "granular_audience": "Males (10)",
      "target_month": 10,
      "environment": "16",
      "figures": {
        "population": "53045.3510597589",
        "impacts": "71.1635723408",
        "impacts_pedestrian": "66.12747321",
        "impacts_vehicular": "5.0360991308",
        "gross_rating_points": "0.1341560965",
        "reach": "58.0329302138",
        "reach_pedestrian": "53.1346070275",
        "reach_vehicular": "5.449553136",
        "rag_status": "green"
      },
      "metrics": {
        "total_frames": 2,
        "total_dynamic_frames": 1,
        "total_contacts": 2897,
        "total_actual_contacts": 107,
        "total_respondents": 698,
        "total_actual_respondents": 48
      }
    },
    {
      "description": "grouping",
      "demographic": "Custom (sex=1 AND social_grade<=3)",
      "granular_audience": "All Adults (1)",
      "target_month": 10,
      "environment": "16",
      "figures": {
        "population": "14385.941746469",
        "impacts": "53.4831453262",
        "impacts_pedestrian": "49.8704570973",
        "impacts_vehicular": "3.6126882288",
        "gross_rating_points": "0.371773682",
        "reach": "20.6793547177",
        "reach_pedestrian": "18.876310193",
        "reach_vehicular": "1.8660491926",
        "rag_status": "amber"
      },
      "metrics": {
        "total_frames": 2,
        "total_dynamic_frames": 1,
        "total_contacts": 1147,
        "total_actual_contacts": 53,
        "total_respondents": 238,
        "total_actual_respondents": 23
      }
    }
  ],
  "total_processing_time": 55,
  "processed_datetime": "2023-06-05 11:27:47"
}
```

* **route_release_id** - int - route release identifier
* **route_release_revision** - int - route release revision
* **route_algorithm_version** - float - algorithm version
* **total_processing_time** - int - processing time in ms
* **frame_exceptions** - array - array of frame identifiers that could not be processed
* A "results" element (one for each schedule) defined as follows:
* **description** - string - set either to 'total' for total values and/or your requested grouping
  * **demographic** - string - description of the demographic used
  * **granular_audience** - string - description of the granular audience used
  * **target_month** - int - target month
  * A "figures" element defined as follows:
* **population** - string - population (in 000s) - **sample_size** - string - sample size (in 000s) - **impacts** - string - impacts (in 000s) - **impacts_pedestrian** - string - pedestrian impacts (in 000s) - **impacts_vehicular** - string - vehicular impacts (in 000s) - **gross_rating_points** - string - gross rating point - **reach** - string - reach (in 000s) - **reach_pedestrian** - string - pedestrian reach (in 000s) - **reach_vehicular** - string - vehicular reach (in 000s) - **rag_status** - string - traffic light confidence rating
  * An "impacts_quarter_hour" array with an element of figures for each quarter hour breakdown (if requested) defined as follows:
* **mode_of_transport** - int - **day** - int - **time** - int - **impacts** - string - **illumination_effect** - string - for single frames only
  * A "metrics" element defined as follows:
* **total_frames** - int - total frames - **total_dynamic_frames** - int - total dynamic frames - **total_contacts** - int - total contacts - **total_actual_contacts** - int - total actual contacts - **total_respondents** - int - total respondents - **total_actual_respondents** - int - total actual respondents
  * A "frequency_distribution" element containing further elements per frequency 0-10, with 10 being 10+:
* **prob** - string - Cover - **cuml** - string - Cumulative Cover - **n+** - string - N+ Cover
  * **respondents** - array - array containing all respondent IDs (both actual and virtual)
  * **actual_respondents** - array - array containing actual respondent IDs
  * If relevant, a "warnings" element containing a code and warning text
* **total_processing_time** - int - total length of time to process a request in ms
* **queue_wait_time** - int - length of any queued time for a request in ms
* **processed_datetime** - string - date and time of processing

There are several alternative terms to describe the event that a respondent passed and possibly looked at a frame and the number of such events: audience, impacts, gross impacts, contacts, visibility adjusted contacts (VACs) etc. The number of such respondents may be termed reach or cover.

* **Impacts** - numerically equivalent to audience, but as computed by the Algorithms, both in total (= Audience) and for breakdowns such as regions and demographic subgroups.
* **Contacts** - the counts based on the travel survey
* **GRPs (gross rating points)** - are Impacts divided by the size of the target population \* 100%.
* **Reach** - is the number of people in the target population seeing at least one frame (in 000s).
* **Cover** - Reach divided by the size of the target population (a decimal).
* **Cover %** - Cover \* 100%.

Note that the Audiences, Impacts and weighted Contacts are comparable measures of 'eyes on frames', and all are visibility-adjusted.

Impacts are calculated with a conforming factor based on the audience within the timeband requested. Please note this means that, depending on the time band being analysed, impacts will not sum due to the use of differing conforming factors.

Days are represented as integers with 1 = Monday, 2 = Tuesday... 7 = Sunday.

The term daypart refers to the day and time divisions.

The term 'environment' refers to the different types of frame or location: roadside, bus sides, underground stations etc.

Respondents have a survey weight; these weights project the sample to the adult population of Great Britain, both in total and for various regional and demographic breakdowns.

The terms reach and cover are usually used interchangeably. For clarity, Route adopt the convention that reach is in 000 while cover is a proportion i.e. cover = reach / population and cover % = cover \* 100

**Traffic light confidence rating (RAG Alerts)**

Although based on an estimated level of tolerance i.e. the 'Confidence level' on the Benchmark Reach figure, as a general rule of thumb, the traffic light colour output as the rag_status depends on the number of contacts for the requested frames:

* Green light - if 100+ contacts then analysis is possible.
* Amber light - if 30-99 then analysis is still possible but be aware of the sample size.
* Red light - if below 30 then analysis is not recommended.

## POST process/standard/multiweek

Used to retrieve figures and metrics for multiple output weeks in a single call.

When accessed via a POST request this API method will retrieve figures and metrics for an input array of weeks. Your HTTP body should consist of JSON similar to the following sample.

Each attribute type/value will be validated to ensure that the data is valid. See the section on errors for how errors are represented.

As this method is accessed via a POST request the raw body must be set to JSON as described below.

```
{
  "route_release_id": 34,
  "route_algorithm_version": 7.51,
  "option_split_reach": true,
  "algorithm_figures": [
    "grp",
    "impacts",
    "reach",
    "population"
  ],
  "demographic_id": null,
  "demographic_custom": "sex=1 AND marital_status=1 AND social_grade<=3",
  "target_month": 8,
  "standard_dayparts": [
    1,
    8
  ],
  "weeks": [
    1,
    2,
    4
  ],
  "spot_length": 10,
  "spot_break_length": 50,
  "frames": [
    1234569931,
    1234569937,
    1234570228,
    1234570562,
    1234570572
  ]
}
```

The table below details the fields used in this example.

| parameter | type | description |
|----|----|----|
| route_release_id | int (required) | Specify Route release data |
| route_algorithm_version | float (required) | Specify Route algorithm version |
| option_split_reach | boolean (optional) | Option to include reach figures split by pedestrian/vehicular. Will only be included where "reach" or "all" are requested and will default to false. Unlike impacts, the sum of split reach figures will be higher than the total reach due to respondents having both pedestrian & vehicular contacts counted. |
| algorithm_figures | array of strings (required) | Custom set of desired figures to be processed including: - cover - average_frequency - reach - impacts - grp - population - sample_size - all  In addition, impacts_quarter_hour can be included and impacts split by quarter hour will be provided.  "frequency_distribution" can also be included, and data values (prob., cumulative prob., n+) for each frequency 0-10 (with 10 being 10+) will be provided. |
| granular_audience_id | int (optional) | The standard granularity audience id to use, options are available from [POST /demographics](https://docs-route.mediatelapi.co.uk/api/documentation/demographics-post). If no value is supplied the API default ("All Adults") will be used |
| demographic_id | int (optional) | The standard demographic to use, options are available from [POST /demographics](https://docs-route.mediatelapi.co.uk/api/documentation/demographics-post). You can either set demographic_id or demographic_custom but not both. If no value is supplied the API default ("All Adults") will be used |
| demographic_custom | string (optional) | Allows for fine-grained demographic definition.  Syntax for the demographic_custom:  **Operators:**  "AND" conjunction   "OR" disjunction    **Logical Operators:**  "=" equal   ">" greater   ">="greater and equal   "<"lower   "<="lower or equal    Use of parentheses should be done to logically separate AND OR operators.  An example demographic scenario "males with a social_grade<=3 and females with a social_grade<=2" will have following API expression: (sex=1 AND social_grade<=3) OR (sex=2 AND social_grade<=2)  The expression is evaluated for each respondent, so expressions like "social_grade=1 AND social_grade=2" would match no respondents. You would need to specify "social_grade=1 OR social_grade=2" if you wanted a group made up of As and Bs.  Non-integer values are also accepted e.g. we're able to query a postcode district using "pdist='E 1'". |
| target_month | int (required) | The target month is used to calculate the Illumination Effect to be applied to the campaign, values range from 01 - January to 12 - December. |
| standard_dayparts | array of ints (required) | The dayparts to use which can include:  **Weekday:**  \| Code \| Time period (24 hour) \| \| --- \| --- \| \| 1 \| 06:00 to 09:59 \| \| 2 \| 10:00 to 15:59 \| \| 3 \| 16:00 to 18:59 \| \| 4 \| 19:00 to 05:59 \|  **Weekend:**  \| Code \| Time period (24 hour) \| \| --- \| --- \| \| 5 \| 06:00 to 09:59 \| \| 6 \| 10:00 to 15:59 \| \| 7 \| 16:00 to 18:59 \| \| 8 \| 19:00 to 05:59 \| |
| weeks | array (required) | Weeks of the campaign |
| spot_length | int (optional) | Length of the spot in seconds. If not populated 10 will be used.  *To be used in conjunction with spot_break_length.* |
| spot_break_length | int (optional) | Length of the break in seconds. If not populated 50 will be used.  *To be used in conjunction with spot_length.* |
| frames | array (required) | List of frame identifiers |

If accessing **POST https://route.mediatelapi.co.uk/rest/process/standard** with the body set to the sample JSON above then the following JSON would be returned:

```
{
  "route_release_id": 34,
  "route_release_revision": 3,
  "route_algorithm_version": 7.51,
  "target_month": 8,
  "demographic": "Custom (sex=1 AND marital_status=1 AND social_grade<=3)",
  "granular_audience": "All Adults (1)",
  "results": [
    {
      "weeks": 1,
      "figures": {
        "population": "8671.507528966",
        "impacts": "6.7577701807",
        "impacts_pedestrian": "6.7577701807",
        "impacts_vehicular": "0",
        "gross_rating_points": "0.0779779863",
        "reach": "5.8429364652",
        "reach_pedestrian": "5.8429364652",
        "reach_vehicular": "0",
        "rag_status": "green"
      }
    },
    {
      "weeks": 2,
      "figures": {
        "population": "8671.507528966",
        "impacts": "13.5155403614",
        "impacts_pedestrian": "13.5155403614",
        "impacts_vehicular": "0",
        "gross_rating_points": "0.1559559725",
        "reach": "10.2298568077",
        "reach_pedestrian": "10.2298568077",
        "reach_vehicular": "0",
        "rag_status": "green"
      }
    },
    {
      "weeks": 4,
      "figures": {
        "population": "8671.507528966",
        "impacts": "27.0310807227",
        "impacts_pedestrian": "27.0310807227",
        "impacts_vehicular": "0",
        "gross_rating_points": "0.311911945",
        "reach": "16.6045260987",
        "reach_pedestrian": "16.6045260987",
        "reach_vehicular": "0",
        "rag_status": "green"
      }
    }
  ],
  "metrics": {
    "total_frames": 5,
    "total_dynamic_frames": 5,
    "total_contacts": 1336,
    "total_actual_contacts": 417,
    "total_respondents": 274,
    "total_actual_respondents": 86
  },
  "total_processing_time": 25,
  "processed_datetime": "2020-02-28 16:53:12"
}
```

* **route_release_id** - int - route release identifier
* **route_release_revision** - int - route release revision
* **route_algorithm_version** - float - algorithm version
* **total_processing_time** - int - processing time in ms
* **target_month** - int - target month
* **frame_exceptions** - array - array of frame identifiers that could not be processed
* **demographic** - string - demographic used
* **granular_audience** - string - granular audience used
* A "results" element (one for each week) defined as follows:
* **weeks** - int - week of campaign
  * A "figures" element defined as follows:
* **population** - string - population (in 000s) - **sample_size** - string - sample size (in 000s) - **impacts** - string - impacts (in 000s) - **impacts_pedestrian** - string - pedestrian impacts (in 000s) - **impacts_vehicular** - string - vehicular impacts (in 000s) - **gross_rating_points** - string - gross rating point - **reach** - string - reach (in 000s) - **reach_pedestrian** - string - pedestrian reach (in 000s) - **reach_vehicular** - string - vehicular reach (in 000s) - **rag_status** - string - traffic light confidence rating
* An "impacts_quarter_hour" array with an element of figures for each quarter hour breakdown (if requested) defined as follows:
* **mode_of_transport** - int
  * **day** - int
  * **time** - int
  * **impacts** - string
  * **illumination_effect** - string - for single frames only
* A "metrics" element defined as follows:
* **total_frames** - int - total frames
  * **total_dynamic_frames** - int - total dynamic frames
  * **total_contacts** - int - total contacts
  * **total_actual_contacts** - int - total actual contacts
  * **total_respondents** - int - total respondents
  * **total_actual_respondents** - int - total actual respondents
* A "frequency_distribution" element containing further elements per frequency 0-10, with 10 being 10+:
* **prob** - string - Cover
  * **cuml** - string - Cumulative Cover
  * **n+** - string - N+ Cover
* If relevant a "warnings" element containing a code and warning text
* **total_processing_time** - int - total length of time to process a request in ms
* **queue_wait_time** - int - length of any queued time for a request in ms
* **processed_datetime** - string - date and time of processing

There are several alternative terms to describe the event that a respondent passed and possibly looked at a frame and the number of such events: audience, impacts, gross impacts, contacts, visibility adjusted contacts (VACs) etc. The number of such respondents may be termed reach or cover.

* **Impacts** - numerically equivalent to audience, but as computed by the Algorithms, both in total (= Audience) and for breakdowns such as regions and demographic subgroups.
* **Contacts** - the counts based on the travel survey
* **GRPs (gross rating points)** - are Impacts divided by the size of the target population \* 100%.
* **Reach** - is the number of people in the target population seeing at least one frame (in 000s).
* **Cover** - Reach divided by the size of the target population (a decimal).
* **Cover %** - Cover \* 100%.

Note that the Audiences, Impacts and weighted Contacts are comparable measures of 'eyes on frames', and all are visibility-adjusted.

Impacts are calculated with a conforming factor based on the audience within the timeband requested. Please note this means that, depending on the time band being analysed, impacts will not sum due to the use of differing conforming factors.

Days are represented as integers with 1 = Monday, 2 = Tuesday... 7 = Sunday.

The term daypart refers to the day and time divisions.

The term 'environment' refers to the different types of frame or location: roadside, bus sides, underground stations etc.

Respondents have a survey weight; these weights project the sample to the adult population of Great Britain, both in total and for various regional and demographic breakdowns.

The terms reach and cover are usually used interchangeably. For clarity, Route adopt the convention that reach is in 000 while cover is a proportion i.e. cover = reach / population and cover % = cover \* 100

**Traffic light confidence rating (RAG Alerts)**

Although based on an estimated level of tolerance i.e. the 'Confidence level' on the Benchmark Reach figure, as a general rule of thumb, the traffic light colour output as the rag_status depends on the number of contacts for the requested frames:

* Green light - if 100+ contacts then analysis is possible.
* Amber light - if 30-99 then analysis is still possible but be aware of the sample size.
* Red light - if below 30 then analysis is not recommended.

## POST process/standard

Used to retrieve figures and metrics.

When accessed via a POST request this API method will retrieve figures and metrics. Your HTTP body should consist of JSON similar to the following sample.

Each attribute type/value will be validated to ensure that the data is valid. See the section on errors for how errors are represented.

As this method is accessed via a POST request the raw body must be set to JSON as described below.

```
{
    "route_release_id": 47,
    "route_algorithm_version": 10.2,
    "option_split_reach": true,
    "algorithm_figures": [
        "grp",
        "impacts",
        "reach",
        "population"
    ],
    "demographic_id": null,
    "demographic_custom": "sex=1 AND marital_status=1 AND social_grade<=3",
    "target_month": 8,
    "standard_dayparts": [
        1,
        8
    ],
    "total_weeks": "4",
    "spot_length": 10,
    "spot_break_length": 50,
    "frames": [
        1234569931,
        1234569937,
        1234570228,
        1234570562,
        1234570572
    ]
}
```

The table below details the fields used in this example.

| parameter | type | description |
|----|----|----|
| route_release_id | int (required) | Specify Route release data |
| route_algorithm_version | float (required) | Specify Route algorithm version |
| option_split_reach | boolean (optional) | Option to include reach figures split by pedestrian/vehicular. Will only be included where "reach" or "all" are requested and will default to false. Unlike impacts, the sum of split reach figures will be higher than the total reach due to respondents having both pedestrian & vehicular contacts counted. |
| algorithm_figures | array of strings (required) | Custom set of desired figures to be processed including: - cover - average_frequency - reach - impacts - grp - population - sample_size - all  In addition, impacts_quarter_hour can be included, and impacts split by quarter hour will be provided.  "frequency_distribution" can also be included, and data values (prob., cumulative prob., n+) for each frequency 0-100 will be provided. |
| granular_audience_id | int (optional) | The standard granularity audience id to use, options are available from [POST /demographics](https://docs-route.mediatelapi.co.uk/api/documentation/demographics-post). If no value is supplied the API default ("All Adults") will be used |
| demographic_id | int (optional) | The standard demographic to use, options are available from [POST /demographics](https://docs-route.mediatelapi.co.uk/api/documentation/demographics-post). You can either set demographic_id or demographic_custom but not both. If no value is supplied the API default ("All Adults") will be used |
| demographic_custom | string (optional) | Allows for fine-grained demographic definition.  Syntax for the demographic_custom:  **Operators:**  "AND" conjunction   "OR" disjunction    **Logical Operators:**  "=" equal   ">" greater   ">="greater and equal   "<"lower   "<="lower or equal    Use of parentheses should be done to logically separate AND OR operators.  An example demographic scenario "males with a social_grade<=3 and females with a social_grade<=2" will have following API expression: (sex=1 AND social_grade<=3) OR (sex=2 AND social_grade<=2)  The expression is evaluated for each respondent, so expressions like "social_grade=1 AND social_grade=2" would match no respondents. You would need to specify "social_grade=1 OR social_grade=2" if you wanted a group made up of As and Bs.  Non-integer values are also accepted e.g. we're able to query a postcode district using "pdist='E 1'". |
| target_month | int (required) | The target month is used to calculate the Illumination Effect to be applied to the campaign, values range from 01 - January to 12 - December. |
| standard_dayparts | array of ints (required) | The dayparts to use which can include:  **Weekday:**  \| Code \| Time period (24 hour) \| \| --- \| --- \| \| 1 \| 06:00 to 09:59 \| \| 2 \| 10:00 to 15:59 \| \| 3 \| 16:00 to 18:59 \| \| 4 \| 19:00 to 05:59 \|  **Weekend:**  \| Code \| Time period (24 hour) \| \| --- \| --- \| \| 5 \| 06:00 to 09:59 \| \| 6 \| 10:00 to 15:59 \| \| 7 \| 16:00 to 18:59 \| \| 8 \| 19:00 to 05:59 \| |
| total_weeks | int (required) | Duration, in weeks, of the campaign |
| spot_length | int (optional) | Length of the spot in seconds. If not populated 10 will be used.  *To be used in conjunction with spot_break_length.* |
| spot_break_length | int (optional) | Length of the break in seconds. If not populated 50 will be used.  *To be used in conjunction with spot_length.* |
| frames | array (required) | List of frame identifiers |
| option_fd_steps | boolean (optional) | Optional parameter to set custom number of frequency distributions steps, default value is 11. |

If accessing **POST https://route.mediatelapi.co.uk/rest/process/standard** with the body set to the sample JSON above then the following JSON would be returned:

```
{
  "route_release_id": 47,
  "route_release_revision": 1,
  "route_algorithm_version": 10.2,
  "target_month": 8,
  "frame_exceptions": [
    1234570228
  ],
  "demographic": "Custom (sex=1 AND marital_status=1 AND social_grade<=3)",
  "granular_audience": "All Adults (1)",
  "figures": {
    "population": "8666.253778863",
    "impacts": "24.8764618666",
    "impacts_pedestrian": "24.8764618666",
    "impacts_vehicular": "0",
    "gross_rating_points": "0.2870497738",
    "reach": "15.8904211035",
    "reach_pedestrian": "15.8904211035",
    "reach_vehicular": "0",
    "rag_status": "green"
  },
  "metrics": {
    "total_frames": 4,
    "total_dynamic_frames": 4,
    "total_contacts": 995,
    "total_actual_contacts": 563,
    "total_respondents": 402,
    "total_actual_respondents": 155
  },
  "total_processing_time": 450,
  "processed_datetime": "2023-06-05 11:27:47"
}
```

* **route_release_id** - int - route release identifier
* **route_release_revision** - int - route release revision
* **route_algorithm_version** - float - algorithm version
* **total_processing_time** - int - processing time in ms
* **target_month** - int - target month
* **frame_exceptions** - array - array of frame identifiers that could not be processed
* **demographic** - string - demographic used
* **granular_audience** - string - granular audience used
* A "figures" element defined as follows:
* **population** - string - population (in 000s)
  * **sample_size** - string - sample size (in 000s)
  * **impacts** - string - impacts (in 000s)
  * **impacts_pedestrian** - string - pedestrian impacts (in 000s)
  * **impacts_vehicular** - string - vehicular impacts (in 000s)
  * **gross_rating_points** - string - gross rating point
  * **reach** - string - reach (in 000s)
  * **reach_pedestrian** - string - pedestrian reach (in 000s)
  * **reach_vehicular** - string - vehicular reach (in 000s)
  * **rag_status** - string - traffic light confidence rating
* An "impacts_quarter_hour" array with an element of figures for each quarter hour breakdown (if requested) defined as follows:
* **mode_of_transport** - int
  * **day** - int
  * **time** - int
  * **impacts** - string
  * **illumination_effect** - string - for single frames only
* A "metrics" element defined as follows:
* **total_frames** - int - total frames
  * **total_dynamic_frames** - int - total dynamic frames
  * **total_contacts** - int - total contacts
  * **total_actual_contacts** - int - total actual contacts
  * **total_respondents** - int - total respondents
  * **total_actual_respondents** - int - total actual respondents
* A "frequency_distribution" element containing further elements per frequency 0-10, with 10 being 10+:
* **prob** - string - Cover
  * **cuml** - string - Cumulative Cover
  * **n+** - string - N+ Cover
* If relevant a "warnings" element containing a code and warning text
* **total_processing_time** - int - total length of time to process a request in ms
* **queue_wait_time** - int - length of any queued time for a request in ms
* **processed_datetime** - string - date and time of processing

There are several alternative terms to describe the event that a respondent passed and possibly looked at a frame and the number of such events: audience, impacts, gross impacts, contacts, visibility adjusted contacts (VACs) etc. The number of such respondents may be termed reach or cover.

* **Impacts** - numerically equivalent to audience, but as computed by the Algorithms, both in total (= Audience) and for breakdowns such as regions and demographic subgroups.
* **Contacts** - the counts based on the travel survey
* **GRPs (gross rating points)** - are Impacts divided by the size of the target population \* 100%.
* **Reach** - is the number of people in the target population seeing at least one frame (in 000s).
* **Cover** - Reach divided by the size of the target population (a decimal).
* **Cover %** - Cover \* 100%.

Note that the Audiences, Impacts and weighted Contacts are comparable measures of 'eyes on frames', and all are visibility-adjusted.

Impacts are calculated with a conforming factor based on the audience within the timeband requested. Please note this means that, depending on the time band being analysed, impacts will not sum due to the use of differing conforming factors.

Days are represented as integers with 1 = Monday, 2 = Tuesday... 7 = Sunday.

The term daypart refers to the day and time divisions.

The term 'environment' refers to the different types of frame or location: roadside, bus sides, underground stations etc.

Respondents have a survey weight; these weights project the sample to the adult population of Great Britain, both in total and for various regional and demographic breakdowns.

The terms reach and cover are usually used interchangeably. For clarity, Route adopt the convention that reach is in 000 while cover is a proportion i.e. cover = reach / population and cover % = cover \* 100

**Traffic light confidence rating (RAG Alerts)**

Although based on an estimated level of tolerance i.e. the 'Confidence level' on the Benchmark Reach figure, as a general rule of thumb, the traffic light colour output as the rag_status depends on the number of contacts for the requested frames:

* Green light - if 100+ contacts then analysis is possible.
* Amber light - if 30-99 then analysis is still possible but be aware of the sample size.
* Red light - if below 30 then analysis is not recommended.

## POST framesearch

Used to locate frame identifiers based on search criteria.

When accessed via a POST request this API method will return frame identifiers matching your search criteria. Your HTTP body should consist of JSON similar to the following sample.

Each attribute type/value will be validated to ensure that the data is valid. See the section on errors for how errors are represented.

As this method is accessed via a POST request the raw body must be set to JSON as described below.

```
{
    "route_release_id": 31,
    "media_owner": [
        2,
        4
    ],
    "frame_type": [
        1
    ],
    "dimension": [],
    "environment": [
        1
    ],
    "illumination": [],
    "tv_area": [],
    "region": [],
    "conurbation": [],
    "vehicle_creative": [],
    "space_format_id": [],
    "town": [],
    "postal_sector": [
        "SE20 8",
        "RM 7 0"
    ],
    "respondent_postal_district": [
        "W  9"
    ]
}
```

The table below details the fields used in this example. See [POST codebook/frame](https://docs-route.mediatelapi.co.uk/api/documentation/codebook-frame-post) for environments and allowable attributes and associated values.

| parameter | type | description |
|----|----|----|
| route_release_id | int (required) | Specify Route release data |
| media_owner | array (optional) | Media Owner ID's to restrict results to |
| frame_type | array (optional) | Frame Type ID's to restrict results to |
| dimension | array (optional) | Dimension ID's to restrict results to |
| illumination | array (optional) | Illumination ID's to restrict results to |
| tv_area | array (optional) | TV Area ID's to restrict results to |
| region | array (optional) | Region ID's to restrict results to |
| conurbation | array (optional) | Conurbation ID's to restrict results to |
| vehicle_creative | array (optional) | Vehicle Creative ID's to restrict results to |
| space_format_id | array (optional) | SPACE Format ID's to restrict results to |
| town | array (optional) | Town ID's to restrict results to |
| postal_sector\* | array (optional) | Postal sectors (of frame locations) to restrict results to |
| respondent_postal_sector\* (pre-R28) or respondent_postal_district\* (R28 onwards) | array (optional) | Postal districts/sectors (where respondents reside) to restrict results to.   At least one other frame attribute is required when using this option |

\*Postal districts/sectors must be formatted as 4 (for districts) or 6 (for sectors) character strings (2 bytes per area code, 2 bytes per district code and 2 bytes per sector), using spaces for padding e.g. `"E  1"` `"NW 1"` `"NW10 8"` `"NW 6 6"` `"W 10 4"` `"W  3 6"`

If accessing **POST https://route.mediatelapi.co.uk/rest/framesearch** with the body set to the sample JSON above then the following JSON would be returned:

```
{
    "frames_matched": [
        1234772178,
        1235115861
    ],
    "processed_datetime": "2016-11-16 09:41:00"
}
```

* **frames_matched** - array - frame identifiers matching the search criteria
* **processed_datetime** - string - date and time of processing

## POST framedata

A lookup call to get all frame attributes for an array of frames.

When accessed via a POST request this API method will return all available frame attributes for the list of frames passed for up to 10,000 frames. Your HTTP body should consist of JSON similar to the following sample.

The input will be validated to ensure that the format is valid. See the section on errors for how errors are represented

As this method is accessed via a POST request the raw body must be set to JSON as described below.

```
{
    "route_release_id": 30,
    "frames": [
        1234717080,
        1234717081,
        1234567890
    ]
}
```

The table below details the fields used in this example.

| parameter | type | description |
|----|----|----|
| route_release_id | int (required) | Specify Route release data |
| frames | array (required) | Specify list of frame identifiers |

If accessing **POST https://route.mediatelapi.co.uk/rest/framedata** with the body set to the sample JSON above then the following JSON would be returned:

```
{
    "route_release_id": 31,
    "frame_exceptions": [
        1234567890
    ],
    "frame_data": [{
            "frame_id": 1234717080,
            "media_owner": 12,
            "environment": 14,
            "dimension": 1,
            "frame_type": 1,
            "illumination": 1,
            "faces": 1,
            "longitude": -0.13245,
            "latitude": 51.52676,
            "coordinate_type": 2,
            "region": 9,
            "tv_area": 4,
            "town": 575,
            "conurbation": 9,
            "postal_sector": "NW 1 2",
            "address": "Victoria Line",
            "sales_code": "TCP",
            "surface_area": 0.13,
            "width": 0.56,
            "height": 0.24,
            "vehicle_creative": 0,
            "depot_id": "",
            "panel_azimuth": 0.0,
            "space_format_id": 21
        },
        {
            "frame_id": 1234717081,
            "media_owner": 12,
            "environment": 14,
            "dimension": 1,
            "frame_type": 1,
            "illumination": 1,
            "faces": 1,
            "longitude": -0.13245,
            "latitude": 51.52676,
            "coordinate_type": 2,
            "region": 9,
            "tv_area": 4,
            "town": 575,
            "conurbation": 9,
            "postal_sector": "NW 1 2",
            "address": "Victoria Line",
            "sales_code": "TCP",
            "surface_area": 0.13,
            "width": 0.56,
            "height": 0.24,
            "vehicle_creative": 0,
            "depot_id": "",
            "panel_azimuth": 0.0,
            "space_format_id": 21
        }
    ],
    "total_processing_time": 3,
    "processed_datetime": "2019-06-10 15:25:47"
}
```

* **route_release_id** - int - the route release ID
* **frame_exceptions** - array - array of frame identifiers that could not be processed
* A "frame_data" element that contains an array of frame attributes defined as follows:
* **frame_id** - int - individual frame identifier
  * **media_owner** - int - id of media owner, values available via /codebook/frame
  * **environment** - int - id of environment, values available via /codebook/frame
  * **dimension** - int - id of frame dimension, values available via /codebook/frame
  * **frame_type** - int - id of frame type, values available via /codebook/frame
  * **illumination** - int - id of illumination type, values available via /codebook/frame
  * **faces** - int - number of faces a frame has
  * **longitude** - signed floats - longitude co-ordinates of frame
  * **latitude** - signed floats - latitude co-ordinates of frame
  * **coordinate_type** - int - frame co-ordinate
  * **region** - int - id of region, values available via /codebook/frame
  * **tv_area** - int - id of TV area, values available via /codebook/frame
  * **town** - int - id of town, values available via /codebook/frame
  * **conurbation** - int - id of conurbation, values available via /codebook/frame
  * **postal_sector** - string - postal sector of frame location (6 alphanumeric characters)
  * **address** - string - freetext field; for roadside this is the address of the poster. For other environments (such as train / tube stations, shopping centres, airports) this is the location address. For buses this will be the depot address.
  * **sales_code** - string - 3 digit code used by media owners
  * **surface_area** - float - used as comparison with width\*height to identify irregular frame shapes
  * **width** - float - width of frame
  * **height** - float - height of frame
  * **vehicle_creative** - int - id of position of vehicle creative, values available via /codebook/frame
  * **depot_id** - string - freetext field for bus exterior frames
  * **panel_azimuth** - float - the angle of the frame for roadside frames
  * **space_format_id** - int - id of SPACE format, values available via /codebook/frame
* **total_processing_time** - int - processing time in ms
* **processed_datetime** - string - date and time of processing

## POST demographics

A lookup call to get all available demographics, including their description, sample size and population.

When accessed via a POST request this API method will return a list of all demographics.

Although this method is accessed via a POST request there is no HTTP body. The following URL options can be specified.

| parameter | type | description |
|----|----|----|
| /release/ | int (optional) | a route release version to restrict results to eg /demographics/release/20 |

If accessing **POST https://route.mediatelapi.co.uk/rest/demographics** the following JSON would be returned:

```
{
    "route_release_id": 34,
    "default_demographic_id": 1,
    "demographics": [{
            "demographic_id": 1,
            "description": "All Adults 15+",
            "expression": "ageband>=1",
            "sample_size": 21994,
            "population": "53045.3510597589"
        },
        {
            "demographic_id": 2,
            "description": "Men 15+",
            "expression": "ageband>=1 and sex=1",
            "sample_size": 10551,
            "population": "25987.9789980031"
        },
        ...
    ],
    "granularity_audiences": [{
            "granular_audience_id": 1,
            "description": "All Adults"
        },
        {
            "granular_audience_id": 10,
            "description": "Males"
        },
        ...
    ],
    "processed_datetime": "2020-04-15 10:41:56"
}
```

* **route_release_id** - int - the route release ID
* **default_demographic_id** - int - default demographic used when one isn't specified
* A "demographics" element that contains an array of demographics defined as follows:
* **demographic_id** - int - the unique identifier to reference the demographic
  * **description** - string - a text description of the demographic
  * **sample_size** - int - the sample size
  * **population** - float - the population
* A "granularity_audiences" element that contains an array of granularity audiences defined as follows:
* **granular_audience_id** - int - the unique identifier to reference the granularity audience
  * **description** - string - a text description of the granularity audience
* **processed_datetime** - string - date and time of processing

## POST codebook/questionnaire

A lookup call to get all available demographic options, including their value and description.

When accessed via a POST request this API method will return a list of all demographic options. Included in the options are Acorn categories, groups and types all of which can be used in demographic queries.

Although this method is accessed via a POST request there is no HTTP body. The following URL options can be specified.

| parameter | type | description |
|----|----|----|
| /{id} | int (optional) | a route release version to restrict results to eg /codebook/questionnaire/20 |

If accessing **POST https://route.mediatelapi.co.uk/rest/codebook/questionnaire** the following JSON would be returned (the sample here has results restricted ):

```
{
    "route_release_id": 21,
    "questionnaire": {
        "social_grade": {
            "wording": "SOCIAL GRADE",
            "mandatory": true,
            "answers": {
                "1": "A",
                "2": "B",
                "3": "C1",
                "4": "C2",
                "5": "D",
                "6": "E"
            }
        }
    },
    "processed_datetime": "2016-11-16 09:41:00"
}
```

* **route_release_id** - int - the route release ID
* A "questionnaire" element that contains an object of demographic options defined as follows:
* **wording** - string - description of the demographic option
  * **mandatory** - boolean - whether this is required by the codebook
  * **answers** - object - key/value pairs of available options for this demographic
* **processed_datetime** - string - date and time of processing

## POST codebook/frame

A lookup call to get all available frame attributes, including their key and description.

When accessed via a POST request this API method will return a list of all frame attributes.

Please note that the following Environments have been depreciated but still appear in the Route data definitions:

* 4 Rail (Rail stations and train interior) was removed in release 2
* 5 Underground (Tube stations and tube car interior) was removed in release 2
* 6 Airport (Inventory in and around an Airport) was removed in release 2
* 8 Retail Open (Supermarket car parks, pedestrian shopping precincts, retail park exterior) was removed in release 14

Although this method is accessed via a POST request there is no HTTP body. The following URL options can be specified.

| parameter | type | description |
|----|----|----|
| /{id} | int (optional) | a route release version to restrict results to eg /codebook/frame/20 |

If accessing **POST https://route.mediatelapi.co.uk/rest/codebook/frame** the following JSON would be returned (the sample here has results restricted to a maximum of 2 records per frame attribute):

```
{
    "route_release_id": 31,
    "frame_attributes": {
        "vehicle_creative": {
            "1": "Front",
            "2": "Taxi (Taxi exteriors)"
        },
        "environment": {
            "1": "Roadside (Inventory with a vehicular audience)",
            "2": "Taxi (Taxi exteriors)"
        },
        "illumination": {
            "1": "Not Illuminated",
            "2": "Illuminated (front)"
        },
        "town": {
            "1": "Abbey Wood",
            "2": "Aberdeen"
        },
        "media_owner": {
            "1": "Adrenalin Advertising",
            "2": "Clear Channel Outdoor"
        },
        "conurbation": {
            "1": "Birkenhead",
            "2": "Bournemouth/Poole"
        },
        "frame_type": {
            "1": "Static",
            "2": "Rotating/Scrolling"
        },
        "region": {
            "1": "Government Office Region - North East",
            "2": "Government Office Region - North West"
        },
        "dimension": {
            "1": "Tube car frame",
            "2": "Digital escalator frame"
        },
        "tv_area": {
            "1": "Border",
            "2": "Central Scotland"
        },
        "space_format_id": {
            "1": "12 Sheets",
            "2": "16 Sheets"
        }
    },
    "processed_datetime": "2016-11-16 09:41:00"
}
```

* **route_release_id** - int - the route release ID
* A "frame_attributes" element that contains an object of attributes with each attribute containing a key/value pair for lookup information
* **processed_datetime** - string - date and time of processing