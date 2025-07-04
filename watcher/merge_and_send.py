#!/usr/bin/env python3

import os
import datetime
import subprocess
import requests
from .config import VIDEO_DIR, MERGED_DIR, LOG_DIR, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from .logger import setup_logger, notify_telegram
from .locale import _
from .notifications import check_storage_space, notify_file_sent

logger = setup_logger("merge_send", os.path.join(LOG_DIR, "merge_send.log"))

# Подготовка директорий
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(MERGED_DIR, exist_ok=True)

def check_video_integrity(filepath):
    """Check if video file is valid and playable"""
    try:
        cmd = ["ffprobe", "-v", "quiet", "-show_format", "-show_streams", filepath]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.returncode == 0
    except Exception as e:
        logger.warning(f"⚠️ Error checking video integrity for {filepath}: {e}")
        return False

def try_repair_video(input_path, output_path):
    """Try to repair corrupted video file"""
    logger.info(f"🔧 Attempting to repair video: {input_path}")
    try:
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-c", "copy",
            "-avoid_negative_ts", "make_zero",
            "-fflags", "+genpts",
            "-y",
            output_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0 and check_video_integrity(output_path):
            logger.info(f"✅ Successfully repaired video: {output_path}")
            return True
        else:
            logger.warning(f"❌ Failed to repair video: {input_path}")
            return False
    except Exception as e:
        logger.warning(f"⚠️ Error during video repair: {e}")
        return False

def get_video_files():
    all_files = sorted([os.path.join(VIDEO_DIR, f) for f in os.listdir(VIDEO_DIR) if f.endswith(".mp4")])
    valid_files = []
    repaired_files = []
    
    logger.info(f"🔍 Checking {len(all_files)} video files for integrity...")
    
    for filepath in all_files:
        if check_video_integrity(filepath):
            valid_files.append(filepath)
            logger.debug(f"✅ Valid: {os.path.basename(filepath)}")
        else:
            logger.warning(f"❌ Corrupted: {os.path.basename(filepath)}")
            # Try to repair the file
            repaired_path = filepath.replace(".mp4", "_repaired.mp4")
            if try_repair_video(filepath, repaired_path):
                valid_files.append(repaired_path)
                repaired_files.append(repaired_path)
                logger.info(f"🔧 Repaired and added: {os.path.basename(repaired_path)}")
            else:
                logger.error(f"💥 Cannot repair, skipping: {os.path.basename(filepath)}")
    
    logger.info(f"📊 Processing {len(valid_files)} valid videos ({len(repaired_files)} repaired)")
    return valid_files, repaired_files

def compress_video(input_path, output_path):
    logger.info(f"⚙️ Compressing file: {input_path}")
    cmd = [
        "ffmpeg",
        "-i", input_path,
        "-vcodec", "libx264",
        "-crf", "30",
        "-preset", "veryfast",
        "-acodec", "aac",
        "-b:a", "128k",
        "-y",
        output_path
    ]
    logger.debug(f"🛠️ Compression command: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=True)
        logger.info(f"✅ Compression completed: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(_("merge_failed", e.output))
        return False

def merge_videos(input_files, output_path):
    logger.info(f"⚙️ " + _("merging_videos", len(input_files)))
    list_file = os.path.join(VIDEO_DIR, "to_merge.txt")
    try:
        with open(list_file, "w") as f:
            for filepath in input_files:
                f.write(f"file '{filepath}'\n")
        logger.debug(f"📝 Merge list created: {list_file}")

        cmd = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            "-y",
            output_path
        ]
        logger.debug(f"🛠️ Merge command: {' '.join(cmd)}")
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=True)
        logger.info(_("merge_completed", output_path))
        os.remove(list_file)
        return True
    except Exception as e:
        logger.exception(_("merge_failed", str(e)))
        notify_telegram(_("merge_failed", str(e)))
        return False

def send_to_telegram(filepath):
    logger.info(f"📤 Sending to Telegram: {filepath}")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    try:
        with open(filepath, 'rb') as f:
            response = requests.post(
                url,
                data={'chat_id': TELEGRAM_CHAT_ID},
                files={'video': f}
            )
        logger.debug(f"📨 Telegram response: {response.status_code} — {response.text}")
        if response.ok:
            logger.info(_("telegram_sent", filepath))
            return True
        else:
            logger.error(_("telegram_failed", response.text))
            notify_telegram(_("telegram_failed", response.text))
            return False
    except Exception as e:
        logger.exception(_("telegram_failed", str(e)))
        return False

def clean_files(file_list):
    logger.info(f"🧹 Cleaning {len(file_list)} temporary files...")
    for f in file_list:
        try:
            os.remove(f)
            logger.debug(f"🗑️ Deleted: {f}")
        except Exception as e:
            logger.warning(f"⚠️ Could not delete {f}: {e}")

def main():
    logger.info(_("script_start"))
    
    # Check storage space before processing
    if not check_storage_space():
        logger.warning("Storage space low, but continuing with processing")
    
    valid_files, repaired_files = get_video_files()
    
    if len(valid_files) < 2:
        logger.warning(_("insufficient_files"))
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    merged_file = os.path.join(MERGED_DIR, f"merged_{timestamp}.mp4")
    compressed_file = os.path.join(MERGED_DIR, f"compressed_{timestamp}.mp4")

    if merge_videos(valid_files, merged_file):
        if compress_video(merged_file, compressed_file):
            if send_to_telegram(compressed_file):
                # Use enhanced notification
                notify_file_sent(compressed_file)
                # Clean up: remove original files and repaired files, keep merged/compressed
                files_to_clean = [f for f in valid_files if not f.endswith("_repaired.mp4")] + repaired_files + [merged_file, compressed_file]
                clean_files(files_to_clean)
            else:
                logger.warning(_("send_failed_keep_files"))
        else:
            logger.warning(_("compression_failed_no_send"))
            # Clean up repaired files even if compression failed
            if repaired_files:
                clean_files(repaired_files)
    else:
        logger.warning(_("merge_failed"))
        # Clean up repaired files even if merge failed
        if repaired_files:
            clean_files(repaired_files)

    logger.info(_("script_complete") + "\n")

if __name__ == "__main__":
    main()