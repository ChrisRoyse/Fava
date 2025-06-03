from unittest import mock
from typing import Tuple # Added for type hinting

# --- Mock Objects for External Libraries (Simplified) ---
# These help in structuring tests if UUTs expect specific types.

class MockOQS_KeyEncapsulation:
    # Class-level mocks
    _mock_generate_keypair_class = mock.Mock(return_value=(b"mock_pqc_pk_class", b"mock_pqc_sk_class"))
    _mock_encapsulate_class = mock.Mock(return_value=(b"mock_kem_ct_class", b"mock_kem_ss_class")) # (ciphertext, shared_secret)
    _correct_pqc_sk_for_mock_ct = b'S' * 2400 # Matches test_tp_dar_hph_003's PQC SK

    @staticmethod
    def _mock_decapsulate_side_effect(sk, ct):
        if ct == b"mock_kem_ct_class" and sk == MockOQS_KeyEncapsulation._correct_pqc_sk_for_mock_ct:
            return b"mock_kem_ss_class" # Correct SS for correct SK and CT
        # For any other SK with the "correct" CT, or any other CT, return a different SS
        return b"ss_for_oqs_WRONG_SK_OR_CT_" + (sk[:5] if sk else b"no_sk")

    _mock_decapsulate_class = mock.Mock(side_effect=_mock_decapsulate_side_effect)
    _mock_keypair_from_secret_class = mock.Mock(return_value=(b"mock_pqc_pk_from_secret_class", b"mock_pqc_sk_from_secret_class"))
    # Mock for the new keypair_from_seed method
    _mock_keypair_from_seed_class = mock.Mock(return_value=(b"mock_pqc_pk_from_seed_class", b"mock_pqc_sk_from_seed_class"))
    # Mock for the new load_keypair_from_secret_key method
    _mock_load_keypair_from_secret_key_class = mock.Mock(return_value=(b"mock_pqc_pk_loaded_class", b"mock_pqc_sk_loaded_class"))
    SUPPORTED_KEMS = {"ML-KEM-768", "Kyber-768", "ML-KEM-1024"} # Added to mock the real attribute

    def __init__(self, kem_name):
        self.kem_name = kem_name
        # Instance-specific mocks are not used when class is replaced with `new=` for these assertions.
        # For clarity, ensure class mocks are reset per test if state needs to be isolated.

    def generate_keypair(self):
        return MockOQS_KeyEncapsulation._mock_generate_keypair_class()

    def encapsulate(self, public_key):
        return MockOQS_KeyEncapsulation._mock_encapsulate_class(public_key)

    def decapsulate(self, secret_key, ciphertext):
        return MockOQS_KeyEncapsulation._mock_decapsulate_class(secret_key, ciphertext)

    def keypair_from_secret(self, secret_bytes):
        return MockOQS_KeyEncapsulation._mock_keypair_from_secret_class(secret_bytes)

    def encap_secret(self, public_key: bytes) -> Tuple[bytes, bytes]:
        # _mock_encapsulate_class default return_value is (b"mock_kem_ct_class", b"mock_kem_ss_class")
        # Let's assume this is (actual_ciphertext, actual_shared_secret)
        actual_ct, actual_ss = MockOQS_KeyEncapsulation._mock_encapsulate_class(public_key)
        # HybridPqcHandler expects (shared_secret, ciphertext)
        return actual_ss, actual_ct

    def decap_secret(self, sk_bytes: bytes, ciphertext: bytes) -> bytes:
        # _mock_decapsulate_class default return_value is b"mock_kem_ss_class"
        # It's a mock, so it will record the call with sk_bytes and ciphertext.
        return MockOQS_KeyEncapsulation._mock_decapsulate_class(sk_bytes, ciphertext)

    def keypair_from_seed(self, seed: bytes) -> Tuple[bytes, bytes]:
        """Mocks deterministic key generation from a seed."""
        return MockOQS_KeyEncapsulation._mock_keypair_from_seed_class(seed)

    def load_keypair_from_secret_key(self, sk_bytes: bytes) -> Tuple[bytes, bytes]:
        """Mocks loading a keypair from secret key bytes."""
        return MockOQS_KeyEncapsulation._mock_load_keypair_from_secret_key_class(sk_bytes)

class MockX25519PrivateKey:
    _generate_return_override = None # Tests can set this to an instance to override generate()
    _from_private_bytes_return_override = None # Similar for from_private_bytes

    def __init__(self, private_bytes=None):
        self._private_bytes = private_bytes if private_bytes is not None else b"default_mock_priv_key_bytes"
        # Each private key instance should have its own public key instance.
        # For mock commutativity in exchange, let public key "material" be same as private key "material".
        self.public_key_instance = MockX25519PublicKey(self._private_bytes)

    @staticmethod
    def generate():
        # If a test has specifically configured an override, use that.
        if MockX25519PrivateKey._generate_return_override is not None:
            instance_to_return = MockX25519PrivateKey._generate_return_override
            # Optional: Reset for next test if state needs to be isolated per call
            # MockX25519PrivateKey._generate_return_override = None
            return instance_to_return
        
        # Otherwise, for default behavior, create and return a fresh instance directly.
        return MockX25519PrivateKey(b"default_generated_private_key_direct_in_generate")

    def public_key(self):
        return self.public_key_instance

    def exchange(self, peer_public_key_instance):
        # peer_public_key_instance is expected to be an instance of MockX25519PublicKey
        if not isinstance(peer_public_key_instance, MockX25519PublicKey):
            raise TypeError(f"peer_public_key must be MockX25519PublicKey, not {type(peer_public_key_instance)}")
        # Make shared secret dependent on both keys for a more realistic (though still mock) exchange.
        # Use first 5 bytes of each key's material for simplicity.
        self_priv_prefix = self._private_bytes[:5] if self._private_bytes else b"noprv"
        peer_pub_prefix = peer_public_key_instance._public_bytes[:5] if peer_public_key_instance._public_bytes else b"nopub"
        # Ensure commutativity by sorting before combining, then hashing (or just concatenating for mock)
        parts = sorted([self_priv_prefix, peer_pub_prefix])
        return b"ss_x25519_" + parts[0] + b"_" + parts[1]
    @staticmethod
    def from_private_bytes(data):
        if MockX25519PrivateKey._from_private_bytes_return_override is not None:
            instance_to_return = MockX25519PrivateKey._from_private_bytes_return_override
            # Optional: Reset for next test
            # MockX25519PrivateKey._from_private_bytes_return_override = None
            return instance_to_return
        return MockX25519PrivateKey(data) # Default behavior

