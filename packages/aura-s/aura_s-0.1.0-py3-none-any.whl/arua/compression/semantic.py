"""Semantic wrapper codecs (Sa/Sb) on top of ARUA core compression.

This module introduces a compact 4-byte semantic header in front of the
existing method-byte-based core compressor, focusing first on:

* Sa – Semantic Atom  (tiny messages, < 100 bytes)
* Sb – Semantic Binary (small messages, 100 bytes – 1 KiB)

Header layout (v1, big-endian):

    [codec_id][domain_id][template_id_hi][template_id_lo]

The header is followed by the payload produced by
``arua.compression.core.compress``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from .core import compress as core_compress
from .core import decompress as core_decompress
from .flow import compress as flow_compress
from .flow import decompress as flow_decompress
from .grain import compress as grain_compress
from .grain import decompress as grain_decompress
from .semantic_combo import compress as combo_compress
from .semantic_combo import decompress as combo_decompress
from .semantic_derivative import encode_derivative, decode_derivative
from .semantic_entropy import compress as entropy_compress
from .semantic_entropy import decompress as entropy_decompress
from .semantic_hash import compress as hash_compress
from .semantic_hash import decompress as hash_decompress
from .semantic_index import compress as index_compress
from .semantic_index import decompress as index_decompress
from .semantic_joint import compress as joint_compress
from .semantic_joint import decompress as joint_decompress
from .semantic_key import compress as key_compress
from .semantic_key import decompress as key_decompress
from .semantic_learned import compress as sl_compress
from .semantic_learned import decompress as sl_decompress
from .semantic_yield import compress as yield_compress
from .semantic_yield import decompress as yield_decompress
from .semantic_memory import compress as sm_compress
from .semantic_memory import decompress as sm_decompress
from .semantic_node import compress as node_compress
from .semantic_node import decompress as node_decompress
from .semantic_orchestration import compress as orchestration_compress
from .semantic_orchestration import decompress as orchestration_decompress
from .semantic_pattern import compress as pattern_compress
from .semantic_pattern import decompress as pattern_decompress
from .semantic_resolver import compress as resolver_compress
from .semantic_resolver import decompress as resolver_decompress
from .semantic_stream import compress as stream_compress
from .semantic_stream import decompress as stream_decompress
from .semantic_table import compress as table_compress
from .semantic_table import decompress as table_decompress
from .semantic_unique import compress as su_compress
from .semantic_unique import decompress as su_decompress
from .semantic_vector import compress as vector_compress
from .semantic_vector import decompress as vector_decompress
from .semantic_sa import get_atom as sa_get_atom
from .semantic_sa import lookup_atom_id as sa_lookup_atom_id
from .semantic_x import compress as sx_compress
from .semantic_x import decompress as sx_decompress
from .semantic_z import compress as sz_compress
from .semantic_z import decompress as sz_decompress
from .semantic_sa import get_atom as sa_get_atom
from .semantic_sa import lookup_atom_id as sa_lookup_atom_id
from .semantic_sb import get_template as sb_get_template
from .semantic_sb import register_template as sb_register_template
from .semantic_cache import compress as cache_compress
from .semantic_cache import decompress as cache_decompress

_CODEC_ID_MAX = 0xFF
_DOMAIN_ID_MAX = 0xFF
_TEMPLATE_ID_MAX = 0xFFFF
_HEADER_SIZE = 4

SA_THRESHOLD = int(os.getenv("ARUA_SA_THRESHOLD", "100"))  # bytes
SB_THRESHOLD = int(os.getenv("ARUA_SB_THRESHOLD", "1024"))  # bytes


@dataclass(frozen=True)
class SemanticHeader:
    """Inlined semantic header used by ARUA v1."""

    codec_id: int
    domain_id: int
    template_id: int

    def to_bytes(self) -> bytes:
        if not (0 <= self.codec_id <= _CODEC_ID_MAX):
            raise ValueError("codec_id must be in 0..255")
        if not (0 <= self.domain_id <= _DOMAIN_ID_MAX):
            raise ValueError("domain_id must be in 0..255")
        if not (0 <= self.template_id <= _TEMPLATE_ID_MAX):
            raise ValueError("template_id must be in 0..65535")
        return bytes(
            [
                self.codec_id,
                self.domain_id,
                (self.template_id >> 8) & 0xFF,
                self.template_id & 0xFF,
            ]
        )

    @staticmethod
    def from_bytes(data: bytes) -> tuple[SemanticHeader, bytes]:
        if len(data) < _HEADER_SIZE:
            raise ValueError("semantic header too short")
        codec_id = data[0]
        domain_id = data[1]
        template_id = (data[2] << 8) | data[3]
        return (
            SemanticHeader(
                codec_id=codec_id, domain_id=domain_id, template_id=template_id
            ),
            data[4:],
        )


# Codec ids for v1. Sa/Sb have concrete behaviour; other ids are
# progressively wired in but may still act as aliases of Sb/core.
CODEC_ID_SA = 0x01  # Semantic Atom
CODEC_ID_SB = 0x02  # Semantic Binary
CODEC_ID_SC = 0x03  # Semantic Context
CODEC_ID_SD = 0x04  # Semantic Derivative
CODEC_ID_SE = 0x05  # Semantic Entropy
CODEC_ID_SF = 0x06  # Semantic Flow
CODEC_ID_SG = 0x07  # Semantic Grain
CODEC_ID_SU = 0x08  # Semantic Unique
CODEC_ID_SH = 0x09  # Semantic Hash
CODEC_ID_SI = 0x0A  # Semantic Index
CODEC_ID_SJ = 0x0B  # Semantic Joint
CODEC_ID_SK = 0x0C  # Semantic Key
CODEC_ID_SL = 0x0D  # Semantic Learned
CODEC_ID_SM = 0x0E  # Semantic Memory
CODEC_ID_SN = 0x0F  # Semantic Node
CODEC_ID_SO = 0x10  # Semantic Orchestration
CODEC_ID_SP = 0x11  # Semantic Pattern
CODEC_ID_SQ = 0x12  # Semantic Quantization
CODEC_ID_SR = 0x13  # Semantic Resolver
CODEC_ID_SS = 0x14  # Semantic Substitution
CODEC_ID_SV = 0x15  # Semantic Vector
CODEC_ID_SW = 0x16  # Semantic Wave
CODEC_ID_SX = 0x17  # Semantic eXcelerator
CODEC_ID_SY = 0x18  # Semantic Yield
CODEC_ID_SZ = 0x19  # Semantic Zero-copy
CODEC_ID_ST = 0x1A  # Semantic Table


def semantic_compress(
    data: bytes,
    codec: str = "auto",
    domain_id: int = 0,
    template_id: int | None = None,
) -> bytes:
    """Compress data with a semantic header (Sa/Sb first).

    Args:
        data: Bytes to compress.
        codec: One of:
            - \"auto\" – choose Sa or Sb based on size thresholds.
            - \"Sa\"   – force Semantic Atom codec.
            - \"Sb\"   – force Semantic Binary codec.
        domain_id: Small domain identifier (0-255) for domain-aware routing.
        template_id: Optional template id (0-65535); None is encoded as 0.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("semantic_compress() expects a bytes-like object")
    raw = bytes(data)

    if codec == "auto":
        size = len(raw)
        # Tiny payloads: favour Sa atoms / header-only.
        if size < SA_THRESHOLD:
            codec = "Sa"
        # Small payloads: Sb wrapper over core.
        elif size < SB_THRESHOLD:
            codec = "Sb"
        else:
            # Larger payloads: choose between Sg/Sf/Sb based on a coarse
            # entropy estimate similar to Se. Low-entropy text goes to Sg,
            # medium entropy to Sf, very high entropy stays with Sb/core.
            sample = raw[:256]
            if not sample:
                codec = "Sb"
            else:
                unique = len(set(sample))
                ratio = unique / len(sample)
                if ratio < 0.5:
                    codec = "Sg"
                elif ratio < 0.8:
                    codec = "Sf"
                else:
                    codec = "Sb"

    if codec == "Sa":
        codec_id = CODEC_ID_SA
        # Try to encode known Sa atoms as header-only using the Sa atom table.
        atom_id = sa_lookup_atom_id(domain_id, raw)
        if atom_id is not None:
            core_payload = b""
            template_id = atom_id
        else:
            # Fallback: legacy behaviour, keep uncompressed body.
            core_payload = core_compress(raw, method="uncompressed")
    elif codec == "Sb":
        codec_id = CODEC_ID_SB
        # For calls that provide an explicit template_id, treat Sb as a
        # binary table lookup codec: register the template and emit a
        # header-only body when possible. For generic Sb usage without a
        # template_id, fall back to the legacy core compressor.
        if template_id is not None and sb_register_template(domain_id, int(template_id), raw):
            core_payload = b""
        else:
            core_payload = core_compress(raw, method="auto")
    elif codec == "Sc":
        codec_id = CODEC_ID_SC
        # Semantic Context codec – delegate to combo prototype which chooses
        # between flow/grain/core based on content and size.
        core_payload = combo_compress(raw)
    elif codec == "Sd":
        codec_id = CODEC_ID_SD
        # Derivative/delta codec – run a simple byte-wise derivative transform
        # before delegating to the core compressor.
        derived = encode_derivative(raw)
        core_payload = core_compress(derived, method="auto")
    elif codec == "Se":
        codec_id = CODEC_ID_SE
        # Entropy-aware codec – delegate to entropy prototype which selects
        # core method based on a coarse entropy bucket.
        core_payload = entropy_compress(raw)
    elif codec == "Sf":
        codec_id = CODEC_ID_SF
        # Use the Semantic Flow codec for chat/stream-style text.
        core_payload = flow_compress(raw)
    elif codec == "Sg":
        codec_id = CODEC_ID_SG
        # Use the Semantic Grain codec for dense/repetitive data.
        core_payload = grain_compress(raw)
    elif codec == "Su":
        codec_id = CODEC_ID_SU
        # Semantic Unique codec – delegate to the Su content-addressed helper.
        core_payload = su_compress(raw)
    elif codec == "Sh":
        codec_id = CODEC_ID_SH
        # Hash/signature codec – delegate to Sh prototype which embeds
        # content hash (algorithm + digest) for content-addressed storage.
        core_payload = hash_compress(raw)
    elif codec == "Si":
        codec_id = CODEC_ID_SI
        # Index metadata codec – delegate to Si prototype which embeds
        # document/section/shard/offset metadata for corpus indexing.
        core_payload = index_compress(raw)
    elif codec == "Sj":
        codec_id = CODEC_ID_SJ
        # Joint/multi-part wrapper – for direct semantic_compress use,
        # treat raw as a pre-encoded joint body. For multi-payload bundling,
        # use semantic_joint.compress() directly.
        # If raw is already a joint-encoded body, compress it; otherwise
        # treat it as a single payload to be wrapped in a joint container.
        # In practice, Sj is best used via helpers.encode_semantic_joint().
        core_payload = core_compress(raw, method="auto")
    elif codec == "Sk":
        codec_id = CODEC_ID_SK
        # Logical keys/tenancy codec – delegate to Sk prototype which embeds
        # key metadata (user/session/tenant IDs) alongside the compressed body.
        core_payload = key_compress(raw)
    elif codec == "Sl":
        codec_id = CODEC_ID_SL
        # Learned/ML codec – delegate to Sl helper which embeds model/latent
        # metadata alongside the compressed body.
        core_payload = sl_compress(raw)
    elif codec == "Sm":
        codec_id = CODEC_ID_SM
        # Memory-oriented codec – split payload into Su-backed chunks so
        # repeated blocks can be cached/deduplicated independently.
        core_payload = sm_compress(raw)
    elif codec == "Sn":
        codec_id = CODEC_ID_SN
        # Node/topology codec – delegate to Sn prototype which embeds
        # location metadata (cluster/region/zone/node/role) for routing.
        core_payload = node_compress(raw)
    elif codec == "So":
        codec_id = CODEC_ID_SO
        # Orchestration codec – delegate to So which embeds workflow DAG
        # metadata for multi-step process coordination.
        core_payload = orchestration_compress(raw)
    elif codec == "Sp":
        codec_id = CODEC_ID_SP
        # Pattern codec – delegate to Sp which embeds pattern template
        # and field metadata for structured events and log messages.
        core_payload = pattern_compress(raw)
    elif codec == "Sq":
        codec_id = CODEC_ID_SQ
        # Quantization-focused codec for tensor/numeric payloads; in the
        # hot path, ``raw`` is expected to be an Sq binary body produced by
        # :mod:`semantic_quantization`, so we store it as-is without an
        # extra layer of core compression.
        core_payload = raw
    elif codec == "Sr":
        codec_id = CODEC_ID_SR
        # Resolver codec – delegate to Sr prototype which embeds routing
        # hints and resolution metadata alongside the compressed body.
        core_payload = resolver_compress(raw)
    elif codec == "Ss":
        codec_id = CODEC_ID_SS
        # Semantic Cache codec – uses frequency-based substitution to replace
        # common patterns with short references. Highly effective for LLM
        # workloads (prompts, system messages, repeated tokens).
        core_payload = cache_compress(raw)
    elif codec == "Sv":
        codec_id = CODEC_ID_SV
        # Vector/embedding codec – delegate to Sv prototype which embeds
        # vector metadata (dimension, model, dtype) alongside the compressed body.
        core_payload = vector_compress(raw)
    elif codec == "Sw":
        codec_id = CODEC_ID_SW
        # Stream/windowing codec – delegate to Sw prototype which embeds
        # stream metadata (sample_rate, window_size, format) alongside the compressed body.
        core_payload = stream_compress(raw)
    elif codec == "Sx":
        codec_id = CODEC_ID_SX
        # Semantic eXperiment / accelerator-friendly codec – delegate to the
        # Sx prototype which uses local dictionary substitution for text and
        # falls back to core compression for non-text.
        core_payload = sx_compress(raw)
    elif codec == "Sy":
        codec_id = CODEC_ID_SY
        # Yield/priority metadata; delegate to Sy helper which embeds
        # yield metadata alongside the compressed body.
        core_payload = yield_compress(raw)
    elif codec == "Sz":
        codec_id = CODEC_ID_SZ
        # Zero-copy/layout-focused codec – delegate to Sz prototype which
        # performs block-level dedup/compression on the body.
        core_payload = sz_compress(raw)
    elif codec == "St":
        codec_id = CODEC_ID_ST
        # Semantic Table codec – delegate to St prototype which embeds
        # table schema metadata (columns, types) alongside the compressed body.
        core_payload = table_compress(raw)
    else:
        # Unknown labels: fall back to Sb semantics but keep compatibility.
        codec_id = CODEC_ID_SB
        core_payload = core_compress(raw, method="auto")

    tid = 0 if template_id is None else int(template_id)
    header = SemanticHeader(codec_id=codec_id, domain_id=domain_id, template_id=tid)
    return header.to_bytes() + core_payload


