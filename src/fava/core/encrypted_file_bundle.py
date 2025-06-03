"""
Defines the structure for an encrypted file bundle used by Fava.
"""

class EncryptedFileBundle:
    """
    Represents the structured data of an encrypted file.
    This includes headers, KEM ciphertexts, symmetric ciphertext, IV, tag, etc.
    """
    def __init__(self):
        self.format_identifier: str = ""
        self.format_version: int = 0
        self.suite_id: str = ""
        self.classical_kem_ciphertext: bytes = b""
        self.pqc_kem_ciphertext: bytes = b""
        self.symmetric_iv: bytes = b""
        self.symmetric_ciphertext: bytes = b""
        self.symmetric_auth_tag: bytes = b""
        # Add other fields as necessary based on the specification

    @staticmethod
    def parse_header_only(file_content_peek: bytes):
        """
        Parses only the header part of the bundle to quickly identify
        format and suite, without decrypting.

        Args:
            file_content_peek: The first few bytes of the encrypted file.

        Returns:
            A dictionary with header information (e.g., {"format_identifier": "...", "suite_id": "..."})
            or None if parsing fails or it's not a recognized format.
        """
        # Placeholder implementation
        # A real implementation would parse bytes to extract structured header.
        if file_content_peek and file_content_peek.startswith(b"FAVA_PQC_HYBRID_V1_HEADER_START"): # Example
            # Simulate extracting info
            return {"format_identifier": "FAVA_PQC_HYBRID_V1", "suite_id": "X25519_KYBER768_AES256GCM"}
        return None

    def to_bytes(self) -> bytes:
        """
        Serializes the bundle object to bytes.
        A simple format: <len_field1><field1_bytes><len_field2><field2_bytes>...
        Lengths are 4-byte little-endian unsigned integers.
        Strings are UTF-8 encoded.
        """
        parts = []
        fields_to_serialize = [
            ("format_identifier", self.format_identifier.encode('utf-8')),
            ("suite_id", self.suite_id.encode('utf-8')),
            ("classical_kem_ciphertext", self.classical_kem_ciphertext),
            ("pqc_kem_ciphertext", self.pqc_kem_ciphertext),
            ("symmetric_iv", self.symmetric_iv),
            ("symmetric_ciphertext", self.symmetric_ciphertext),
            ("symmetric_auth_tag", self.symmetric_auth_tag),
        ]

        for _, field_bytes in fields_to_serialize:
            parts.append(len(field_bytes).to_bytes(4, 'little'))
            parts.append(field_bytes)
        
        return b"".join(parts)

    @classmethod
    def from_bytes(cls, data: bytes):
        """
        Deserializes bytes into an EncryptedFileBundle object.
        """
        bundle = cls()
        offset = 0

        def read_field(current_offset: int) -> tuple[bytes, int]:
            if current_offset + 4 > len(data):
                raise ValueError("Data too short to read length prefix.")
            length = int.from_bytes(data[current_offset : current_offset + 4], 'little')
            current_offset += 4
            if current_offset + length > len(data):
                raise ValueError("Data too short to read field content.")
            field_data = data[current_offset : current_offset + length]
            current_offset += length
            return field_data, current_offset

        bundle.format_identifier, offset = read_field(offset)
        bundle.format_identifier = bundle.format_identifier.decode('utf-8')
        
        bundle.suite_id, offset = read_field(offset)
        bundle.suite_id = bundle.suite_id.decode('utf-8')

        bundle.classical_kem_ciphertext, offset = read_field(offset)
        bundle.pqc_kem_ciphertext, offset = read_field(offset)
        bundle.symmetric_iv, offset = read_field(offset)
        bundle.symmetric_ciphertext, offset = read_field(offset)
        bundle.symmetric_auth_tag, offset = read_field(offset)
        
        # Add version parsing if it's included in serialization
        # For now, assuming format_version is not part of this simple serialization.
        # bundle.format_version = ...

        return bundle