

def create_empty_requirement():
    requirement = {
    #-----------------------------
    # Customer/Application
    #-----------------------------
    
    "application":{
        "name": None,
        "category": None, 
        "description": None
        },
        
    # ---------------------------
    # Required Wireless Function
    #----------------------------
    "connectivity": {
        "wifi_required": False,
        "ble_required": False,
        "bluetooth_classic_required": False
        },
    
    # ----------------------------
    # Wi-Fi Requirements
    #-----------------------------
    "wifi": {
        "required": False,
        "band_2_4ghz_required": False,
        "band_5ghz_required": False,
        "wifi6_required": False,
        "mimo_2x2_required": False,
        "high_throughput_required": False
        },
        
    # ----------------------------
    # Bluetooth Requirements
    # ----------------------------
    "bluetooth": {
        "ble_required": False,
        "classic_required": False,
        "audio_required": False,
        "latest_generation_preferred": False
        },
        
    # -----------------------------
    # Architecture
    # -----------------------------
    "architecture": {
        "preference": None
        },
        
    # ------------------------------
    # Host / peripheral interfaces
    # ------------------------------
    "interfaces": {
    
        # Host Interface availability is tri-state:
        # 
        # True = Confirmed available
        # False = Confirmed unavailable
        # None = Not Yet Known
        
        "usb_available": None,
        "sdio_available": None,
        "pcie_available": None,
        "uart_required": False,
        "spi_required": False,
        "i2c_required": False,
        "can_required": False
        },
        
    # -------------------------------
    # Embedded Application Needs
    # -------------------------------
    
    "embedded_features": {
        "integrated_mcu_required": False,
        "adc_required": False, 
        "capacitive_touch_required": False
        },
        
    # ---------------------------------
    # Environmental Requirements
    # ---------------------------------
    "environment": {
        "minimum_temperature_c": None,
        "maximum_temperature_c": None
        },
        
    # ----------------------------------
    # Ranking Preferences
    # ----------------------------------
    "preferences": {
        "compact_size": False,
        "low_power": False,
        "cost_optimized": False,
        "high_performance": False
    }
    
    }
    
    return requirement
    
 
  
  