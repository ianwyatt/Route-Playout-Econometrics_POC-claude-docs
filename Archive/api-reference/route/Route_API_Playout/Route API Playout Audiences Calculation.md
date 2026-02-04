### Route API Playout audiences Calculation
For the **Playout** data we only need to pass the "impacts" to the "algorithm_figures" parameter when using the playout endpoint:
https://route.mediatelapi.co.uk/rest/process/playout

`Post: https://route.mediatelapi.co.uk/rest/process/playout
`{`
 ` "route_release_id": 54,`
 ` "route_algorithm_version": 10.2,`
 ` "target_month": 1,`
 ` "campaign": [`
 `   {`
 `     "schedule": [`
 `       {`
 `         "datetime_from": "2025-06-01 00:00",`
 `         "datetime_until": "2025-06-01 00:14"`
 `       }`
 `     ],`
 `     "spot_length": 10,`
 `     "spot_break_length": 0,`
 `     "frames": [`
 `       2000287546`
 `     ]`
 `   }`
 ` ]`
`}`
This returns:
`{`
 ` "route_release_id": 54,`
 ` "route_release_revision": 1,`
 ` "route_algorithm_version": 10.2,`
 ` "results": [`
 `   {`
 `     "description": "total",`
 `     "demographic": "All Adults 15+ (1)",`
 `     "granular_audience": "All Adults (1)",`
 `     "target_month": 1,`
 `     "figures": {`
 `       "impacts": "0.1738974052",`
 `       "impacts_pedestrian": "0.0056352068",`
 `       "impacts_vehicular": "0.1682621984",`
 `       "rag_status": "red",`
 `       "playouts_total": "90",`
 `       "audience_spot_avg": "0.0019321934"`
 `     },`
 `     "metrics": {`
 `       "total_frames": 1,`
 `       "total_dynamic_frames": 1,`
 `       "total_contacts": 4,`
 `       "total_actual_contacts": 0,`
 `       "total_respondents": 4,`
 `       "total_actual_respondents": 0`
 `     }`
 `   }`
 ` ],`
 ` "total_processing_time": 14,`
 ` "processed_datetime": "2025-07-30 00:18:10"`
`}`

Time in the Route API are handled by rounding to the nearest 15 min so, the playout call is required to be able to get the Route audience for playouts that are measured in seconds:
`Times are measured in "dayparts" and will be rounded to the nearest quarter of an hour daypart (e.g. 10:07 will be handled as 10:00, 10:08 as 10:15).`

Playouts are defined in seconds and milliseconds, we don't have the option to specify those in Route, the audience is for a complete 15min, but we do have a playout API call that allow us to get the avg audience per playout.

To get the audience for a playout take the start & end time from playout e.g., for frameID 2000287546: `2025-06-01 00:00.14.946 to 2025-06-01 00:00.24.946`

Round these to the nearest second and get the total playout time, in this case 10 seconds.

This 10 second playout time is then used to pass to the Route API Playout endpoint as spot length = 10 and break length = 0 for example:

`{`
  `"route_release_id": 54,`
  `"route_algorithm_version": 10.2,`
  `"grouping": "frame_id",`
  `"target_month": 1,`
  `"campaign": [`
    `{`
      `"schedule": [`
        `{`
          `"datetime_from": "2025-06-01 00:00",`
          `"datetime_until": "2025-06-01 00:14"`
        `}`
      `],`
      `"spot_length": 10,`
      `"spot_break_length": 0,`
      `"frames": [`
        `1234842296`
      `]`
    `}`

  `]`
`}`

Playout records will include multiple playouts for each frame and multiple frames:

For example taking frames 2000312252 and 1234842296

Let's suppose they have the following playout records:

## **Example 1 - playouts - 2 frames**

| rowId | frameID    | startdate               | enddate                 |
| ----- | ---------- | ----------------------- | ----------------------- |
| 1     | 1234842296 | 2025-08-01 13:00.09.922 | 2025-08-01 13:00.14.922 |
| 2     | 1234842296 | 2025-08-01 13:00.14.946 | 2025-08-01 13:00.24.946 |
| 3     | 2000287546 | 2025-08-01 13:00.09.922 | 2025-08-01 13:00.14.922 |
| 4     | 2000287546 | 2025-08-01 13:00.14.946 | 2025-08-01 13:00.24.946 |
PlayoutTime = endate-startdate 

**Note round the start & end date to the nearest second**

frameID: 2000312252
row 1 PlayoutTime = 5 seconds
row 2 PlayoutTime = 10 seconds

frameID: 1234842296
row 3 PlayoutTime = 5 seconds
row 4 PlayoutTime = 10 seconds

Now from this we can use the playout time to call the Route API Playout endpoint passing playout time as the spot length and the break length as zero. As Route audiences are determined at a 15min level we can't pass multiple spot lengths within the same 15 minute so, we have to calculate the audience per spot for each break length per frame in a particular 15 minutes. 

For example:
In our above table records are in the same 15min period, but we have two different playout times (spot lengths), thus we need to make two calls to the API to get the audience per spot for each frame. The actual audience for the playout will be equal to avg_spot_audience in the API output.

#### Calls for this example:

##### 5 second spot length (5 second playout time)

Body:

```
{
  "route_release_id": 54,
  "route_algorithm_version": 10.2,
  "grouping": "frame_id",
  "target_month": 1,
  "campaign": [
    {
      "schedule": [
        {
          "datetime_from": "2025-08-01 13:00",
          "datetime_until": "2025-08-01 13:14"
        }
      ],
      "spot_length": 5,
      "spot_break_length": 0,
      "frames": [
        1234842296
      ]
    },
    {
      "spot_length": 5,
      "spot_break_length": 0,
      "schedule": [
        {
          "datetime_from": "2025-08-01 13:00",
          "datetime_until": "2025-08-01 13:14"
        }
      ],
      "frames": [
        2000287546
      ]
    }
  ]
}
```

Response:
 ```
 {
  "route_release_id": 54,
  "route_release_revision": 1,
  "route_algorithm_version": 10.2,
  "results": [
    {
      "description": "total",
      "demographic": "All Adults 15+ (1)",
      "granular_audience": "All Adults (1)",
      "target_month": 1,
      "figures": {
        "impacts": "1.8719887943",
        "impacts_pedestrian": "1.3084970705",
        "impacts_vehicular": "0.5634917238",
        "rag_status": "red",
        "playouts_total": "360",
        "audience_spot_avg": "0.0051999689"
      },
      "metrics": {
        "total_frames": 2,
        "total_dynamic_frames": 2,
        "total_contacts": 55,
        "total_actual_contacts": 49,
        "total_respondents": 15,
        "total_actual_respondents": 9
      }
    },
    {
      "description": "grouping",
      "demographic": "All Adults 15+ (1)",
      "granular_audience": "All Adults (1)",
      "target_month": 1,
      "frame_id": "1234842296",
      "figures": {
        "impacts": "1.2431835489",
        "impacts_pedestrian": "1.2431835489",
        "impacts_vehicular": "0",
        "rag_status": "red",
        "playouts_total": "180",
        "audience_spot_avg": "0.0069065753"
      },
      "metrics": {
        "total_frames": 1,
        "total_dynamic_frames": 1,
        "total_contacts": 50,
        "total_actual_contacts": 47,
        "total_respondents": 11,
        "total_actual_respondents": 8
      }
    },
    {
      "description": "grouping",
      "demographic": "All Adults 15+ (1)",
      "granular_audience": "All Adults (1)",
      "target_month": 1,
      "frame_id": "2000287546",
      "figures": {
        "impacts": "0.6288052453",
        "impacts_pedestrian": "0.0653135215",
        "impacts_vehicular": "0.5634917238",
        "rag_status": "red",
        "playouts_total": "180",
        "audience_spot_avg": "0.0034933625"
      },
      "metrics": {
        "total_frames": 1,
        "total_dynamic_frames": 1,
        "total_contacts": 5,
        "total_actual_contacts": 2,
        "total_respondents": 4,
        "total_actual_respondents": 1
      }
    }
  ],
  "total_processing_time": 34,
  "processed_datetime": "2025-08-29 20:31:34"
}
 ```
##### 10 second spot length (5 second playout time)

Body:
```
{
  "route_release_id": 54,
  "route_algorithm_version": 10.2,
  "grouping": "frame_id",
  "target_month": 1,
  "campaign": [
    {
      "schedule": [
        {
          "datetime_from": "2025-08-01 13:00",
          "datetime_until": "2025-08-01 13:14"
        }
      ],
      "spot_length": 10,
      "spot_break_length": 0,
      "frames": [
        1234842296
      ]
    },
    {
      "spot_length": 10,
      "spot_break_length": 0,
      "schedule": [
        {
          "datetime_from": "2025-08-01 13:00",
          "datetime_until": "2025-08-01 13:14"
        }
      ],
      "frames": [
        2000287546
      ]
    }
  ]
}
```

Response:
```
{
  "route_release_id": 54,
  "route_release_revision": 1,
  "route_algorithm_version": 10.2,
  "results": [
    {
      "description": "total",
      "demographic": "All Adults 15+ (1)",
      "granular_audience": "All Adults (1)",
      "target_month": 1,
      "figures": {
        "impacts": "1.3828172535",
        "impacts_pedestrian": "0.8796510976",
        "impacts_vehicular": "0.5031661558",
        "rag_status": "red",
        "playouts_total": "180",
        "audience_spot_avg": "0.0076823181"
      },
      "metrics": {
        "total_frames": 2,
        "total_dynamic_frames": 2,
        "total_contacts": 55,
        "total_actual_contacts": 49,
        "total_respondents": 15,
        "total_actual_respondents": 9
      }
    },
    {
      "description": "grouping",
      "demographic": "All Adults 15+ (1)",
      "granular_audience": "All Adults (1)",
      "target_month": 1,
      "frame_id": "1234842296",
      "figures": {
        "impacts": "0.8211053898",
        "impacts_pedestrian": "0.8211053898",
        "impacts_vehicular": "0",
        "rag_status": "red",
        "playouts_total": "90",
        "audience_spot_avg": "0.0091233932"
      },
      "metrics": {
        "total_frames": 1,
        "total_dynamic_frames": 1,
        "total_contacts": 50,
        "total_actual_contacts": 47,
        "total_respondents": 11,
        "total_actual_respondents": 8
      }
    },
    {
      "description": "grouping",
      "demographic": "All Adults 15+ (1)",
      "granular_audience": "All Adults (1)",
      "target_month": 1,
      "frame_id": "2000287546",
      "figures": {
        "impacts": "0.5617118636",
        "impacts_pedestrian": "0.0585457078",
        "impacts_vehicular": "0.5031661558",
        "rag_status": "red",
        "playouts_total": "90",
        "audience_spot_avg": "0.0062412429"
      },
      "metrics": {
        "total_frames": 1,
        "total_dynamic_frames": 1,
        "total_contacts": 5,
        "total_actual_contacts": 2,
        "total_respondents": 4,
        "total_actual_respondents": 1
      }
    }
  ],
  "total_processing_time": 54,
  "processed_datetime": "2025-08-29 20:32:15"
}
```

From the two responses we can apply the audience_spot_avg to the data in our table in a column called 'routeimpacts'

In the JSON response we need to lookup audience_spot_avg for each individual frame and assign it as routeimpacts in the table.

**NOTE the route impacts are in 1000s, so audience_spot_avg (0.0069065753) x 1000  becomes 6.9065753 impacts

| rowId | frameID    | startdate               | enddate                 | routeimpacts | spotlength |
| ----- | ---------- | ----------------------- | ----------------------- | ------------ | ---------- |
| 1     | 1234842296 | 2025-08-01 13:00.09.922 | 2025-08-01 13:00.14.922 | 6.9065753    | 5          |
| 2     | 1234842296 | 2025-08-01 13:00.14.946 | 2025-08-01 13:00.24.946 | 9.1233932    | 10         |
| 3     | 2000287546 | 2025-08-01 13:00.09.922 | 2025-08-01 13:00.14.922 | 3.4933625    | 5          |
| 4     | 2000287546 | 2025-08-01 13:00.14.946 | 2025-08-01 13:00.24.946 | 9.1233932    | 10         |

We can then sum the route_impacts column to get the total audience (impacts), in this case 28.6467242, or 29 impacts to the nearest whole impact.