def semantic_decompress(payload: bytes) -> bytes:
    """Decompress data produced by :func:`semantic_compress`."""
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError("semantic_decompress() expects a bytes-like object")
    header, body = SemanticHeader.from_bytes(bytes(payload))
    if header.codec_id == CODEC_ID_SA:
        # Header-only Sa: resolve atom via Sa table.
        if not body:
            atom = sa_get_atom(header.domain_id, header.template_id)
            if atom is None:
                return b""
            return atom
            # Legacy Sa payloads fall back to core decompression.
            return core_decompress(body)
    if header.codec_id == CODEC_ID_SB:
        # Header-only Sb: resolve template via Sb table when available.
        if not body:
            template = sb_get_template(header.domain_id, header.template_id)
            if template is not None:
                return template
        # Fallback: legacy Sb payloads are handled by the core codec.
        return core_decompress(body)
    if header.codec_id == CODEC_ID_SD:
        # Decode the core payload then undo the derivative transform.
        derived = core_decompress(body)
        return decode_derivative(derived)
    if header.codec_id == CODEC_ID_SC:
        return combo_decompress(body)
    if header.codec_id == CODEC_ID_SE:
        return entropy_decompress(body)
    if header.codec_id == CODEC_ID_SQ:
        # Sq bodies are already binary quantized payloads; return as-is
        # so higher-level helpers can decode them into floats.
        return body
    if header.codec_id == CODEC_ID_SK:
        # Sk embeds key metadata; decompress and return just the data.
        # Note: key metadata is discarded in this simple API. For access to
        # keys, use semantic_key.decompress() directly.
        data, _metadata = key_decompress(body)
        return data
    if header.codec_id == CODEC_ID_SL:
        # Sl embeds learned/latent codec metadata; decompress and return data.
        data, _meta = sl_decompress(body)
        return data
    if header.codec_id == CODEC_ID_SH:
        # Sh embeds hash metadata; decompress and return just the data.
        # Note: hash metadata is discarded in this simple API. For access to
        # algorithm and digest, use semantic_hash.decompress() directly.
        data, _algorithm, _digest = hash_decompress(body)
        return data
    if header.codec_id == CODEC_ID_SI:
        # Si embeds index metadata; decompress and return just the data.
        # Note: index metadata is discarded in this simple API. For access to
        # index info, use semantic_index.decompress() directly.
        data, _index = index_decompress(body)
        return data
    if header.codec_id == CODEC_ID_SN:
        # Sn embeds node location metadata; decompress and return just the data.
        # Note: location metadata is discarded in this simple API. For access to
        # node location, use semantic_node.decompress() directly.
        data, _location = node_decompress(body)
        return data
    if header.codec_id == CODEC_ID_SO:
        # So embeds orchestration graph metadata; decompress and return just the data.
        # Note: graph metadata is discarded in this simple API. For access to
        # orchestration graph, use semantic_orchestration.decompress() directly.
        data, _graph = orchestration_decompress(body)
        return data
    if header.codec_id == CODEC_ID_SP:
        # Sp embeds pattern metadata; decompress and return just the data.
        # Note: pattern and fields are discarded in this simple API. For access to
        # pattern metadata, use semantic_pattern.decompress() directly.
        data, _pattern, _fields = pattern_decompress(body)
        return data
    if header.codec_id == CODEC_ID_SM:
        return sm_decompress(body)
    if header.codec_id == CODEC_ID_SY:
        # Sy embeds yield metadata; decompress and return just the data.
        data, _yield = yield_decompress(body)
        return data
    if header.codec_id == CODEC_ID_SR:
        # Sr embeds resolver/routing hints; decompress and return just the data.
        # Note: routing hints are discarded in this simple API. For access to
        # hints, use semantic_resolver.decompress() directly.
        data, _hints = resolver_decompress(body)
        return data
    if header.codec_id == CODEC_ID_SV:
        # Sv embeds vector metadata; decompress and return just the data.
        # Note: vector metadata is discarded in this simple API. For access to
        # metadata, use semantic_vector.decompress() directly.
        data, _metadata = vector_decompress(body)
        return data
    if header.codec_id == CODEC_ID_SW:
        # Sw embeds stream metadata; decompress and return just the data.
        # Note: stream metadata is discarded in this simple API. For access to
        # metadata, use semantic_stream.decompress() directly.
        data, _metadata = stream_decompress(body)
        return data
    if header.codec_id == CODEC_ID_ST:
        # St embeds table schema; decompress and return just the data.
        # Note: table schema is discarded in this simple API. For access to
        # schema, use semantic_table.decompress() directly.
        data, _schema = table_decompress(body)
        return data
    if header.codec_id == CODEC_ID_SX:
        return sx_decompress(body)
    if header.codec_id == CODEC_ID_SU:
        return su_decompress(body)
    if header.codec_id == CODEC_ID_SZ:
        return sz_decompress(body)
    if header.codec_id == CODEC_ID_SG:
        return grain_decompress(body)
    if header.codec_id == CODEC_ID_SF:
        return flow_decompress(body)
    if header.codec_id == CODEC_ID_SS:
        # Ss uses frequency-based cache substitution; decompress and return data.
        # Note: cache metadata is discarded in this simple API. For access to
        # cache statistics, use semantic_cache.decompress() directly.
        data, _metadata = cache_decompress(body)
        return data
    # For v1 we otherwise ignore codec_id/domain_id/template_id in the data
    # path and simply delegate to the core compressor.
    return core_decompress(body)
