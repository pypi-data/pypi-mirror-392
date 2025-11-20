# this file used to compabilble with the csv file!
from typing import List
import numpy as np
import os
import enum
import pandas as pd
import h5py

import logging
import sys
from gefpy.stereo_map_extension_cy import (
    py_create_gef_file_with_coordinates, py_convert_bgef_2_gem, py_create_cgef_file_with_coordinates
)
import gzip
import cv2
import tifffile as tiffi


class CoordinateType(enum.Enum):
    Gene = 0
    Cell = 1
    Others = 2


class GeneFileKind(enum.Enum):
    Gene = 0
    Cell = 1
    Others = 2


class SimpleLogger(object):
    logger: logging.Logger = logging.getLogger(__file__)
    logger.setLevel(logging.INFO)
    # set the format
    log_format: logging.Formatter = logging.Formatter(
        "[%(asctime)s %(filename)s %(funcName)s %(lineno)s %(levelname)s]:%(message)s",
        "%Y-%m-%d %H:%M:%S",
    )
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(log_format)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)
    # you can add file to it,but it is not need!

    @staticmethod
    def get_logger() -> logging.Logger:
        return SimpleLogger.logger


global_logger = SimpleLogger.get_logger()


# like the namespace in c++
class HelperFuns(object):
    """
    define some simple util funcs...w
    """

    @staticmethod
    def check_positive_int_value(value, raise_exception: bool = True) -> bool:
        ret: bool = True
        if not isinstance(value, int):
            ret = False
            global_logger.info("the expected type is int,but got type:{}".format(type(value)))
        else:
            if value <= 0:
                global_logger.info("got negative value {}".format(value))
                ret = False
        if raise_exception and not ret:
            raise RuntimeError("fail to check int value {}".format(value))
        return ret

    @staticmethod
    def create_dir(dir: str) -> None:
        if not os.path.exists(dir):
            global_logger.info("create directory {}".format(dir))
            os.makedirs(dir)

    @staticmethod
    def get_gene_file_kind(file: str = None) -> GeneFileKind:
        file_kind = GeneFileKind.Others
        if not os.path.exists(file):
            return file_kind
        try:
            with h5py.File(file) as f:
                if "cellBin" in f:
                    file_kind = GeneFileKind.Cell
                elif "geneExp" in f:
                    file_kind = GeneFileKind.Gene
                else:
                    file_kind = GeneFileKind.Others

        except Exception as ex:
            global_logger.info("can not open file {} with error:{}".format(file, str(ex)))

        return file_kind

    @staticmethod
    def strip_escape_char_of_line(line_data: List[str]) -> List[str]:
        """
        the csv file's content contains the " char,we need to clear it!
        """
        return [item.replace("\"", "") for item in line_data]

    @staticmethod
    def save_mask(
        mask: np.ndarray = None,
        output_file: str = None,
        compress: bool = False,
        compress_level: int = 6,
        ignore_failure: bool = True
    ) -> True:
        """
        Args:
            ignore_api_chan
        """
        if mask is None:
            global_logger.info("the mask is None")
            return
        if not isinstance(mask, np.ndarray):
            global_logger.info("the mask should be a ndarry!")
            raise TypeError("the expected type of mask is np.ndarray,but get others {}".format(type(mask)))

        result_dir = os.path.dirname(output_file)
        HelperFuns.create_dir(result_dir)
        if compress:
            global_logger.info("save the mask with zlib compress,compress_level:{}".format(compress_level))
            try:
                tiffi.imwrite(output_file, mask, compression="zlib", compressionargs={"level": compress_level})
            except Exception as ex:
                if ignore_failure:
                    global_logger.info(
                        "fail to save mask.tif with zlib compress,the error is '{}',maybe the tiff api changed!".format(
                            str(ex)
                        )
                    )
                    global_logger.info("we will save the mask without compress....")
                    tiffi.imwrite(output_file, mask)
                else:
                    # just raise the exception!
                    raise RuntimeError from ex
        else:
            global_logger.info("save the mask without compress!")
            tiffi.imwrite(output_file, mask)

    def compress_file_with_gzip(
        input_file: str, output_file: str, compress_level: int = 6, chunk_size: int = 1024 * 1024
    ) -> None:
        """
        compress a file with gzip
        Args:
            input_file:the file to comrpess
            ouput_file:we will check the dir of it
            compress_level:using zlib compress
            chunk_size:int,the size we compress every time!
        """
        if not output_file.endswith("gz"):
            global_logger.info(
                "the output file {} not endswith gz,maybe the gunzip not recognize it!".format(output_file)
            )
        if not os.path.exists(input_file):
            return
        result_dir = os.path.dirname(output_file)
        HelperFuns.create_dir(result_dir)

        # then,we write the file with zlib compress,^_^
        global_logger.info("convert file {} -> {} with gzip format!".format(input_file, output_file))
        with gzip.GzipFile(output_file, "wb", compresslevel=compress_level) as writer:
            with open(input_file, "rb") as reader:
                while True:
                    content = reader.read(chunk_size)
                    if not content:
                        break
                    writer.write(content)


