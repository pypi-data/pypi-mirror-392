import argparse
import math
from pathlib import Path

import matplotlib.patches as mpatches
import pandas as pd
import tifffile
import numpy as np
from matplotlib import cm
from matplotlib import patches
from matplotlib import pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.colors import to_rgba
from matplotlib.patches import Rectangle
from matplotlib_scalebar.scalebar import ScaleBar
from scipy import ndimage
from skimage.measure import label, regionprops
from skimage.morphology import skeletonize
from tqdm import tqdm


def run():
    parser = argparse.ArgumentParser(description="Analyze cell extension orientation")

    # Define arguments
    parser.add_argument('--input_raw', type=str, required=True,
                        help="The input raw data as TIFF (2D, 1 channel).")
    parser.add_argument('--input_target', type=str, required=False,
                        help="Masked areas used for orientation calculation (optional).")
    parser.add_argument('--output', type=str, required=False,
                        help="Output folder for saving plots; if omitted, plots are displayed.")
    parser.add_argument('--output_res', type=str, default="12:9",
                        help="Resolution of output plots as WIDTH:HEIGHT, e.g., 800:600.")
    parser.add_argument('--roi', type=str, required=False,
                        help="Region of interest as MIN_X:MAX_X:MIN_Y:MAX_Y. Multiple ROIs are comma-separated.")
    parser.add_argument('--tiles', type=str, default="100,250,500",
                        help="Tile sizes for average plots, e.g., SIZE1,SIZE2,SIZE3.")
    parser.add_argument('--max_size', type=str, required=False,
                        help="Exclude segments with area above this size (pixels).")
    parser.add_argument('--min_size', type=str, required=False,
                        help="Exclude segments with area below this size (pixels).")
    parser.add_argument('--pixel_in_micron', type=float, required=False,
                        help="Pixel width in microns, for adding a scalebar.")
    parser.add_argument('--input_table', type=str, required=False,
                        help="Table of cells to analyze, with first column as label IDs.")
    parser.add_argument('--input_labeling', type=str, required=True,
                        help="Label map for segmentation analysis (2D, 1 channel).")

    # Parse arguments
    args = parser.parse_args()

    print('Reading raw image %s and segmentation %s..' % (args.input_raw, args.input_labeling))
    image_raw = tifffile.imread(args.input_raw).T
    image = tifffile.imread(args.input_labeling).T.astype(int)
    image_target_mask = None
    image_target_distances = None
    if args.input_target is not None:
        image_target_mask = tifffile.imread(args.input_target).T.astype(bool)
        image_target_distances = ndimage.distance_transform_edt(np.invert(image_target_mask))

    # crop input images to ROI
    roi, additional_rois = get_roi(args.roi, image)  # returns array with [min_x, max_x, min_y, max_y]
    image = image[roi[0]:roi[1], roi[2]:roi[3]]
    image_raw = image_raw[roi[0]:roi[1], roi[2]:roi[3]]
    if image_target_mask is not None:
        image_target_distances = image_target_distances[roi[0]:roi[1], roi[2]:roi[3]]
        image_target_mask = image_target_mask[roi[0]:roi[1], roi[2]:roi[3]]

    pixel_in_micron = args.pixel_in_micron

    regions = get_regions(image, args.min_size, args.max_size)
    cell_table_content = analyze_segments(regions, image_target_distances, pixel_in_micron)
    write_table(cell_table_content, args.output)

    plot(cell_table_content, image_raw, image, roi, additional_rois, image_target_mask, pixel_in_micron, args.tiles,
         args.output, args.output_res)


def get_roi(crop, image):
    crop_min_x = 0
    crop_max_x = image.shape[0]
    crop_min_y = 0
    crop_max_y = image.shape[1]
    print('Input image dimensions: %sx%s' % (crop_max_x, crop_max_y))
    additional_rois = []
    roi = [crop_min_x, crop_max_x, crop_min_y, crop_max_y]
    if crop:
        crops = crop.split(",")
        for single_crop in crops:
            if len(str(single_crop).strip()) != 0:
                crop_parts = single_crop.split(":")
                if len(crop_parts) != 4:
                    exit(
                        "Please provide crop in the following form: MIN_X:MAX_X:MIN_Y:MAX_Y - for example 100:200:100:200")
                additional_rois.append([int(crop_parts[0]), int(crop_parts[1]), int(crop_parts[2]), int(crop_parts[3])])
        if len(additional_rois) == 1:
            roi = additional_rois[0]
            additional_rois = []
    return roi, additional_rois


