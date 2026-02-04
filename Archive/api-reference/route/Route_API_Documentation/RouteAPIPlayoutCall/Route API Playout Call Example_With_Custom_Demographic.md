[POST] /rest/process/playout

{

  "route_release_id": 54,

  "route_algorithm_version": 10.2,

  "demographics": [

    {

      "demographic_id": 1

    },

    {

      "demographic_custom": "ageband>0 AND social_grade<=3"

    }

  ],

  "grouping": "frame_id",

  "target_month": 1,

  "default_spot_length": 10,

  "default_spot_break_length": 50,

  "campaign": [

    {

      "schedule": [

        {

          "datetime_from": "2025-05-01 00:00",

          "datetime_until": "2025-05-07 23:59"

        }

      ],

      "frames": [

        1234842296

      ]

    },

    {

      "schedule": [

        {

          "datetime_from": "2025-05-01 00:00",

          "datetime_until": "2025-05-01 23:59"

        }

      ],

      "spot_length": 15,

      "spot_break_length": 30,

      "frames": [

        2000287546

      ]

    }

  ]

}