class SteremapCSVDefines(object):
    # the default defines...
    EXPECTED_COLUMN: int = 6
    # the cell define from the stereomap!
    CELL_BIN_SIZE_STR: str = "cell"

    # the define col names
    BIN_SIZE_COL_NAME: str = "Binsize"

    # very important!
    X_COL_NAME: str = "X coordinate"
    Y_COL_NAME: str = "Y coordinate"
    GROUP_COL_NAME: str = "GroupName"
    LABEL_COL_NAME: str = "ClusterName"


# the parsed coordinate info from stereomap exported csv file,constains the coor_type,coordinates,groups and bin_size(this is used for the gene file )
class MapCoordinateInfo:

    def __init__(
        self, bin_size: int, coordinates: List[np.ndarray], label_names: List[str], coor_type: CoordinateType
    ) -> None:
        """
        Args:
            bin_size:int,the bin size,like the scale
            coordiantes:a list of array,the coordinates of selected datas...
            label_names:a list of str,if has same group name,raise exception
            coor_type:gene or cell
        """
        if coor_type != CoordinateType.Gene and coor_type != CoordinateType.Cell:
            raise ValueError("unexpected coor type,we just want gene or cell")

        self.coor_type = coor_type
        if not isinstance(bin_size, int):
            raise TypeError("the bin_size {} is not a int type", bin_size)
        if coor_type == CoordinateType.Gene:
            if bin_size <= 0:
                raise ValueError("the bin_size can not zero or negative!")
        self.bin_size = bin_size

        for coor in coordinates:
            if not isinstance(coor, np.ndarray):
                global_logger.info("try to convert the coordinate to ndarray!")
                coor = np.array(coor, dtype=np.int32)
            if not (np.issubdtype(coor.dtype, np.integer)):
                raise ValueError("the dtype of coordiante must be integer type,but got {}".format(coor.dtype))
            shape = coor.shape
            if len(shape) != 2 or shape[1] != 2:
                raise ValueError("the coor '{}' has unexpected shape!", coor)

        if len(coordinates) != len(label_names):
            raise ValueError("the size of coordinates and group names are mismatch!")

        if len(label_names) > 1:
            unique_label_names = set(label_names)
            if len(unique_label_names) < len(label_names):
                raise ValueError("the label_names '{}' has repeated name,this is not expecte!")

        self.coordinates = coordinates
        self.label_names = label_names

    def __str__(self):
        return "type:{} bin_size:{} coordinates:{} names:{}".format(
            self.coor_type, self.bin_size, self.coordinates, self.label_names
        )