class MockX25519PublicKey:
    def __init__(self, public_bytes=None):
        self._public_bytes = public_bytes if public_bytes is not None else b"default_mock_public_key_bytes"

    @staticmethod
    def from_public_bytes(data):
        return MockX25519PublicKey(public_bytes=data)

    def public_bytes(self, encoding, format):
        # encoding and format are part of the real API (e.g., serialization.Encoding.Raw)
        return self._public_bytes


class MockAESGCMEncryptor:
    def __init__(self):
        self.update = mock.Mock(return_value=b"") # Can be chained if needed
        self.finalize = mock.Mock(return_value=b"mock_aes_ciphertext")
        self.tag = b"mock_aes_auth_tag"

class MockAESGCMDecryptor:
    def __init__(self):
        self.update = mock.Mock(return_value=b"")
        self.finalize = mock.Mock(return_value=b"mock_aes_plaintext")


class MockArgon2id:
    def __init__(self, time_cost=mock.ANY, memory_cost=mock.ANY, parallelism=mock.ANY, length=mock.ANY, salt_len=mock.ANY, backend=None):
        self.time_cost = time_cost
        self.memory_cost = memory_cost
        self.parallelism = parallelism
        self.length = length
        self.salt_len = salt_len
        self.backend = backend
        self.derive_mock = mock.Mock(return_value=b"mock_argon2id_ikm_64_bytes_default")

    def derive(self, password, salt):
        return self.derive_mock(password, salt)


class MockAESGCM:
    _correct_key_for_test = None
    _stored_plaintext_for_mock_success = None
    _expected_mock_ciphertext_for_success = None
    _expected_mock_tag_for_success = None

    @classmethod
    def reset_correct_key_for_test(cls):
        cls._correct_key_for_test = None
        cls._stored_plaintext_for_mock_success = None
        cls._expected_mock_ciphertext_for_success = None
        cls._expected_mock_tag_for_success = None

    def __init__(self, key):
        self.key = key

    def encrypt(self, nonce, data, associated_data):
        MockAESGCM._correct_key_for_test = self.key
        MockAESGCM._stored_plaintext_for_mock_success = data
        
        MockAESGCM._expected_mock_ciphertext_for_success = b'c' * len(data)
        MockAESGCM._expected_mock_tag_for_success = b't' * 16
        
        return MockAESGCM._expected_mock_ciphertext_for_success + MockAESGCM._expected_mock_tag_for_success

    def decrypt(self, nonce, data, associated_data):
        if MockAESGCM._correct_key_for_test is not None and self.key != MockAESGCM._correct_key_for_test:
            raise ValueError("Simulated AESGCM InvalidTag: Decryption key does not match encryption key.")

        tag_length = 16
        if len(data) < tag_length:
            raise ValueError("Simulated AESGCM InvalidTag: Received data too short to contain tag.")
            
        received_ciphertext = data[:-tag_length]
        received_tag = data[-tag_length:]

        if (MockAESGCM._expected_mock_ciphertext_for_success is not None and
            received_ciphertext != MockAESGCM._expected_mock_ciphertext_for_success) or \
           (MockAESGCM._expected_mock_tag_for_success is not None and
            received_tag != MockAESGCM._expected_mock_tag_for_success):
            raise ValueError("Simulated AESGCM InvalidTag: Tampered ciphertext or tag.")

        if MockAESGCM._stored_plaintext_for_mock_success is not None:
            return MockAESGCM._stored_plaintext_for_mock_success
        
        raise RuntimeError("MockAESGCM: Decryption called without prior successful encryption state.")

class MockHKDFExpand:
    def __init__(self, algorithm, length, info, backend=None): # Added backend=None to make it optional for other mocks
        self.algorithm = algorithm
        self.length = length
        self.info = info
        self.backend = backend
        # Ensure the mock returns bytes of the correct length specified during instantiation
        self.derive_mock = mock.Mock(return_value=b"M" * int(self.length))

    def derive(self, ikm):
        # If side_effect is set, it will be used. Otherwise, use the default return_value.
        return self.derive_mock(ikm)

class MockHKDF:
    def __init__(self, algorithm, length, salt, info, backend):
        self.algorithm = algorithm
        self.length = length
        self.salt = salt
        self.info = info
        self.backend = backend
        self.derive_mock = mock.Mock(return_value=b"M" * self.length)

    def derive(self, ikm):
        return self.derive_mock(ikm)