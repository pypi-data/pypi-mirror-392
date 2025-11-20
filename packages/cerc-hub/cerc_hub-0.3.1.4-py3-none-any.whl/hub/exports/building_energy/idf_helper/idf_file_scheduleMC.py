"""
Cerc Idf exports one city or some buildings to idf format
SPDX - License - Identifier: LGPL -3.0-or-later
Copyright © 2022 Concordia CERC group
Project Coder Guille Guillermo.GutierrezMorote@concordia.ca
Code contributors: Oriol Gavalda Torrellas oriol.gavalda@concordia.ca
Code contributors: Saeed Rayegan sr283100@gmail.com
"""

from pathlib import Path
import hub.exports.building_energy.idf_helper as idf_cte
from hub.exports.building_energy.idf_helper.idf_base import IdfBase


class IdfFileScheduleMC(IdfBase):
  @staticmethod
  def add(cerc_idf, schedule_name, column_number, file_name):
    """
    Add a Schedule:File object for external microclimate schedules.

    :param cerc_idf: The IDF exporter object
    :param schedule_name: Name of the schedule to appear in IDF
    :param column_number: Column number in the CSV file
    :param file_name: Path or name of the CSV file
    """
    file = cerc_idf.files['file_schedules']
    cerc_idf.write_to_idf_format(file, idf_cte.FILE_SCHEDULE)
    cerc_idf.write_to_idf_format(file, schedule_name, 'Name')
    cerc_idf.write_to_idf_format(file, "Any Number", 'Schedule Type Limits Name')
    cerc_idf.write_to_idf_format(file, Path(file_name).name, 'File Name')
    cerc_idf.write_to_idf_format(file, column_number, 'Column Number')
    cerc_idf.write_to_idf_format(file, 1, 'Rows to Skip at Top')
    cerc_idf.write_to_idf_format(file, 8760, 'Number of Hours of Data')
    cerc_idf.write_to_idf_format(file, 'Comma', 'Column Separator')
    cerc_idf.write_to_idf_format(file, 'No', 'Interpolate to Timestep')
    cerc_idf.write_to_idf_format(file, '60', 'Minutes per Item')
    cerc_idf.write_to_idf_format(file, 'Yes', 'Adjust Schedule for Daylight Savings', ';')