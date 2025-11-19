from datetime import datetime
from pathlib import Path

import numpy as np
import numpy.typing as npt
import sep  # type: ignore
from astropy.coordinates import SkyCoord  # type: ignore
from astropy.io import fits  # type: ignore
from astropy.wcs import WCS  # type: ignore
from astropy.wcs.utils import fit_wcs_from_points  # type: ignore
from keplemon.bodies import Constellation, Observatory
from keplemon.elements import TopocentricElements
from keplemon.enums import ReferenceFrame
from keplemon.time import Epoch, TimeSpan
from numpy.lib import recfunctions as rfn
from pydantic import BaseModel, Field

from pixelemon._plate_solve import PlateSolve, TetraSolver
from pixelemon._telescope import Telescope
from pixelemon.constants import BASE_TO_KILO, KILO_TO_BASE, MAD_TO_STD, PERCENT_TO_DECIMAL, SUN_MAGNITUDE
from pixelemon.correlation import CorrelatedDetection, CorrelationCandidate, CorrelationCandidates, CorrelationSettings
from pixelemon.logging import PixeLemonLog
from pixelemon.processing import (
    MIN_BACKGROUND_MESH_COUNT,
    BackgroundSettings,
    Detection,
    DetectionLine,
    Detections,
    DetectionSettings,
)


