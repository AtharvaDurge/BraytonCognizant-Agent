import io
import pandas as pd

def get_clean_dataframe_from_bytes(file_bytes: bytes) -> pd.DataFrame:
    text_data = file_bytes.decode("utf-8")
    data_buffer = io.StringIO(text_data)
    
    # NASA C-MAPSS FD001: 26 columns total
    cmapss_headers = [
        'unit', 'cycle', 'op1', 'op2', 'op3',
        'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9', 'S10',
        'S11', 'S12', 'S13', 'S14', 'S15', 'S16', 'S17', 'S18', 'S19', 'S20', 'S21'
    ]
    
    df = pd.read_csv(data_buffer, sep=r"\s+", header=None, names=cmapss_headers)
    return df.apply(pd.to_numeric)

def get_sensor_mapping(df):
    """Dynamically identifies sensor columns based on value ranges."""
    # Mapping based on NASA physical telemetry ranges
    # Returns a map like {"HpcBleed": "S17", ...}
    mapping = {}
    for col in [f'S{i}' for i in range(1, 22)]:
        mean = df[col].mean()
        if 640 < mean < 650: mapping['T24'] = col
        elif 1580 < mean < 1600: mapping['T30'] = col
        elif 1400 < mean < 1410: mapping['T50'] = col
        elif 550 < mean < 560: mapping['P30'] = col
        elif 2388 < mean < 2389: mapping['Nf'] = col
        elif 9000 < mean < 9100: mapping['Nc'] = col
        elif 47 < mean < 48: mapping['Ps30'] = col
        elif 390 < mean < 400: mapping['HpcBleed'] = col
        elif 38 < mean < 40: mapping['W31'] = col
        elif 23 < mean < 24: mapping['W32'] = col
    return mapping