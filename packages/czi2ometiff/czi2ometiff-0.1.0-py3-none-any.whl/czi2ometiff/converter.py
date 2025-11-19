import numpy as np
from czifile import CziFile
from numpy2ometiff import write_ome_tiff
import warnings
import os
import xml.etree.ElementTree as ET

def extract_channel_names(czi):
    """
    Extract unique channel names from CZI metadata.
    """
    try:
        if hasattr(czi, 'metadata') and czi.metadata:
            metadata_str = str(czi.metadata) if isinstance(czi.metadata, (str, bytes)) else czi.metadata()
            if isinstance(metadata_str, str):
                metadata_str = metadata_str.encode('utf-8')
            
            metadata_root = ET.fromstring(metadata_str)
            channel_names = []
            processed_names = set()  # To track unique names
            
            print("Attempting to extract channel names from metadata...")
            
            # Try to find channels with IDs first (these are usually the actual channels)
            channels = metadata_root.findall('.//Channel[@Id]')
            if not channels:
                # If no channels with IDs found, try other paths
                for path in ['.//Channel']:
                    channels = metadata_root.findall(path)
                    if channels:
                        break
            
            if channels:
                print(f"Found {len(channels)} channels")
                # Sort channels by ID if available
                def get_channel_id(channel):
                    channel_id = channel.get('Id', '')
                    try:
                        return int(channel_id.split(':')[1]) if ':' in channel_id else float('inf')
                    except (ValueError, IndexError):
                        return float('inf')
                
                channels = sorted(channels, key=get_channel_id)
                
                for channel in channels:
                    channel_id = channel.get('Id', '')
                    if 'Channel:' in str(channel_id):  # Only process channels with proper IDs
                        name = channel.get('Name')
                        if name and name not in processed_names:
                            print(f"Found channel: ID={channel_id}, Name={name}")
                            channel_names.append(name)
                            processed_names.add(name)
            
            if channel_names:
                print(f"Final channel names: {channel_names}")
                return channel_names
            
    except Exception as e:
        print(f"Error extracting channel names: {e}")
        import traceback
        traceback.print_exc()
    return []



def extract_pixel_sizes(metadata_root):
    """
    Extract pixel sizes from metadata.
    CZI standard stores physical sizes in meters, we convert to micrometers.
    
    Parameters:
    -----------
    metadata_root : xml.etree.ElementTree.Element
        The metadata XML root element
        
    Returns:
    --------
    dict:
        Dictionary containing pixel sizes in micrometers
    """
    pixel_sizes = {}
    
    print("\nExtracting pixel sizes...")
    
    # Get scaling information from Items/Distance
    try:
        scaling_items = metadata_root.find('.//Scaling/Items')
        if scaling_items is not None:
            print("Found scaling items:")
            for distance in scaling_items.findall('.//Distance'):
                axis_id = distance.get('Id')
                if axis_id:
                    value_elem = distance.find('Value')
                    if value_elem is not None and value_elem.text:
                        # Values in CZI are stored in meters, convert to micrometers
                        value_in_m = float(value_elem.text)
                        value_in_um = value_in_m * 1e6
                        pixel_sizes[f'pixel_size_{axis_id.lower()}'] = value_in_um
                        print(f"{axis_id} axis: {value_in_m} m = {value_in_um} µm")
    except Exception as e:
        print(f"Error reading scaling items: {e}")

    # Set defaults for any missing dimensions
    default_value = 1.0
    for axis in ['x', 'y', 'z']:
        key = f'pixel_size_{axis}'
        if key not in pixel_sizes:
            print(f"No scaling found for {axis.upper()} axis, using default: {default_value} µm")
            pixel_sizes[key] = default_value
    
    print("\nFinal pixel sizes:")
    for axis in ['x', 'y', 'z']:
        print(f"{axis.upper()}: {pixel_sizes[f'pixel_size_{axis}']} µm")
    
    return pixel_sizes




