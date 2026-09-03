

def _pass(result, message):
    """
    Record a successful satisfied mandatory requirement
    """
    result["passed_requirements"].append(message)
    
def _fail(result, message):
    """
    Record a hard requirement that the module cannot satisfy
    
    """
    result["hard_failures"].append(message)
    
    
def _clarify(result, message):
    """
    Record information that must be confirmed before
    making a final recommendation
    """
    result["clarifications"].append(message)
    
def _preference_match(result, points, message):
    """
    Add ranking points for a soft preference.
    Soft preferences never make a module incompatible
    """
    result["preference_score"] += points
    result["preference_notes"].append(message)
    
def _preference_mismatch(result, message):
    """
    Record a soft preference that was not matched.
    """
    result["preference_notes"].append(message)
    
def _preference_penalty(result, points, message):
    """
    Apply a small ranking penalty.
    This never makes a module technically incompatible
    It is used to favour the simplest module that
    satifies the customer's actual requirement.
    """
    
    result["preference_score"] -= points
    result["preference_notes"].append(message)
    
def _check_boolean_capability( result, required, module_value, pass_message, fail_message, unknown_message):
    """
    Evaluate a Boolen hard requirement.
    
    module_value:
        True -> capability supported
        False -> Capability explicitly unsupported
        None -> Capability not documented / unknown
    """
    if not required:
        return 
    
    if module_value is True:
        _pass( result, pass_message )
    elif module_value is False:
        _fail(result, fail_message)
    else:
        _clarify(result, unknown_message)

def _check_host_interface(
    result,
    required_interfaces,
    customer_interfaces,
    description
):
    """
    Determine whether at least one host interface required
    by the module is available on the customer's processor.

    Example:

        required_interfaces = ["PCIe"]

        customer_interfaces = {
            "pcie_available": True,
            "usb_available": True
        }
    """

    if not required_interfaces:

        _clarify(
            result,
            f"{description} interface is not documented "
            f"in the module database."
        )

        return

    interface_key_map = {

        "USB": "usb_available",

        "SDIO": "sdio_available",

        "PCIe": "pcie_available"
    }

    states = []

    readable_interfaces = []

    for interface in required_interfaces:

        readable_interfaces.append(interface)

        key = interface_key_map.get(interface)

        if key is None:
            continue

        value = customer_interfaces.get(key)

        states.append(value)

    # At least one valid interface exists

    if any(
        state is True
        for state in states
    ):

        _pass(
            result,
            f"{description} interface requirement satisfied "
            f"using {', '.join(readable_interfaces)}."
        )

        return

    # Every known possibility is explicitly unavailable

    if states and all(
        state is False
        for state in states
    ):

        _fail(
            result,
            f"{description} requires "
            f"{', '.join(readable_interfaces)}, "
            f"but the customer has confirmed it is unavailable."
        )

        return

    # Otherwise something remains unknown

    _clarify(
        result,
        f"Confirm whether the customer host supports "
        f"{', '.join(readable_interfaces)} "
        f"for {description}."
    )

def _check_peripheral_interface(result, required, module, interface):
    """
    Evaluate a required module peripheral interface.
    The first stage selector treates the interface explicitly 
    listed in the portfolio as the supported selection set.
    
    Detailed datasheets should still be checked during 
    DECISION-IN
    """
    
    if not required:
        return 
        
    interfaces = module.get("peripheral_interfaces")
    
    if interfaces is None:
        _clarify(result, f"{interface} support is not documented.")
        return 
    if interface in interfaces:
        _pass(result, f"{interfaces} interface is supported.")
    else:
        _fail(result, f"Customer requires {interface}, "
              f"but it is not listed as a supported "
              f"interface for this module." )
              
              


