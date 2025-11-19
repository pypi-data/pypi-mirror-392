"""
EMS helpers for microclimate inputs
SPDX - License - Identifier: LGPL -3.0-or-later
Copyright © 2025 Concordia CERC group
Code contributors: Saeed Rayegan sr283100@gmail.com
"""

import hub.exports.building_energy.idf_helper as idf_cte
from hub.exports.building_energy.idf_helper.idf_base import IdfBase

class IdfEmsProgramCallingManager(IdfBase):
  @staticmethod
  def add(cerc_idf, manager_name, calling_point, program_name):
    """
    Add an EnergyManagementSystem:ProgramCallingManager object to the IDF.

    A ProgramCallingManager schedules one or more EMS programs to run at a
    specified point in the EnergyPlus simulation loop.

    :param cerc_idf: The IDF exporter object where the manager will be added.
    :param manager_name: A unique name for the ProgramCallingManager
                         (e.g., "Update MC Temperature Each Hour").
    :param calling_point: The simulation calling point that triggers the program(s)
                          (e.g., "BeginZoneTimestepBeforeSetCurrentWeather").
    :param program_name: The name of the EMS program to call at the specified point
                         (e.g., "Update_MC_Temperature").
    """
    file = cerc_idf.files['ems_program_calling_manager']
    cerc_idf.write_to_idf_format(file, idf_cte.EMS_ProgramCallingManager)
    cerc_idf.write_to_idf_format(file, manager_name, 'Name')
    cerc_idf.write_to_idf_format(file, calling_point, 'EnergyPlus Model Calling Point')
    cerc_idf.write_to_idf_format(file, program_name, 'Actuated Component Control Type',';')