def analyze_segments(regions, image_target, pixel_in_micron):
    cell_table_content = {
        "Label": {},
        "Area in px²": {},
        "Area in um²": {},
        "Mean": {},
        "XM": {},
        "YM": {},
        "X center biggest circle": {},
        "Y center biggest circle": {},
        "%Area": {},
        "AR": {},
        "Circ.": {},
        "Round": {},
        "Solidity": {},
        "MScore": {},
        "Length cell vector": {},
        "Absolute angle": {},
        "Rolling ball angle": {},
        "Relative angle (0-180 deg)": {},
    }
    for index, region in enumerate(tqdm(regions, desc="Processing Regions")):
        # write regionprops into table
        label = region.label

        cell_table_content["Label"][label] = label
        cell_table_content["Area in px²"][label] = region.area
        if pixel_in_micron:
            cell_table_content["Area in um²"][label] = region.area * (pixel_in_micron ** 2)
        cell_table_content["Mean"][label] = region.intensity_mean
        cell_table_content["XM"][label] = region.centroid[0]
        cell_table_content["YM"][label] = region.centroid[1]
        circularity = 0
        if region.perimeter > 0:
            circularity = max(0, min(4 * math.pi * region.area / math.pow(region.perimeter, 2), 1.0))
        cell_table_content["Circ."][label] = circularity
        cell_table_content["%Area"][label] = region.area / region.area_filled * 100 if region.area_filled > 0 else 0
        # cell_table_content["AR"][region.label] = ""
        # cell_table_content["Round"][region.label] = ""
        # cell_table_content["Solidity"][region.label] = ""
        if pixel_in_micron:
            cell_table_content["MScore"][label] = circularity * ((cell_table_content["Area in um²"][label] - 27) / 27)

        skeleton, center, length_cell_vector, absolute_angle, relative_angle, rolling_ball_angle = region_extension_analysis(
            region, image_target)

        cell_table_content["X center biggest circle"][label] = center[0]
        cell_table_content["Y center biggest circle"][label] = center[1]
        cell_table_content["Length cell vector"][label] = length_cell_vector
        cell_table_content["Absolute angle"][label] = absolute_angle
        cell_table_content["Rolling ball angle"][label] = rolling_ball_angle
        cell_table_content["Relative angle (0-180 deg)"][label] = relative_angle

    return cell_table_content


def region_extension_analysis(region, image_target):
    # skeletonize
    skeleton = skeletonize(region.intensity_image)
    # calculate distance map
    distance_region = ndimage.distance_transform_edt(region.intensity_image)
    minx, miny, maxx, maxy = region.bbox
    # calculate center
    center = np.unravel_index(np.argmax(distance_region, axis=None), distance_region.shape)
    distance_center = np.linalg.norm(distance_region[center])
    distances_center = np.indices(region.image.shape) - np.array(center)[:, None, None]
    distances_center = np.apply_along_axis(np.linalg.norm, 0, distances_center)
    # label inside/outside cell
    condition_outside = (skeleton > 0) & (distances_center - distance_center >= 0)
    pixel_locations_relevant_to_direction = np.column_stack(np.where(condition_outside))
    pixel_locations_relevant_to_direction = pixel_locations_relevant_to_direction - center
    center_translated = [center[0] + minx, center[1] + miny]
    target_vector = [0, 0]
    if image_target is not None:
        neighbor_x = [center_translated[0] + 1, center_translated[1]]
        neighbor_y = [center_translated[0], center_translated[1] + 1]
        if neighbor_x[0] < image_target.shape[0] and neighbor_y[1] < image_target.shape[1]:
            value_at_center = image_target[center_translated[0], center_translated[1]]
            value_at_neighbor_x = image_target[neighbor_x[0], neighbor_x[1]]
            value_at_neighbor_y = image_target[neighbor_y[0], neighbor_y[1]]
            target_vector = [value_at_center - value_at_neighbor_x, value_at_center - value_at_neighbor_y]

    length_cell_vector = 0
    absolute_angle = 0  # Signed angle in radians
    rolling_ball_angle = 0  # Signed angle in radians
    relative_angle = 0  # Unsigned angle in degrees [0, 180]

    if len(pixel_locations_relevant_to_direction) > 1:
        mean_outside = np.mean(pixel_locations_relevant_to_direction, axis=0)
        length = np.linalg.norm(mean_outside)

        relative_angle_rad = 0
        if image_target is not None and np.linalg.norm(target_vector) > 0:
            relative_angle_rad = angle_between(target_vector, mean_outside)
        relative_angle = np.degrees(np.abs(relative_angle_rad))

        length_cell_vector = length
        absolute_angle = angle_between((0, 1), mean_outside)

        if image_target is not None and np.linalg.norm(target_vector) > 0:
            rolling_ball_angle = angle_between((0, 1), target_vector)
        else:
            rolling_ball_angle = 0

    return skeleton, center_translated, length_cell_vector, absolute_angle, relative_angle, rolling_ball_angle