def evaluate_module(
    requirement,
    module
):
    """
    Evaluate one Unisem module against one customer
    requirement.

    Returns:

        COMPATIBLE
        NOT_SUITABLE
        NEEDS_CLARIFICATION
    """

    result = {

        "module_id": module["id"],

        "module_name": module["name"],
        
        "family": module["family"],
        
        "choose_when": module.get("choose_when"),

        "status": None,

        "passed_requirements": [],

        "hard_failures": [],

        "clarifications": [],

        "preference_score": 0,

        "preference_notes": []
    }

    # =====================================================
    # CUSTOMER REQUIREMENTS
    # =====================================================

    customer_connectivity = requirement[
        "connectivity"
    ]

    customer_wifi = requirement[
        "wifi"
    ]

    customer_bluetooth = requirement[
        "bluetooth"
    ]

    customer_interfaces = requirement[
        "interfaces"
    ]

    environment = requirement[
        "environment"
    ]

    preferences = requirement[
        "preferences"
    ]

    architecture_requirement = requirement[
        "architecture"
    ]


    # =====================================================
    # MODULE CAPABILITIES
    # =====================================================

    module_connectivity = module.get(
        "connectivity",
        {}
    )
    #print("Module Connectivity:", module_connectivity)
    module_wifi = module.get(
        "wifi",
        {}
    )
    #print("Module Wifi:", module_wifi)
    module_bluetooth = module.get(
        "bluetooth",
        {}
    )
    #print("Module Bluetooth:", module_bluetooth)
    module_architecture = module.get(
        "architecture",
        {}
    )
    #print("Module Architecture:",module_architecture)
    module_host_interfaces = module.get(
        "host_interfaces",
        {}
    )
    #print("Module Host Interface:", module_host_interfaces)

    # =====================================================
    # HARD CONSTRAINT:
    # Wi-Fi
    # =====================================================

    _check_boolean_capability(

        result,

        customer_connectivity[
            "wifi_required"
        ],

        module_connectivity.get(
            "wifi"
        ),

        "Wi-Fi capability is supported.",

        "Customer requires Wi-Fi, but the module "
        "does not provide Wi-Fi.",

        "Wi-Fi capability is not documented."
    )


    # =====================================================
    # HARD CONSTRAINT:
    # BLE
    # =====================================================

    _check_boolean_capability(

        result,

        customer_connectivity[
            "ble_required"
        ],

        module_connectivity.get(
            "ble"
        ),

        "Bluetooth LE capability is supported.",

        "Customer requires Bluetooth LE, but the module "
        "does not provide BLE.",

        "Bluetooth LE capability is not documented."
    )


    # =====================================================
    # HARD CONSTRAINT:
    # Bluetooth Classic
    # =====================================================

    _check_boolean_capability(

        result,

        customer_connectivity[
            "bluetooth_classic_required"
        ],

        module_connectivity.get(
            "bluetooth_classic"
        ),

        "Bluetooth Classic capability is supported.",

        "Customer requires Bluetooth Classic, but the "
        "module does not provide it.",

        "Bluetooth Classic capability is not documented."
    )


    # =====================================================
    # HARD CONSTRAINT:
    # 5 GHz
    # =====================================================

    if customer_wifi[
        "band_5ghz_required"
    ]:

        bands = module_wifi.get(
            "bands"
        )

        if bands is None:

            _clarify(
                result,
                "The module Wi-Fi bands are not documented."
            )

        elif "5GHz" in bands:

            _pass(
                result,
                "5 GHz Wi-Fi is supported."
            )

        else:

            _fail(
                result,
                "Customer requires 5 GHz Wi-Fi, "
                "but the module does not support it."
            )


    # =====================================================
    # HARD CONSTRAINT:
    # Wi-Fi 6
    # =====================================================

    if customer_wifi[
        "wifi6_required"
    ]:

        generation = module_wifi.get(
            "generation"
        )

        if generation is None:

            _clarify(
                result,
                "Wi-Fi generation is not documented."
            )

        elif generation >= 6:

            _pass(
                result,
                "Wi-Fi 6 requirement is satisfied."
            )

        else:

            _fail(
                result,
                "Customer requires Wi-Fi 6, "
                "but this module is an earlier Wi-Fi generation."
            )


    # =====================================================
    # HARD CONSTRAINT:
    # 2x2 MIMO
    # =====================================================

    if customer_wifi[
        "mimo_2x2_required"
    ]:

        mimo = module_wifi.get(
            "mimo"
        )

        if mimo is None:

            _clarify(
                result,
                "MIMO capability is not documented."
            )

        elif mimo in (
            "2x2",
            "2×2"
        ):

            _pass(
                result,
                "2x2 MIMO requirement is satisfied."
            )

        else:

            _fail(
                result,
                "Customer requires 2x2 MIMO, "
                "but the module does not provide 2x2 MIMO."
            )


    # =====================================================
    # HARD CONSTRAINT:
    # Host interface for Wi-Fi
    # =====================================================

    if (
        customer_connectivity[
            "wifi_required"
        ]
        and
        module_connectivity.get("wifi") is True
        and
        module_architecture.get(
            "type"
        ) == "host_based"
    ):

        _check_host_interface(

            result,

            module_host_interfaces.get(
                "wifi"
            ),

            customer_interfaces,

            "Wi-Fi"
        )


    # =====================================================
    # HARD CONSTRAINT:
    # Host interface for Bluetooth
    # =====================================================

    bluetooth_required = (

        customer_connectivity[
            "ble_required"
        ]

        or

        customer_connectivity[
            "bluetooth_classic_required"
        ]
    )
    
    module_has_requested_bluetooth = ( module_connectivity.get("ble") is True
                                     or module_connectivity.get("bluetooth_classic") is True)

    if (
        bluetooth_required
        and
        module_has_requested_bluetooth
        and
        module_architecture.get(
            "type"
        ) == "host_based"
    ):

        _check_host_interface(

            result,

            module_host_interfaces.get(
                "bluetooth"
            ),

            customer_interfaces,

            "Bluetooth"
        )


    # =====================================================
    # HARD CONSTRAINT:
    # Minimum operating temperature
    # =====================================================

    required_min_temperature = environment.get(
        "minimum_temperature_c"
    )

    module_temperature = module.get(
        "operating_temperature",
        {}
    )

    module_min_temperature = module_temperature.get(
        "minimum_c"
    )

    if required_min_temperature is not None:

        if module_min_temperature is None:

            _clarify(
                result,
                "Minimum module operating temperature "
                "is not documented."
            )

        elif module_min_temperature <= required_min_temperature:

            _pass(
                result,
                "Minimum operating-temperature "
                "requirement is satisfied."
            )

        else:

            _fail(
                result,
                f"Customer requires operation down to "
                f"{required_min_temperature}°C, "
                f"but the module is rated only down to "
                f"{module_min_temperature}°C."
            )


    # =====================================================
    # HARD CONSTRAINT:
    # Maximum operating temperature
    # =====================================================

    required_max_temperature = environment.get(
        "maximum_temperature_c"
    )

    module_max_temperature = module_temperature.get(
        "maximum_c"
    )

    if required_max_temperature is not None:

        if module_max_temperature is None:

            _clarify(
                result,
                "Maximum module operating temperature "
                "is not documented."
            )

        elif module_max_temperature >= required_max_temperature:

            _pass(
                result,
                "Maximum operating-temperature "
                "requirement is satisfied."
            )

        else:

            _fail(
                result,
                f"Customer requires operation up to "
                f"{required_max_temperature}°C, "
                f"but the module is rated only up to "
                f"{module_max_temperature}°C."
            )


    # =====================================================
    # SOFT PREFERENCE:
    # Architecture
    # =====================================================

    architecture_preference = architecture_requirement.get(
        "preference"
    )

    if architecture_preference is not None:

        module_type = module_architecture.get(
            "type"
        )

        if module_type == architecture_preference:

            _preference_match(
                result,
                10,
                "Preferred architecture matches."
            )

        else:

            _preference_mismatch(
                result,
                "Preferred architecture does not match."
            )


    # =====================================================
    # SOFT PREFERENCE:
    # High performance
    # =====================================================


    tags = set(module.get("positioning",{}).get("tags",[]))

    if preferences["high_performance"]:

        if "high_performance" in tags:

            _preference_match(result, 10, "High-performance preference matches.")
        else:
            _preference_mismatch(result, "Module is not positioned as a high-performance option.")

    if preferences["low_power"]:
        if "low_power" in tags:

            _preference_match(result, 5, "Low-power preference matches.")

        else:

            _preference_mismatch(result, "Low-power positioning is not explicitly stated.")


    if preferences["cost_optimized"]:

        if "cost_optimized" in tags:

            _preference_match(result, 5, "Cost-optimized positioning matches.")

        else:

            _preference_mismatch(result, "Cost-optimized positioning is not explicitly stated.")

    if preferences["compact_size"]:

        if "compact" in tags:

            _preference_match(result, 3, "Compact-module preference matches.")

        else:

            _preference_mismatch(result, "Compact positioning is not explicitly stated.")
    #======================================================
    # HARD CONSTRAINT:
    # Integrated MCU
    #======================================================
    if requirement["embedded_features"]["integrated_mcu_required"]:
        integrated_mcu = ( module.get("architecture", {}).get("integrated_mcu"))
        
        if integrated_mcu is True:
            _pass(result, "integrated MCU requirement is satisfied")
        elif integrated_mcu is False:
            _fail(result, "Customer requires an integrated MCU, but this is a host-based module.")
        else:
            _clarify(result, "Integrated MCU capability needs technical confirmation.")
            
    #=====================================================
    # HARD CONSTRAINT:
    # Peripheral Interfaces
    #====================================================
    _check_peripheral_interface(result, customer_interfaces["uart_required"], module, "UART")
    _check_peripheral_interface(result, customer_interfaces["spi_required"],  module, "SPI")
    _check_peripheral_interface(result, customer_interfaces["i2c_required"], module, "I2C")
    _check_peripheral_interface(result, customer_interfaces["can_required"], module, "CAN")
    
    # =====================================================
    # HARD CONSTRAINT:
    # ADC
    # =====================================================

    if requirement["embedded_features"]["adc_required"]:

        adc = (module.get("embedded_features",{}).get("adc"))


        if adc is True:

            _pass(result, "ADC requirement is satisfied.")

        elif adc is False:

            _fail(result, "Required ADC capability is not supported.")

        else:

            _clarify(result, "ADC capability is not documented for this module.")
            
    # =====================================================
    # HARD CONSTRAINT:
    # Capacitive touch
    # =====================================================

    if requirement["embedded_features"]["capacitive_touch_required"]:

        capacitive_touch = (module.get("embedded_features",{}).get("capacitive_touch"))


        if capacitive_touch is True:

            _pass(result, "Capacitive-touch requirement is satisfied.")

        elif capacitive_touch is False:

            _fail(result, "Required capacitive-touch capability is not supported.")

        else:

            _clarify(result, "Capacitive-touch capability is not documented for this module.")
    
    # =====================================================
    # HARD CONSTRAINT:
    # Bluetooth audio
    # =====================================================

    if customer_bluetooth["audio_required"]:

        audio = (module.get("embedded_features", {}).get("bluetooth_audio"))


        if audio is True:

            _pass(result, "Bluetooth audio requirement is satisfied.")

        elif audio is False:

            _fail(result, "Bluetooth audio requirement is not supported.")

        else:

            _clarify(result, "Bluetooth audio capability requires technical confirmation." )
            
            
    # =====================================================
    # SOFT HEURISTIC:
    # Prefer the minimum sufficient wireless capability
    # =====================================================

    customer_needs_wifi = (customer_connectivity["wifi_required"])
    customer_needs_ble = (customer_connectivity["ble_required"])
    customer_needs_classic = (customer_connectivity["bluetooth_classic_required"])
    module_has_wifi = (module_connectivity.get("wifi") is True)
    module_has_ble = (module_connectivity.get("ble") is True)
    module_has_classic = (module_connectivity.get("bluetooth_classic") is True)

    # -----------------------------------------------------
    # Customer doesn't need Wi-Fi but module contains it
    # -----------------------------------------------------

    if (not customer_needs_wifi and module_has_wifi):
        _preference_penalty(result, 2, "Module includes Wi-Fi although the customer does not require Wi-Fi.")

    # -----------------------------------------------------
    # Customer needs no Bluetooth capability
    # -----------------------------------------------------

    if (not customer_needs_ble and not customer_needs_classic and (module_has_ble or module_has_classic)):
        _preference_penalty(result, 2, "Module includes Bluetooth capability although the customer only requires Wi-Fi.")

    # -----------------------------------------------------
    # BLE required but Classic Bluetooth is unnecessary
    # -----------------------------------------------------

    elif (customer_needs_ble and not customer_needs_classic and module_has_classic):
        _preference_penalty(result, 1, "Module also includes Classic Bluetooth, which is not required.")
        
        
    # =====================================================
    # SOFT HEURISTIC:
    # Rich embedded peripherals
    # =====================================================

    adc_required = requirement["embedded_features"]["adc_required"]

    touch_required = requirement["embedded_features"]["capacitive_touch_required"]

    module_features = module.get("embedded_features", {})
    module_has_adc = (module_features.get("adc") is True)
    module_has_touch = (module_features.get("capacitive_touch") is True)

    if (not adc_required and not touch_required and (module_has_adc or module_has_touch)):
        _preference_penalty(result,1,"Module includes richer embedded peripherals that are not required by this  application.")
    # =====================================================
    # FINAL STATUS
    # =====================================================

    if result[
        "hard_failures"
    ]:

        result[
            "status"
        ] = "NOT_SUITABLE"

    elif result[
        "clarifications"
    ]:

        result[
            "status"
        ] = "NEEDS_CLARIFICATION"

    else:

        result[
            "status"
        ] = "COMPATIBLE"


    return result
    
    
def evaluate_portfolio(requirement,modules):
    """
    Evaluate every module in the Unisem portfolio
    and return the results ranked by suitability.
    """

    results = []


    for module in modules:

        result = evaluate_module(requirement, module)

        results.append(result)


    def ranking_key(result):

        status = result["status"]


        # ---------------------------------------------
        # Fully compatible modules come first.
        # ---------------------------------------------

        if status == "COMPATIBLE":

            return (0, -result["preference_score"], -len(result["passed_requirements"]))


        # ---------------------------------------------
        # Potential matches needing clarification
        # come next.
        # ---------------------------------------------

        if status == "NEEDS_CLARIFICATION":

            return (1, len(result["clarifications"]),-result["preference_score"])


        # ---------------------------------------------
        # Rejected modules come last.
        # Fewer hard failures rank above many failures
        # because they may still be useful alternatives.
        # ---------------------------------------------

        return (2,len(result["hard_failures"]),len(result["clarifications"]))


    results.sort(key=ranking_key)


    return results