# parse the coordinate info from the csv file!
def parse_cooridnate_info_from_csv(file: str) -> MapCoordinateInfo:
    """
    Args:
        file:str,the csv file,if the file is invalid,just raise an exception!
    """
    if not os.path.exists(file):
        raise FileNotFoundError("file {} is not exist!".format(file))
    if not file.endswith("csv"):
        global_logger.info("the file should be a csv file,but got unexpected suffix,maybe get error!")

    global_logger.info(
        "required csv cols:{} cell type str:{}".format(
            SteremapCSVDefines.EXPECTED_COLUMN, SteremapCSVDefines.CELL_BIN_SIZE_STR
        )
    )

    coor_type: CoordinateType = CoordinateType.Others
    bin_size: int = 0

    with open(file, "r", encoding="utf-8") as f:
        skip_num: int = 1
        for _ in range(skip_num):
            f.readline()
        header_line = f.readline().strip().split(",")
        header_line = HelperFuns.strip_escape_char_of_line(header_line)
        if len(header_line) != SteremapCSVDefines.EXPECTED_COLUMN:
            raise ValueError(
                "the columns should be {},but get {}".format(SteremapCSVDefines.EXPECTED_COLUMN, len(header_line))
            )

        header_map = {header_line[i]: i for i in range(SteremapCSVDefines.EXPECTED_COLUMN)}
        for name in [
            SteremapCSVDefines.BIN_SIZE_COL_NAME, SteremapCSVDefines.X_COL_NAME, SteremapCSVDefines.Y_COL_NAME,
            SteremapCSVDefines.GROUP_COL_NAME
        ]:
            if name not in header_map:
                raise ValueError("missing required col name {}".format(name))
        global_logger.info("the header map is {}".format(header_map))

        bin_size_col_index = header_map[SteremapCSVDefines.BIN_SIZE_COL_NAME]
        data_line = f.readline().strip().split(",")
        data_line = HelperFuns.strip_escape_char_of_line(data_line)

        if len(data_line) != SteremapCSVDefines.EXPECTED_COLUMN:
            raise ValueError(
                "the line columns should be {},but get {}".format(SteremapCSVDefines.EXPECTED_COLUMN, len(data_line))
            )

        # try to get the type from first line!
        bin_size_str = data_line[bin_size_col_index]
        if bin_size_str == SteremapCSVDefines.CELL_BIN_SIZE_STR:
            global_logger.info(
                "the bin_size_str is {},so the csv file is from cellbin file,we will set the coor_type to cell!".
                format(bin_size_str)
            )
            coor_type = CoordinateType.Cell
        else:
            try:
                bin_size = int(bin_size_str)
            except Exception as ex:
                global_logger.info("the bin size should be convert to int with base10,but fail....")
                raise ValueError from ex
            global_logger.info(
                "the bin size is a int type,so the csv file is from gene,and we will set the coor type to it!"
            )
            coor_type = CoordinateType.Gene
    global_logger.info("parse the coordinates,we will ignore the bad lines..")
    coor_df: pd.DataFrame = pd.read_csv(file, sep=",", skiprows=1, on_bad_lines="skip")
    global_logger.info("group by {}".format(SteremapCSVDefines.LABEL_COL_NAME))
    grouped_sub_dfs = coor_df.groupby(SteremapCSVDefines.LABEL_COL_NAME)

    # define the list to save the parsed values...
    label_names = []
    coordinates = []
    for label_name, sub_df in grouped_sub_dfs:
        # convert to string
        label_names.append(str(label_name))
        coordinates.append(
            sub_df[[SteremapCSVDefines.X_COL_NAME, SteremapCSVDefines.Y_COL_NAME]].to_numpy().astype(np.int32)
        )

    # construct the ojb
    coordinate_info = MapCoordinateInfo(
        bin_size=bin_size, coordinates=coordinates, label_names=label_names, coor_type=coor_type
    )
    return coordinate_info