def get_regions(labeled, min_size, max_size):
    # obtain labels
    print("Labeling segmentation..")
    # Heuristic: if the image has only two unique values and one is 0, assume it's a binary mask
    unique_vals = np.unique(labeled)
    if len(unique_vals) == 2 and 0 in unique_vals:
        # Binary mask case (e.g., 0 and 255)
        binary_mask = labeled != 0  # Covers 255 or 1 as foreground
        labeled, n_components = label(binary_mask, return_num=True)

    else:
        n_components = len(unique_vals)
    print(f'{n_components} objects detected.')
    # calculate region properties
    segmentation = labeled > 0
    regions = regionprops(label_image=labeled, intensity_image=segmentation)
    regions = filter_regions_by_size(min_size, max_size, n_components, regions)
    return regions


def filter_regions_by_size(min_size, max_size, n_components, regions):
    # sort out regions which are too big
    max_area = max_size
    if max_area:
        regions = [region for region in regions if region.area < int(max_area)]
        region_count = len(regions)
        print(
            "Ignored %s labels because their region is bigger than %s pixels" % (n_components - region_count, max_area))
    # sort out regions which are too small
    min_area = min_size
    if min_area:
        regions = [region for region in regions if region.area >= int(min_area)]
        region_count = len(regions)
        print("Ignored %s labels because their region is smaller than %s pixels" % (
            n_components - region_count, min_area))
    return regions


def angle_between(v1, v2):
    """
    Returns the signed angle in radians between vectors 'v1' and 'v2' in the 2D plane.
    The result is in the interval (-π, π].
    """
    if (v1[0] == 0 and v1[1] == 0) or (v2[0] == 0 and v2[1] == 0):
        return 0.0

    v1_u = np.array(v1) / np.linalg.norm(v1)
    v2_u = np.array(v2) / np.linalg.norm(v2)

    dot = np.dot(v1_u, v2_u)
    dot = np.clip(dot, -1.0, 1.0)
    det = v1_u[0] * v2_u[1] - v1_u[1] * v2_u[0]
    angle = np.arctan2(det, dot)
    return angle


def write_table(cell_table_content, output):
    if cell_table_content is not None:
        if output:
            output = Path(output)
            output.mkdir(parents=True, exist_ok=True)
            pd.DataFrame(data=cell_table_content).to_csv(output.joinpath("cells.csv"))


