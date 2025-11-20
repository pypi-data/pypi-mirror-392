"""
Dictionaries module for CERC energy system archetypes to Hub energy system archetypes
SPDX - License - Identifier: LGPL - 3.0 - or -later
Copyright © 2025 Concordia CERC group
Project Coder Koa Wells kekoa.wells@concordia.ca
"""


class CercEnergySystemToHubEnergySystem:
  """
  CERC energy system archetypes to Hub energy system archetypes class
  """

  def __init__(self):
    self._dictionary = {'system 1 gas': 'system 1 gas',
                        'system 1 gas pv': 'system 1 gas pv',
                        'system 1 electricity': 'system 1 electricity',
                        'system 1 electricity pv': 'system 1 electricity pv',
                        'system 2 gas': 'system 2 gas',
                        'system 2 gas pv': 'system 2 gas pv',
                        'system 2 electricity': 'system 2 electricity',
                        'system 2 electricity pv': 'system 2 electricity pv',
                        'system 3 and 4 gas': 'system 3 and 4 gas',
                        'system 3 and 4 gas pv': 'system 3 and 4 gas pv',
                        'system 3 and 4 electricity': 'system 3 and 4 electricity',
                        'system 3 and 4 electricity pv': 'system 3 and 4 electricity pv',
                        'system 5': 'system 5',
                        'system 5 pv': 'system 5 pv',
                        'system 6 gas': 'system 6 gas',
                        'system 6 gas pv': 'system 6 gas pv',
                        'system 6 electricity': 'system 6 electricity',
                        'system 6 electricity pv': 'system 6 electricity pv',
                        'system 7 electricity pv': 'system 7 electricity pv',
                        'system 8 gas': 'system 8 gas',
                        'system 8 gas pv': 'system 8 gas pv',
                        'system 8 electricity': 'system 8 electricity',
                        'system 8 electricity pv': 'system 8 electricity pv'
                        }

  @property
  def dictionary(self) -> dict:
    """
    Get the dictionary
    :return: {}
    """
    return self._dictionary
