example_sync = {
    "next_batch": "s72595_4483_1934",
    "presence": {
        "events": [
            {
                "sender": "@alice:example.com",
                "type": "m.presence",
                "content": {
                    "presence": "online"
                }
            }
        ]
    },
    "account_data": {
        "events": [
            {
                "type": "org.example.custom.config",
                "content": {
                    "custom_config_key": "custom_config_value"
                }
            }
        ]
    },
    "rooms": {
        "join": {
            "!726s6s6q:example.com": {
                "state": {
                    "events": [
                        {
                            "sender": "@alice:example.com",
                            "type": "m.room.member",
                            "state_key": "@alice:example.com",
                            "content": {
                                "membership": "join"
                            },
                            "origin_server_ts": 1417731086795,
                            "event_id": "$66697273743031:example.com"
                        }
                    ]
                },
                "timeline": {
                    "events": [
                        {
                            "sender": "@bob:example.com",
                            "type": "m.room.member",
                            "state_key": "@bob:example.com",
                            "content": {
                                "membership": "join"
                            },
                            "prev_content": {
                                "membership": "invite"
                            },
                            "origin_server_ts": 1417731086795,
                            "event_id": "$7365636s6r6432:example.com"
                        },
                        {
                            "sender": "@alice:example.com",
                            "type": "m.room.message",
                            "age": 124524,
                            "txn_id": "1234",
                            "content": {
                                "body": "I am a fish",
                                "msgtype": "m.text"
                            },
                            "origin_server_ts": 1417731086797,
                            "event_id": "$74686972643033:example.com"
                        }
                    ],
                    "limited": True,
                    "prev_batch": "t34-23535_0_0"
                },
                "ephemeral": {
                    "events": [
                        {
                            "type": "m.typing",
                            "content": {
                                "user_ids": [
                                    "@alice:example.com"
                                ]
                            }
                        }
                    ]
                },
                "account_data": {
                    "events": [
                        {
                            "type": "m.tag",
                            "content": {
                                "tags": {
                                    "work": {
                                        "order": 1
                                    }
                                }
                            }
                        },
                        {
                            "type": "org.example.custom.room.config",
                            "content": {
                                "custom_config_key": "custom_config_value"
                            }
                        }
                    ]
                }
            }
        },
        "invite": {
            "!696r7674:example.com": {
                "invite_state": {
                    "events": [
                        {
                            "sender": "@alice:example.com",
                            "type": "m.room.name",
                            "state_key": "",
                            "content": {
                                "name": "My Room Name"
                            }
                        },
                        {
                            "sender": "@alice:example.com",
                            "type": "m.room.member",
                            "state_key": "@bob:example.com",
                            "content": {
                                "membership": "invite"
                            }
                        }
                    ]
                }
            }
        },
        "leave": {}
    }
}

example_pl_event = {
    "age": 242352,
    "content": {
        "ban": 50,
        "events": {
            "m.room.name": 100,
            "m.room.power_levels": 100
        },
        "events_default": 0,
        "invite": 50,
        "kick": 50,
        "redact": 50,
        "state_default": 50,
        "users": {
            "@example:localhost": 100
        },
        "users_default": 0
    },
    "event_id": "$WLGTSEFSEF:localhost",
    "origin_server_ts": 1431961217939,
    "room_id": "!Cuyf34gef24t:localhost",
    "sender": "@example:localhost",
    "state_key": "",
    "type": "m.room.power_levels"
}

example_event_response = {
    "event_id": "YUwRidLecu"
}

example_key_upload_response = {
    "one_time_key_counts": {
        "curve25519": 10,
        "signed_curve25519": 20
    }
}

example_success_login_response = {
    "user_id": "@example:localhost",
    "access_token": "abc123",
    "home_server": "matrix.org",
    "device_id": "GHTYAJCE"
}

example_key_query_response = {
    "failures": {},
    "device_keys": {
        "@alice:example.com": {
            "JLAFKJWSCS": {
                "user_id": "@alice:example.com",
                "device_id": "JLAFKJWSCS",
                "algorithms": [
                    "m.olm.curve25519-aes-sha256",
                    "m.megolm.v1.aes-sha"
                ],
                "keys": {
                    "curve25519:JLAFKJWSCS": ("3C5BFWi2Y8MaVvjM8M22DBmh24PmgR0nPvJOIAr"
                                              "zgyI"),
                    "ed25519:JLAFKJWSCS": "VzJIYXQ85u19z2ZpEeLLVu8hUKTCE0VXYUn4IY4iFcA"
                },
                "signatures": {
                    "@alice:example.com": {
                        "ed25519:JLAFKJWSCS":
                        ("wux6Dhjtk7GYPMW54hnx0doVH0NvuUAFBleL5OW99jhbjIutufglAgrYAcu8"
                         "ueacgNyeSumvtzVIPZXgbB2BCg")
                    }
                },
                "unsigned": {
                    "device_display_name": "Alice'smobilephone"
                }
            }
        }
    }
}

