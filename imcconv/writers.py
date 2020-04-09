import xarray as xr
import tifffile

from pathlib import Path
from typing import Union, List, Sequence, Generator


def write_ometiff(imarr: xr.DataArray, outpath: Union[Path, str], **kwargs) -> None:
    """Write DataArray to a multi-page OME-TIFF file.
    Args:
        imarr: image DataArray object
        outpath: file to output to
        **kwargs: Additional arguments to tifffile.imwrite
    """
    outpath = Path(outpath)
    imarr = imarr.transpose("c", "y", "x")
    Nc, Ny, Nx = imarr.shape
    # Generate standard OME-XML
    channels_xml = '\n'.join(
        [f"""<Channel ID="Channel:0:{i}" Name="{channel}" SamplesPerPixel="1" />"""
            for i, channel in enumerate(imarr.c.values)]
    )
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <OME xmlns="http://www.openmicroscopy.org/Schemas/OME/2016-06"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://www.openmicroscopy.org/Schemas/OME/2016-06 http://www.openmicroscopy.org/Schemas/OME/2016-06/ome.xsd">
        <Image ID="Image:0" Name="{outpath.stem}">
            <Pixels BigEndian="false"
                    DimensionOrder="XYZCT"
                    ID="Pixels:0"
                    Interleaved="false"
                    SizeC="{Nc}"
                    SizeT="1"
                    SizeX="{Nx}"
                    SizeY="{Ny}"
                    SizeZ="1"
                    PhysicalSizeX="1.0"
                    PhysicalSizeY="1.0"
                    Type="float">
                <TiffData />
                {channels_xml}
            </Pixels>
        </Image>
    </OME>
    """
    outpath.parent.mkdir(parents=True, exist_ok=True)
    # Note resolution: 1 um/px = 25400 px/inch
    tifffile.imwrite(outpath, data=imarr.values, description=xml, contiguous=True, 
                     resolution=(25400, 25400, "inch"), **kwargs)


def write_individual_tiffs(imarr: xr.DataArray, outdir: Union[Path, str], **kwargs) -> None:
    """Write DataArray to individual TIFF files in a folder.
    Args:
        imarr: image DataArray object
        outdir: folder to output to
        **kwargs: Additional arguments to tifffile.imwrite
    """
    imarr = imarr.transpose("c", "y", "x")
    outdir.mkdir(parents=True, exist_ok=True)
    for imchannel in imarr:
        # Sanitize slashes in channel name
        imchannel_name = str(imchannel.c.values).replace("/", "-")
        tifffile.imwrite(Path(outdir) / f"{imchannel_name}.tiff", data=imchannel.values, 
                         resolution=(25400, 25400, "inch"), **kwargs)
