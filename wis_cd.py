""" API for accessing the Saab WIS CD.
"""

from typing import Iterable
from typing import List

import os
import re
import glob
import zipfile



def _integers_to_string(integer_list: Iterable[int]) -> str:
    """ Combine integers to a user readable string.

    Example:
        >>> _integers_to_string([1,2,3,5])
        '1-3, 5'

    :param integer_list: A list of integers.
    :return: User readable string of the integers in the supplied list.
    """
    result = ''

    previous_value = None
    previous_is_interval = False
    for i in sorted(integer_list):
        if not previous_value:
            result += str(i)
        elif previous_value + 1 == i:
            if not previous_is_interval:
                result += '-'
                previous_is_interval = True
        else:
            if previous_is_interval:
                result += str(previous_value)
                previous_is_interval = False
            result += ', '
            result += str(i)

        previous_value = i

    if previous_is_interval:
        result += str(previous_value)

    return result


class InvalidWISCD(Exception):
    pass


class SaabWISCD:
    _VIEWS_REGEX = re.compile('^(.*? \(\d+\))([\d]{4})(\w*?)([\w]{2})\.xml$')
    _LANGUAGE_LOOKUP = {
        'de': 'German',
        'es': 'Spanish',
        'fi': 'Finnish',
        'fr': 'French',
        'gb': 'International English',
        'it': 'Italian',
        'jp': 'Japanese',
        'kr': 'Korean',
        'nl': 'Dutch',
        'ru': 'Russian',
        'sc': 'Simplified Chinese',
        'se': 'Swedish',
        'tc': 'Traditional Chinese',
        'th': 'Thai',
    }

    # Found in setup in Select default market
    _COUNTRY_LOOKUP = {
        'ae': 'United Arab Emirates',
        'ar': 'Argentina',
        'at': 'Austria',
        'au': 'Australia',
        'be': 'Belgium/Luxembourg',
        'bh': 'Bahrain',
        'ca': 'Canada',
        'ch': 'Switzerland',
        'cl': 'Chile',
        'cn': 'China',
        'cr': 'Czech Republic',
        'cy': 'Cyprus',
        'de': 'Germany',
        'dk': 'Denmark',
        'es': 'Spain',
        'ee': 'Estonia',
        'fi': 'Finland',
        'fr': 'France',
        'gb': 'Great Britain',
        'gr': 'Greece',
        'hk': 'Hong Kong',
        'hu': 'Hungary',
        'ie': 'Ireland',
        'el': 'Israel',
        'is': 'Iceland',
        'it': 'Italy',
        'jo': 'Jordan',
        'jp': 'Japan',
        'kr': 'Republic of Korea',
        'kw': 'Kuwait',
        'lb': 'Lebanon',
        'lv': 'Latvia',
        'lt': 'Lithuania',
        'mt': 'Malta',
        'my': 'Malaysia',
        'nl': 'Holland',
        'no': 'Norway',
        'om': 'Oman',
        'pl': 'Poland',
        'pt': 'Portugal',
        'qa': 'Qatar',
        'ru': 'Russia',
        'sa': 'Saudi Arabia',
        'se': 'Sweden',
        'sg': 'Singapore',
        'th': 'Thailand',
        'tr': 'Turkey',
        'tw': 'Taiwan',
        'us': 'United States',
        'za': 'South Africa',
        'zn': 'New Zealand',
    }

    def __init__(self, directory: str):
        if not SaabWISCD._is_valid_wis_cd(directory):
            raise InvalidWISCD()

        self.directory = directory

        # Grab information from the CD
        self.languages = set()  # Assumes all languages exists for all models
        self.models = {}

        for model_directory in os.listdir(self.directory):
            views_file = os.path.join(self.directory, model_directory,
                                      'package', 'views.zip')
            if not os.path.isfile(views_file):
                raise InvalidWISCD()

            with zipfile.ZipFile(views_file) as z:
                current_models = {}
                for f in z.namelist():
                    match = SaabWISCD._VIEWS_REGEX.match(f)

                    if not match:
                        raise InvalidWISCD()

                    model = match.group(1)
                    model_year = int(match.group(2))
                    language_code = match.group(4)

                    model_years = current_models.get(model, set())
                    model_years.add(model_year)
                    current_models[model] = model_years

                    self.languages.add(language_code)

                if len(current_models) != 1:
                    raise InvalidWISCD()

            for model, model_years in current_models.items():
                self.models['{} {}'.format(model, _integers_to_string(model_years))] = model_directory

    def get_models(self) -> List[str]:
        """ Get a list of all models available on the CD.

        :return: A list of all models available on the CD.
        """
        return sorted(list(self.models.keys()))

    def get_languages(self) -> List[str]:
        """ Get a list of all languages available on the CD.

        :return: A list of all languages available on the CD.
        """
        return sorted(list(self.languages))

    def get_languages_full(self) -> List[str]:
        """ Similar to get_languages(), but includes the full name of the
        country.

        :return: A list of all languages available on the CD.
        """
        languages_full = []
        for lang_code in self.languages:
            language = self._LANGUAGE_LOOKUP.get(lang_code, '???')

            languages_full.append('{} ({})'.format(language, lang_code.upper()))

        return sorted(languages_full)

    def extract_data(self, model: str, languages: List[str],
                     destination: str):
        directory = self.models[model]
        if directory is None:
            raise ValueError('Invalid model')

        # extract views files

        for l in languages:
            dir = os.path.join(self.directory, directory,
                               'package', '{}*.zip'.format(l))
            print(dir)
            for doc_file in glob.glob(dir):
                with zipfile.ZipFile(doc_file) as z:
                    z.extractall(destination)




    @staticmethod
    def _is_valid_wis_cd(directory) -> bool:
        """ Check if the directory is a valid WIS CD.

        :param directory: Directory that should be checked.
        :return: True if the directory is a valid WIS CD, otherwise False.
        """
        if not os.path.isdir(directory):
            return False

        wis_directories = ['9-3 (400)', '9-3 (440)', '9-5 (600)', '9-5 (650)']
        files = os.listdir(directory)

        for wis_directory in wis_directories:
            if wis_directory in files \
                    and os.path.isdir(os.path.join(directory, wis_directory)):
                return True

        return False


if __name__ == '__main__':
    s = SaabWISCD('D:/')
    print(s.get_languages())
    print(s.get_languages_full())
    m = s.get_models()
    print('models', m)
    print(m[0])

    s.extract_data(m[0], ['se'], 'tmp')