def plot(cell_table, raw_image, label_image, roi, additional_rois, image_target_mask, pixel_in_micron, tiles, output,
         output_res):
    if output:
        output = Path(output)
        output.mkdir(parents=True, exist_ok=True)
    output_res = output_res.split(':')
    output_res = [int(res) for res in output_res]
    roi_colors = []
    if len(additional_rois) > 0:
        roi_colors = plot_rois(output, output_res, label_image, roi, additional_rois)

    directions = create_arrows(cell_table, image_target_mask)
    plot_all_directions(output, output_res, directions, label_image, roi, additional_rois, roi_colors,
                        image_target_mask, pixel_in_micron)

    for tile in tiles.split(','):
        tile_size = int(tile)
        # NEW: Prepare data first, then plot from the results
        tile_df = prepare_tile_data(directions, raw_image.shape, roi, tile_size, image_target_mask)
        if output:
            tile_df.to_csv(output.joinpath(f"tile_analysis_size_{tile_size}.csv"), index=False)

        plot_average_directions(output, output_res, tile_df, raw_image, roi, additional_rois, roi_colors,
                                tile_size=tile_size, image_target_mask=image_target_mask,
                                pixel_in_micron=pixel_in_micron)
    if output:
        print("Results written to %s" % output)


def create_arrows(cell_table_content, image_target_mask):
    """
    Generate arrow definitions for each cell based on a fully computed cell table.
    """
    arrows = []
    for label in cell_table_content["Label"]:
        XM = cell_table_content["X center biggest circle"][label]
        YM = cell_table_content["Y center biggest circle"][label]
        center = [XM, YM]

        length_vector = cell_table_content["Length cell vector"][label]
        absolute_angle_rad = cell_table_content["Absolute angle"][label]
        relative_angle_deg = cell_table_content["Relative angle (0-180 deg)"][label]

        dx = length_vector * np.sin(absolute_angle_rad)
        dy = length_vector * np.cos(absolute_angle_rad)

        metadata = [relative_angle_deg, absolute_angle_rad, length_vector]
        arrow = [center, [dx, dy], metadata]
        arrows.append(arrow)

    return np.array(arrows, dtype=object)


def prepare_tile_data(directions, shape, crop_extend, tile_size, image_target_mask):
    """
    Performs all calculations for the tile-based average plot and returns a DataFrame.
    """
    print(f"Calculating tile data for size {tile_size}...")
    tiles_num_x = int(shape[0] / tile_size) + 1
    tiles_num_y = int(shape[1] / tile_size) + 1

    tile_coords_x = np.array(
        [tile_x * tile_size + crop_extend[0] for tile_x, _ in np.ndindex(tiles_num_x, tiles_num_y)], dtype=int)
    tile_coords_y = np.array(
        [tile_y * tile_size + crop_extend[2] for _, tile_y in np.ndindex(tiles_num_x, tiles_num_y)], dtype=int)

    arrow_centers = np.array([d[0] for d in directions])
    arrow_indices_x = np.array(np.floor((arrow_centers[:, 0] - crop_extend[0]) / tile_size), dtype=int)
    arrow_indices_y = np.array(np.floor((arrow_centers[:, 1] - crop_extend[2]) / tile_size), dtype=int)

    results = []

    max_length = 10.
    max_count = tile_size * tile_size / 10000.

    if image_target_mask is not None:
        colormap = cm.coolwarm_r
        norm = Normalize(0, 180)
    else:
        colormap = cm.hsv
        norm = Normalize(-np.pi, np.pi)

    for index_x, index_y in tqdm(list(np.ndindex(tiles_num_x, tiles_num_y)), desc=f"Processing {tile_size}px tiles"):
        in_tile_mask = (arrow_indices_x == index_x) & (arrow_indices_y == index_y)
        tile_arrows = directions[in_tile_mask]

        cell_count = len(tile_arrows)
        tile_x_pos = index_x * tile_size + crop_extend[0]
        tile_y_pos = index_y * tile_size + crop_extend[2]

        avg_absolute_vector_x, avg_absolute_vector_y = 0.0, 0.0
        avg_relative_direction_deg = 0.0
        alpha = 0.0
        rgba_color = (0, 0, 0, 0)

        if cell_count > 0:
            arrow_vectors = np.array([d[1] for d in tile_arrows])
            arrow_metadata = np.array([d[2] for d in tile_arrows])
            lengths = arrow_metadata[:, 2]
            avg_length = np.mean(lengths)
            alpha = min(1., cell_count / max_count) * min(1., avg_length / max_length) * 0.9

            if image_target_mask is not None:
                relative_angles_deg = arrow_metadata[:, 0]
                if np.sum(lengths) > 0:
                    avg_relative_direction_deg = np.average(relative_angles_deg, weights=lengths)
                else:
                    avg_relative_direction_deg = np.mean(relative_angles_deg)
                rgba_color = colormap(norm(avg_relative_direction_deg))
            else:
                avg_vector = np.mean(arrow_vectors, axis=0)
                avg_absolute_vector_x, avg_absolute_vector_y = avg_vector[0], avg_vector[1]
                color_angle_rad = np.arctan2(-avg_absolute_vector_y, -avg_absolute_vector_x)
                rgba_color = colormap(norm(color_angle_rad))

        final_rgba = list(to_rgba(rgba_color))
        final_rgba[3] = alpha

        results.append({
            "tile_x_pos": tile_x_pos, "tile_y_pos": tile_y_pos, "tile_size": tile_size,
            "cell_count": cell_count, "avg_absolute_vector_x": avg_absolute_vector_x,
            "avg_absolute_vector_y": avg_absolute_vector_y,
            "avg_relative_direction_deg": avg_relative_direction_deg, "alpha": alpha,
            "color_r": final_rgba[0], "color_g": final_rgba[1], "color_b": final_rgba[2], "color_a": final_rgba[3],
        })
    return pd.DataFrame(results)


