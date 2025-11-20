"""
EMS helpers for microclimate inputs
SPDX - License - Identifier: LGPL -3.0-or-later
Copyright © 2025 Concordia CERC group
Code contributors: Saeed Rayegan sr283100@gmail.com
"""

import hub.exports.building_energy.idf_helper as idf_cte
from hub.exports.building_energy.idf_helper.idf_base import IdfBase

class IdfEmsProgram(IdfBase):
  @staticmethod
  def add(cerc_idf, program_name, source_variables, target_variables):
    """
    Add an EnergyManagementSystem:Program object to the IDF.

    An EMS Program defines the control logic executed by the EnergyPlus
    Energy Management System (EMS). Each program consists of one or more
    lines of EMS instructions (e.g., SET, IF, ELSEIF, ENDIF).

    :param cerc_idf: The IDF exporter object where the program will be added.
    :param program_name: A unique name for the EMS program
                         (e.g., "Update_MC_Temperature").
    :param old_variables: A list of variable names to read from (e.g., EMS Sensors).
                          Example: ["AvgBuildingTemp_Sensor", "Surf1_Sensor"].
    :param new_variables: A list of variable names to write to (e.g., EMS Actuators).
                          Example: ["AvgBuildingTemp_Act", "Surf1_Ta_Act"].

    Notes:
        - The program lines will typically map sensor values to actuator values.
        - Both lists (`old_variables` and `new_variables`) should be aligned by index,
          so each old variable is assigned to the corresponding new variable.
    """
    file = cerc_idf.files['ems_program']
    cerc_idf.write_to_idf_format(file, idf_cte.EMS_Program)
    cerc_idf.write_to_idf_format(file, program_name, 'Name')
    # Loop through variables and write SET statements
    for i, (target, source) in enumerate(zip(target_variables, source_variables), start=1):
      line = f"SET {target} = {source}"
      if i == len(target_variables):
        cerc_idf.write_to_idf_format(file, line, f"A{i}", ';')
      else:
        cerc_idf.write_to_idf_format(file, line, f"A{i}")