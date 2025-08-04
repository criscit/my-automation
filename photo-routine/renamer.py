import os
from datetime import datetime
from pillow_heif import register_heif_opener
from PIL import Image
from mutagen.mp4 import MP4


def get_photo_dates(directory):
    file_name_dates = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        valid_extensions = ['heic', 'jpg', 'jpeg', 'png']
        register_heif_opener()

        if os.path.isfile(file_path):
            try:
                created_dt = datetime.fromtimestamp(os.path.getctime(file_path)).strftime("%Y%m%d")

                file_ext = filename.split('.')[1].lower()
                date_taken = ''

                if file_ext in valid_extensions:
                    # Open the image
                    image = Image.open(file_path)

                    metadata = None

                    # Get the EXIF metadata
                    if file_ext == 'heic':
                        metadata = image.getexif()
                    else:
                        metadata = image._getexif()

                    # Get the date taken from the metadata
                    if not metadata:
                        print(f"EXIF metadata not found in file: {filename}")
                    elif 36867 in metadata.keys():

                        date_taken = metadata[36867]
                    elif 306 in metadata.keys():
                        date_taken = metadata[306]
                    else:
                        print(f"Date not found in file: {filename}")

                    # Close the image
                    image.close()

                file_name_dates.append((
                    file_path,
                    file_ext,
                    created_dt,
                    date_taken[:10].replace(':', '')
                ))

            except Exception as e:
                print(f"Error {filename}: {e}")

    file_name_dates.sort(key=lambda x: x[1])
    return file_name_dates

def rename_photos(directory):
    file_name_dates = get_photo_dates(directory)
    file_count = 0
    for i, (file_path, new_filename, *_) in enumerate(file_name_dates):

        if file_name_dates[i - 1][1] == new_filename:
            file_count += 1
            new_filename += f'_{file_count}'
        else:
            file_count = 0

        # Rename the file
        # add check if already exists -> try increment i
        # when we find date_part we need to split by this in order to add something new
        old_filename = file_path.rsplit("\\")[-1]
        old_file_type = old_filename.split(".")[1]
        if old_filename.split('.')[0].split('_')[0] == new_filename.split('_')[0]:
            continue

        new_file_path = os.path.join(directory, new_filename + "." + old_file_type)
        os.rename(file_path, new_file_path)

        print(f"Renamed: {old_filename} -> {new_filename}")

def check_photos(directory):
    file_name_dates = get_photo_dates(directory)
    check_files = []
    for i, (file_path, file_ext, created_dt, taken_dt) in enumerate(file_name_dates):
        old_file_date = file_path.rsplit("\\")[-1].split('.')[0].split('_')[0].split(' ')[0].split('-')[0]

        if old_file_date not in [taken_dt, created_dt]:
            check_files.append((file_path.rsplit("\\")[-1], file_ext, created_dt, taken_dt))

    with open(r'C:\Users\crisc\OneDrive\Desktop\check_photos.csv', 'w', encoding='utf-8') as f:
        f.write(';'.join(['filename', 'file_ext', 'creation_dt', 'taken_dt\n']))
        for filename, file_ext, created_dt, taken_dt in check_files:

            f.write(";".join([
                filename,
                file_ext,
                created_dt,
                taken_dt
            ]) + '\n')
    return check_files

def check_heic_photos(directory):
    file_name_dates = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        register_heif_opener()

        if os.path.isfile(file_path):
            try:
                file_ext = filename.split('.')[1].lower()
                date_taken = ''

                if file_ext == 'heic':
                    # Open the image
                    image = Image.open(file_path)
                    metadata = image.getexif()

                    # Get the date taken from the metadata
                    if not metadata:
                        print(f"EXIF metadata not found in file: {filename}")
                    elif 36867 in metadata.keys():
                        date_taken = metadata[36867]
                    elif 306 in metadata.keys():
                        date_taken = metadata[306]
                    else:
                        print(f"Date not found in file: {filename}")

                    # Close the image
                    image.close()
                else:
                    continue

            except Exception as e:
                print(f"Error {filename}: {e}")
        file_name_dates.append((
            file_path,
            date_taken[:10].replace(':', '')
        ))

    file_name_dates.sort(key=lambda x: x[1])
    check_files = []

    for i, (file_path, taken_dt) in enumerate(file_name_dates):
        old_file_date = file_path.rsplit("\\")[-1].split('.')[0].split('_')[0].split(' ')[0].split('-')[0]

        if old_file_date != taken_dt:
            check_files.append((file_path.rsplit("\\")[-1], taken_dt))

    with open(r'C:\Users\crisc\OneDrive\Desktop\check_photos_heic.csv', 'w', encoding='utf-8') as f:
        f.write(';'.join(['filename', 'taken_dt\n']))
        for filename, taken_dt in check_files:
            f.write(";".join([
                filename,
                taken_dt
            ]) + '\n')
    return check_files


def check_videos(directory):
    file_name_dates = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            try:
                file_ext = filename.split('.')[1].lower()
                date_taken = ''
                if file_ext in ['mp4', 'mov']:

                    # Load the .mov file
                    video = MP4(file_path)

                    # Extract the creation date from the metadata
                    print(filename, video)
                    if '©day' in video:
                        date_taken = video['©day'][0]
                    else:
                        print(f"Date not found in file: {filename}")
                else:
                    continue
            except Exception as e:
                print(f"Error {filename}: {e}")

        file_name_dates.append((
            file_path,
            date_taken[:10].replace(':', '')
        ))

    file_name_dates.sort(key=lambda x: x[1])
    check_files = []

    for i, (file_path, taken_dt) in enumerate(file_name_dates):
        old_file_date = file_path.rsplit("\\")[-1].split('.')[0].split('_')[0].split(' ')[0].split('-')[0]

        if old_file_date != taken_dt:
            check_files.append((file_path.rsplit("\\")[-1], taken_dt))

    with open(r'C:\Users\crisc\OneDrive\Desktop\check_videos.csv', 'w', encoding='utf-8') as f:
        f.write(';'.join(['filename', 'taken_dt\n']))
        for filename, taken_dt in check_files:
            f.write(";".join([
                filename,
                taken_dt
            ]) + '\n')
    return check_files


import subprocess
import json


