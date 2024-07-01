import os
"""https://www.freeformatter.com/xml-to-json-converter.html#before-output
this is the website to text converting XML to JSON"""

#############################################################################
# change this folder later to be the 'Source Code' folder
OS_ROOT_FOLDER = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))


RHINO_TOOLBAR_FOLDER = os.path.join(OS_ROOT_FOLDER, "Apps", "_rhino")
DIST_RUI = RHINO_TOOLBAR_FOLDER + "\\EnneadTab_For_Rhino.rui"


INSTALLATION_FOLDER = os.path.join(OS_ROOT_FOLDER, "Installation")
INSTALLATION_RUI = INSTALLATION_FOLDER + "\\EnneadTab_For_Rhino_Installer.rui"


##############################################################################


"""
Things below are for local test only, not that important...
"""









# the special keysare are key names in rui that want to be make a dedicated sub element
SPECIAL_KEYS = ["locale_1033", 
                "bitmap", 
                "script", 
                "macro_id", 
                "left_macro_id", 
                "right_macro_id", 
                "tool_bar_id"]


# specail list are directly pass to parent tree without creating new sub tree
SPECIAL_LIST_KEY = "special_list"

# Sample JSON data
SAMPLE_JSON_DATA_SIMPLE = {
    "@major_ver": "3",
    "@minor_ver": "0",
    "extend_rhino_menus": {
        "menu": {
            "@guid": "12345567790",
            "text": {
                
                "locale_1033": "Extend Rhino Menus"
            }
        }
    },
    "macros":[{"macro_item":{"@guid":"999",
                               "text":{"locale_1033":"ppp"}}},
                {"macro_item":{"@guid":"999",
                               "text":{"locale_1033":"ppp"}}}],

    "bitmaps": {
    "small_bitmap": {
      "@item_width": "16",
      "@item_height": "16",
      "bitmap_item": [
        {"bitmap_item":{
          "@guid": "329c4ab7-6a9e-4e1e-acd7-0a57500af57a",
          "@index": "0"
        }},
        {"bitmap_item":{
          "@guid": "c787ee68-7db1-4db1-977b-aaed9cbcfb88",
          "@index": "1"
        }}
      ],
      "bitmap": "iVBORSuQmCC"
    },
    "normal_bitmap": {
      "@item_width": "24",
      "@item_height": "24",
      "bitmap_item": [
        {"bitmap_item":{
          "@guid": "329c4ab7-6a9e-4e1e-acd7-0a57500af57a",
          "@index": "0"
        }},
        {"bitmap_item":{
          "@guid": "c787ee68-7db1-4db1-977b-aaed9cbcfb88",
          "@index": "1"
        }}
      ],
      "bitmap": "iVBORSuQmCC"
    },
    "large_bitmap": {
      "@item_width": "32",
      "@item_height": "32",
      "bitmap_item": [
        {"bitmap_item":{
          "@guid": "329c4ab7-6a9e-4e1e-acd7-0a57500af57a",
          "@index": "0"
        }},
        {"bitmap_item":{
          "@guid": "c787ee68-7db1-4db1-977b-aaed9cbcfb88",
          "@index": "1"
        }}
      ],
      "bitmap": "iVBORSuQmCC"
    }
  }
    
    
}
# print (type(SAMPLE_JSON_DATA_SIMPLE["Mymacros"]))