def plot_average_directions(output, output_res, tile_df, bg_image, roi, additional_rois, roi_colors, tile_size,
                            image_target_mask, pixel_in_micron):
    print("Plotting average directions, tile size %s..." % tile_size)
    rois = [roi]
    rois.extend(additional_rois)
    colors = ['black']
    colors.extend(roi_colors)

    plt.figure(f"Average directions tile size {tile_size}", figsize=output_res)
    plt.imshow(bg_image.T, extent=roi, origin='upper', cmap='gray')
    ax = plt.gca()
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    scalebar = None
    if pixel_in_micron:
        scalebar = ScaleBar(pixel_in_micron, 'um', location='upper right', color='white', box_color='black')
        plt.gca().add_artist(scalebar)

    plot_grid(tile_df, tile_size, image_target_mask)
    if image_target_mask is not None:
        generate_target_contour(image_target_mask)

    plt.margins(0, 0)
    plt.tight_layout(pad=1)
    if output:
        for i, region in enumerate(rois):
            adjust_to_region(roi[3] + roi[2], region, colors[i], scalebar if pixel_in_micron else None)
            plt.savefig(
                output.joinpath(f'directions_tile{tile_size}_{region[0]}-{region[1]}-{region[2]}-{region[3]}.png'))
        plt.close()
    else:
        plt.show()


def plot_arrows(x, y, u, v):
    norm = Normalize(-np.pi, np.pi)
    colors = np.arctan2(v, u)
    colormap = cm.hsv
    return plt.quiver(x, y, u, v, color=colormap(norm(colors)), angles='xy', width=0.003)


def plot_arrows_relative(x, y, u, v, relative_angle_deg):
    norm = Normalize(0, 180)
    colormap = cm.coolwarm_r  # Reversed map: low angle (towards) is hot/red
    return plt.quiver(x, y, u, v, color=colormap(norm(relative_angle_deg)), angles='xy', width=2, units='dots')


def plot_grid(tile_df, tile_size, image_target_mask):
    # Draw tiles using pre-calculated colors from the DataFrame
    for _, row in tile_df.iterrows():
        if row['cell_count'] > 0:
            facecolor = (row['color_r'], row['color_g'], row['color_b'], row['color_a'])
            plt.gca().add_patch(
                Rectangle((row['tile_x_pos'], row['tile_y_pos']), tile_size, tile_size, facecolor=facecolor))

    # Generate the legend with numerical ranges
    if image_target_mask is not None:
        colormap = cm.coolwarm_r
        norm = Normalize(0, 180)
        sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=plt.gca(), location='bottom', pad=0.01, aspect=50, ticks=[0, 90, 180])
        cbar.set_ticklabels(['Towards (0°)', 'Perpendicular (90°)', 'Away (180°)'])
        cbar.set_label("Alignment with Target Gradient (Angle in Degrees)")
        circ1 = mpatches.Rectangle((0, 0), 1, 1, edgecolor='#ff0000', facecolor='#000000', hatch=r'O', label='target')
        plt.legend(handles=[circ1], loc='upper left', frameon=False, labelcolor='white')
    else:
        colormap = cm.hsv
        norm = Normalize(-180, 180)
        sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=plt.gca(), location='bottom', pad=0.01, aspect=50, ticks=[-180, -90, 0, 90, 180])
        cbar.set_ticklabels(['-180°', '-90°', '0°', '90°', '180°'])
        cbar.set_label("Average Absolute Angle (degrees)")