def read_czi_image(file_path):
    """
    Read a multi-channel .czi fluorescence microscopy image and return it as a numpy array.
    """
    try:
        print(f"\nReading CZI file: {file_path}")
        with CziFile(file_path) as czi:
            # Initialize metadata dictionary first
            metadata = {}
            
            # Get the image data
            print("Reading image data...")
            image_array = czi.asarray()
            print(f"Original image array shape: {image_array.shape}")
            print(f"Image dimensions: {czi.axes}")
            
            # Handle SCYX0 dimension format
            if czi.axes == 'SCYX0':
                print("Detected SCYX0 format, reorganizing dimensions...")
                # Remove the trailing 0 dimension and scene dimension
                image_array = np.squeeze(image_array, axis=-1)  # Remove trailing dimension
                image_array = np.squeeze(image_array, axis=0)   # Remove scene dimension
                print(f"Reorganized shape: {image_array.shape}")
            
            # Extract channel names
            print("\nExtracting channel names...")
            channel_names = extract_channel_names(czi)
            
            # Verify channel count matches the data
            num_channels = image_array.shape[0]
            if len(channel_names) != num_channels:
                print(f"Warning: Number of channel names ({len(channel_names)}) doesn't match number of channels in data ({num_channels})")
                channel_names = [f'Channel_{i}' for i in range(num_channels)]
            
            # Extract pixel sizes
            try:
                if hasattr(czi, 'metadata') and czi.metadata:
                    metadata_str = str(czi.metadata) if isinstance(czi.metadata, (str, bytes)) else czi.metadata()
                    if isinstance(metadata_str, str):
                        metadata_str = metadata_str.encode('utf-8')
                    metadata_root = ET.fromstring(metadata_str)
                    
                    # Extract pixel sizes with units
                    pixel_sizes = extract_pixel_sizes(metadata_root)
                    metadata.update(pixel_sizes)
            except Exception as e:
                print(f"Error extracting pixel sizes: {e}")
            
            # Set default values for missing pixel sizes
            metadata.setdefault('pixel_size_x', 1.0)
            metadata.setdefault('pixel_size_y', 1.0)
            metadata.setdefault('pixel_size_z', 1.0)
            
            print(f"\nFinal measurements:")
            print(f"Image shape: {image_array.shape}")
            print(f"Channel names: {channel_names}")
            print(f"Pixel sizes: X={metadata['pixel_size_x']} µm, "
                  f"Y={metadata['pixel_size_y']} µm, "
                  f"Z={metadata['pixel_size_z']} µm")
            
            metadata['channel_names'] = channel_names
            return image_array, channel_names, metadata
            
    except Exception as e:
        raise Exception(f"Error reading CZI file: {str(e)}")
        
def convert_czi_to_ometiff(input_path, output_path=None, downsample_count=8):
    """
    Convert a CZI file to OME-TIFF format.
    """
    try:
        # Generate output path if not provided
        if output_path is None:
            output_path = os.path.splitext(input_path)[0] + '.ome.tiff'
        
        print(f"\nConverting CZI to OME-TIFF...")
        print(f"Input: {input_path}")
        print(f"Output: {output_path}")
        
        # Read the CZI file
        image_data, channel_names, metadata = read_czi_image(input_path)
        
        print(f"Initial image shape: {image_data.shape}")
        
        # Ensure data is in the correct shape (Z, C, Y, X)
        if len(image_data.shape) == 3:  # CYX format
            # Add Z dimension at the start for ZCYX format
            image_data = np.expand_dims(image_data, axis=0)
            print(f"Added Z dimension at start. New shape: {image_data.shape}")
        
        # Verify channel count after all shape transformations
        num_channels = image_data.shape[1]  # Channels should be second dimension
        print(f"Number of channels in data: {num_channels}")
        print(f"Number of channel names: {len(channel_names)}")
        print(f"Current channel names: {channel_names}")
        
        if num_channels != len(channel_names):
            if num_channels > len(channel_names):
                # If we have more channels than names, add generic names
                print(f"Adding generic names for extra channels")
                channel_names.extend([f'Channel_{i}' for i in range(len(channel_names), num_channels)])
            else:
                # If we have more names than channels, keep only the first num_channels names
                print(f"Truncating channel names to match data")
                channel_names = channel_names[:num_channels]
        
        print(f"Final channel names: {channel_names}")
        
        # Get pixel sizes from metadata
        pixel_size_x = metadata.get('pixel_size_x', 1.0)
        pixel_size_y = metadata.get('pixel_size_y', 1.0)
        physical_size_z = metadata.get('pixel_size_z', 1.0)
        
        print(f"\nWriting OME-TIFF...")
        print(f"Final image shape (Z,C,Y,X): {image_data.shape}")
        print(f"Channel names: {channel_names}")
        print(f"Pixel sizes (µm): X={pixel_size_x}, Y={pixel_size_y}, Z={physical_size_z}")
        
        # Write OME-TIFF
        write_ome_tiff(
            data=image_data,
            channel_names=channel_names,
            output_filename=output_path,
            pixel_size_x=pixel_size_x,
            pixel_size_y=pixel_size_y,
            physical_size_z=physical_size_z,
            create_pyramid=True,
            downsample_count=downsample_count,
            imagej=False
        )
        
        print("\nConversion completed successfully!")
        return output_path
        
    except Exception as e:
        raise Exception(f"Error converting CZI to OME-TIFF: {str(e)}")

