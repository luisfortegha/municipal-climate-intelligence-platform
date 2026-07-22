
from __future__ import annotations
from dataclasses import dataclass
from typing import List
import os
from datetime import datetime, timedelta
import earthaccess
import numpy as np
import h5py
from pathlib import Path
from analysis.logger import logger
import pickle
import time

class GPMServiceError(Exception):
    """Raised when NASA GPM retrieval fails."""
    pass


@dataclass
class RainfallObservation:

    timestamp: str

    precipitation_mm: float


@dataclass
class GPMObservation:

    observations: List[RainfallObservation]

    latest_mm: float | None

    accumulation_24h: float | None

    accumulation_48h: float | None

    accumulation_72h: float | None

    maximum_interval_mm: float | None

    trend: str | None

    source: str

    status: str


def _login():

    username = os.getenv("EARTHDATA_USERNAME")
    password = os.getenv("EARTHDATA_PASSWORD")

    if not username or not password:

        raise GPMServiceError(
            "EARTHDATA_USERNAME and EARTHDATA_PASSWORD must be configured."
        )

    earthaccess.login(
        strategy="environment",
        persist=False,
    )

CACHE_DIR = Path(__file__).parent.parent / "data" / "gpm_cache"

RETENTION_DAYS = 7


def latest_cached_timestamp():

    files = list(CACHE_DIR.glob("*.HDF5"))

    if not files:
        return None

    newest = max(
        files,
        key=lambda f: f.stat().st_mtime,
    )

    return datetime.utcfromtimestamp(
        newest.stat().st_mtime,
    )

def cleanup_cache():

    cutoff = datetime.utcnow() - timedelta(days=RETENTION_DAYS)

    for file in CACHE_DIR.glob("*.HDF5"):

        modified = datetime.utcfromtimestamp(
            file.stat().st_mtime,
        )

        if modified < cutoff:

            file.unlink()

            print(
                f"Removed cache: {file.name}"
            )

def get_precipitation_timeseries(
    study_area,
):

    cache_file = CACHE_DIR / f"{study_area.name}_summary.pkl"

    CACHE_HOURS = 6

    if cache_file.exists():

        age = (
            time.time()
            - cache_file.stat().st_mtime
        )
    
        if age < CACHE_HOURS * 3600:
    
            with open(
                cache_file,
                "rb",
            ) as f:

                return pickle.load(f)

    _login()

    cleanup_cache()

    end = datetime.utcnow()

    start = end - timedelta(hours=72)
    
    west, south, east, north = study_area.bounds

    granules = earthaccess.search_data(

        short_name="GPM_3IMERGHHE",

        version="07",

        temporal=(
            start,
            end,
        ),

        bounding_box=(
            west,
            south,
            east,
            north,
        ),
    )

    logger.info(
        f"NASA GPM granules located: {len(granules)}"
    )

    if not granules:

        return GPMObservation(
    
            observations=[],
    
            latest_mm=None,
    
            accumulation_24h=None,

            accumulation_48h=None,
    
            accumulation_72h=None,
        
            maximum_interval_mm=None,
    
            trend=None,
    
            source="NASA GES DISC",
    
            status="No observations found",
        )
    
    download_dir = os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "gpm_cache",
    )
    
    os.makedirs(
        download_dir,
        exist_ok=True,
    )
    
    before = set(
        CACHE_DIR.glob("*.HDF5")
    )
    
    if latest_cached_timestamp():

        age = (
            datetime.utcnow()
            - latest_cached_timestamp()
        )

        if age < timedelta(hours=1):

            print(
                "NASA cache current."
            )

        else:

            earthaccess.download(
                granules,
                local_path=download_dir,
            )
    
    files = sorted(
        CACHE_DIR.glob("*.HDF5")
    )
    
    new_downloads = len(
        set(files) - before
    )

    logger.info(f"New NASA downloads: {new_downloads}")
    logger.info(f"Cached files: {len(files)}")
    logger.info(f"Downloaded {len(files)} files.")
    
    observations = []

    for file in sorted(files):

        with h5py.File(file, "r") as f:

            grid = f["Grid"]
    
            precipitation = grid["precipitation"][:]
    
            latitudes = grid["lat"][:]
    
            longitudes = grid["lon"][:]
    
            west, south, east, north = study_area.bounds
    
            lat_mask = (
                (latitudes >= south)
                &
                (latitudes <= north)
            )
    
            lon_mask = (
                (longitudes >= west)
                &
                (longitudes <= east)
            )
    
            if not lat_mask.any() or not lon_mask.any():
                continue
    
            subset = precipitation[
                ...,
                lon_mask,
                :
            ]
    
            subset = subset[
                ...,
                :,
                lat_mask
            ]

            mean_precip = float(
                np.nanmean(subset)
            )
    
            timestamp = str(grid["time"][0])
    
            observations.append(
    
                RainfallObservation(
    
                    timestamp=timestamp,
    
                    precipitation_mm=mean_precip,
    
                )
    
            )

    if not observations:

        return GPMObservation(
    
            observations=[],
    
            latest_mm=None,
    
            accumulation_24h=None,
    
            accumulation_48h=None,
    
            accumulation_72h=None,
    
            maximum_interval_mm=None,
    
            trend=None,
    
            source="NASA GES DISC",
    
            status="No observations inside study area",
        )

    values = np.array(
        [
            o.precipitation_mm
            for o in observations
        ],
        dtype=float,
    )

    # Remove fill values and invalid measurements
    values = np.where(
        values < 0,
        np.nan,
        values,
    )
    
    if np.all(np.isnan(values)):

        observation = GPMObservation(

            observations=observations,
    
            latest_mm=None,
    
            accumulation_24h=None,
    
            accumulation_48h=None,
    
            accumulation_72h=None,
    
            maximum_interval_mm=None,
    
            trend=None,
    
            source="NASA GES DISC",
    
            status="No valid precipitation values",
    
        )

        with open(
            cache_file,
            "wb",
        ) as f:

            pickle.dump(
                observation,
                f,
            )

        return observation

    latest = float(
        np.nanmean(
            values[-1:]
        )
    )
    
    acc24 = float(
        np.nansum(
            values[-48:]
        )
    )
    
    acc48 = float(
        np.nansum(
            values[-96:]
        )
    )
    
    acc72 = float(
        np.nansum(
            values
        )
    )
    
    maximum = float(
        np.nanmax(
            values
        )
    )
    
    trend = "Stable"
    
    if len(values) >= 12:
    
        previous = np.nanmean(
            values[-12:-6]
        )
        
        recent = np.nanmean(
            values[-6:]
        )
    
        if recent > previous:
    
            trend = "Increasing"
    
        elif recent < previous:
    
            trend = "Decreasing"


    logger.info(
        f"""
    NASA GPM Summary
    
    Latest: {latest:.2f} mm
    
    24 h: {acc24:.2f} mm
    
    48 h: {acc48:.2f} mm
    
    72 h: {acc72:.2f} mm
    
    Maximum: {maximum:.2f} mm
    
    Trend: {trend}
    """
    )

    observation = GPMObservation(
    
        observations=observations,

        latest_mm=latest,
    
        accumulation_24h=acc24,
    
        accumulation_48h=acc48,
    
        accumulation_72h=acc72,
    
        maximum_interval_mm=maximum,
    
        trend=trend,
    
        source="NASA GES DISC",
    
        status="Operational",

    )

    with open(
        cache_file,
        "wb",
    ) as f:

        pickle.dump(
            observation,
            f,
        )

    return observation