example_claim_keys_response = {
    "failures": {},
    "one_time_keys": {
        "@alice:example.com": {
            "JLAFKJWSCS": {
                'signed_curve25519:AAAAAQ': {
                    'key': '9UOzQjF2j2Xf8mBIiMgruuCkuWtD0ea9kvx63mO92Ws',
                    'signatures': {
                        '@alice:example.com': {
                            'ed25519:JLAFKJWSCS': (
                                '6O+VYxN7mVcr/j66YdHASRrpW4ydC/0FcYmEWVAGIFzU4+yjzxxinhQD'
                                'l7InhhdGuXeQlk4/w/CyU76TY6wdBA'
                            )
                        }
                    }
                }
            }
        }
    }
}

example_room_key_event = {
    "sender": "@alice:example.com",
    "sender_device": "JLAFKJWSCS",
    "content": {
        "algorithm": "m.megolm.v1.aes-sha2",
        "room_id": "!test:example.com",
        "session_id": "AVCXMm6LZ+J/vyCcomXmE48mbD1IyKbUBUd3UOW0wHE",
        "session_key": (
            "AgAAAAAJS98WXiCc90wJ23H1ucZ+XFCv8pN8C5p/XojdA6l7PWlFwAV1fQXe7afrQMRL9BxeeF8M"
            "uNnpvGX0hGOWcW0e2LU3EzQ0j8+jhxrPkQHUOJ8387CjRSA9UTBDmw3y8xquy3cXvuGE5DSpFUU7"
            "J7Xh+Dli8XRaRDCbmPmMtSdPMwFQlzJui2fif78gnKJl5hOPJmw9SMim1AVHd1DltMBx4vB/3Kse"
            "G413GWJkw9T+G6y51bsNEKsSU23lnJz32u5XwgNY9qdFKxGA6WL1wZZS6/iGW4gfTU/Jk89aGSA8"
            "Aw")
    },
    "type": "m.room_key",
    "keys": {
        "ed25519": "4VjV3OhFUxWFAcO5YOaQVmTIn29JdRmtNh9iAxoyhkc",
    }
}

example_forwarded_room_key_event = {
    "content": {
        "algorithm": "m.megolm.v1.aes-sha2",
        "forwarding_curve25519_key_chain": [
            "hPQNcabIABgGnx3/ACv/jmMmiQHoeFfuLB17tzWp6Hw"
        ],
        "room_id": "!Cuyf34gef24t:localhost",
        "sender_claimed_ed25519_key": "aj40p+aw64yPIdsxoog8jhPu9i7l7NcFRecuOQblE3Y",
        "sender_key": "RF3s+E7RkTQTGF2d8Deol0FkQvgII2aJDf3/Jp5mxVU",
        "session_id": "iR4Q8LUXrtjwse7U80iALTZjcezHm0fI1UvXloTV0xs",
        "session_key":
        ("AQAAAADk1Ouk7LX6RuCsuHvtkD3/yvEDx4q4oXaK3sfPh03lUxNM3mXx6OHOH8kGFANHEVXQYr0OdYh"
         "UeFM6xNSididZ5jiFpSQ0rIftSl+z4RlmFZPbt3XkvS2/8Q0mDr70g4rSYMkqxdWQy9Vi2lj0sWfQNl"
         "QR92G0RwGsPNZdzYsBJokeEPC1F67Y8LHu1PNIgC02Y3Hsx5tHyNVL15aE1dMb")
    },
    "type": "m.room_key"
}

example_room_key_request_event = {
    "content": {
        "action": "request",
        "body": {
            "algorithm": "m.megolm.v1.aes-sha2",
            "room_id": "!Cuyf34gef24t:localhost",
            "sender_key": "RF3s+E7RkTQTGF2d8Deol0FkQvgII2aJDf3/Jp5mxVU",
            "session_id": "iR4Q8LUXrtjwse7U80iALTZjcezHm0fI1UvXloTV0xs"
        },
        "request_id": "1495474790150.19",
        "requesting_device_id": "RJYKSTBOIE"
    },
    "type": "m.room_key_request"
}

example_room_key_cancel_event = {
    "content": {
        "action": "cancel_request",
        "request_id": "1495474790150.19",
        "requesting_device_id": "RJYKSTBOIE"
    },
    "type": "m.room_key_request"
}