def get_mov_metadata(file_path):
    try:
        # Run exiftool command to get metadata in JSON format
        result = subprocess.run(
            [r'C:\Users\crisc\Downloads\exiftool-13.18_64\exiftool.exe', '-j', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Check if the command was successful
        if result.returncode == 0:
            # Parse the JSON output
            metadata = json.loads(result.stdout)
            return metadata[0]  # Return the first (and only) dictionary in the list
        else:
            print(f"Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# # Example usage
# file_path = r"D:\Cloud\Life\20060531_123456.heic"
# # 20210212.MOV.jpeg"
# metadata = get_mov_metadata(file_path)
#
# if metadata:
#     print(str(metadata))
#     print("Metadata extracted successfully:")
#     # for key, value in metadata.items():
#     #     print(f"{key}: {value}")
# else:
#     print("Failed to extract metadata.")

# rename_photos(r"C:\Users\crisc\OneDrive\Pictures")
# check_files = check_videos(r"D:\Cloud\Life")
# print(check_files)
# print(len(check_files))
# check_files.sort(key=lambda x: x[1])
# with open(r'C:\Users\crisc\OneDrive\Desktop\check_photos.csv', 'w', encoding='utf-8') as f:
#     for filename, file_create_date in check_files:
#         filename = filename.split('.')[0]
#         filename_date = filename.split('_')[0].split(' ')[0].split('-')[0]
#         # delta_days = str(abs((datetime.fromisoformat(file_create_date).date() - datetime.fromisoformat(filename_date).date()).days))
#
#         f.write(";".join([
#             filename,
#             file_create_date,
#             delta_days]) + "\n")

import subprocess
import json
import os
from openpyxl import Workbook

def get_metadata(file_path):
    try:
        # Run exiftool command to get metadata in JSON format
        result = subprocess.run(
            [r'C:\Users\crisc\Downloads\exiftool-13.18_64\exiftool.exe', '-j', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Check if the command was successful
        if result.returncode == 0:
            # Parse the JSON output
            metadata = json.loads(result.stdout)
            return metadata[0]  # Return the first (and only) dictionary in the list
        else:
            print(f"Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def check_files(directory):
    check_fs = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if len(filename.split('.')) < 2:
            continue
        file_ext = filename.split('.')[-1]
        possible_dates = []
        if os.path.isfile(file_path):
            metadata = get_metadata(file_path)
            for key in metadata:
                if 'date' in key.lower():
                    possible_dates.append(metadata[key][:10].replace(':', ''))
        else:
            continue

        old_file_date = file_path.rsplit("\\")[-1].split('.')[0].split('_')[0].split(' ')[0].split('-')[0]

        dto = cd = mcd = oto = fcd = dc = ccd = date_taken = ''

        if "DateTimeOriginal" in metadata:
            date_taken = metadata["DateTimeOriginal"][:10].replace(':', '')
        elif "CreationDate" in metadata:
            date_taken = metadata["CreationDate"][:10].replace(':', '')
        elif "MediaCreateDate" in metadata:
            date_taken = metadata["MediaCreateDate"][:10].replace(':', '')
        elif "FileCreateDate" in metadata:
            date_taken = metadata["FileCreateDate"][:10].replace(':', '')
        elif "DateCreated" in metadata:
            date_taken = metadata['DateCreated'][:10].replace(':', '')
        elif "ContentCreateDate" in metadata:
            date_taken = metadata['ContentCreateDate'][:10].replace(':', '')

        if "DateTimeOriginal" in metadata:
            dto = metadata["DateTimeOriginal"]
        if "CreationDate" in metadata:
            cd = metadata["CreationDate"]
        if "MediaCreateDate" in metadata:
            mcd = metadata["MediaCreateDate"]
        if "FileCreateDate" in metadata:
            fcd = metadata["FileCreateDate"]
        if "DateCreated" in metadata:
            dc = metadata['DateCreated']
        if "ContentCreateDate" in metadata:
            ccd = metadata['ContentCreateDate']
        if "OffsetTimeOriginal" in metadata:
            oto = metadata['OffsetTimeOriginal']

        # if old_file_date == date_taken:
        #     check_flg = "no"
        # elif old_file_date in possible_dates:
        #     check_flg = "part"
        # else:
        #     check_flg = "full"

        check_fs.append((
            str(metadata),
            str(sorted(list((set(possible_dates))))),
            filename,
            fcd, cd, dto,
            dc, ccd, mcd,
            oto
        ))

    wb = Workbook()
    ws = wb.active

    ws.append([
        'metadata',
        'possible_dates',
        'filename',
        'FileCreateDate',
        'CreationDate',
        'DateTimeOriginal',
        'DateCreated',
        'ContentCreateDate',
        'MediaCreateDate',
        'OffsetTimeOriginal'
    ])
    for row in check_fs:
        ws.append(row)

    wb.save(r'C:\Users\crisc\OneDrive\Desktop\check_files_final.xlsx')

    return check_fs
# renaming should consider order of naming if
meta = get_metadata(r"C:\Users\crisc\Downloads\1000035697.jpg")

print(meta)
# meta_info = {'mp4': {'SourceFile': 58, 'ExifToolVersion': 58, 'FileName': 58, 'Directory': 58, 'FileSize': 58, 'FileModifyDate': 58, 'FileAccessDate': 58, 'FileCreateDate': 58, 'FilePermissions': 58, 'FileType': 58, 'FileTypeExtension': 58, 'MIMEType': 58, 'MajorBrand': 58, 'MinorVersion': 58, 'CompatibleBrands': 58, 'MovieHeaderVersion': 58, 'CreateDate': 58, 'ModifyDate': 58, 'TimeScale': 58, 'Duration': 58, 'PreferredRate': 58, 'PreferredVolume': 58, 'PreviewTime': 58, 'PreviewDuration': 58, 'PosterTime': 58, 'SelectionTime': 58, 'SelectionDuration': 58, 'CurrentTime': 58, 'NextTrackID': 58, 'TrackHeaderVersion': 58, 'TrackCreateDate': 58, 'TrackModifyDate': 58, 'TrackID': 58, 'TrackDuration': 58, 'TrackLayer': 58, 'TrackVolume': 58, 'ImageWidth': 58, 'ImageHeight': 58, 'GraphicsMode': 58, 'OpColor': 58, 'CompressorID': 58, 'SourceImageWidth': 58, 'SourceImageHeight': 58, 'XResolution': 58, 'YResolution': 58, 'BitDepth': 58, 'VideoFrameRate': 58, 'MatrixStructure': 58, 'MediaHeaderVersion': 58, 'MediaCreateDate': 58, 'MediaModifyDate': 58, 'MediaTimeScale': 58, 'MediaDuration': 58, 'MediaLanguageCode': 37, 'HandlerDescription': 58, 'Balance': 57, 'AudioFormat': 57, 'AudioChannels': 57, 'AudioBitsPerSample': 57, 'AudioSampleRate': 57, 'HandlerType': 58, 'HandlerVendorID': 26, 'Encoder': 26, 'MediaDataSize': 58, 'MediaDataOffset': 58, 'ImageSize': 58, 'Megapixels': 58, 'AvgBitrate': 58, 'Rotation': 58, 'ContentCreateDate': 1, 'AndroidVersion': 18, 'PixelAspectRatio': 26, 'ColorProfiles': 25, 'ColorPrimaries': 25, 'TransferCharacteristics': 25, 'MatrixCoefficients': 25, 'VideoFullRangeFlag': 25, 'DateTimeOriginal': 1, 'Author': 1, 'CompressorName': 1, 'StartTimecode': 1, 'XMPToolkit': 1, 'MetadataDate': 1, 'CreatorTool': 1, 'VideoFieldOrder': 1, 'VideoPixelAspectRatio': 1, 'AudioSampleType': 1, 'AudioChannelType': 1, 'StartTimeScale': 1, 'StartTimeSampleSize': 1, 'Orientation': 1, 'InstanceID': 1, 'DocumentID': 1, 'OriginalDocumentID': 1, 'Format': 1, 'DurationValue': 1, 'DurationScale': 1, 'ProjectRefType': 1, 'VideoFrameSizeW': 1, 'VideoFrameSizeH': 1, 'VideoFrameSizeUnit': 1, 'StartTimecodeTimeFormat': 1, 'StartTimecodeTimeValue': 1, 'AltTimecodeTimeValue': 1, 'AltTimecodeTimeFormat': 1, 'HistoryAction': 1, 'HistoryInstanceID': 1, 'HistoryWhen': 1, 'HistorySoftwareAgent': 1, 'HistoryChanged': 1, 'IngredientsInstanceID': 1, 'IngredientsDocumentID': 1, 'IngredientsFromPart': 1, 'IngredientsToPart': 1, 'IngredientsFilePath': 1, 'IngredientsMaskMarkers': 1, 'PantryAeProjectLinkRenderTimeStamp': 1, 'PantryAeProjectLinkCompositionID': 1, 'PantryAeProjectLinkRenderQueueItemID': 1, 'PantryAeProjectLinkRenderOutputModuleIndex': 1, 'PantryAeProjectLinkFullPath': 1, 'PantryGenre': 1, 'PantryVideoFrameRate': 1, 'PantryVideoFieldOrder': 1, 'PantryVideoPixelAspectRatio': 1, 'PantryProjectRefType': 1, 'PantryVideoFrameSizeW': 1, 'PantryVideoFrameSizeH': 1, 'PantryVideoFrameSizeUnit': 1, 'PantryStartTimecodeTimeFormat': 1, 'PantryStartTimecodeTimeValue': 1, 'PantryIngredientsFilePath': 1, 'PantryWindowsAtomExtension': 1, 'PantryWindowsAtomInvocationFlags': 1, 'PantryWindowsAtomUncProjectPath': 1, 'PantryMacAtomApplicationCode': 1, 'PantryMacAtomInvocationAppleEvent': 1, 'PantryGPSLatitude': 1, 'PantryGPSLongitude': 1, 'PantryStartTimeScale': 1, 'PantryStartTimeSampleSize': 1, 'PantryAltTimecodeTimeValue': 1, 'PantryAltTimecodeTimeFormat': 1, 'PantryCreatorTool': 1, 'PantryDerivedFromInstanceID': 1, 'PantryDerivedFromDocumentID': 1, 'PantryDerivedFromOriginalDocumentID': 1, 'PantryArtist': 1, 'PantryAlbum': 1, 'PantryPartOfCompilation': 1, 'PantryAudioSampleRate': 1, 'PantryAudioSampleType': 1, 'PantryAudioChannelType': 1, 'PantryTracksTrackName': 1, 'PantryTracksTrackType': 1, 'PantryTracksFrameRate': 1, 'PantryTracksMarkersStartTime': 1, 'PantryTracksMarkersGuid': 1, 'PantryTracksMarkersCuePointParamsKey': 1, 'PantryTracksMarkersCuePointParamsValue': 1, 'PantryHistoryParameters': 1, 'PantryFormat': 1, 'PantryTitle': 1, 'PantryIngredientsInstanceID': 1, 'PantryIngredientsDocumentID': 1, 'PantryIngredientsFromPart': 1, 'PantryIngredientsToPart': 1, 'PantryIngredientsMaskMarkers': 1, 'PantryCreateDate': 1, 'PantryModifyDate': 1, 'PantryMetadataDate': 1, 'PantryOrientation': 1, 'PantryInstanceID': 1, 'PantryDocumentID': 1, 'PantryOriginalDocumentID': 1, 'PantryHistoryAction': 1, 'PantryHistoryInstanceID': 1, 'PantryHistoryWhen': 1, 'PantryHistorySoftwareAgent': 1, 'PantryHistoryChanged': 1, 'PantryDurationValue': 1, 'PantryDurationScale': 1, 'DerivedFromInstanceID': 1, 'DerivedFromDocumentID': 1, 'DerivedFromOriginalDocumentID': 1, 'WindowsAtomExtension': 1, 'WindowsAtomInvocationFlags': 1, 'WindowsAtomUncProjectPath': 1, 'MacAtomApplicationCode': 1, 'MacAtomInvocationAppleEvent': 1}, 'jpg': {'SourceFile': 798, 'ExifToolVersion': 798, 'FileName': 798, 'Directory': 798, 'FileSize': 798, 'FileModifyDate': 798, 'FileAccessDate': 798, 'FileCreateDate': 798, 'FilePermissions': 798, 'FileType': 798, 'FileTypeExtension': 798, 'MIMEType': 798, 'JFIFVersion': 427, 'ResolutionUnit': 771, 'XResolution': 771, 'YResolution': 771, 'ImageWidth': 798, 'ImageHeight': 798, 'EncodingProcess': 798, 'BitsPerSample': 798, 'ColorComponents': 798, 'YCbCrSubSampling': 798, 'ImageSize': 798, 'Megapixels': 798, 'CurrentIPTCDigest': 54, 'SpecialInstructions': 5, 'ExifByteOrder': 493, 'Orientation': 426, 'ImageDescription': 116, 'Make': 396, 'Model': 396, 'Software': 386, 'ModifyDate': 397, 'YCbCrPositioning': 451, 'ExposureTime': 378, 'FNumber': 378, 'ExposureProgram': 369, 'ISO': 378, 'ExifVersion': 458, 'DateTimeOriginal': 383, 'CreateDate': 377, 'ComponentsConfiguration': 456, 'ExposureCompensation': 372, 'MeteringMode': 395, 'LightSource': 179, 'Flash': 377, 'FocalLength': 378, 'FlashpixVersion': 456, 'ColorSpace': 455, 'ExifImageWidth': 466, 'ExifImageHeight': 466, 'InteropIndex': 165, 'InteropVersion': 168, 'ExposureMode': 378, 'WhiteBalance': 378, 'DigitalZoomRatio': 129, 'SceneCaptureType': 404, 'Compression': 441, 'ThumbnailOffset': 438, 'ThumbnailLength': 438, 'Aperture': 378, 'ShutterSpeed': 378, 'ThumbnailImage': 436, 'FocalLength35efl': 378, 'LightValue': 376, 'Padding': 2, 'Warning': 113, 'UserComment': 22, 'OtherImageStart': 17, 'OtherImageLength': 17, 'Artist': 4, 'Copyright': 2, 'SensitivityType': 2, 'RecommendedExposureIndex': 2, 'ShutterSpeedValue': 367, 'ApertureValue': 358, 'MacroMode': 2, 'SelfTimer': 2, 'Quality': 2, 'CanonFlashMode': 2, 'ContinuousDrive': 2, 'FocusMode': 2, 'RecordMode': 2, 'CanonImageSize': 2, 'EasyMode': 2, 'DigitalZoom': 82, 'Contrast': 151, 'Saturation': 153, 'CameraISO': 2, 'FocusRange': 2, 'CanonExposureMode': 2, 'LensType': 2, 'MaxFocalLength': 2, 'MinFocalLength': 2, 'FocalUnits': 2, 'MaxAperture': 2, 'MinAperture': 2, 'FlashActivity': 2, 'FlashBits': 2, 'ZoomSourceWidth': 2, 'ZoomTargetWidth': 2, 'ManualFlashOutput': 2, 'ColorTone': 2, 'AutoISO': 2, 'BaseISO': 2, 'MeasuredEV': 2, 'TargetAperture': 2, 'TargetExposureTime': 2, 'SlowShutter': 2, 'SequenceNumber': 2, 'OpticalZoomCode': 2, 'CameraTemperature': 2, 'FlashGuideNumber': 2, 'FlashExposureComp': 2, 'AutoExposureBracketing': 2, 'AEBBracketValue': 2, 'ControlMode': 2, 'MeasuredEV2': 2, 'BulbDuration': 2, 'CameraType': 72, 'NDFilter': 2, 'CanonImageType': 2, 'CanonFirmwareVersion': 2, 'CameraOrientation': 82, 'FirmwareVersion': 82, 'ContrastStandard': 2, 'SharpnessStandard': 2, 'SaturationStandard': 2, 'ColorToneStandard': 2, 'ContrastPortrait': 2, 'SharpnessPortrait': 2, 'SaturationPortrait': 2, 'ColorTonePortrait': 2, 'ContrastLandscape': 2, 'SharpnessLandscape': 2, 'SaturationLandscape': 2, 'ColorToneLandscape': 2, 'ContrastNeutral': 2, 'SharpnessNeutral': 2, 'SaturationNeutral': 2, 'ColorToneNeutral': 2, 'ContrastFaithful': 2, 'SharpnessFaithful': 2, 'SaturationFaithful': 2, 'ColorToneFaithful': 2, 'ContrastMonochrome': 2, 'SharpnessMonochrome': 2, 'FilterEffectMonochrome': 2, 'ToningEffectMonochrome': 2, 'ContrastAuto': 2, 'SharpnessAuto': 2, 'SaturationAuto': 2, 'ColorToneAuto': 2, 'FilterEffectAuto': 2, 'ToningEffectAuto': 2, 'ContrastUserDef1': 2, 'SharpnessUserDef1': 2, 'SaturationUserDef1': 2, 'ColorToneUserDef1': 2, 'FilterEffectUserDef1': 2, 'ToningEffectUserDef1': 2, 'ContrastUserDef2': 2, 'SharpnessUserDef2': 2, 'SaturationUserDef2': 2, 'ColorToneUserDef2': 2, 'FilterEffectUserDef2': 2, 'ToningEffectUserDef2': 2, 'ContrastUserDef3': 2, 'SharpnessUserDef3': 2, 'SaturationUserDef3': 2, 'ColorToneUserDef3': 2, 'FilterEffectUserDef3': 2, 'ToningEffectUserDef3': 2, 'UserDef1PictureStyle': 2, 'UserDef2PictureStyle': 2, 'UserDef3PictureStyle': 2, 'CanonModelID': 2, 'ThumbnailImageValidArea': 2, 'AFAreaMode': 2, 'NumAFPoints': 2, 'ValidAFPoints': 2, 'CanonImageWidth': 2, 'CanonImageHeight': 2, 'AFImageWidth': 2, 'AFImageHeight': 2, 'AFAreaWidths': 2, 'AFAreaHeights': 2, 'AFAreaXPositions': 2, 'AFAreaYPositions': 2, 'AFPointsInFocus': 2, 'AFPointsSelected': 2, 'TimeZone': 82, 'TimeZoneCity': 2, 'DaylightSavings': 2, 'BracketMode': 2, 'BracketValue': 2, 'BracketShotNumber': 2, 'RawJpgSize': 2, 'LongExposureNoiseReduction2': 2, 'WBBracketMode': 2, 'WBBracketValueAB': 2, 'WBBracketValueGM': 2, 'LiveViewShooting': 2, 'FocusDistanceUpper': 2, 'FocusDistanceLower': 2, 'ShutterMode': 2, 'FlashExposureLock': 2, 'InternalSerialNumber': 2, 'DustRemovalData': 2, 'CropLeftMargin': 2, 'CropRightMargin': 2, 'CropTopMargin': 2, 'CropBottomMargin': 2, 'ExposureLevelIncrements': 2, 'ISOExpansion': 2, 'FlashSyncSpeedAv': 2, 'LongExposureNoiseReduction': 2, 'HighISONoiseReduction': 2, 'HighlightTonePriority': 2, 'AFAssistBeam': 2, 'ShutterButtonAFOnButton': 2, 'SetButtonWhenShooting': 2, 'FlashButtonFunction': 2, 'LCDDisplayAtPowerOn': 2, 'AspectRatio': 2, 'CroppedImageWidth': 2, 'CroppedImageHeight': 2, 'CroppedImageLeft': 2, 'CroppedImageTop': 2, 'ToneCurve': 2, 'Sharpness': 153, 'SharpnessFrequency': 2, 'SensorRedLevel': 2, 'SensorBlueLevel': 2, 'WhiteBalanceRed': 2, 'WhiteBalanceBlue': 2, 'ColorTemperature': 72, 'PictureStyle': 2, 'DigitalGain': 2, 'WBShiftAB': 2, 'WBShiftGM': 2, 'MeasuredRGGB': 2, 'VRDOffset': 2, 'SensorWidth': 2, 'SensorHeight': 2, 'SensorLeftBorder': 2, 'SensorTopBorder': 2, 'SensorRightBorder': 2, 'SensorBottomBorder': 2, 'BlackMaskLeftBorder': 2, 'BlackMaskTopBorder': 2, 'BlackMaskRightBorder': 2, 'BlackMaskBottomBorder': 2, 'ColorDataVersion': 2, 'WB_RGGBLevelsAsShot': 2, 'ColorTempAsShot': 2, 'WB_RGGBLevelsAuto': 2, 'ColorTempAuto': 2, 'WB_RGGBLevelsMeasured': 2, 'ColorTempMeasured': 2, 'WB_RGGBLevelsDaylight': 2, 'ColorTempDaylight': 2, 'WB_RGGBLevelsShade': 2, 'ColorTempShade': 2, 'WB_RGGBLevelsCloudy': 2, 'ColorTempCloudy': 2, 'WB_RGGBLevelsTungsten': 2, 'ColorTempTungsten': 2, 'WB_RGGBLevelsFluorescent': 2, 'ColorTempFluorescent': 2, 'WB_RGGBLevelsKelvin': 2, 'ColorTempKelvin': 2, 'WB_RGGBLevelsFlash': 2, 'ColorTempFlash': 2, 'AverageBlackLevel': 2, 'RawMeasuredRGGB': 2, 'PerChannelBlackLevel': 2, 'SpecularWhiteLevel': 2, 'LinearityUpperMargin': 2, 'PictureStyleUserDef': 2, 'PictureStylePC': 2, 'CustomPictureStyleFileName': 2, 'VignettingCorrVersion': 2, 'PeripheralLighting': 2, 'DistortionCorrection': 2, 'ChromaticAberrationCorr': 2, 'PeripheralLightingValue': 2, 'DistortionCorrectionValue': 2, 'OriginalImageWidth': 2, 'OriginalImageHeight': 2, 'PeripheralLightingSetting': 2, 'PeripheralIlluminationCorr': 2, 'AutoLightingOptimizer': 2, 'AmbienceSelection': 2, 'SubSecTime': 157, 'SubSecTimeOriginal': 358, 'SubSecTimeDigitized': 357, 'FocalPlaneXResolution': 2, 'FocalPlaneYResolution': 2, 'FocalPlaneResolutionUnit': 2, 'CustomRendered': 165, 'OwnerName': 2, 'SerialNumber': 91, 'LensInfo': 203, 'LensModel': 203, 'LensSerialNumber': 2, 'GPSVersionID': 3, 'Rating': 2, 'DriveMode': 2, 'Lens': 4, 'ShootingMode': 2, 'WB_RGGBLevels': 2, 'BlueBalance': 2, 'LensID': 203, 'RedBalance': 2, 'ScaleFactor35efl': 362, 'SubSecCreateDate': 357, 'SubSecDateTimeOriginal': 358, 'SubSecModifyDate': 297, 'Lens35efl': 2, 'CircleOfConfusion': 362, 'DOF': 2, 'FOV': 362, 'HyperfocalDistance': 362, 'BrightnessValue': 285, 'MakerNoteVersion': 199, 'RunTimeFlags': 199, 'RunTimeValue': 199, 'RunTimeEpoch': 199, 'RunTimeScale': 199, 'AEStable': 199, 'AETarget': 199, 'AEAverage': 199, 'AFStable': 199, 'AccelerationVector': 199, 'ImageCaptureType': 199, 'SensingMethod': 356, 'SceneType': 357, 'FocalLengthIn35mmFormat': 365, 'LensMake': 201, 'GPSLatitudeRef': 198, 'GPSLongitudeRef': 198, 'GPSAltitudeRef': 195, 'GPSTimeStamp': 119, 'GPSSpeedRef': 191, 'GPSSpeed': 191, 'GPSImgDirectionRef': 191, 'GPSImgDirection': 191, 'GPSDestBearingRef': 191, 'GPSDestBearing': 191, 'GPSDateStamp': 228, 'GPSHPositioningError': 191, 'XMPToolkit': 74, 'RegionAreaY': 68, 'RegionAreaW': 68, 'RegionAreaX': 68, 'RegionAreaH': 68, 'RegionAreaUnit': 68, 'RegionType': 68, 'RegionExtensionsAngleInfoYaw': 68, 'RegionExtensionsAngleInfoRoll': 68, 'RegionExtensionsConfidenceLevel': 68, 'RegionExtensionsTimeStamp': 48, 'RegionExtensionsFaceID': 68, 'RegionAppliedToDimensionsH': 68, 'RegionAppliedToDimensionsW': 68, 'RegionAppliedToDimensionsUnit': 68, 'RunTimeSincePowerUp': 199, 'GPSAltitude': 194, 'GPSDateTime': 119, 'GPSLatitude': 198, 'GPSLongitude': 198, 'GPSPosition': 194, 'ProfileCMMType': 100, 'ProfileVersion': 100, 'ProfileClass': 100, 'ColorSpaceData': 100, 'ProfileConnectionSpace': 100, 'ProfileDateTime': 100, 'ProfileFileSignature': 100, 'PrimaryPlatform': 100, 'CMMFlags': 100, 'DeviceManufacturer': 100, 'DeviceModel': 100, 'DeviceAttributes': 100, 'RenderingIntent': 100, 'ConnectionSpaceIlluminant': 100, 'ProfileCreator': 100, 'ProfileID': 100, 'ProfileDescription': 100, 'ProfileCopyright': 100, 'MediaWhitePoint': 100, 'MediaBlackPoint': 3, 'RedMatrixColumn': 100, 'GreenMatrixColumn': 100, 'BlueMatrixColumn': 100, 'RedTRC': 100, 'GreenTRC': 100, 'BlueTRC': 100, 'DocumentName': 78, 'MakerNoteUnknownText': 70, 'FileSource': 149, 'GainControl': 149, 'SubjectDistanceRange': 149, 'DeviceSettingDescription': 95, 'ProcessingSoftware': 1, 'About': 1, 'CreatorTool': 9, 'IPTCDigest': 49, 'SubjectArea': 168, 'LivePhotoVideoIndex': 197, 'PhotosAppFeatureFlags': 197, 'SignalToNoiseRatio': 197, 'HDRImageType': 12, 'ImageUniqueID': 9, 'DateCreated': 7, 'OffsetTime': 220, 'OffsetTimeOriginal': 219, 'OffsetTimeDigitized': 218, 'PhotoIdentifier': 138, 'ChromaticAdaptation': 76, 'ContentIdentifier': 2, 'HostComputer': 73, 'FocusPosition': 73, 'TileWidth': 16, 'TileLength': 16, 'FocusDistanceRange': 59, 'OISMode': 42, 'HDRHeadroom': 68, 'HDRGainCurve': 70, 'DisplayedUnitsX': 2, 'DisplayedUnitsY': 2, 'CodedCharacterSet': 2, 'ApplicationRecordVersion': 2, 'TimeCreated': 1, 'By-line': 2, 'Caption-Abstract': 2, 'PhotoshopThumbnail': 2, 'DeviceMfgDesc': 2, 'DeviceModelDesc': 2, 'ViewingCondDesc': 2, 'ViewingCondIlluminant': 2, 'ViewingCondSurround': 2, 'ViewingCondIlluminantType': 2, 'Luminance': 2, 'MeasurementObserver': 2, 'MeasurementBacking': 2, 'MeasurementGeometry': 2, 'MeasurementFlare': 2, 'MeasurementIlluminant': 2, 'Technology': 2, 'Format': 2, 'MetadataDate': 2, 'RawFileName': 2, 'Version': 2, 'ProcessVersion': 2, 'IncrementalTemperature': 2, 'IncrementalTint': 2, 'Exposure2012': 2, 'Contrast2012': 2, 'Highlights2012': 2, 'Shadows2012': 2, 'Whites2012': 2, 'Blacks2012': 2, 'Texture': 2, 'Clarity2012': 2, 'Dehaze': 2, 'Vibrance': 2, 'ParametricShadows': 2, 'ParametricDarks': 2, 'ParametricLights': 2, 'ParametricHighlights': 2, 'ParametricShadowSplit': 2, 'ParametricMidtoneSplit': 2, 'ParametricHighlightSplit': 2, 'SharpenRadius': 2, 'SharpenDetail': 2, 'SharpenEdgeMasking': 2, 'LuminanceSmoothing': 2, 'ColorNoiseReduction': 2, 'ColorNoiseReductionDetail': 2, 'ColorNoiseReductionSmoothness': 2, 'HueAdjustmentRed': 2, 'HueAdjustmentOrange': 2, 'HueAdjustmentYellow': 2, 'HueAdjustmentGreen': 2, 'HueAdjustmentAqua': 2, 'HueAdjustmentBlue': 2, 'HueAdjustmentPurple': 2, 'HueAdjustmentMagenta': 2, 'SaturationAdjustmentRed': 2, 'SaturationAdjustmentOrange': 2, 'SaturationAdjustmentYellow': 2, 'SaturationAdjustmentGreen': 2, 'SaturationAdjustmentAqua': 2, 'SaturationAdjustmentBlue': 2, 'SaturationAdjustmentPurple': 2, 'SaturationAdjustmentMagenta': 2, 'LuminanceAdjustmentRed': 2, 'LuminanceAdjustmentOrange': 2, 'LuminanceAdjustmentYellow': 2, 'LuminanceAdjustmentGreen': 2, 'LuminanceAdjustmentAqua': 2, 'LuminanceAdjustmentBlue': 2, 'LuminanceAdjustmentPurple': 2, 'LuminanceAdjustmentMagenta': 2, 'SplitToningShadowHue': 2, 'SplitToningShadowSaturation': 2, 'SplitToningHighlightHue': 2, 'SplitToningHighlightSaturation': 2, 'SplitToningBalance': 2, 'ColorGradeMidtoneHue': 2, 'ColorGradeMidtoneSat': 2, 'ColorGradeShadowLum': 2, 'ColorGradeMidtoneLum': 2, 'ColorGradeHighlightLum': 2, 'ColorGradeBlending': 2, 'ColorGradeGlobalHue': 2, 'ColorGradeGlobalSat': 2, 'ColorGradeGlobalLum': 2, 'AutoLateralCA': 2, 'LensProfileEnable': 2, 'LensManualDistortionAmount': 2, 'VignetteAmount': 2, 'DefringePurpleAmount': 2, 'DefringePurpleHueLo': 2, 'DefringePurpleHueHi': 2, 'DefringeGreenAmount': 2, 'DefringeGreenHueLo': 2, 'DefringeGreenHueHi': 2, 'PerspectiveUpright': 2, 'PerspectiveVertical': 2, 'PerspectiveHorizontal': 2, 'PerspectiveRotate': 2, 'PerspectiveAspect': 2, 'PerspectiveScale': 2, 'PerspectiveX': 2, 'PerspectiveY': 2, 'GrainAmount': 2, 'GrainSize': 2, 'GrainFrequency': 2, 'PostCropVignetteAmount': 2, 'ShadowTint': 2, 'RedHue': 2, 'RedSaturation': 2, 'GreenHue': 2, 'GreenSaturation': 2, 'BlueHue': 2, 'BlueSaturation': 2, 'ConvertToGrayscale': 2, 'OverrideLookVignette': 2, 'ToneCurveName2012': 2, 'CameraProfile': 2, 'CameraProfileDigest': 2, 'GrainSeed': 2, 'HasSettings': 2, 'CropTop': 2, 'CropLeft': 2, 'CropBottom': 2, 'CropRight': 2, 'CropAngle': 2, 'CropConstrainToWarp': 2, 'HasCrop': 2, 'AlreadyApplied': 2, 'DocumentID': 2, 'InstanceID': 2, 'OriginalDocumentID': 2, 'Creator': 2, 'Description': 2, 'ToneCurvePV2012': 2, 'ToneCurvePV2012Red': 2, 'ToneCurvePV2012Green': 2, 'ToneCurvePV2012Blue': 2, 'HistoryAction': 2, 'HistoryParameters': 2, 'HistoryInstanceID': 2, 'HistoryWhen': 2, 'HistorySoftwareAgent': 2, 'HistoryChanged': 2, 'DerivedFrom': 2, 'DCTEncodeVersion': 2, 'APP14Flags0': 2, 'APP14Flags1': 2, 'ColorTransform': 2, 'DateTimeCreated': 1, 'AFPerformance': 2, 'CompositeImage': 3, 'SemanticStyleRenderingVer': 3, 'Mirror': 6, 'Sensor_type': 6, 'Hdr': 6, 'OpMode': 6, 'AIScene': 6, 'FilterId': 6, 'ZoomMultiple': 6, 'GPSProcessingMethod': 5, 'CompressedBitsPerPixel': 80, 'MaxApertureValue': 81, 'SubjectDistance': 80, 'ExposureIndex': 80, 'OffsetSchema': 3, 'MPFVersion': 80, 'NumberOfImages': 80, 'MPImageFlags': 80, 'MPImageFormat': 80, 'MPImageType': 80, 'MPImageLength': 80, 'MPImageStart': 80, 'DependentImage1EntryNumber': 80, 'DependentImage2EntryNumber': 80, 'ImageUIDList': 80, 'TotalFrames': 80, 'MetadataVersion': 80, 'CameraSerialNumber': 80, 'MediaUniqueID': 80, 'ChapterNumber': 80, 'AutoRotation': 80, 'DigitalZoomOn': 80, 'SpotMeter': 80, 'Protune': 80, 'ColorMode': 80, 'ExposureType': 80, 'AutoISOMax': 80, 'AutoISOMin': 80, 'Rate': 80, 'PhotoResolution': 80, 'HDRSetting': 80, 'LensProjection': 80, 'GravityVector': 80, 'ImageOrientation': 80, 'CreationDate': 80, 'ScheduleCaptureTime': 80, 'ScheduleCapture': 80, 'CaptureDelayTimer': 80, 'DurationSetting': 80, 'DigitalZoomAmount': 80, 'ControlLevel': 80, 'OrientationDataPresent': 80, 'DeviceName': 80, 'AutoBoostScore': 80, 'DiagonalFieldOfView': 80, 'FieldOfView': 80, 'MappingXMode': 80, 'MappingXCoefficients': 80, 'MappingYMode': 80, 'MappingYCoefficients': 80, 'PolynomialPower': 80, 'PolynomialCoefficients': 80, 'ZoomScaleNormalization': 80, 'AspectRatioUnwarped': 80, 'AspectRatioWarped': 80, 'PreviewImage': 80}, 'jpeg': {'SourceFile': 1, 'ExifToolVersion': 1, 'FileName': 1, 'Directory': 1, 'FileSize': 1, 'FileModifyDate': 1, 'FileAccessDate': 1, 'FileCreateDate': 1, 'FilePermissions': 1, 'FileType': 1, 'FileTypeExtension': 1, 'MIMEType': 1, 'JFIFVersion': 1, 'ResolutionUnit': 1, 'XResolution': 1, 'YResolution': 1, 'ImageWidth': 1, 'ImageHeight': 1, 'EncodingProcess': 1, 'BitsPerSample': 1, 'ColorComponents': 1, 'YCbCrSubSampling': 1, 'ImageSize': 1, 'Megapixels': 1}, 'png': {'SourceFile': 24, 'ExifToolVersion': 24, 'FileName': 24, 'Directory': 24, 'FileSize': 24, 'FileModifyDate': 24, 'FileAccessDate': 24, 'FileCreateDate': 24, 'FilePermissions': 24, 'FileType': 24, 'FileTypeExtension': 24, 'MIMEType': 24, 'ImageWidth': 24, 'ImageHeight': 24, 'BitDepth': 23, 'ColorType': 23, 'Compression': 23, 'Filter': 23, 'Interlace': 23, 'SignificantBits': 5, 'ImageSize': 24, 'Megapixels': 24, 'SRGBRendering': 16, 'XMPToolkit': 9, 'DateCreated': 9, 'UserComment': 9, 'ExifByteOrder': 18, 'Orientation': 18, 'DateTimeOriginal': 8, 'ColorSpace': 16, 'ExifImageWidth': 18, 'ExifImageHeight': 18, 'JFIFVersion': 1, 'XResolution': 1, 'YResolution': 1, 'ResolutionUnit': 1, 'CurrentIPTCDigest': 1, 'IPTCDigest': 1, 'EncodingProcess': 1, 'BitsPerSample': 1, 'ColorComponents': 1, 'YCbCrSubSampling': 1, 'ProfileName': 2, 'ProfileCMMType': 2, 'ProfileVersion': 2, 'ProfileClass': 2, 'ColorSpaceData': 2, 'ProfileConnectionSpace': 2, 'ProfileDateTime': 2, 'ProfileFileSignature': 2, 'PrimaryPlatform': 2, 'CMMFlags': 2, 'DeviceManufacturer': 2, 'DeviceModel': 2, 'DeviceAttributes': 2, 'RenderingIntent': 2, 'ConnectionSpaceIlluminant': 2, 'ProfileCreator': 2, 'ProfileID': 2, 'ProfileDescription': 2, 'ProfileCopyright': 2, 'MediaWhitePoint': 2, 'RedMatrixColumn': 2, 'GreenMatrixColumn': 2, 'BlueMatrixColumn': 2, 'RedTRC': 2, 'ChromaticAdaptation': 2, 'BlueTRC': 2, 'GreenTRC': 2}, '42': {'SourceFile': 1, 'ExifToolVersion': 1, 'FileName': 1, 'Directory': 1, 'FileSize': 1, 'FileModifyDate': 1, 'FileAccessDate': 1, 'FileCreateDate': 1, 'FilePermissions': 1, 'FileType': 1, 'FileTypeExtension': 1, 'MIMEType': 1, 'ExifByteOrder': 1, 'Make': 1, 'Model': 1, 'Orientation': 1, 'XResolution': 1, 'YResolution': 1, 'ResolutionUnit': 1, 'Software': 1, 'ModifyDate': 1, 'YCbCrPositioning': 1, 'ExposureTime': 1, 'FNumber': 1, 'ExposureProgram': 1, 'ISO': 1, 'ExifVersion': 1, 'DateTimeOriginal': 1, 'CreateDate': 1, 'ComponentsConfiguration': 1, 'MaxApertureValue': 1, 'MeteringMode': 1, 'FocalLength': 1, 'FlashpixVersion': 1, 'ColorSpace': 1, 'ExifImageWidth': 1, 'ExifImageHeight': 1, 'InteropIndex': 1, 'InteropVersion': 1, 'SceneType': 1, 'ExposureMode': 1, 'WhiteBalance': 1, 'DigitalZoomRatio': 1, 'SceneCaptureType': 1, 'GPSVersionID': 1, 'Compression': 1, 'ThumbnailOffset': 1, 'ThumbnailLength': 1, 'ImageWidth': 1, 'ImageHeight': 1, 'EncodingProcess': 1, 'BitsPerSample': 1, 'ColorComponents': 1, 'YCbCrSubSampling': 1, 'Aperture': 1, 'ImageSize': 1, 'Megapixels': 1, 'ShutterSpeed': 1, 'ThumbnailImage': 1, 'FocalLength35efl': 1, 'LightValue': 1}, 'mov': {'SourceFile': 77, 'ExifToolVersion': 77, 'FileName': 77, 'Directory': 77, 'FileSize': 77, 'FileModifyDate': 77, 'FileAccessDate': 77, 'FileCreateDate': 77, 'FilePermissions': 77, 'FileType': 77, 'FileTypeExtension': 77, 'MIMEType': 77, 'MajorBrand': 77, 'MinorVersion': 77, 'CompatibleBrands': 77, 'MediaDataSize': 77, 'MediaDataOffset': 77, 'MovieHeaderVersion': 77, 'CreateDate': 77, 'ModifyDate': 77, 'TimeScale': 77, 'Duration': 77, 'PreferredRate': 77, 'PreferredVolume': 77, 'PreviewTime': 77, 'PreviewDuration': 77, 'PosterTime': 77, 'SelectionTime': 77, 'SelectionDuration': 77, 'CurrentTime': 77, 'NextTrackID': 77, 'TrackHeaderVersion': 77, 'TrackCreateDate': 77, 'TrackModifyDate': 77, 'TrackID': 77, 'TrackDuration': 77, 'TrackLayer': 77, 'TrackVolume': 77, 'ImageWidth': 77, 'ImageHeight': 77, 'CleanApertureDimensions': 76, 'ProductionApertureDimensions': 76, 'EncodedPixelsDimensions': 76, 'GraphicsMode': 77, 'OpColor': 77, 'CompressorID': 77, 'SourceImageWidth': 77, 'SourceImageHeight': 77, 'XResolution': 77, 'YResolution': 77, 'CompressorName': 76, 'BitDepth': 77, 'VideoFrameRate': 77, 'Balance': 77, 'AudioFormat': 77, 'AudioBitsPerSample': 77, 'AudioSampleRate': 77, 'LayoutFlags': 20, 'AudioChannels': 77, 'PurchaseFileFormat': 74, 'Warning': 75, 'MatrixStructure': 77, 'ContentDescribes': 71, 'MediaHeaderVersion': 77, 'MediaCreateDate': 77, 'MediaModifyDate': 77, 'MediaTimeScale': 77, 'MediaDuration': 77, 'MediaLanguageCode': 77, 'GenMediaVersion': 75, 'GenFlags': 75, 'GenGraphicsMode': 75, 'GenOpColor': 75, 'GenBalance': 75, 'HandlerClass': 76, 'HandlerVendorID': 76, 'HandlerDescription': 77, 'MetaFormat': 75, 'HandlerType': 77, 'GPSCoordinates': 73, 'Make': 75, 'Model': 75, 'Software': 75, 'CreationDate': 75, 'ImageSize': 77, 'Megapixels': 77, 'AvgBitrate': 77, 'GPSAltitude': 73, 'GPSAltitudeRef': 73, 'GPSLatitude': 73, 'GPSLongitude': 73, 'Rotation': 77, 'GPSPosition': 73, 'ContentIdentifier': 2, 'ColorProfiles': 1, 'ColorPrimaries': 1, 'TransferCharacteristics': 1, 'MatrixCoefficients': 1, 'VideoFullRangeFlag': 1, 'PixelAspectRatio': 1, 'LocationAccuracyHorizontal': 36, 'ApplePhotosOriginatingSignature': 3, 'LensModel-eng-RU': 4, 'FocalLengthIn35mmFormat-eng-RU': 4, 'LensModel': 4, 'FocalLengthIn35mmFormat': 4, 'LensID': 4}, 'heic': {'SourceFile': 232, 'ExifToolVersion': 232, 'FileName': 232, 'Directory': 232, 'FileSize': 232, 'FileModifyDate': 232, 'FileAccessDate': 232, 'FileCreateDate': 232, 'FilePermissions': 232, 'FileType': 232, 'FileTypeExtension': 232, 'MIMEType': 232, 'MajorBrand': 232, 'MinorVersion': 232, 'CompatibleBrands': 232, 'HandlerType': 232, 'PrimaryItemReference': 232, 'MetaImageSize': 232, 'ExifByteOrder': 232, 'Make': 232, 'Model': 232, 'Orientation': 230, 'XResolution': 232, 'YResolution': 232, 'ResolutionUnit': 232, 'Software': 232, 'ModifyDate': 232, 'HostComputer': 232, 'ExposureTime': 232, 'FNumber': 232, 'ExposureProgram': 232, 'ISO': 232, 'ExifVersion': 232, 'DateTimeOriginal': 232, 'CreateDate': 232, 'OffsetTime': 232, 'OffsetTimeOriginal': 232, 'OffsetTimeDigitized': 232, 'ShutterSpeedValue': 232, 'ApertureValue': 232, 'BrightnessValue': 232, 'ExposureCompensation': 232, 'MeteringMode': 232, 'Flash': 232, 'FocalLength': 232, 'SubjectArea': 226, 'MakerNoteVersion': 232, 'RunTimeFlags': 232, 'RunTimeValue': 232, 'RunTimeScale': 232, 'RunTimeEpoch': 232, 'AEStable': 232, 'AETarget': 232, 'AEAverage': 232, 'AFStable': 232, 'AccelerationVector': 232, 'FocusDistanceRange': 221, 'ContentIdentifier': 19, 'ImageCaptureType': 232, 'LivePhotoVideoIndex': 232, 'PhotosAppFeatureFlags': 232, 'HDRHeadroom': 232, 'AFPerformance': 226, 'SignalToNoiseRatio': 232, 'PhotoIdentifier': 232, 'ColorTemperature': 232, 'CameraType': 232, 'FocusPosition': 232, 'SemanticStyleRenderingVer': 198, 'SubSecTimeOriginal': 232, 'SubSecTimeDigitized': 232, 'ColorSpace': 232, 'ExifImageWidth': 232, 'ExifImageHeight': 232, 'SensingMethod': 232, 'SceneType': 232, 'ExposureMode': 232, 'WhiteBalance': 232, 'FocalLengthIn35mmFormat': 232, 'LensInfo': 232, 'LensMake': 232, 'LensModel': 232, 'CompositeImage': 231, 'GPSLatitudeRef': 228, 'GPSLongitudeRef': 228, 'GPSAltitudeRef': 228, 'GPSSpeedRef': 228, 'GPSSpeed': 228, 'GPSImgDirectionRef': 228, 'GPSImgDirection': 228, 'GPSDestBearingRef': 228, 'GPSDestBearing': 228, 'GPSDateStamp': 226, 'GPSHPositioningError': 228, 'ProfileCMMType': 232, 'ProfileVersion': 232, 'ProfileClass': 232, 'ColorSpaceData': 232, 'ProfileConnectionSpace': 232, 'ProfileDateTime': 232, 'ProfileFileSignature': 232, 'PrimaryPlatform': 232, 'CMMFlags': 232, 'DeviceManufacturer': 232, 'DeviceModel': 232, 'DeviceAttributes': 232, 'RenderingIntent': 232, 'ConnectionSpaceIlluminant': 232, 'ProfileCreator': 232, 'ProfileID': 232, 'ProfileDescription': 232, 'ProfileCopyright': 232, 'MediaWhitePoint': 232, 'RedMatrixColumn': 232, 'GreenMatrixColumn': 232, 'BlueMatrixColumn': 232, 'RedTRC': 232, 'ChromaticAdaptation': 232, 'BlueTRC': 232, 'GreenTRC': 232, 'HEVCConfigurationVersion': 232, 'GeneralProfileSpace': 232, 'GeneralTierFlag': 232, 'GeneralProfileIDC': 232, 'GenProfileCompatibilityFlags': 232, 'ConstraintIndicatorFlags': 232, 'GeneralLevelIDC': 232, 'MinSpatialSegmentationIDC': 232, 'ParallelismType': 232, 'ChromaFormat': 232, 'BitDepthLuma': 232, 'BitDepthChroma': 232, 'AverageFrameRate': 232, 'ConstantFrameRate': 232, 'NumTemporalLayers': 232, 'TemporalIDNested': 232, 'ImageWidth': 232, 'ImageHeight': 232, 'ImageSpatialExtent': 232, 'Rotation': 232, 'ImagePixelDepth': 232, 'MediaDataSize': 232, 'MediaDataOffset': 232, 'RunTimeSincePowerUp': 232, 'Aperture': 232, 'ImageSize': 232, 'Megapixels': 232, 'ScaleFactor35efl': 232, 'ShutterSpeed': 232, 'SubSecCreateDate': 232, 'SubSecDateTimeOriginal': 232, 'SubSecModifyDate': 232, 'GPSAltitude': 228, 'GPSLatitude': 228, 'GPSLongitude': 228, 'CircleOfConfusion': 232, 'FOV': 232, 'FocalLength35efl': 232, 'GPSPosition': 228, 'HyperfocalDistance': 232, 'LightValue': 232, 'LensID': 232, 'XMPToolkit': 90, 'CreatorTool': 70, 'DateCreated': 70, 'RegionAreaY': 68, 'RegionAreaW': 68, 'RegionAreaX': 68, 'RegionAreaH': 68, 'RegionAreaUnit': 68, 'RegionType': 68, 'RegionExtensionsAngleInfoYaw': 68, 'RegionExtensionsAngleInfoRoll': 68, 'RegionExtensionsConfidenceLevel': 68, 'RegionExtensionsFaceID': 68, 'RegionAppliedToDimensionsH': 68, 'RegionAppliedToDimensionsW': 68, 'RegionAppliedToDimensionsUnit': 68, 'TileWidth': 2, 'TileLength': 2, 'OISMode': 16, 'CompositeImageCount': 16, 'CompositeImageExposureTimes': 16, 'DigitalZoomRatio': 15, 'HDRGainMapHeadroom': 33, 'HDRGainMapVersion': 33, 'HDRGain': 33, 'AFMeasuredDepth': 33, 'AFConfidence': 33, 'SemanticStyle': 33, 'GPSTimeStamp': 33, 'AuxiliaryImageType': 33, 'GPSDateTime': 33, 'IntMaxValue': 6, 'StoredFormat': 6, 'NativeFormat': 6, 'IntMinValue': 6, 'FloatMaxValue': 6, 'FloatMinValue': 6, 'IntrinsicMatrixReferenceWidth': 6, 'DepthDataVersion': 6, 'Quality': 6, 'IntrinsicMatrix': 6, 'IntrinsicMatrixReferenceHeight': 6, 'InverseLensDistortionCoefficients': 6, 'LensDistortionCenterOffsetX': 6, 'LensDistortionCoefficients': 6, 'Accuracy': 6, 'PixelSize': 6, 'Filtered': 6, 'ExtrinsicMatrix': 6, 'LensDistortionCenterOffsetY': 6, 'RenderingParameters': 6, 'SimulatedAperture': 6, 'EffectStrength': 6, 'AuxiliaryImageSubType': 6, 'PortraitEffectsMatteVersion': 6, 'SemanticSegmentationMatteVersion': 6, 'LuminanceNoiseAmplitude': 6, 'RegionExtensions': 6, 'GrayTRC': 6, 'PortraitScoreIsHigh': 2, 'PortraitScore': 2, 'Rating': 1, 'RatingPercent': 1, 'OffsetSchema': 1}}
# meta_date_info = {'mp4': {'FileModifyDate': 58, 'FileAccessDate': 58, 'FileCreateDate': 58, 'CreateDate': 58, 'ModifyDate': 58, 'TrackCreateDate': 58, 'TrackModifyDate': 58, 'MediaCreateDate': 58, 'MediaModifyDate': 58, 'ContentCreateDate': 1, 'DateTimeOriginal': 1, 'MetadataDate': 1, 'PantryCreateDate': 1, 'PantryModifyDate': 1, 'PantryMetadataDate': 1}, 'jpg': {'FileModifyDate': 798, 'FileAccessDate': 798, 'FileCreateDate': 798, 'ModifyDate': 397, 'DateTimeOriginal': 383, 'CreateDate': 377, 'SubSecCreateDate': 357, 'SubSecDateTimeOriginal': 358, 'SubSecModifyDate': 297, 'GPSDateStamp': 228, 'GPSDateTime': 119, 'ProfileDateTime': 100, 'DateCreated': 7, 'MetadataDate': 2, 'DateTimeCreated': 1, 'CreationDate': 80}, 'jpeg': {'FileModifyDate': 1, 'FileAccessDate': 1, 'FileCreateDate': 1}, 'png': {'FileModifyDate': 24, 'FileAccessDate': 24, 'FileCreateDate': 24, 'DateCreated': 9, 'DateTimeOriginal': 8, 'ProfileDateTime': 2}, '42': {'FileModifyDate': 1, 'FileAccessDate': 1, 'FileCreateDate': 1, 'ModifyDate': 1, 'DateTimeOriginal': 1, 'CreateDate': 1}, 'mov': {'FileModifyDate': 77, 'FileAccessDate': 77, 'FileCreateDate': 77, 'CreateDate': 77, 'ModifyDate': 77, 'TrackCreateDate': 77, 'TrackModifyDate': 77, 'MediaCreateDate': 77, 'MediaModifyDate': 77, 'CreationDate': 75}, 'heic': {'FileModifyDate': 232, 'FileAccessDate': 232, 'FileCreateDate': 232, 'ModifyDate': 232, 'DateTimeOriginal': 232, 'CreateDate': 232, 'GPSDateStamp': 226, 'ProfileDateTime': 232, 'SubSecCreateDate': 232, 'SubSecDateTimeOriginal': 232, 'SubSecModifyDate': 232, 'DateCreated': 70, 'GPSDateTime': 33}}
#
# for key in meta_info:
#     print(key)


#
# print(meta_date_info['jpg'])
