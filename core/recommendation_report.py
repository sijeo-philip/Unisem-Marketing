

def summarize_requirement(requirement):
    """
    Convert the structured customer requirement
    into human-readable requirement statements.
    """

    summary = []


    # =====================================================
    # APPLICATION
    # =====================================================

    application_name = (requirement.get("application", {}).get("name"))

    if application_name:
        summary.append(f"Application: {application_name}")


    # =====================================================
    # CONNECTIVITY
    # =====================================================

    connectivity = requirement["connectivity"]
    required_connectivity = []

    if connectivity["wifi_required"]:
        required_connectivity.append("Wi-Fi")


    if connectivity["ble_required"]:
        required_connectivity.append("Bluetooth LE")


    if connectivity["bluetooth_classic_required"]:

        required_connectivity.append("Bluetooth Classic")


    if required_connectivity:

        summary.append("Connectivity: "+" + ".join(required_connectivity))


    # =====================================================
    # WI-FI
    # =====================================================

    wifi = requirement["wifi"]
    if wifi["band_5ghz_required"]:
        summary.append("5 GHz Wi-Fi required")

    if wifi["wifi6_required"]:
        summary.append("Wi-Fi 6 required")

    if wifi["mimo_2x2_required"]:
        summary.append("2x2 MIMO required")

    if wifi["high_throughput_required"]:
        summary.append("High Wi-Fi throughput required")


    # =====================================================
    # ARCHITECTURE
    # =====================================================

    architecture = (requirement["architecture"]["preference"])
    if architecture == "embedded_mcu":
        summary.append("Embedded MCU architecture preferred")


    elif architecture == "host_based":
        summary.append("Host-based architecture preferred")


    # =====================================================
    # INTEGRATED MCU
    # =====================================================

    embedded = requirement["embedded_features"]
    if embedded["integrated_mcu_required"]:
        summary.append("Integrated MCU required")

    if embedded["adc_required"]:
        summary.append("ADC capability required")


    if embedded["capacitive_touch_required"]:
        summary.append("Capacitive-touch capability required")


    # =====================================================
    # BLUETOOTH AUDIO
    # =====================================================

    bluetooth = requirement["bluetooth"]

    if bluetooth["audio_required"]:
        summary.append("Bluetooth audio required")


    # =====================================================
    # PERIPHERAL INTERFACES
    # =====================================================

    interfaces = requirement["interfaces"]
    required_peripherals = []
    if interfaces["uart_required"]:
        required_peripherals.append("UART")


    if interfaces["spi_required"]:
        required_peripherals.append("SPI")
    if interfaces["i2c_required"]:
        required_peripherals.append("I2C")


    if interfaces["can_required"]:
        required_peripherals.append("CAN")
    if required_peripherals:
        summary.append("Required peripheral interfaces: "+", ".join(required_peripherals))


    # =====================================================
    # AVAILABLE HOST INTERFACES
    # =====================================================

    host_interfaces = []
    if interfaces["usb_available"] is True:
        host_interfaces.append("USB")

    if interfaces["sdio_available"] is True:
        host_interfaces.append("SDIO")

    if interfaces["pcie_available"] is True:
        host_interfaces.append("PCIe")

    if host_interfaces:
        summary.append("Available host interfaces: "+", ".join(host_interfaces))


    # =====================================================
    # TEMPERATURE
    # =====================================================

    environment = requirement["environment"]
    min_temp = environment["minimum_temperature_c"]

    max_temp = environment["maximum_temperature_c"]

    if (min_temp is not None and max_temp is not None):
        summary.append(f"Required operating temperature: {min_temp}°C to {max_temp}°C")


    elif min_temp is not None:
        summary.append(f"Required minimum operating temperature: {min_temp}°C")


    elif max_temp is not None:
        summary.append(f"Required maximum operating temperature: {max_temp}°C")


    # =====================================================
    # PREFERENCES
    # =====================================================

    preferences = requirement["preferences"]
    preferred = []
    if preferences["compact_size"]:
        preferred.append("compact size")

    if preferences["low_power"]:
        preferred.append("low power")

    if preferences["cost_optimized"]:
        preferred.append("cost optimization")

    if preferences["high_performance"]:
        preferred.append("high performance")

    if preferred:
        summary.append("Preferences: "+", ".join(preferred))

    return summary
    
    
def _build_module_card(result,module,role):
    """
    Convert one selection-engine result into a
    presentation-friendly module recommendation.
    """

    positioning = module.get("positioning",{})

    card = {

        "module_id": result["module_id"],
        "module_name": result["module_name"],
        "family": result["family"],
        "role": role,
        "status": result["status"],
        "headline": positioning.get("description"),
        "choose_when": module.get("choose_when" ),
        "why": list(result["passed_requirements"]),
        "preference_matches": list(result["preference_matches"]),
        "tradeoffs": list(result["preference_tradeoffs"]),
        "clarifications": list(result["clarifications"]),
        "hard_failures": list(result["hard_failures"]),
        "applications": list(module.get("applications", []))
    }
    return card
    
    