class TelescopeImage(BaseModel):
    _original_array: npt.NDArray[np.float32] | None = None
    _processed_array: npt.NDArray[np.float32] | None = None
    _segmentation_map: npt.NDArray[np.int32] | None = None
    _star_segments: npt.NDArray[np.int32] | None = None
    _plate_solve: PlateSolve | None = None
    _satellites: Detections | None = None
    _background: sep.Background | None = None
    _background_removed: bool = False
    epoch: datetime | None = None
    telescope: Telescope | None = None
    exposure_time: float | None = None
    _ground_site: Observatory | None = None
    _stars: Detections | None = None
    _wcs: WCS | None = None
    image_scale: float = Field(default=1.0, description="The image scale due to cropping")
    background_settings: BackgroundSettings = Field(default=BackgroundSettings())
    detection_settings: DetectionSettings = Field(default=DetectionSettings.streak_source_defaults())
    correlation_settings: CorrelationSettings = Field(default=CorrelationSettings())

    @classmethod
    def from_fits_file(cls, file_path: Path, telescope: Telescope) -> "TelescopeImage":
        with fits.open(file_path) as hdul:
            img = cls()
            assert hasattr(hdul[0], "header")
            header = getattr(hdul[0], "header")
            img.exposure_time = header["EXPTIME"]
            img._wcs = WCS(header)
            img.epoch = datetime.fromisoformat(header["DATE-OBS"])
            img.telescope = telescope
            img._original_array = getattr(hdul[0], "data").astype(np.float32)

            if "SITELAT" in header and "SITELONG" in header and "SITEALT" in header:
                lat = header["SITELAT"]
                lon = header["SITELONG"]
                h = header["SITEALT"] * BASE_TO_KILO
            elif "OBSGEO-L" in header and "OBSGEO-B" in header and "OBSGEO-H" in header:
                lon = header["OBSGEO-L"]
                lat = header["OBSGEO-B"]
                h = header["OBSGEO-H"] * BASE_TO_KILO
            else:
                site_msg = "(SITELAT, SITELONG, and SITEALT)"
                geo_msg = "(OBSGEO-L, OBSGEO-B, and OBSGEO-H)"
                raise ValueError(f"Location not found in FITS header. Expected either {site_msg} or {geo_msg}.")

            img._ground_site = Observatory(lat, lon, h)
            assert img._original_array is not None
            actual_ratio = img._original_array.shape[1] / img._original_array.shape[0]
            if not np.isclose(img.telescope.aspect_ratio, actual_ratio, atol=1e-6):
                new_width = int(img._original_array.shape[0] * img.telescope.aspect_ratio)
                img._original_array = img._original_array[:, 0:new_width]
                img._original_array = np.ascontiguousarray(img._original_array)
                new_shape = img._original_array.shape
                PixeLemonLog().warning(f"Trimmed {file_path} to expected {new_shape[0]}h x {new_shape[1]}w")
            assert img._original_array is not None
            img._processed_array = img._original_array.copy()
        return img

    def get_correlation_candidates(self, sats: Constellation) -> CorrelationCandidates:
        if self._ground_site is None:
            raise ValueError("Ground site is not set.")
        solve = self.plate_solve
        if solve is None:
            raise ValueError("Plate solve is not available.")
        if self.epoch is None:
            raise ValueError("Image epoch is not set.")
        if self.exposure_time is None:
            raise ValueError("Exposure time is not set.")

        kepoch = Epoch.from_datetime(self.epoch) + TimeSpan.from_seconds(self.exposure_time * 0.5)

        sats_in_fov = self._ground_site.get_field_of_view_report(
            kepoch,
            TopocentricElements.from_j2000(
                kepoch,
                solve.right_ascension,
                solve.declination,
            ),
            self.horizontal_field_of_view * 0.5,
            sats,
            ReferenceFrame.J2000,
        )

        correlation_candidates = CorrelationCandidates([])
        for start_candidate in sats_in_fov.candidates:

            r = start_candidate.direction.range
            assert r is not None
            r = r * KILO_TO_BASE
            area = self.detection_settings.satellite_area
            albedo = self.detection_settings.satellite_albedo
            vis_mag = SUN_MAGNITUDE + 2.5 * np.log10((4 * np.pi * r**2) / (albedo * area))
            if vis_mag <= self.detection_settings.limiting_magnitude:
                sat_range = start_candidate.direction.range
                assert sat_range is not None

                xc, yc = self.get_fits_pixels(
                    start_candidate.direction.right_ascension,
                    start_candidate.direction.declination,
                )

                correlation_candidate = CorrelationCandidate(
                    id=start_candidate.satellite_id,
                    x_centroid=xc,
                    y_centroid=yc,
                    range=sat_range,
                )
                correlation_candidates.root.append(correlation_candidate)

        return correlation_candidates

    def get_angular_distance(self, x0: float, y0: float, x1: float, y1: float) -> float:
        if self._wcs is None:
            raise ValueError("WCS is not set.")
        sky0 = self._wcs.pixel_to_world(x0, y0)
        sky1 = self._wcs.pixel_to_world(x1, y1)
        return sky0.separation(sky1).deg

    def get_angles(self, x: float, y: float) -> tuple[float, float]:
        if self._wcs is None:
            raise ValueError("WCS is not set.")
        sky = self._wcs.pixel_to_world(x, y)
        return sky.ra.deg, sky.dec.deg

    def get_correlation_to_candidate(self, candidate: CorrelationCandidate) -> CorrelatedDetection | None:
        detections = self.satellites
        if len(detections) == 0:
            return None

        angular_distances = []

        for det in detections:
            xc, yc = det.x_centroid, self.height - 1 - det.y_centroid
            angular_distances.append(self.get_angular_distance(xc, yc, candidate.x_centroid, candidate.y_centroid))

        best_angular_distance = int(np.argmin(angular_distances))

        if angular_distances[best_angular_distance] <= self.correlation_settings.centroid_angle_limit:
            best_i = best_angular_distance
        else:
            best_i = -1

        if best_i >= 0:
            ra_dec = self.get_angles(det.x_centroid, det.y_centroid)
            zp = self.zero_point
            assert zp is not None
            return CorrelatedDetection(
                satellite_id=candidate.id,
                right_ascension=ra_dec[0],
                declination=ra_dec[1],
                magnitude=det.get_visual_magnitude(zp),
                angle_between_centroids=angular_distances[best_i],
                cross_line_of_sight_range=candidate.range * np.deg2rad(angular_distances[best_i]),
            )
        else:
            return None

    def get_correlation_to_detection(self, det: Detection, sats: CorrelationCandidates) -> CorrelatedDetection | None:

        xc, yc = det.x_centroid, self.height - 1 - det.y_centroid
        angular_distances = []

        for candidate in sats:
            angular_distances.append(self.get_angular_distance(xc, yc, candidate.x_centroid, candidate.y_centroid))

        best_angular_distance = int(np.argmin(angular_distances))
        if angular_distances[best_angular_distance] <= self.correlation_settings.centroid_angle_limit:
            best_i = best_angular_distance
        else:
            best_i = -1

        if best_i >= 0:
            candidate = sats[best_i]
            ra_dec = self.get_angles(det.x_centroid, det.y_centroid)
            zp = self.zero_point
            assert zp is not None
            return CorrelatedDetection(
                satellite_id=candidate.id,
                right_ascension=ra_dec[0],
                declination=ra_dec[1],
                magnitude=det.get_visual_magnitude(zp),
                angle_between_centroids=angular_distances[best_i],
                cross_line_of_sight_range=candidate.range * np.deg2rad(angular_distances[best_i]),
            )
        else:
            return None

    def get_mask(self, detection: Detection, is_star) -> npt.NDArray[np.int32]:
        if self._segmentation_map is None and not is_star:
            raise ValueError("Segmentation map is not available. Run detection first.")
        elif self._star_segments is None and is_star:
            raise ValueError("Star segmentation map is not available. Run star detection first.")
        elif is_star:
            assert self._star_segments is not None
            return (self._star_segments == detection.segmentation_index).astype(np.int32)
        else:
            assert self._segmentation_map is not None
            return (self._segmentation_map == detection.segmentation_index).astype(np.int32)

    def get_streak_line(self, detection: Detection, is_star) -> DetectionLine:
        if self._processed_array is None:
            raise ValueError("Image array is not loaded.")
        mask = self.get_mask(detection, is_star)
        y_indices, x_indices = np.nonzero(mask)
        y_indices = self.height - 1 - y_indices

        if len(x_indices) < 2:
            raise ValueError("Not enough points to fit a line.")
        a_mat = np.vstack([x_indices, np.ones(len(x_indices))]).T
        m, b = np.linalg.lstsq(a_mat, y_indices, rcond=None)[0]

        x0 = x_indices.min()
        y0 = m * x0 + b
        x1 = x_indices.max()
        y1 = m * x1 + b
        length = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5

        return DetectionLine(
            slope=m,
            intercept=b,
            length=length,
            x_centroid=detection.x_centroid,
            y_centroid=detection.y_centroid,
        )

    def get_fits_line(self, detection: Detection, is_star) -> tuple[tuple[float, float], tuple[float, float]]:
        xc, yc = detection.x_centroid, self.height - 1 - detection.y_centroid
        theta = detection.angle_to_horizon

        streak_line = self.get_streak_line(detection, is_star)

        length = streak_line.length
        dx = (length / 2) * np.cos(theta)
        dy = (length / 2) * np.sin(-theta)
        return (xc - dx, yc - dy), (xc + dx, yc + dy)

    def get_fits_circle(self, detection: Detection, is_star) -> tuple[tuple[float, float], tuple[float, float]]:
        xc, yc = detection.x_centroid, self.height - 1 - detection.y_centroid
        streak = self.get_streak_line(detection, is_star)
        r = streak.length / 2
        return (xc - r, yc - r), (xc + r, yc + r)

    def write_to_fits_file(self, file_path: Path):
        if self._processed_array is None:
            raise ValueError("Image array is not loaded.")
        fits.writeto(file_path, self._processed_array.astype("uint8"), overwrite=True)

    def dampen_hot_rows(self):
        if self._processed_array is None:
            raise ValueError("Image array is not loaded.")
        row_means = np.mean(self._processed_array, axis=1)
        global_mean = np.mean(row_means)
        global_std = np.std(row_means)
        threshold = global_mean + self.detection_settings.satellite_sigma * global_std
        for i, row_mean in enumerate(row_means):
            if row_mean > threshold:
                PixeLemonLog().debug(f"Dampening hot row {i} with mean {row_mean:.2f}")
                self._processed_array[i, :] *= global_mean / row_mean

    def crop(self, crop_percent: float):
        if self._original_array is None:
            raise ValueError("Image array is not loaded.")

        crop_fraction = crop_percent * PERCENT_TO_DECIMAL
        height, width = self._original_array.shape
        crop_height = int(height * crop_fraction / 2)
        crop_width = int(width * crop_fraction / 2)
        self._processed_array = np.ascontiguousarray(
            self._original_array[crop_height : height - crop_height, crop_width : width - crop_width]
        )
        self.image_scale = self.image_scale * (1.0 - crop_fraction)
        self._plate_solve = None
        self._satellites = None
        self._segmentation_map = None
        self._star_segments = None
        self._stars = None
        self._background = None
        self._background_removed = False

    def get_brightest_stars(self, count: int) -> Detections:
        sorted_detections = sorted(self.stars, key=lambda det: det.total_flux, reverse=True)
        return_count = min(count, len(sorted_detections))
        return Detections(sorted_detections[:return_count])

    @property
    def background(self) -> sep.Background:
        if self._processed_array is None:
            raise ValueError("Image array is not loaded.")

        if self._background is None:

            self.dampen_hot_rows()

            bw = max(
                MIN_BACKGROUND_MESH_COUNT, int(self._processed_array.shape[1] / self.background_settings.mesh_count)
            )
            bh = max(
                MIN_BACKGROUND_MESH_COUNT, int(self._processed_array.shape[0] / self.background_settings.mesh_count)
            )

            self._background = sep.Background(
                self._processed_array,
                bw=bw,
                bh=bh,
                fw=self.background_settings.filter_size,
                fh=self.background_settings.filter_size,
                fthresh=self.background_settings.detection_threshold,
            )

        return self._background

    def remove_background(self):
        if self._processed_array is None:
            raise ValueError("Image array is not loaded.")
        self._processed_array = self._processed_array - self.background
        self._background_removed = True

    def reset(self):
        if self._original_array is None:
            raise ValueError("Image array is not loaded.")
        self._processed_array = self._original_array.copy()
        self.image_scale = 1.0
        self._background = None
        self._satellites = None
        self._stars = None
        self._plate_solve = None
        self._background_removed = False
        self._segmentation_map = None

    def get_fits_pixels(self, ra: float, dec: float) -> tuple[float, float]:
        if self._wcs is None:
            raise ValueError("WCS is not set.")
        sky = SkyCoord(ra, dec, unit="deg")
        x, y = self._wcs.world_to_pixel(sky)
        return x, y

    def get_nearest_star(self, ra: float, dec: float) -> Detection:
        x, y = self.get_fits_pixels(ra, dec)
        h = self.height
        detections = self.stars
        if len(detections) == 0:
            raise ValueError("No star detections available.")
        distances = [((det.x_centroid - x) ** 2 + (h - 1 - det.y_centroid - y) ** 2) ** 0.5 for det in detections]
        nearest_index = int(np.argmin(distances))
        return detections[nearest_index]

    @property
    def horizontal_field_of_view(self) -> float:
        if self.telescope is None:
            raise ValueError("Telescope is not set.")
        return self.telescope.horizontal_field_of_view * self.image_scale

    @property
    def vertical_field_of_view(self) -> float:
        if self.telescope is None:
            raise ValueError("Telescope is not set.")
        return self.telescope.vertical_field_of_view * self.image_scale

    @property
    def diagonal_field_of_view(self) -> float:
        if self.telescope is None:
            raise ValueError("Telescope is not set.")
        return self.telescope.diagonal_field_of_view * self.image_scale

    @property
    def stars(self) -> Detections:
        if self._processed_array is None:
            raise ValueError("Image array is not loaded.")

        if not self._background_removed:
            self.remove_background()

        if self._stars is None:
            objects, self._star_segments = sep.extract(
                self._processed_array,
                thresh=self.detection_settings.star_sigma * self.background.globalrms,
                minarea=self.detection_settings.min_pixel_count,
                filter_kernel=self.detection_settings.gaussian_kernel,
                deblend_nthresh=self.detection_settings.deblend_mesh_count,
                deblend_cont=self.detection_settings.deblend_contrast,
                clean=self.detection_settings.merge_small_detections,
                segmentation_map=True,
            )
            # add instrumental magnitude to the objects
            instrumental_mag = -2.5 * np.log10(objects["flux"] / self.exposure_time)
            objects = rfn.append_fields(objects, "inst_mag", instrumental_mag, usemask=False)

            # add segmentation index to the objects
            seg_idx = np.arange(1, len(objects) + 1, dtype=np.int32)
            objects = rfn.append_fields(objects, "seg_idx", seg_idx, usemask=False)

            elongations = objects["a"] / objects["b"]
            median_elongation = float(np.median(elongations))
            sigma_elongation = float(np.std(elongations))
            PixeLemonLog().debug(f"{len(objects)} total detections with {median_elongation:.2f} median elongation")
            mad = np.median(np.abs(elongations - median_elongation))
            sigma_elongation = MAD_TO_STD * mad  # convert MAD to standard
            sigma_limit = self.detection_settings.star_elongation_threshold * sigma_elongation
            star_detections = objects[
                (elongations >= (median_elongation - sigma_limit)) & (elongations <= (median_elongation + sigma_limit))
            ]
            PixeLemonLog().debug(f"{len(star_detections)} star-like objects selected after elongation filter")
            self._stars = Detections.from_sep_extract(star_detections)

        return self._stars

    @property
    def satellites(self):
        if self._processed_array is None:
            raise ValueError("Image array is not loaded.")

        if not self._background_removed:
            self.remove_background()

        if self._satellites is None:
            objects, self._segmentation_map = sep.extract(
                self._processed_array,
                thresh=self.detection_settings.satellite_sigma * self.background.globalrms,
                minarea=self.detection_settings.min_pixel_count,
                filter_kernel=self.detection_settings.gaussian_kernel,
                deblend_nthresh=self.detection_settings.deblend_mesh_count,
                deblend_cont=self.detection_settings.deblend_contrast,
                clean=self.detection_settings.merge_small_detections,
                segmentation_map=True,
            )

            # add instrumental magnitude to the objects
            instrumental_mag = -2.5 * np.log10(objects["flux"] / self.exposure_time)
            objects = rfn.append_fields(objects, "inst_mag", instrumental_mag, usemask=False)

            # add segmentation index to the objects
            seg_idx = np.arange(1, len(objects) + 1, dtype=np.int32)
            objects = rfn.append_fields(objects, "seg_idx", seg_idx, usemask=False)

            elongations = objects["a"] / objects["b"]
            median_elongation = self.stars.elongation_median
            sigma_elongation = self.stars.elongation_sigma
            sigma_limit = self.detection_settings.satellite_elongation_threshold * sigma_elongation

            sat_detections = objects[
                (elongations >= (median_elongation + sigma_limit)) | (elongations <= (median_elongation - sigma_limit))
            ]
            PixeLemonLog().debug(f"{len(sat_detections)} satellite-like objects selected after elongation filter")
            self._satellites = Detections.from_sep_extract(sat_detections)

        return self._satellites

    @property
    def plate_solve(self) -> PlateSolve | None:
        if self._processed_array is None:
            raise ValueError("Image array is not loaded.")
        if self.telescope is None:
            raise ValueError("Telescope is not set.")

        if self._plate_solve is None:

            tetra_solve = TetraSolver().solve_from_centroids(
                self.get_brightest_stars(TetraSolver().settings.verification_star_count).y_x_array,
                size=self._processed_array.shape,
                fov_estimate=self.diagonal_field_of_view,
                return_matches=True,
            )
            plate_solve = PlateSolve.from_tetra_result(tetra_solve)

            if plate_solve is not None:

                pixel_scale = self.telescope.horizontal_pixel_scale
                assert self._wcs is not None

                # seed the WCS to improve chances of solution with fit_wcs_from_points
                self._wcs.wcs.crpix = [self._processed_array.shape[1] / 2, self._processed_array.shape[0] / 2]
                self._wcs.wcs.crval = [plate_solve.right_ascension, plate_solve.declination]
                self._wcs.wcs.ctype = ["RA---TAN", "DEC--TAN"]
                self._wcs.wcs.cunit = ["deg", "deg"]
                theta = np.deg2rad(-plate_solve.roll)
                cd11 = -pixel_scale * np.cos(theta)
                cd12 = pixel_scale * np.sin(theta)
                cd21 = pixel_scale * np.sin(theta)
                cd22 = pixel_scale * np.cos(theta)
                self._wcs.wcs.cd = np.array([[cd11, cd12], [cd21, cd22]], dtype=float)

                # invert matched centroids for WCS fitting
                yx = np.array(tetra_solve["matched_centroids"])
                x, y = yx[:, 1], self.height - 1 - yx[:, 0]
                ra_dec = np.array(tetra_solve["matched_stars"])

                # fit WCS from matched stars
                sky = SkyCoord(ra=ra_dec[:, 0], dec=ra_dec[:, 1], unit="deg")
                self._wcs = fit_wcs_from_points((x, y), sky, sip_degree=5, proj_point="center")
                self._plate_solve = plate_solve

        return self._plate_solve

    @property
    def height(self) -> int:
        if self._processed_array is None:
            raise ValueError("Image array is not loaded.")
        return self._processed_array.shape[0]

    @property
    def width(self) -> int:
        if self._processed_array is None:
            raise ValueError("Image array is not loaded.")
        return self._processed_array.shape[1]

    @property
    def zero_point(self) -> float | None:
        solve = self.plate_solve
        if solve is None:
            return None

        offsets = []
        for star in solve.matched_stars:
            detection = self.get_nearest_star(star.right_ascension, star.declination)
            offsets.append(star.magnitude - detection.instrumental_magnitude)

        if offsets:
            return float(np.mean(offsets))
        else:
            return None
