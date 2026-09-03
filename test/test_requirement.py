from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(
    0,
    str(BASE_DIR)
)


from core.customer_requirement import create_empty_requirement

requirement = create_empty_requirement()

print()
print("CUSTOMER REQUIREMENT")
print("====================")
print()

print(
    "Wi-Fi Required:",
    requirement["connectivity"]["wifi_required"]
    )
    
print(
      "BLE Required:",
      requirement["connectivity"]["ble_required"]
      )
      
print(
      "Bluetooth Classic Required:",
      requirement["connectivity"]["bluetooth_classic_required"]
      )
      
print()

print(
      "Architecture:",
      requirement["architecture"]["preference"]
     )
     
print()

print(
        "PCIe Available:",
        requirement["interfaces"]["pcie_available"]
        )
        
print(
        "USB Available:",
        requirement["interfaces"]["usb_available"]
        )
        
        
print()

print()
print("SIMULATING CUSTOMER REQUIREMENT")
print("===============================")
print()

requirement["application"]["name"] = True
requirement["connectivity"]["wifi_required"] = True
requirement["connectivity"]["ble_required"] = True
requirement["connectivity"]["bluetooth_classic_required"] = True

requirement["wifi"]["required"] = True
requirement["wifi"]["band_2_4ghz_required"] = True
requirement["wifi"]["band_5ghz_required"] = True
requirement["wifi"]["wifi6_required"] = True
requirement["wifi"]["mimo_2x2_required"] = True
requirement["wifi"]["high_throughput_required"] = True

requirement["interfaces"]["pcie_available"] = True
requirement["interfaces"]["usb_available"] = True
requirement["preferences"]["high_performance"] = True

print(
    "Application:",
    requirement["application"]["name"]
)

print(
    "Wi-Fi:",
    requirement["connectivity"]["wifi_required"]
)

print(
    "BLE:",
    requirement["connectivity"]["ble_required"]
)

print(
    "Bluetooth Classic:",
    requirement["connectivity"]["bluetooth_classic_required"]
)

print(
    "5 GHz required:",
    requirement["wifi"]["band_5ghz_required"]
)

print(
    "Wi-Fi 6 required:",
    requirement["wifi"]["wifi6_required"]
)

print(
    "2x2 MIMO required:",
    requirement["wifi"]["mimo_2x2_required"]
)

print(
    "PCIe available:",
    requirement["interfaces"]["pcie_available"]
)

print(
    "USB available:",
    requirement["interfaces"]["usb_available"]
)
    