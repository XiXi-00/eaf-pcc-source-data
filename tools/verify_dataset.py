"""Verify the packaged data using only the Python standard library."""
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import csv
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parent.parent

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def read_table(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))

def main():
    checks = (ROOT/'checksums.sha256').read_text(encoding='utf-8').splitlines()
    for entry in checks:
        expected, name = entry.split('  ', 1)
        path = (ROOT/name).resolve()
        require(path.is_relative_to(ROOT.resolve()), 'Checksum path leaves repository')
        require(path.is_file(), 'Missing file: '+name)
        require(hashlib.sha256(path.read_bytes()).hexdigest() == expected, 'Checksum mismatch: '+name)
    metadata = json.loads((ROOT/'metadata/dataset_manifest.json').read_text(encoding='utf-8'))
    measurement = read_table(ROOT/'data/processed/pcc_measurements_aligned.csv')
    sequence = read_table(ROOT/'data/processed/data1_gru_phase_sequence.csv')
    wide = read_table(ROOT/'data/processed/data1_physical_model_dataset.csv')
    require(len(measurement) == len(wide) == 1140, 'Unexpected aligned row count')
    require(len(measurement[0]) == 148, 'Unexpected aligned column count')
    require(len(wide[0]) == 77, 'Unexpected historical wide-table column count')
    require(len(sequence) == 3420 and len(sequence[0]) == 22, 'Unexpected phase sequence shape')
    times = [datetime.strptime(r['Timestamp'], '%Y-%m-%d %H:%M:%S') for r in measurement]
    require(len(set(times)) == 1140 and times == sorted(times), 'Timestamps must be unique and sorted')
    require(str(times[0]) == metadata['time_window']['start'], 'Unexpected start time')
    require(str(times[-1]) == metadata['time_window']['end'], 'Unexpected end time')
    require(all((b-a).total_seconds() == 60 for a,b in zip(times,times[1:])), 'Unexpected time interval')
    require(all(math.isfinite(float(v)) for r in measurement for k,v in r.items() if k != 'Timestamp'), 'Missing or nonfinite aligned measurement')
    lookup = {r['Timestamp']:r for r in measurement}
    wide_lookup = {r['Timestamp']:r for r in wide}
    phase_counts = Counter()
    split_counts = Counter()
    timestamp_splits = defaultdict(set)
    seen = set()
    for r in sequence:
        phase = r['Phase']
        timestamp = r['Timestamp']
        idx = int(r['TimeIndex'])
        require((phase,timestamp) not in seen, 'Duplicate phase/time key')
        seen.add((phase,timestamp))
        require(times[idx-1].strftime('%Y-%m-%d %H:%M:%S') == timestamp, 'TimeIndex mismatch')
        split = 'Train' if idx <= 798 else 'Validation' if idx <= 969 else 'Test'
        require(r['Split'] == split, 'Nonchronological split')
        require(wide_lookup[timestamp]['Split'] == split, 'Wide-table split mismatch')
        reference = float(r['Reference_RealActivePower_kW'])
        baseline = float(r['Feature_CassieMayrPower_kW'])
        target = float(r['Target_ActivePowerResidual_kW'])
        measured = float(lookup[timestamp]['power__Active power '+phase])
        require(reference == measured, 'Reference power differs from aligned measurement')
        require(reference == float(wide_lookup[timestamp]['RealActivePower_'+phase+'_kW']), 'Reference power differs from wide table')
        require(math.isclose(reference-baseline,target,rel_tol=1e-10,abs_tol=1e-8), 'Residual identity failed')
        phase_counts[phase] += 1
        split_counts[split] += 1
        timestamp_splits[timestamp].add(split)
    require(phase_counts == dict(L1=1140,L2=1140,L3=1140), 'Unexpected phase counts')
    require(split_counts == dict(Train=2394,Validation=513,Test=513), 'Unexpected split counts')
    require(all(len(v)==1 for v in timestamp_splits.values()), 'Same-time phases cross data splits')
    print(json.dumps(dict(verified=True,checksummed_files=len(checks),data_files=len(metadata['files']),
                          timestamps=len(times),phase_rows=len(sequence),splits=dict(split_counts)),indent=2))

if __name__ == '__main__':
    main()