def plot_all_directions(output, output_res, directions, bg_image, roi, additional_rois, additional_roi_colors,
                        image_target_mask, pixel_in_micron):
    print("Plotting all directions...")
    rois = [roi]
    rois.extend(additional_rois)
    colors = ['black']
    colors.extend(additional_roi_colors)
    plt.figure("All directions", figsize=output_res)
    plt.imshow(bg_image.T, extent=roi, origin='upper', cmap='gray')
    scalebar = None
    if pixel_in_micron:
        scalebar = ScaleBar(pixel_in_micron, 'um', location='upper right', color='white', box_color='black')
        plt.gca().add_artist(scalebar)

    if image_target_mask is not None:
        generate_target_contour(image_target_mask)

    # Unpack the object array correctly
    centers = np.array([d[0] for d in directions])
    vectors = np.array([d[1] for d in directions])
    metadata = np.array([d[2] for d in directions])

    x = centers[:, 0]
    y = centers[:, 1]
    u = vectors[:, 0]
    v = vectors[:, 1]
    rel_angle_deg = metadata[:, 0]

    if image_target_mask is not None:
        quiver = plot_arrows_relative(x, y, u, v, rel_angle_deg)
    else:
        quiver = plot_arrows(x, y, u, v)

    plt.margins(0, 0)
    plt.tight_layout(pad=1)
    if output:
        for i, region in enumerate(rois):
            adjust_to_region(roi[3] + roi[2], region, colors[i], scalebar if pixel_in_micron else None)
            plt.savefig(output.joinpath(f'directions_{region[0]}-{region[1]}-{region[2]}-{region[3]}.png'))
        plt.close()
    else:
        plt.show()
    print("Done printing all directions")


def generate_target_contour(image_target_mask):
    plt.contour(image_target_mask.T, 1, origin='upper', colors='red', extent=plt.xlim() + plt.ylim())
    cs = plt.contourf(image_target_mask.T, 1, hatches=['', 'O'], origin='upper', colors='none',
                      extent=plt.xlim() + plt.ylim())
    cs.set_edgecolor((1, 0, 0.2, 1))


def adjust_to_region(data_height, region, region_color, scalebar):
    plt.setp(plt.gca().spines.values(), color=region_color)
    plt.setp([plt.gca().get_xticklines(), plt.gca().get_yticklines()], color=region_color)
    [x.set_linewidth(2) for x in plt.gca().spines.values()]
    plt.xlim(region[0], region[1])
    plt.ylim(region[2], region[3])
    if scalebar:
        # Re-add scalebar to ensure it is visible in the current view
        scalebar.remove()
        plt.gca().add_artist(scalebar)


def plot_rois(output, output_res, bg_image, roi, additional_rois):
    print("Plotting ROIs...")
    plt.figure("ROIs", figsize=output_res)
    plt.imshow(bg_image.T, extent=roi, origin='upper', cmap='gray', vmin=0, vmax=np.max(bg_image))
    indices = [i for i, _ in enumerate(additional_rois)]
    norm = Normalize()
    if indices:
        norm.autoscale(indices)
    colormap = cm.rainbow
    colors = colormap(norm(indices))
    for i, region in enumerate(additional_rois):
        rect = patches.Rectangle((region[0], region[2]), region[1] - region[0],
                                 region[3] - region[2],
                                 linewidth=1, edgecolor=colors[i], facecolor='none')
        plt.gca().add_patch(rect)
    plt.margins(0, 0)
    plt.tight_layout(pad=1)
    if output:
        plt.savefig(output.joinpath('ROIs.png'))
    plt.close()
    return colors


if __name__ == "__main__":
    run()