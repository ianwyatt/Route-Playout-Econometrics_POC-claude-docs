{
  "route_release_id": 55,
  "route_algorithm_version": 10.2,
  "option_split_reach": true,
   "grouping": "frame_id",
    "demographics": [
    {
      "demographic_custom": "Social_grade=1 or social_grade=2"
    },
    {
      "demographic_custom": "ageband>0 AND social_grade<=3"
    }
  ],
  "algorithm_figures": [
    "impacts",
    "reach"
  ],
  "campaign": [
    {
      "schedule": [
        {
          "datetime_from": "2025-06-01 00:00",
          "datetime_until": "2025-06-01 00:15"
        }
      ],
      "frames": [
        2000312252,
        2000287546
      ],
      "spot_length": 5,
      "spot_break_length": 15
    },
    {
      "schedule": [
        {
          "datetime_from": "2025-06-01 00:00",
          "datetime_until": "2025-06-01 00:30"
        }
      ],
      "frames": [
        1234842296
      ],
      "spot_length": 10,
      "spot_break_length": 46
    },
    {
      "schedule": [
        {
          "datetime_from": "2025-06-01 00:15",
          "datetime_until": "2025-06-01 00:30"
        }
      ],
      "frames": [
        2000312252
      ],
      "spot_length": 5,
      "spot_break_length": 29
    },
        {
      "schedule": [
        {
          "datetime_from": "2025-06-01 00:15",
          "datetime_until": "2025-06-01 00:30"
        }
      ],
      "frames": [       
        2000287546
      ],
      "spot_length": 5,
      "spot_break_length": 32
    }
  ]
}