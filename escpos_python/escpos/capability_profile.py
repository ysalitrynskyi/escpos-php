"""
CapabilityProfile class for printer capability management.

This file is part of escpos-python: Python library for ESC/POS-compatible
thermal and impact printers.

Copyright (c) 2014-20 Michael Billington <michael.billington@gmail.com>,
incorporating modifications by others.

This software is distributed under the terms of the MIT license.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional

from escpos.code_page import CodePage


class CapabilityProfile:
    """
    Store compatibility information about one printer.
    """

    # Class-level cache for loaded data
    _encodings: Optional[Dict[str, Any]] = None
    _profiles: Optional[Dict[str, Any]] = None

    def __init__(self, profile_id: str, profile_data: Dict[str, Any]):
        """
        Construct new CapabilityProfile.

        The encoding data must be loaded from disk before calling.

        Args:
            profile_id: ID of the profile.
            profile_data: Profile data from disk.
        """
        # Basic primitive fields
        self._profile_id = profile_id
        self._name = profile_data.get('name', profile_id)
        self._notes = profile_data.get('notes')
        self._vendor = profile_data.get('vendor', '')

        # More complex fields
        self._features = profile_data.get('features', {})
        self._colors = profile_data.get('colors', [])
        self._fonts = profile_data.get('fonts', [])
        self._media = profile_data.get('media', {})

        # Load code pages
        self._code_pages: Dict[int, CodePage] = {}
        code_pages_data = profile_data.get('codePages', {})

        # Generate cache key from code pages data
        self._code_page_cache_key = hashlib.md5(
            json.dumps(code_pages_data, sort_keys=True).encode()
        ).hexdigest()

        # Load each code page
        for k, v in code_pages_data.items():
            if CapabilityProfile._encodings and v in CapabilityProfile._encodings:
                self._code_pages[int(k)] = CodePage(v, CapabilityProfile._encodings[v])

    def get_id(self) -> str:
        """
        Get the ID of the profile.

        Returns:
            Profile ID.
        """
        return self._profile_id

    def get_name(self) -> str:
        """
        Get the name of the printer.

        Returns:
            Printer name.
        """
        return self._name

    def get_vendor(self) -> str:
        """
        Get the vendor of this printer.

        Returns:
            Vendor name.
        """
        return self._vendor

    def get_code_page_cache_key(self) -> str:
        """
        Get hash of the code page data structure, to identify it for caching.

        Returns:
            MD5 hash of code pages.
        """
        return self._code_page_cache_key

    def get_code_pages(self) -> Dict[int, CodePage]:
        """
        Get associative dict of CodePage objects.

        Returns:
            Dict mapping code page numbers to CodePage objects.
        """
        return self._code_pages

    def get_feature(self, feature_name: str) -> Any:
        """
        Get a feature value.

        Args:
            feature_name: Name of the feature to retrieve.

        Returns:
            Feature value.

        Raises:
            ValueError: If the feature does not exist.
        """
        if feature_name in self._features:
            return self._features[feature_name]

        suggestions = self._suggest_feature_name(feature_name)
        suggestions_str = ", ".join(suggestions)
        raise ValueError(
            f"The feature '{feature_name}' does not exist. "
            f"Try one that does exist, such as {suggestions_str}"
        )

    def get_supports_barcode_b(self) -> bool:
        """
        Check if Barcode B command is supported.

        Returns:
            True if supported, False otherwise.
        """
        return self.get_feature('barcodeB') is True

    def get_supports_bit_image_raster(self) -> bool:
        """
        Check if Bit Image Raster command is supported.

        Returns:
            True if supported, False otherwise.
        """
        return self.get_feature('bitImageRaster') is True

    def get_supports_graphics(self) -> bool:
        """
        Check if Graphics command is supported.

        Returns:
            True if supported, False otherwise.
        """
        return self.get_feature('graphics') is True

    def get_supports_pdf417_code(self) -> bool:
        """
        Check if PDF417 code command is supported.

        Returns:
            True if supported, False otherwise.
        """
        return self.get_feature('pdf417Code') is True

    def get_supports_qr_code(self) -> bool:
        """
        Check if QR code command is supported.

        Returns:
            True if supported, False otherwise.
        """
        return self.get_feature('qrCode') is True

    def get_supports_star_commands(self) -> bool:
        """
        Check if Star mode commands are supported.

        Returns:
            True if supported, False otherwise.
        """
        return self.get_feature('starCommands') is True

    def _suggest_feature_name(self, feature_name: str) -> List[str]:
        """
        Suggest similar feature names.

        Args:
            feature_name: Feature that does not exist.

        Returns:
            Three most similar feature names that do exist.
        """
        return self._suggest_nearest(feature_name, list(self._features.keys()), 3)

    @staticmethod
    def get_profile_names() -> List[str]:
        """
        Get names of all profiles that exist.

        Returns:
            List of profile names.
        """
        CapabilityProfile._load_capabilities_data_file()
        return list(CapabilityProfile._profiles.keys())

    @staticmethod
    def load(profile_name: str) -> 'CapabilityProfile':
        """
        Retrieve the CapabilityProfile with the given ID.

        Args:
            profile_name: The ID of the profile to load.

        Returns:
            The requested CapabilityProfile.

        Raises:
            ValueError: If the profile does not exist.
        """
        CapabilityProfile._load_capabilities_data_file()

        if profile_name not in CapabilityProfile._profiles:
            suggestions = CapabilityProfile._suggest_profile_name(profile_name)
            suggestions_str = ", ".join(suggestions)
            raise ValueError(
                f"The CapabilityProfile '{profile_name}' does not exist. "
                f"Try one that does exist, such as {suggestions_str}."
            )

        return CapabilityProfile(profile_name, CapabilityProfile._profiles[profile_name])

    @staticmethod
    def _load_capabilities_data_file():
        """
        Ensure that the capabilities.json data file has been loaded.
        """
        if CapabilityProfile._profiles is None:
            # Find the capabilities.json file
            resources_dir = Path(__file__).parent / "resources"
            filename = resources_dir / "capabilities.json"

            with open(filename, 'r', encoding='utf-8') as f:
                capabilities_data = json.load(f)

            CapabilityProfile._profiles = capabilities_data.get('profiles', {})
            CapabilityProfile._encodings = capabilities_data.get('encodings', {})

    @staticmethod
    def _suggest_nearest(input_str: str, choices: List[str], num: int) -> List[str]:
        """
        Return choices with smallest edit distance to an invalid input.

        Args:
            input_str: Input that is not a valid choice.
            choices: List of valid choices.
            num: Number of suggestions to return.

        Returns:
            List of suggestions.
        """
        def levenshtein(s1: str, s2: str) -> int:
            """Calculate Levenshtein distance between two strings."""
            if len(s1) < len(s2):
                return levenshtein(s2, s1)

            if len(s2) == 0:
                return len(s1)

            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row

            return previous_row[-1]

        # Calculate distances
        distances = {word: levenshtein(input_str, word) for word in choices}

        # Sort by distance and return top N
        sorted_choices = sorted(distances.keys(), key=lambda x: distances[x])
        return sorted_choices[:min(num, len(choices))]

    @staticmethod
    def _suggest_profile_name(profile_name: str) -> List[str]:
        """
        Suggest similar profile names.

        Args:
            profile_name: Profile name that does not exist.

        Returns:
            List of suggestions including 'simple' and 'default'.
        """
        suggestions = CapabilityProfile._suggest_nearest(
            profile_name,
            list(CapabilityProfile._profiles.keys()),
            3
        )

        # Always suggest these
        always_suggest = ['simple', 'default']
        for item in always_suggest:
            if item not in suggestions and item in CapabilityProfile._profiles:
                suggestions.append(item)

        return suggestions