# this func generate a mask from the gene file,it will read the geneExp/bin1/expression as the fill pixel!
def create_gene_mask_v1(gene_file, fill_color: int = 255) -> np.ndarray:
    if fill_color <= 0:
        fill_color = 1
    elif fill_color > 255:
        fill_color = 255

    x1_attr_name = "minX"
    y1_attr_name = "minY"
    x2_attr_name = "maxX"
    y2_attr_name = "maxY"
    mask = None
    global_logger.info("we will generate mask from bin1 expression!")
    with h5py.File(gene_file) as f:
        expressiion_dataset = f["/geneExp/bin1/expression"]
        expression_attrs = expressiion_dataset.attrs
        x1 = expression_attrs[x1_attr_name][0]
        y1 = expression_attrs[y1_attr_name][1]
        x2 = expression_attrs[x2_attr_name][0]
        y2 = expressiion_dataset[y2_attr_name][1]

        height = y2 - y1 + 1
        width = x2 - x1 + 1
        if height <= 0 or width <= 0:
            return None
        mask = np.zeros(shape=(height, width), dtype=np.uint8)
        READ_BATCH_SIZE = 65536

        len_expression = expressiion_dataset.shape[0]

        iters = (len_expression + READ_BATCH_SIZE - 1) // READ_BATCH_SIZE

        for i in range(iter):
            left = i * READ_BATCH_SIZE
            right = left + READ_BATCH_SIZE
            if i == (iters - 1):
                right = len_expression
            batch_expression = expressiion_dataset[left:right]
            x = batch_expression["x"]
            y = batch_expression["y"]
            mask[y, x] = fill_color
    return mask


# this func will generate a mask from given coordinate,but fill the range with x1:x1+bin_size,y1:y1+bin_size
def create_gene_mask_v2(
    coordinates: List[np.ndarray], height: int, width: int, bin_size: int, fill_color: int = 255
) -> np.ndarray:
    mask: np.ndarray = None
    if height <= 0 or width <= 0:
        global_logger.info("the height:{} width:{} is invalid".format(height, width))
    if bin_size <= 0:
        global_logger.info("invalid bin_size:{}".format(bin_size))

    mask = np.zeros(shape=(height, width), dtype=np.uint8)
    if fill_color <= 0:
        fill_color = 1
    elif fill_color > 255:
        fill_color = 255
    if bin_size == 1:
        global_logger.info("bin size = 1,just pixel position to fill color")
        for coordinate in coordinates:
            x = coordinate[:, 0]
            y = coordinate[:, 1]
            mask[y, x] = fill_color
    else:
        # this maybe slow,how to make it faster?
        for coordinate in coordinates:
            for x, y in coordinate:
                mask[y:y + bin_size, x:x + bin_size] = fill_color
    return mask


# this func create a mask from the cell file,it will read the cell polygon from file,and fill the pixel!
def create_cell_mask(cell_file: str, fill_color: int = 255) -> np.ndarray:
    if fill_color <= 0:
        fill_color = 1
    elif fill_color > 255:
        fill_color = 255

    mask: np.ndarray = None
    if not os.path.exists(cell_file):
        return mask
    pad_value: int = 32767
    with h5py.File(cell_file, locking=False) as f:
        cell_border_dataset = f["cellBin/cellBorder"]
        cell_dataset = f["cellBin/cell"]
        try:
            x1 = f.attrs["offsetX"][0]
            y1 = f.attrs["offsetY"][0]
            x2 = f.attrs["maxX"][0]
            y2 = f.attrs["maxY"][0]
            global_logger.info("get the range of the chip,so we will create a mask for cell!")
        except Exception as ex:
            global_logger.info("fail to read the attrs with error {}".format(str(ex)))
            return mask
        height = y2 - y1 + 1
        width = x2 - x1 + 1
        if height <= 0 or width <= 0:
            return mask
        cell_border_mat = cell_border_dataset[:]
        cell_center_xs = cell_dataset["x"]
        cell_center_ys = cell_dataset["y"]

    cell_polygons = []
    cell_num, point_size, coor_size = cell_border_mat.shape
    global_logger.info("the padding point size per cell is {}".format(point_size))
    # check whether the matrix is expected!
    if len(cell_center_xs) != cell_num:
        global_logger.info(
            "the cell dataset size not equal to the cell border dataset size,we can not match one by one!"
        )
        return mask
    if coor_size != 2:
        global_logger.info("the cell border should be an 2d cooridnates,but we get {}".format(coor_size))
        return mask

    # x,y can not be the pad value!
    cell_index_mask = cell_border_mat != pad_value
    cell_index_mask = np.all(cell_index_mask, axis=2)
    for i in range(cell_num):
        polygon = cell_border_mat[i][cell_index_mask[i]].astype(np.int32)
        polygon[:, 0] += cell_center_xs[i]
        polygon[:, 1] += cell_center_ys[i]
        cell_polygons.append(polygon)
    # now we can filling by the polygon!
    mask = np.zeros(shape=(height, width), dtype=np.uint8)
    cv2.fillPoly(mask, cell_polygons, fill_color)
    return mask