SAMPLE_JSON_DATA_REAL = {
  "@major_ver": "3",
  "@minor_ver": "0",
  "@guid": "e8584e56-dc7a-4646-8198-1d5d14e95f84",
  "@localize": "False",
  "@default_language_id": "1033",
  "@dpi_scale": "150",
  "extend_rhino_menus": {
    "menu": {
      "@guid": "d58ceae7-fdb0-4104-80da-274b94ad44a9",
      "text": {
        "locale_1033": "Extend Rhino Menus"
      }
    }
  },
  "menus": {
    "menu": {
      "@guid": "05035255-7d3d-4d20-b3d6-82044fdbc507",
      "text": {
        "locale_1033": "TestRui"
      },
      "menu_item": {
        "@guid": "1f5beacf-9ab7-4026-8a89-92ab659185ef",
        "text": {
          "locale_1033": "menu text"
        },
        "macro_id": "1b6e5543-3cb7-4f67-8e43-fd217c7865c7",
        "macro_lib_id": "e8584e56-dc7a-4646-8198-1d5d14e95f84"
      }
    }
  },
  "tool_bar_groups": {
    "tool_bar_group": {
      "@guid": "fb209b37-3a90-4551-8c5e-36d544b2b5f6",
      "@dock_bar_guid32": "00000000-0000-0000-0000-000000000000",
      "@dock_bar_guid64": "83ae5f77-b8e0-43b4-8f99-5e06e0d15940",
      "@active_tool_bar_group": "45b65783-f09e-459c-9297-6c832cddcf59",
      "@single_file": "False",
      "@hide_single_tab": "False",
      "@point_floating": "140,414",
      "text": {
        "locale_1033": "MyCollection"
      },
      "tool_bar_group_item": [
        {
          "@guid": "a3a20efb-ebed-471b-9c1e-8790863dfc50",
          "@major_version": "1",
          "@minor_version": "1",
          "text": {
            "locale_1033": "toolbar #1"
          },
          "tool_bar_id": "7230d392-94f4-493d-85f8-5d4e1fa70053"
        },
        {
          "@guid": "45b65783-f09e-459c-9297-6c832cddcf59",
          "@major_version": "1",
          "@minor_version": "1",
          "text": {
            "locale_1033": "tab#2"
          },
          "tool_bar_id": "f41de913-1654-4ebf-8289-537bbc694e9c"
        }
      ],
      "dock_bar_info": {
        "@dpi_scale": "150",
        "@dock_bar": "False",
        "@docking": "True",
        "@horz": "False",
        "@visible": "True",
        "@floating": "True",
        "@mru_float_style": "8192",
        "@bar_id": "59472",
        "@mru_width": "49150",
        "@point_pos": "-2,-2",
        "@float_point": "140,414",
        "@rect_mru_dock_pos": "0,0,0,0",
        "@dock_location_u": "59420",
        "@dock_location": "left",
        "@float_size": "444,87"
      }
    }
  },
  "tool_bars": [
    {
      "@guid": "7230d392-94f4-493d-85f8-5d4e1fa70053",
      "@bitmap_id": "c787ee68-7db1-4db1-977b-aaed9cbcfb88",
      "@item_display_style": "control_and_text",
      "text": {
        "locale_1033": "tab#1"
      },
      "tool_bar_item": {
        "@guid": "8272d84b-27c2-4efc-83cb-daed34185807",
        "text": {
          "locale_1033": "Toolbar item 00"
        },
        "left_macro_id": "f15302e0-b388-452e-aa50-791a080ae744",
        "right_macro_id": "dff201ae-0207-464b-a85a-5f57c4eb8040"
      }
    },
    {
      "@guid": "f41de913-1654-4ebf-8289-537bbc694e9c",
      "@bitmap_id": "f188d0a0-2cc0-497f-952e-2c65ef49075a",
      "@item_display_style": "control_and_text",
      "text": {
        "locale_1033": "tab#2"
      },
      "tool_bar_item": [
        {
          "@guid": "891b973b-f26f-4bc6-b5fc-eff025c4a485",
          "text": {
            "locale_1033": "Toolbar item"
          },
          "left_macro_id": "d8323222-0605-4714-b90b-f721acb6a0d8",
          "right_macro_id": "2eae6e58-4423-4b66-bf6a-97361af3790d"
        },
        {
          "@guid": "29ecbabe-e9f8-4d0f-b228-0f47649e4ab1",
          "@button_style": "spacer"
        },
        {
          "@guid": "e1d3a331-2ed0-4861-9e22-465b164607e7",
          "left_macro_id": "6ab3e813-dc2a-4997-8ec5-6bceb6ea6058",
          "right_macro_id": "35bff704-e92b-40dd-8b02-8ed3de09b15b"
        }
      ]
    }
  ],
  "macros": [
    {
      "@guid": "f15302e0-b388-452e-aa50-791a080ae744",
      "@bitmap_id": "329c4ab7-6a9e-4e1e-acd7-0a57500af57a",
      "text": {
        "locale_1033": "macro_name_test"
      },
      "tooltip": {
        "locale_1033": "tooltip text test"
      },
      "help_text": {
        "locale_1033": "help text test"
      },
      "button_text": {
        "locale_1033": "button_text_test"
      },
      "menu_text": {
        "locale_1033": "menu_text_test"
      },
      "script": "_show"
    },
    {
      "@guid": "dff201ae-0207-464b-a85a-5f57c4eb8040",
      "@bitmap_id": "becc5d5f-1946-42d1-8635-770f5ac60776",
      "text": {
        "locale_1033": "Macro(created by editing button)"
      },
      "tooltip": {
        "locale_1033": "tool text right(created by editing button)"
      },
      "help_text": {
        "locale_1033": "(created by editing button)"
      },
      "button_text": {
        "locale_1033": "button_text_test(created by editing button)"
      },
      "menu_text": {
        "locale_1033": "(created by editing button)"
      },
      "script": "_hide"
    },
    {
      "@guid": "d8323222-0605-4714-b90b-f721acb6a0d8",
      "@bitmap_id": "1fcd6f41-e3d0-472e-81fd-37a040d98508",
      "text": {
        "locale_1033": "tab_B_L"
      },
      "tooltip": {
        "locale_1033": "bt_B_left"
      },
      "help_text": {
        "locale_1033": []
      },
      "button_text": {
        "locale_1033": "buttonB"
      },
      "menu_text": {
        "locale_1033": []
      },
      "script": "_Purge"
    },
    {
      "@guid": "2eae6e58-4423-4b66-bf6a-97361af3790d",
      "@bitmap_id": "b9ccb67a-519e-4827-931a-5402055f7e66",
      "text": {
        "locale_1033": "tab_B_R"
      },
      "tooltip": {
        "locale_1033": "bt_B_right"
      },
      "help_text": {
        "locale_1033": []
      },
      "button_text": {
        "locale_1033": "buttonB"
      },
      "menu_text": {
        "locale_1033": []
      },
      "script": "_Move"
    },
    {
      "@guid": "6ab3e813-dc2a-4997-8ec5-6bceb6ea6058",
      "@bitmap_id": "81097c12-0c96-4162-a4fd-768211135fef",
      "text": {
        "locale_1033": "tab_D_L"
      },
      "tooltip": {
        "locale_1033": "bt_d_L"
      },
      "help_text": {
        "locale_1033": []
      },
      "button_text": {
        "locale_1033": "button D"
      },
      "menu_text": {
        "locale_1033": []
      },
      "script": "_show"
    },
    {
      "@guid": "35bff704-e92b-40dd-8b02-8ed3de09b15b",
      "@bitmap_id": "e6170681-050d-4e98-a759-d59655ef21f2",
      "text": {
        "locale_1033": "tab_D_R"
      },
      "tooltip": {
        "locale_1033": "bt_d_R"
      },
      "help_text": {
        "locale_1033": []
      },
      "button_text": {
        "locale_1033": "button D"
      },
      "menu_text": {
        "locale_1033": []
      },
      "script": "_show"
    },
    {
      "@guid": "1b6e5543-3cb7-4f67-8e43-fd217c7865c7",
      "@bitmap_id": "4ae80bb5-e41e-4cc3-a9e1-d40d25037607",
      "text": {
        "locale_1033": "menu"
      },
      "tooltip": {
        "locale_1033": []
      },
      "help_text": {
        "locale_1033": []
      },
      "button_text": {
        "locale_1033": []
      },
      "menu_text": {
        "locale_1033": "menu text"
      }
    }
  ],
  "bitmaps": {
    "small_bitmap": {
      "@item_width": "16",
      "@item_height": "16",
      "bitmap_item": [
        {
          "@guid": "329c4ab7-6a9e-4e1e-acd7-0a57500af57a",
          "@index": "0"
        },
        {
          "@guid": "c787ee68-7db1-4db1-977b-aaed9cbcfb88",
          "@index": "1"
        },
        {
          "@guid": "becc5d5f-1946-42d1-8635-770f5ac60776",
          "@index": "2"
        },
        {
          "@guid": "f188d0a0-2cc0-497f-952e-2c65ef49075a",
          "@index": "3"
        },
        {
          "@guid": "1fcd6f41-e3d0-472e-81fd-37a040d98508",
          "@index": "4"
        },
        {
          "@guid": "b9ccb67a-519e-4827-931a-5402055f7e66",
          "@index": "5"
        },
        {
          "@guid": "81097c12-0c96-4162-a4fd-768211135fef",
          "@index": "6"
        },
        {
          "@guid": "e6170681-050d-4e98-a759-d59655ef21f2",
          "@index": "7"
        },
        {
          "@guid": "4ae80bb5-e41e-4cc3-a9e1-d40d25037607",
          "@index": "8"
        }
      ],
      "bitmap": "iVBORw0KGgoAAAANSUhEUgAAABAAAACQCAYAAAABQ+u5AAAAAXNSR0IArs4c6QAAAARnQU1BAACx\njwv8YQUAAAAJcEhZcwAAFiUAABYlAUlSJPAAAAJDSURBVGhD7Ze/axRBFMfPFFoI1inEQg0WNkY7\nUVRI9mY3lx8W+Q/ExkoQEm2WECzS2aikSG53fuzpBuPdLQmoje39CXZ2iuDfMM5bEnPMm3V3WUQ8\n3sHnON5+58PMO3jMtlr8u26Es+jAfE656pUEoi0efLz/6YNaUA/Rc1QYIwzDqXQ1PS188czwigcy\nRDlUOCJpJ1eToHegAqUiL/4aM7HOffkUZVHhiMiXvvDVptn+lbedVEtfbtTaQcSEFzG+Fs/FF2Rb\nfusvDg5q9eB4BzFTtwRTWzrUU65coSAN0mnFFM9Wspec8VVXJge+ZCDvDZazTdPp38CZYyafCya2\n3izubfC2fIQWA/AVsejS/srQnFl4IItZMmuad938vgb0l/qzr+d2Z9BiwC7weX62F/SemI6vma3n\nQDOHS8N1c6Q7dh4JugFnpnmp6fiNyDsh6ew9Nkd6YeeRQCyI28JPPnN2sgPgXef9DvTEziPBITs8\nY45w0zQv78kx2XJ2txt0p+08EtTm5/nLugkkIAFAgskQOIdEHZxFB//7/WA++tf3A4/uB3Q/+Nv3\ng4uDjm5CZQHMA1e9kmB8HtjP/ihwzQM7Uygoel+wc4WConlg54oF+f+P3xfsXOkOxueBK1cosOeB\nKwPkgqrzwF4M5IKq88BeDKAjlM0DO48EZfPAziNB2Tyw80hQNg/sPBLUpbX95YduAglIAJCABAAJ\nSACQYDIEenRON4EEJABIQAKABCQASDAhgv2RbgIJSACQYAIEI/0LEybGHTpr3bEAAAAASUVORK5C\nYII="
    },
    "normal_bitmap": {
      "@item_width": "24",
      "@item_height": "24",
      "bitmap_item": [
        {
          "@guid": "329c4ab7-6a9e-4e1e-acd7-0a57500af57a",
          "@index": "0"
        },
        {
          "@guid": "c787ee68-7db1-4db1-977b-aaed9cbcfb88",
          "@index": "1"
        },
        {
          "@guid": "becc5d5f-1946-42d1-8635-770f5ac60776",
          "@index": "2"
        },
        {
          "@guid": "f188d0a0-2cc0-497f-952e-2c65ef49075a",
          "@index": "3"
        },
        {
          "@guid": "1fcd6f41-e3d0-472e-81fd-37a040d98508",
          "@index": "4"
        },
        {
          "@guid": "b9ccb67a-519e-4827-931a-5402055f7e66",
          "@index": "5"
        },
        {
          "@guid": "81097c12-0c96-4162-a4fd-768211135fef",
          "@index": "6"
        },
        {
          "@guid": "e6170681-050d-4e98-a759-d59655ef21f2",
          "@index": "7"
        },
        {
          "@guid": "4ae80bb5-e41e-4cc3-a9e1-d40d25037607",
          "@index": "8"
        }
      ],
      "bitmap": "iVBORw0KGgoAAAANSUhEUgAAABgAAADYCAYAAADxnyNMAAAAAXNSR0IArs4c6QAAAARnQU1BAACx\njwv8YQUAAAAJcEhZcwAAFiUAABYlAUlSJPAAAAHASURBVHhe7ddRSgMxFIVhV+AKfBI3I7hBX9Vn\nwWV0Ce5ABNcQzTAJ0/DbE9qbOh1P4INym+SvtUK9unr6SEPhMBIOI+Gww/P9S0XPVzjsMF38sy4n\nkC9qhQfyhXltJ1DQ/gqHoA3QHoRDcJbAEu1BOIxUHrSvsNfeZQSHkXAYCYczeksIna1wOJsOi7X+\nQA86W+EwEg4j4TDS181dGskByQHJAckByQHJAckBaQMB/LIUCYeRcBgJhx2Gf32fLj71H5BDwgP5\nolZ4IF+Y13YCBe2vcAjaAO1BOARnCSzRHoTDSOVB+wp77V1GcBgJh5FwOKO3hNDZCoez6bBY6w/0\noLMVDiPhMBIOI92+PaSR/nFg+TGl54uTAuUPjZ4v1hPIF7XCA/nCvLYTKGh/cXSA9pB1BZZoD+kO\nHKsG2lfYa3kZOd9PMMrBAL0lhM4WMjB/Mn9d6w/0oLPF3/6SI4wPPL5/ppEckByQHJAckByQHJAc\nkByQHJAckByQHJAckByQHJA2EEi76zSSA5IDkgOSA5IDkgOSA5IDkgOSA5IDkgOSA5IDkgPSFgKv\nuzSSA5IDkgOSA5IDkgOSA9KlB3bpG8ej9dLGSSpAAAAAAElFTkSuQmCC"
    },
    "large_bitmap": {
      "@item_width": "32",
      "@item_height": "32",
      "bitmap_item": [
        {
          "@guid": "329c4ab7-6a9e-4e1e-acd7-0a57500af57a",
          "@index": "0"
        },
        {
          "@guid": "c787ee68-7db1-4db1-977b-aaed9cbcfb88",
          "@index": "1"
        },
        {
          "@guid": "becc5d5f-1946-42d1-8635-770f5ac60776",
          "@index": "2"
        },
        {
          "@guid": "f188d0a0-2cc0-497f-952e-2c65ef49075a",
          "@index": "3"
        },
        {
          "@guid": "1fcd6f41-e3d0-472e-81fd-37a040d98508",
          "@index": "4"
        },
        {
          "@guid": "b9ccb67a-519e-4827-931a-5402055f7e66",
          "@index": "5"
        },
        {
          "@guid": "81097c12-0c96-4162-a4fd-768211135fef",
          "@index": "6"
        },
        {
          "@guid": "e6170681-050d-4e98-a759-d59655ef21f2",
          "@index": "7"
        },
        {
          "@guid": "4ae80bb5-e41e-4cc3-a9e1-d40d25037607",
          "@index": "8"
        }
      ],
      "bitmap": "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"
    }
  },
  "scripts": []
}