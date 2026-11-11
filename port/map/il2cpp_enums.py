"""Read enum names and constant values from the game's IL2CPP metadata (global-metadata.dat, data only).

The metadata stores every managed type's name, its fields and their default (constant) values. Enum members are
static literal fields, so their names and values can be read without running anything. Underlying types live in
GameAssembly, not in the metadata, so a value's width is taken from the gap to the next value in the data blob,
and v29+'s compressed 32-bit encoding is decoded when the width is not 1, 2 or 8.

  python port/map/il2cpp_enums.py METADATA [NAME_SUBSTRING ...]      # prints JSON {Namespace.Type: {member: value}}
"""
import json, struct, sys
from pathlib import Path

SECTIONS = ['stringLiteral', 'stringLiteralData', 'string', 'events', 'properties', 'methods', 'parameterDefaultValues',
            'fieldDefaultValues', 'fieldAndParameterDefaultValueData', 'fieldMarshaledSizes', 'parameters', 'fields']


def load(path):
    """Metadata v38+ (Unity 6): the header holds (offset, size, count) per section and index widths vary."""
    d = Path(path).read_bytes()
    magic, version = struct.unpack_from('<Ii', d, 0)
    if magic != 0xFAB11BAF: raise ValueError('not IL2CPP metadata')
    if version < 38: raise ValueError(f'metadata version {version}: only v38+ is handled')
    sec = {name: struct.unpack_from('<iii', d, 8 + 12 * i) for i, name in enumerate(SECTIONS)}
    return d, version, sec


def cstr(d, base, index):
    end = d.index(b'\0', base + index)
    return d[base + index:end].decode('utf8', 'replace')


def compressed_u32(d, p):
    b = d[p]
    if b & 0x80 == 0: return b, 1
    if b & 0xc0 == 0x80: return ((b & 0x3f) << 8) | d[p + 1], 2
    if b & 0xe0 == 0xc0: return ((b & 0x1f) << 24) | (d[p + 1] << 16) | (d[p + 2] << 8) | d[p + 3], 4
    if b == 0xf0: return struct.unpack_from('<I', d, p + 1)[0], 5
    if b == 0xfe: return 0xffffffff - 1, 1
    if b == 0xff: return 0xffffffff, 1
    raise ValueError('bad compressed integer')


def compressed_i32(d, p):
    v, n = compressed_u32(d, p)
    return (-(v >> 1) - 1 if v & 1 else v >> 1), n


def enums(path, wanted=()):
    """{first member name: {member: value}} for every enum (a 'value__' field followed by constant fields)."""
    d, version, sec = load(path)
    s_off = sec['string'][0]
    f_off, f_size, f_count = sec['fields']
    dv_off, dv_size, dv_count = sec['fieldDefaultValues']
    data_off, data_size, _ = sec['fieldAndParameterDefaultValueData']
    fw = f_size // f_count; dw = dv_size // dv_count
    if (fw, dw) != (10, 10): raise ValueError(f'unexpected record sizes {fw}, {dw}')
    defaults = {}
    for i in range(dv_count):   # fieldIndex u32, typeIndex u16, dataIndex u32
        field, _, index = struct.unpack_from('<IHI', d, dv_off + dw * i)
        defaults[field] = index
    starts = sorted(set(defaults.values())) + [data_size]
    width = {a: b - a for a, b in zip(starts, starts[1:])}
    name = lambda k: cstr(d, s_off, struct.unpack_from('<I', d, f_off + fw * k)[0])
    out, k = {}, 0
    while k < f_count:
        if name(k) != 'value__': k += 1; continue
        members = {}; k += 1
        while k < f_count and k in defaults and name(k) != 'value__':
            p = data_off + defaults[k]; w = width.get(defaults[k], 0)
            if w == 8: v = struct.unpack_from('<q', d, p)[0]
            elif w == 2: v = struct.unpack_from('<h', d, p)[0]
            elif w == 1: v = d[p]
            else:
                try: v = compressed_i32(d, p)[0]
                except ValueError: v = None
            members[name(k)] = v; k += 1
        if members and (not wanted or any(x in members for x in wanted)):
            out[next(iter(members))] = members
    return version, out


if __name__ == '__main__':
    version, out = enums(sys.argv[1], sys.argv[2:])
    print(json.dumps({'metadata_version': version, 'types': out}, indent=1))