def generate_bgef_file_with_coordinate(
    input_file: str = None,
    result_dir: str = None,
    export_bin_sizes: List[int] = None,
    coordinate_info: MapCoordinateInfo = None,
    omics_type: str = None,
    sample_id: str = None,
    fill_color: int = 255
) -> bool:
    if not os.path.exists(input_file):
        global_logger.info("the input gene file {} is not exist".format(input_file))
        return False
    if len(export_bin_sizes) == 0:
        global_logger.info("the specify bin_size {} is empty!".format(export_bin_sizes))
        return False
    for export_bin_size in export_bin_sizes:
        if not HelperFuns.check_positive_int_value(value=export_bin_size, raise_exception=False):
            return False
    HelperFuns.create_dir(result_dir)
    n_labels = len(coordinate_info.label_names)

    if omics_type == "Transcriptomics":
        output_file_fmt = "{}.{}.label.gef"
    else:
        output_file_fmt = "{}.protein.{}.label.gef"
    for i in range(n_labels):
        label_name = coordinate_info.label_names[i]
        label_result_dir = os.path.join(result_dir, label_name)
        HelperFuns.create_dir(label_result_dir)

        # just make them happy
        csv_result_dir = os.path.join(label_result_dir, "segmentation")
        HelperFuns.create_dir(csv_result_dir)

        output_file_name = output_file_fmt.format(sample_id, label_name)
        output_gene_file = os.path.join(label_result_dir, output_file_name)
        global_logger.info("we will create the gene file {} with coordinates".format(output_gene_file))
        flat_coordinates = coordinate_info.coordinates[i].reshape(-1).tolist()
        ret = py_create_gef_file_with_coordinates(
            input_file, output_gene_file, flat_coordinates, export_bin_sizes, False, 4096, True, 6,
            coordinate_info.bin_size
        )
        if not ret:
            global_logger.info("fail to generate gene file {}".format(output_gene_file))
            return False
    for export_bin_size in export_bin_sizes:
        # make hidden
        temp_output_csv_file: str = os.path.join(
            csv_result_dir, ".{}.lasso.bin{}.{}.gem".format(sample_id, export_bin_size, label_name)
        )
        global_logger.info("export csv file to {}....".format(temp_output_csv_file))
        py_convert_bgef_2_gem(output_gene_file, temp_output_csv_file, sample_id, export_bin_size, True)
        output_csv_file = os.path.join(
            csv_result_dir, "{}.lasso.bin{}.{}.gem.gz".format(sample_id, export_bin_size, label_name)
        )

        global_logger.info("compress file with gzip to {}".format(output_csv_file))
        HelperFuns.compress_file_with_gzip(input_file=temp_output_csv_file, output_file=output_csv_file)
        try:
            global_logger.info("remove the temp file {}".format(temp_output_csv_file))
            os.remove(temp_output_csv_file)
        except Exception as ex:
            global_logger.info("fail to remove temp file {},the error is {}".format(temp_output_csv_file, str(ex)))

        with h5py.File(input_file, locking=False) as f:
            expression_dataset = f["geneExp/bin1/expression"]
            expression_attrs = expression_dataset.attrs
            x1 = expression_attrs["minX"][0]
            y1 = expression_attrs["minY"][0]
            x2 = expression_attrs["maxX"][0]
            y2 = expression_attrs["maxY"][0]
        height = y2 - y1 + 1
        width = x2 - x1 + 1
        global_logger.info("create a mask with shape {}x{}".format(height, width))
        # mask = create_gene_mask_v1(gene_file=output_gene_file, fill_color=fill_color)
        global_logger.info("just fill with lt + bin_size,this maybe got some nosie data...")
        mask = create_gene_mask_v2(
            coordinate_info.coordinates,
            height=height,
            width=width,
            bin_size=coordinate_info.bin_size,
            fill_color=fill_color
        )
        if mask is not None:
            ouptut_mask_file = os.path.join(csv_result_dir, "{}.lasso.{}.mask.tif".format(sample_id, label_name))
        HelperFuns.save_mask(
            mask=mask, output_file=ouptut_mask_file, compress=True, compress_level=6, ignore_failure=True
        )


