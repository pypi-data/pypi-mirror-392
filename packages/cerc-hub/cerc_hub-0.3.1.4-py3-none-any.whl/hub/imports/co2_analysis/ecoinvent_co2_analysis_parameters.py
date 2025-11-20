"""
Co2AnalysisParameters enrich the city with embodied and end-of-life CO2 emissions
SPDX - License - Identifier: LGPL - 3.0 - or -later
Copyright © 2019 - 2025 Concordia CERC group
Project Coder Koa Wells kekoa.wells@concordia.ca
Code contributors: Alireza Adli alireza.adli@mail.concordia.ca
"""
import logging

import hub.helpers.constants as cte
from hub.catalog_factories.co2_analysis_catalog_factory import Co2AnalysisCatalogFactory
from hub.helpers.dictionaries import NrcanConstructionToEcoinventMaterialCo2, NrcanConstructionToEcoinventWindowCo2

class EcoinventCo2AnalysisParameters:
  """
  EcoinventCo2AnalysisParameters class
  """
  def __init__(self, city):
    self._city = city
    self._co2_analysis_catalog = Co2AnalysisCatalogFactory('ecoinvent').catalog
    self._embodied_co2_material_catalog = self._co2_analysis_catalog.entries('embodied_co2_materials')
    self._end_of_life_co2_material_catalog = self._co2_analysis_catalog.entries('end_of_life_co2_materials')
    self._embodied_co2_window_catalog = self._co2_analysis_catalog.entries('embodied_co2_windows')
    self._end_of_life_co2_window_catalog = self._co2_analysis_catalog.entries('end_of_life_co2_windows')

  def enrich_buildings(self):
    """
    Enriches the buildings of the city with embodied and end-of-life CO2 emissions
    """
    for building in self._city.buildings:
      envelope_embodied_co2 = 0
      envelope_end_of_life_co2 = 0
      opening_embodied_co2 = 0
      opening_end_of_life_co2 = 0

      for surface in building.surfaces:
        if surface.associated_thermal_boundaries is None:
            logging.error(f'Building {building.name} has no associated thermal boundaries. Embodied co2 analysis cannot be calculated')
            continue
        for thermal_boundary in surface.associated_thermal_boundaries:
          if thermal_boundary.layers is None:
            logging.error(f'Building {building.name} has no associated thermal layers. Embodied co2 analysis cannot be calculated')
            continue
          for layer in thermal_boundary.layers:
            if not layer.no_mass:
              layer_envelope_embodied_co2, layer_envelope_end_of_life_co2 = self._calculate_envelope_emissions(layer, thermal_boundary.opaque_area)
              envelope_embodied_co2 += layer_envelope_embodied_co2
              envelope_end_of_life_co2 += layer_envelope_end_of_life_co2

          for thermal_opening in thermal_boundary.thermal_openings:
            #TODO: find better value for thickness than thermal_boundary.thickness
            thermal_opening_embodied_co2, thermal_opening_end_of_life_co2 = self._calculate_opening_emissions(thermal_opening, thermal_boundary.thickness)
            opening_embodied_co2 += thermal_opening_embodied_co2
            opening_end_of_life_co2 += thermal_opening_end_of_life_co2

      building.embodied_co2[cte.ENVELOPE_CO2] = envelope_embodied_co2
      building.embodied_co2[cte.OPENING_CO2] = opening_embodied_co2
      building.end_of_life_co2[cte.ENVELOPE_CO2] = envelope_end_of_life_co2
      building.end_of_life_co2[cte.OPENING_CO2] = opening_end_of_life_co2

  def _calculate_envelope_emissions(self, layer, opaque_area):
    """
    Calculate the embodied and end-of-life envelope emissions of the provided layer
    """
    layer_envelope_embodied_co2 = 0
    layer_envelope_end_of_life_co2 = 0

    co2_material_dictionary = NrcanConstructionToEcoinventMaterialCo2().dictionary
    nrcan_layer_material_name = layer.material_name
    hub_layer_material_name = co2_material_dictionary.get(nrcan_layer_material_name)['name']

    layer_area = opaque_area
    layer_thickness = layer.thickness
    layer_material_density = layer.density
    layer_mass = layer_area * layer_thickness * layer_material_density

    for material in self._embodied_co2_material_catalog:
      if material['Material']['name'] == hub_layer_material_name:
        material_emissions_factor = material['Material']['embodied_carbon']
        layer_envelope_embodied_co2 += layer_mass * material_emissions_factor
        break

    for material in self._end_of_life_co2_material_catalog:
      if material['Material']['name'] == hub_layer_material_name:
        material_recycling_ratio = material['Material']['recycling_ratio']
        material_onsite_recycling_ratio = material['Material']['onsite_recycling_ratio']
        material_company_recycling_ratio = material['Material']['company_recycling_ratio']
        material_landfilling_ratio = material['Material']['landfilling_ratio']
        material_demolition_machine_emission = material['Material']['demolition_machine_emission']
        material_onsite_machine_emission = material['Material']['onsite_machine_emission']
        material_companies_recycling_machine_emission = material['Material']['companies_recycling_machine_emission']
        material_landfilling_machine_emission = material['Material']['landfilling_machine_emission']

        demolition_co2 = layer_mass * material_demolition_machine_emission
        onsite_recycling_co2 = layer_mass * material_recycling_ratio * material_onsite_recycling_ratio * material_onsite_machine_emission
        company_recycling_co2 = layer_mass * material_company_recycling_ratio * material_companies_recycling_machine_emission
        landfilling_co2 = layer_mass * material_landfilling_ratio * material_landfilling_machine_emission

        layer_envelope_end_of_life_co2 += demolition_co2 + onsite_recycling_co2 + company_recycling_co2 + landfilling_co2
        break

    return layer_envelope_embodied_co2, layer_envelope_end_of_life_co2

  def _calculate_opening_emissions(self, thermal_opening, opening_thickness):
    """
    Calculate the embodied and end-of-life window emissions of the provided thermal opening
    """
    window_embodied_co2 = 0
    window_end_of_life_co2 = 0

    co2_window_dictionary = NrcanConstructionToEcoinventWindowCo2().dictionary
    nrcan_window_name = thermal_opening.construction_name
    hub_window_name = co2_window_dictionary.get(nrcan_window_name)['name']

    opening_area = thermal_opening.area
    opening_thickness = opening_thickness

    for window in self._embodied_co2_window_catalog:
      if window['Window']['name'] == f'window_{hub_window_name}':

        window_emissions_factor = window['Window']['embodied_carbon']
        window_embodied_co2 += opening_area * window_emissions_factor
        break

    for window in self._end_of_life_co2_window_catalog:
      if window['Window']['name'] == f'window_{hub_window_name}':
        window_density = window['Window']['density']
        window_recycling_ratio = window['Window']['recycling_ratio']
        window_onsite_recycling_ratio = window['Window']['onsite_recycling_ratio']
        window_company_recycling_ratio = window['Window']['company_recycling_ratio']
        window_landfilling_ratio = window['Window']['landfilling_ratio']
        window_demolition_machine_emission = window['Window']['demolition_machine_emission']
        window_onsite_machine_emission = window['Window']['onsite_machine_emission']
        window_companies_recycling_machine_emission = window['Window']['companies_recycling_machine_emission']
        window_landfilling_machine_emission = window['Window']['landfilling_machine_emission']

        window_mass = opening_area * opening_thickness * window_density
        demolition_co2 = window_mass * window_demolition_machine_emission
        onsite_recycling_co2 = window_mass * window_recycling_ratio * window_onsite_recycling_ratio * window_onsite_machine_emission
        company_recycling_co2 = window_mass * window_company_recycling_ratio * window_companies_recycling_machine_emission
        landfilling_co2 = window_mass * window_landfilling_ratio * window_landfilling_machine_emission

        window_end_of_life_co2 += demolition_co2 + onsite_recycling_co2 + company_recycling_co2 + landfilling_co2
        break

    return window_embodied_co2, window_end_of_life_co2
