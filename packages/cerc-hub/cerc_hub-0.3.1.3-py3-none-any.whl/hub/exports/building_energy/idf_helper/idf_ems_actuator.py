"""
EMS helpers for microclimate inputs
SPDX - License - Identifier: LGPL -3.0-or-later
Copyright © 2025 Concordia CERC group
Code contributors: Saeed Rayegan sr283100@gmail.com
"""

import hub.exports.building_energy.idf_helper as idf_cte
from hub.exports.building_energy.idf_helper.idf_base import IdfBase

class IdfEmsActuator(IdfBase):
  @staticmethod
  def add(cerc_idf, actuator_name, unique_name, type, control_type):
    """
        Add an EnergyManagementSystem:Actuator object to the IDF.

        An EMS actuator allows the EnergyPlus Energy Management System (EMS)
        to override or control specific simulation variables (e.g., thermostat setpoints, airflow rates, schedules).

        :param cerc_idf: The IDF exporter object where the actuator will be added.
        :param actuator_name: A unique name for the actuator (e.g., "SupplyAirFlow_Actuator").
        :param unique_name: The specific component or schedule to control
                            (e.g., a schedule name, a node name, or "*" for all).
        :param type: The type of component being controlled
                     (e.g., "Schedule:Compact", "Node", "Zone Temperature Control").
        :param control_type: The control variable of the component to override
                             (e.g., "Schedule Value", "Mass Flow Rate", "Temperature Setpoint").
    """
    file = cerc_idf.files['ems_actuator']
    cerc_idf.write_to_idf_format(file, idf_cte.EMS_Actuator)
    cerc_idf.write_to_idf_format(file, actuator_name, 'Name')
    cerc_idf.write_to_idf_format(file, unique_name, 'Actuated Component Unique Name')
    cerc_idf.write_to_idf_format(file, type, 'Actuated Component Type')
    cerc_idf.write_to_idf_format(file, control_type, 'Actuated Component Control Type',';')