def build_recommendation_report(requirement,results,modules, max_alternatives=2):
    """
    Build the final recommendation structure that will
    eventually be consumed by the browser UI.
    """

    module_lookup = {module["id"]: module for module in modules }

    compatible = [result for result in results if result["status"] == "COMPATIBLE"]
    clarification = [result for result in results if result["status"] == "NEEDS_CLARIFICATION"]
    rejected = [result for result in results if result["status"] == "NOT_SUITABLE"]
    report = {
        "decision": None,
        "requirements": summarize_requirement(requirement),
        "primary": None,
        "alternatives": [],
        "needs_clarification": [],
        "rejected": [],
        "next_steps": [
            "Review the detailed module datasheet",
            "Proceed with technical evaluation",
            "Evaluate sample / EVK where appropriate",
            "Proceed to design-in support"
        ]
    }


    # =====================================================
    # CASE 1:
    # At least one fully compatible module
    # =====================================================

    if compatible:
        report["decision"] = "RECOMMEND"
        primary_result = compatible[0]
        primary_module = module_lookup[primary_result["module_id"]]
        report["primary"] = _build_module_card(primary_result,primary_module,"PRIMARY_RECOMMENDATION")

        # -------------------------------------------------
        # Compatible alternatives first
        # -------------------------------------------------
        alternative_results = compatible[1:1 + max_alternatives]
        for alternative in alternative_results:
            module = module_lookup[alternative["module_id"]]
            report["alternatives"].append(_build_module_card(alternative, module, "COMPATIBLE_ALTERNATIVE"))


        # -------------------------------------------------
        # If fewer compatible alternatives exist,
        # show provisional alternatives that require
        # technical confirmation.
        # -------------------------------------------------

        remaining_slots = ( max_alternatives - len(report["alternatives"]))
        if remaining_slots > 0:
            for candidate in clarification[:remaining_slots]:
                module = module_lookup[candidate["module_id"]]
                report["alternatives"].append(_build_module_card(candidate, module, "PROVISIONAL_ALTERNATIVE"))


    # =====================================================
    # CASE 2:
    # Nothing fully compatible, but potential candidates
    # exist pending clarification
    # =====================================================

    elif clarification:
        report["decision"] = "CONFIRM_BEFORE_RECOMMENDING"
        primary_result = clarification[0]

        primary_module = module_lookup[primary_result["module_id"]]
        report["primary"] = _build_module_card(primary_result, primary_module, "PROVISIONAL_PRIMARY")
        for candidate in clarification[1:1 + max_alternatives]:
            module = module_lookup[candidate["module_id"]]
            report["alternatives"].append(_build_module_card(candidate,module,"PROVISIONAL_ALTERNATIVE"))


    # =====================================================
    # CASE 3:
    # No suitable candidate
    # =====================================================

    else:
        report["decision"] = "NO_SUITABLE_MODULE"


    # =====================================================
    # Keep all clarification candidates available
    # for engineering / salesperson review
    # =====================================================

    for candidate in clarification:
        module = module_lookup[candidate["module_id"]]
        report["needs_clarification"].append(_build_module_card(candidate, module, "NEEDS_CLARIFICATION"))

    # =====================================================
    # Rejected products
    # =====================================================

    for candidate in rejected:
        module = module_lookup[candidate["module_id"]]
        report["rejected"].append(_build_module_card(candidate, module, "NOT_SUITABLE"))

    return report
    
    
def print_recommendation_report(report):
    """
    Human-readable console representation used during
    development and testing.
    """

    print()
    print("=" * 72)
    print("UNISEM MODULE RECOMMENDATION")
    print("=" * 72)
    print()


    # =====================================================
    # REQUIREMENTS
    # =====================================================

    print("CUSTOMER REQUIREMENT")
    print("--------------------")
    for item in report["requirements"]:
        print("•",item)
    print()


    # =====================================================
    # DECISION
    # =====================================================

    print("DECISION:",report["decision"])
    print()


    # =====================================================
    # PRIMARY
    # =====================================================

    primary = report["primary"]
    if primary:
        print("PRIMARY RECOMMENDATION")
        print("----------------------")
        print(primary["module_name"])

        if primary["headline"]:
            print(primary["headline"])
        print()
        if primary["choose_when"]:
            print("Portfolio positioning:")
            print(primary["choose_when"])
            print()

        if primary["why"]:
            print("Why this module:")
            for reason in primary["why"]:
                print("  PASS:", reason)
            print()

        if primary["preference_matches"]:
            print("Additional fit:")
            for reason in primary["preference_matches"]:
                print("  +", reason)
            print()

        if primary["tradeoffs"]:
            print("Considerations:")
            for item in primary["tradeoffs"]:
                print("  -", item)
            print()

        if primary["clarifications"]:
            print("Confirm before finalizing:")
            for question in primary["clarifications"]:
                print("  ?", question)
            print()
    else:
        print("No module can currently be recommended.")
        print()


    # =====================================================
    # ALTERNATIVES
    # =====================================================

    if report["alternatives"]:
        print("ALTERNATIVES")
        print("------------")
        for index, alternative in enumerate(report["alternatives"], start=1):
            print()
            print(f"{index}.", alternative["module_name"])
            print("   Status:",alternative["status"])

            if alternative["headline"]:
                print("  ", alternative["headline"])

            if alternative["tradeoffs"]:
                print("   Considerations:")

                for item in alternative["tradeoffs"]:
                    print("     -", item)

            if alternative["clarifications"]:
                print("   Needs confirmation:")

                for item in alternative["clarifications"]:
                    print("     ?", item)
        print()

    # =====================================================
    # NEXT STEPS
    # =====================================================

    print("NEXT STEPS")
    print("----------")
    for index, step in enumerate(report["next_steps"], start=1):
        print(f"{index}.", step)
        
    print()
    print("=" * 72)
    
    