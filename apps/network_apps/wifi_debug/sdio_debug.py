# TODO:
# check for MMC init errors
# check for ESP-fails-after-reboot errors
# check if any MMC activity is even present


def check_lowlevel_mmc_errors(msgs, mmc_marker = "mmc1"):
    mmc_msgs = [msg for msg in msgs if msg["message"].startswith(mmc_marker)]
    sd_init_errors = [msg for msg in mmc_msgs \
                       if "whilst initialising SDIO card" in msg["message"]
                       and "error" in msg["message"]]
    if sd_init_errors:
        return True
    else:
        return False