def generate_cgef_file_with_coordinate(
    input_file: str,
    result_dir: str,
    coordinate_info: MapCoordinateInfo,
    omics_type: str,
    sample_id: str,
    fill_color: int = 255
) -> bool:
    if not os.path.exists(input_file):
        global_logger.info("the input gene file {} is not exist".format(input_file))
        return False
    HelperFuns.create_dir(result_dir)
    n_labels = len(coordinate_info.label_names)
    global_logger.info("the specify omics type is {}".format(omics_type))
    if omics_type == "Transcriptomics":
        output_file_fmt = "{}.{}.label.cellbin.gef"
    else:
        output_file_fmt = "{}.protein.{}.label.cellbin.gef"

    for i in range(n_labels):
        label_name = coordinate_info.label_names[i]
        cell_centers = coordinate_info.coordinates[i].reshape(-1).tolist()
        label_result_dir = os.path.join(result_dir, label_name)
        HelperFuns.create_dir(label_result_dir)

        output_cell_file = os.path.join(label_result_dir, output_file_fmt.format(sample_id, label_name))
        ret = py_create_cgef_file_with_coordinates(input_file, output_cell_file, cell_centers)
        if not ret:
            global_logger.info("fail to generate the cell file!")
            return False
        mask = create_cell_mask(cell_file=output_cell_file, fill_color=fill_color)
        output_mask_file = os.path.join(label_result_dir, "{}.alsso.cellbin.{}.mask.tif".format(sample_id, label_name))
        if mask is not None:
            HelperFuns.save_mask(
                mask=mask, output_file=output_mask_file, compress=True, compress_level=6, ignore_failure=True
            )


def test_gene():
    csv_file = "/home/lazydog/workspace/bgi_datas/gene_datas/csv_test/Leiden-custom-bin.csv"
    gene_file = "/home/lazydog/workspace/bgi_datas/gene_datas/csv_test/C04042E2.tissue.gef"
    result_dir = "/home/lazydog/workspace/bgi_datas/gene_datas/csv_test/test_gene"
    sample_id = "lazydog"
    omics_type = "Transcriptomics"
    coordinate_info = parse_cooridnate_info_from_csv(file=csv_file)
    print(coordinate_info)

    generate_bgef_file_with_coordinate(
        input_file=gene_file,
        result_dir=result_dir,
        export_bin_sizes=[1, 10, 20, 50],
        coordinate_info=coordinate_info,
        omics_type=omics_type,
        sample_id=sample_id,
        fill_color=255
    )


def test_cell():
    csv_file = "/home/lazydog/workspace/bgi_datas/gene_datas/csv_test/Leiden-custom-cell1.csv"
    gene_file = "/home/lazydog/workspace/bgi_datas/gene_datas/csv_test/A02677B5.adjusted.cellbin.gef"
    result_dir = "/home/lazydog/workspace/bgi_datas/gene_datas/csv_test/test_cell"
    sample_id = "lazydog"
    omics_type = "Transcriptomics"
    coordinate_info = parse_cooridnate_info_from_csv(file=csv_file)
    generate_cgef_file_with_coordinate(
        input_file=gene_file,
        result_dir=result_dir,
        coordinate_info=coordinate_info,
        omics_type=omics_type,
        sample_id=sample_id,
        fill_color=255
    )


if __name__ == "__main__":
    # test_cell()
    test_gene()
