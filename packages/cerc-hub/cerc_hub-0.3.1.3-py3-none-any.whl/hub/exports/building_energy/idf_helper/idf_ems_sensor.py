"""
EMS helpers for microclimate inputs
SPDX - License - Identifier: LGPL -3.0-or-later
Copyright © 2025 Concordia CERC group
Code contributors: Saeed Rayegan sr283100@gmail.com
"""

import hub.exports.building_energy.idf_helper as idf_cte
from hub.exports.building_energy.idf_helper.idf_base import IdfBase

class IdfEmsSensor(IdfBase):
  @staticmethod
  def add(cerc_idf, sensor_name, key_name, variable_name):
    """
    Add an EnergyManagementSystem:Sensor object.

    :param cerc_idf: The IDF exporter object
    :param sensor_name: EMS sensor name (e.g. AvgBuildingTemp_Sensor)
    :param key_name: The key (e.g. schedule name, zone name, or * for all)
    :param variable_name: The Output:Variable or Meter name (e.g. Schedule Value)
    """
    file = cerc_idf.files['ems_sensor']
    cerc_idf.write_to_idf_format(file, idf_cte.EMS_Sensor)
    cerc_idf.write_to_idf_format(file, sensor_name, 'Name')
    cerc_idf.write_to_idf_format(file, key_name, 'Output:Variable or Output:Meter Index Key Name')
    cerc_idf.write_to_idf_format(file, variable_name, 'Output:Variable or Output:Meter Name', ';')