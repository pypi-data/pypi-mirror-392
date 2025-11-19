from bluer_sbc.README.designs import (
    adapter_bus,
    battery_bus,
    bryce,
    cheshmak,
    nafha,
    pwm_generator,
    regulated_bus,
    shelter,
    template,
    ultrasonic_sensor_tester,
)
from bluer_sbc.README.designs.swallow import docs as swallow
from bluer_sbc.README.designs.swallow_head import docs as swallow_head


docs = (
    adapter_bus.docs
    + battery_bus.docs
    + bryce.docs
    + cheshmak.docs
    + nafha.docs
    + pwm_generator.docs
    + regulated_bus.docs
    + shelter.docs
    + swallow_head.docs
    + swallow.docs
    + ultrasonic_sensor_tester.docs
    + template.docs
)
