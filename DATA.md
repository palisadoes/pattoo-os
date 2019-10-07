# pattoo-os JSON Data Formatting

The `pattoo-os` JSON files look like this:

```json
{
   "agent_program" : "pattoo-os-passived",
   "agent_id" : "f95784520cdf96cdcc6125378d9d90f47db8caf6d31543f60d828a3182ccec0f",
   "timestamp" : 1570413300,
   "agent_hostname" : "swim",
   "devices" : {
      "swim" : {
         "timefixed" : {
            "system" : {
               "base_type" : null,
               "description" : "Operating System",
               "data" : [
                  [
                     null,
                     "Linux"
                  ]
               ]
            },
            "distribution" : {
               "description" : "Linux Distribution",
               "data" : [
                  [
                     null,
                     "Ubuntu 18.04 Bionic Beaver"
                  ]
               ],
               "base_type" : null
            },
            "release" : {
               "base_type" : null,
               "data" : [
                  [
                     null,
                     "4.15.0-65-generic"
                  ]
               ],
               "description" : "Kernel Version"
            },
            "version" : {
               "base_type" : null,
               "data" : [
                  [
                     null,
                     "#74-Ubuntu SMP Tue Sep 17 17:06:04 UTC 2019"
                  ]
               ],
               "description" : "Kernel Type"
            }
         },
         "timeseries" : {
            "network_bytes_sent" : {
               "base_type" : 64,
               "data" : [
                  [
                     "enp3s0f1",
                     0
                  ],
                  [
                     "lo",
                     26923324
                  ],
                  [
                     "wlp2s0",
                     461076329
                  ]
               ],
               "description" : "Bytes (Out)"
            },
            "cpu_count" : {
               "base_type" : 1,
               "data" : [
                  [
                     null,
                     8
                  ]
               ],
               "description" : "CPU Count"
            },
            "disk_usage_percent" : {
               "base_type" : 1,
               "data" : [
                  [
                     "/",
                     23.2
                  ],
                  [
                     "/boot/efi",
                     1.2
                  ],
                  [
                     "/data",
                     92
                  ]
               ],
               "description" : "Partition Utilization (%)"
            }
         }
      }
   }
}

```