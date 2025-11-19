"""Common type definitions."""

from enum import Enum
from typing import Literal


class LanguageCode(str, Enum):
    """Supported language codes in BCP-47 format with script."""

    # English
    ENG_LATN = "eng_Latn"

    # Hindi
    HIN_DEVA = "hin_Deva"

    # Bengali
    BEN_BENG = "ben_Beng"

    # Telugu
    TEL_TELU = "tel_Telu"

    # Tamil
    TAM_TAML = "tam_Taml"

    # Gujarati
    GUJ_GUJR = "guj_Gujr"

    # Kannada
    KAN_KNDA = "kan_Knda"

    # Malayalam
    MAL_MLYM = "mal_Mlym"

    # Marathi
    MAR_DEVA = "mar_Deva"

    # Punjabi
    PAN_GURU = "pan_Guru"

    # Oriya
    ORY_ORYA = "ory_Orya"

    # Assamese
    ASM_BENG = "asm_Beng"

    # Urdu
    URD_ARAB = "urd_Arab"

    # Kashmiri
    KAS_ARAB = "kas_Arab"
    KAS_DEVA = "kas_Deva"

    # Konkani
    GOM_DEVA = "gom_Deva"

    # Manipuri
    MNI_BENG = "mni_Beng"
    MNI_MTEI = "mni_Mtei"

    # Nepali
    NPI_DEVA = "npi_Deva"

    # Sanskrit
    SAN_DEVA = "san_Deva"

    # Santali
    SAT_OLCK = "sat_Olck"

    # Sindhi
    SND_ARAB = "snd_Arab"
    SND_DEVA = "snd_Deva"


# Type alias for language codes
LanguageCodeLiteral = Literal[
    "eng_Latn",
    "hin_Deva",
    "ben_Beng",
    "tel_Telu",
    "tam_Taml",
    "guj_Gujr",
    "kan_Knda",
    "mal_Mlym",
    "mar_Deva",
    "pan_Guru",
    "ory_Orya",
    "asm_Beng",
    "urd_Arab",
    "kas_Arab",
    "kas_Deva",
    "gom_Deva",
    "mni_Beng",
    "mni_Mtei",
    "npi_Deva",
    "san_Deva",
    "sat_Olck",
    "snd_Arab",
    "snd_Deva",
]
